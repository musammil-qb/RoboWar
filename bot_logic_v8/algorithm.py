import time
import cv2

from targetDetection import filter_balls, choose_next_target_point
from util import draw_polygons, calculate_distance
from edge_logic_new import find_target_and_direction,edge_move
from random_movement_points import random_movement_algorithm, get_defense_points
from score_goal import score_goal
from defense import check_defense_needed, execute_defense
from sweep_corners import find_sweep_movements, sweep, find_best_sweep_movement
from const import BLUE, GREEN, RED,  YELLOW, \
    SLEEP_AFTER_MOVEMENT, SLEEP_FOR_KEY_PRESS, SLEEP_BALL_NOT_FOUND, \
    EXTENDED_POINT_OFFSET, EDGE_BALL_ROTATION_DISTANCE, SLEEP_AFTER_DISPLAYING,\
    EDGE_BALL_MOVEMENT_DISTANCE, SLEEP_AFTER_DEFENSE, \
    NO_DEFENSE_MOVE_WITH_NO_TARGET_BALLS, DEFENSE_MODE, \
    EDGE_ROTATION_DELAY, DEFENSE_COOLDOWN


target_point = None

def algorithm(detection, bot, display=True, test=False, image=False, disable_algorithm=False):
    """
    Main algorithm for robot soccer system.
    
    Key decisions and rationale:
    1. Edge handling first - Prioritizes edge cases to prevent balls from going out of bounds
    2. Defense mechanism - Implements defense strategy when opponent is threatening
    3. Weighted movement - Uses progressive corrections for more precise movements
    4. Ball filtering - Filters balls to only consider valid targets within play area
    5. Multiple strategies - Supports different play strategies (sweep, edge, etc.)
    
    The algorithm follows this priority:
    -  Scoring > Defense > Edge handling > Sweeping
    """
    global target_point
    edge_movement_direction, defense_start_time = None, None
    
    # Initialize sweep movements - Pre-calculated paths for ball collection
    sweep_movements = find_sweep_movements(detection)

    # Get key field positions - Cached for efficiency
    goal_center_point = detection.goal_posts['opponent']['post_center_point']
    self_goal_center_point = detection.goal_posts['self']['post_center_point']
    opponent_edge = detection.goal_posts['opponent']['edge']
    self_edge = detection.goal_posts['self']['edge']

    balls, pressed_key = None, None

    # Get field boundaries - Used for movement constraints
    trimmed_field = detection.trimmed_field
    field_corners = detection.field_corners
    bot_movement_trimmed_field = detection.bot_movement_trimmed_field
    
    # Get defense points - Pre-calculated defensive positions
    defense_point_1, defense_point_2, defense_center = get_defense_points(detection)
    
    # Strategy selection - Allows dynamic switching between play styles
    strategy = input("Enter strategy (o: offensive-first, d: defensive-first, s: sweep, e: edge): ").lower()
    if strategy == "":
        strategy = "oe"
    # Edge counter - Prevents infinite edge handling loops
    edge_counter = 0
    
    while True:
        # Initialize variables for each iteration
        filtered_balls, intersection_points = [], []
        next_target_point = None
        
        # Display field and markers if in test mode
        if display and test:
            frame = detection.video_stream.read() 
            draw_polygons(frame, trimmed_field, BLUE)
            draw_polygons(frame, field_corners, GREEN)
            draw_polygons(frame, bot_movement_trimmed_field, RED)
            cv2.circle(frame, detection.default_point,5, GREEN, -1)
            cv2.circle(frame, detection.goal_posts['self']['post_center_point'],10, BLUE, 2)
            cv2.circle(frame, goal_center_point,10, BLUE, 2)
            cv2.circle(frame, detection.center_point,5, RED, -1)
            cv2.line(frame, *detection.goal_posts['self']['goal_post_end_points'],RED, 2)
            cv2.line(frame, *detection.goal_posts['opponent']['goal_post_end_points'],YELLOW, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)

        # Process current frame and detect objects
        detection_object = detection.process_frame()
        bot_center_point, balls = detection_object['aruco']['bot_center_point'], detection_object['yolo']['balls']
        opponent_bot = detection_object['aruco']['opponent_bot']
        
        bot.updatePosition(bot_center_point,detection_object['aruco']['bot_angle'])
            
            
        # Handle case when no balls are detected
        if balls == []:
            print(f"Detection failed goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")
            if not pressed_key:
                pressed_key = cv2.waitKey(SLEEP_BALL_NOT_FOUND)
                continue
                
        # Display detected balls in test mode
        if display and test:
            frame =  detection.video_stream.read()
            for ball in balls:
                cv2.circle(frame, ball,10, BLUE, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            
        print(f"Detection results goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")

        # Main algorithm logic
        if not disable_algorithm and balls:
            # Filter balls and find potential target points
            filtered_balls, intersection_points = filter_balls(
                trimmed_field, balls, goal_center_point,
                buffer_distance=int(EXTENDED_POINT_OFFSET*detection.cm_to_pixel_rate))
            next_target_point = choose_next_target_point(intersection_points, bot_center_point,opponent_bot,goal_center_point,detection,test)


            # Check if defense is needed
            defense_needed, defense_ball, defense_start_time = check_defense_needed(opponent_bot, balls, detection, defense_start_time)
            
            # Implement strategy-based decision making
            if 'o' in strategy:  # Offensive-first strategy
                # First check if there's an ongoing defense within cooldown
                if defense_start_time is not None and defense_needed:
                    execute_defense(bot, opponent_bot, balls, defense_ball, self_goal_center_point, 
                                 defense_point_1, detection, display, "continuing defense within cooldown")
                    continue
                
                # Then try to score if possible (even if defense is needed but not started)
                if next_target_point is not None:
                    score_goal(next_target_point, detection, bot, bot_center_point, bot_movement_trimmed_field, goal_center_point, opponent_bot, display=True)
                    continue
                
                # If no scorable ball and defense is needed, start defense
                elif defense_needed:
                    defense_start_time = time.time()
                    execute_defense(bot, opponent_bot, balls, defense_ball, self_goal_center_point, 
                                 defense_point_1, detection, display, "starting new defense - no scorable balls")
                    continue
            
            elif 'd' in strategy:  # Defensive-first strategy
                # Always check defense first (cooldown is handled by check_defense_needed)
                if defense_needed:
                    execute_defense(bot, opponent_bot, balls, defense_ball, self_goal_center_point, 
                                 defense_point_1, detection, display)
                    continue
                
                # If no defense needed, try to score
                elif next_target_point is not None:
                    score_goal(next_target_point, detection, bot, bot_center_point, bot_movement_trimmed_field, goal_center_point, opponent_bot, display=True)
                    continue
            
            # If no primary actions (score/defend) are possible, use secondary strategies
            print("no primary actions possible, trying secondary strategies")
            
            # Execute sweep strategy if selected
            if "s" in strategy:
                print("sweeping")
                best_sweep_movement, sweep_balls = find_best_sweep_movement(sweep_movements, balls, detection.cm_to_pixel_rate,detection)
                sweep(detection, best_sweep_movement, bot, opponent_bot, display, sweep_balls)
            else:
                edge_counter += 1
                print("Targeting edge ball")
                if balls and bot_center_point:
                    edge_move(balls, bot_center_point, field_corners, goal_center_point, 
                                self_goal_center_point, self_edge, opponent_edge,detection,bot,opponent_bot,display=True)
                else:
                    print("No possible movement found")

        
        if display and test and not disable_algorithm:
            for ball in filtered_balls:
                cv2.circle(frame, ball, 3, GREEN, -1)
            for possible_movement in intersection_points:
                cv2.circle(frame, possible_movement['target_point'], 5, RED, -1)
                cv2.circle(frame, possible_movement['goal_point'], 5, YELLOW, -1)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        
        print("loop end")
        if image:
            pressed_key = cv2.waitKey(0)
        if not pressed_key:
            print("waiting for key interrupt")
            pressed_key = cv2.waitKey(SLEEP_FOR_KEY_PRESS)
        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('i'):
            input("waiting for interrupt")
