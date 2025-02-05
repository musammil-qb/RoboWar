import time
import cv2

from targetDetection import filter_balls, choose_next_target_point
from util import draw_polygons, calculate_distance
from edge_logic_new import find_target_and_direction,edge_move
from random_movement_points import random_movement_algorithm, get_defense_points
from score_goal import score_goal
from defense import calculate_blocking_point
from sweep_corners import find_sweep_movements, sweep, find_best_sweep_movement
from const import BLUE, GREEN, RED,  YELLOW, \
    SLEEP_AFTER_MOVEMENT, SLEEP_FOR_KEY_PRESS, SLEEP_BALL_NOT_FOUND, \
    EXTENDED_POINT_OFFSET, EDGE_BALL_ROTATION_DISTANCE, SLEEP_AFTER_DISPLAYING,\
    EDGE_BALL_MOVEMENT_DISTANCE, SLEEP_AFTER_DEFENSE, \
    NO_DEFENSE_MOVE_WITH_NO_TARGET_BALLS, DEFENSE_MODE, \
    EDGE_ROTATION_DELAY, DEFENSE_COOLDOWN


target_point,selected_point = None, None

def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)

def algorithm(detection, bot, display=True, test=False, image=False, disable_algorithm=False):
    global target_point,selected_point
    edge_movement_direction, defense_start_time = None, None
    sweep_movements = find_sweep_movements(detection)

    if display:
        cv2.namedWindow("Feed")
        cv2.setMouseCallback("Feed",select_point)

    goal_center_point = detection.goal_posts['opponent']['post_center_point']
    self_goal_center_point = detection.goal_posts['self']['post_center_point']
    opponent_edge = detection.goal_posts['opponent']['edge']
    self_edge = detection.goal_posts['self']['edge']

    balls, pressed_key = None, None

    trimmed_field = detection.trimmed_field
    field_corners = detection.field_corners
    bot_movement_trimmed_field = detection.bot_movement_trimmed_field
    defense_point_1, defense_point_2, defense_center = get_defense_points(detection)
    strategy = input("Enter staring strategy to start: ")
    # random_movement_algorithm(detection, bot, strategy,defense_point_1,defense_point_2, defense_center)
    edge_counter = 0
    while True:
        filtered_balls, intersection_points = [], []
        next_target_point = None
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
        if selected_point is not None:
            if display:
                cv2.circle(frame,selected_point,5,RED,5)
                cv2.imshow('Feed', frame)
                cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            if bot:
                bot.updatePosition()
                bot.move(selected_point)
                time.sleep(SLEEP_AFTER_MOVEMENT)
            selected_point = None

        detection_object = detection.process_frame()
        bot_center_point, balls = detection_object['aruco']['bot_center_point'], detection_object['yolo']['balls']
        opponent_bot = detection_object['aruco']['opponent_bot']
        if not bot_center_point and bot:
            bot.updatePosition(detection_object['aruco']['bot_center_point'],
                               detection_object['aruco']['bot_angle'])
            bot_center_point = bot.position
        if balls == []:
            print(f"Detection failed goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")
            if not pressed_key:
                pressed_key = cv2.waitKey(SLEEP_BALL_NOT_FOUND)
                continue
        if display and test:
            frame =  detection.video_stream.read()
            for ball in balls:
                cv2.circle(frame, ball,10, BLUE, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        print(f"Detection results goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")

        if not disable_algorithm and balls:
            filtered_balls, intersection_points = filter_balls(
                trimmed_field, balls, goal_center_point,
                buffer_distance=int(EXTENDED_POINT_OFFSET*detection.cm_to_pixel_rate))
            next_target_point = choose_next_target_point(intersection_points, bot_center_point)
            
            if next_target_point is not None:
                if not score_goal(next_target_point, detection, bot, bot_center_point, bot_movement_trimmed_field, goal_center_point, edge_counter, display=True):
                    continue
            else:
                print("no target balls")
                defense_needed = False
                if opponent_bot:
                    # Check if any balls are within 50cm of opponent bot
                    balls_near_opponent, defense_ball = False, None
                    for defense_ball in balls:
                        if calculate_distance(opponent_bot, defense_ball) < 50 * detection.cm_to_pixel_rate:
                            balls_near_opponent = True
                            defense_needed = True
                            break
                    
                    # Only maintain cooldown if balls are near opponent
                    if defense_start_time is not None and current_time - defense_start_time <= DEFENSE_COOLDOWN:
                        if balls_near_opponent:
                            defense_needed = True
                        else:
                            defense_start_time = None  # Reset cooldown if no balls near opponent
                else:
                    print("no opponent bot")
                if display:
                    frame = detection.video_stream.read()
                    for ball in balls:
                        if ball == defense_ball:
                            cv2.circle(frame, ball, 5, RED, -1)
                        else:
                            cv2.circle(frame, ball, 5, BLUE, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)

                if defense_needed:
                    current_time = time.time()
                    if defense_start_time is None:
                        defense_start_time = current_time
                        
                    if current_time - defense_start_time <= DEFENSE_COOLDOWN:
                        print(f"defending (cooldown: {DEFENSE_COOLDOWN - (current_time - defense_start_time):.1f}s remaining)")
                    else:
                        defense_start_time = None
                        
                    point_of_intercept = calculate_blocking_point(
                        opponent_bot, self_goal_center_point, detection.cm_to_pixel_rate)
                    if not point_of_intercept:
                        bot.updatePosition()
                        bot.move(defense_point_1, acquire_target=False)
                        point_of_intercept = detection.default_point
                    
                    bot.updatePosition()
                    bot.move(point_of_intercept, acquire_target=False)
                    
                elif "s" in strategy:
                    print("sweeping")
                    best_sweep_movement = find_best_sweep_movement(sweep_movements, balls, detection.cm_to_pixel_rate)
                    sweep(detection, best_sweep_movement, bot, display)
                else:
                    edge_counter += 1
                    print("Targeting edge ball")
                    if balls and bot_center_point:
                        edge_move(balls, bot_center_point, field_corners, goal_center_point, 
                                  self_goal_center_point, self_edge, opponent_edge,detection,bot,display=True)
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
        if not disable_algorithm and next_target_point is None and strategy == "e" and edge_counter <=5:
            edge_counter += 1
            print("Targeting edge ball")
            if balls and bot_center_point:
                closest_ball = min(balls, key=lambda ball: calculate_distance(ball, bot_center_point))
                target_point, edge_movement_direction = find_target_and_direction(
                    field_corners, closest_ball, goal_center_point,self_goal_center_point, self_edge, opponent_edge,
                    detection.cm_to_pixel_rate * EDGE_BALL_ROTATION_DISTANCE, detection.cm_to_pixel_rate * EDGE_BALL_MOVEMENT_DISTANCE
                )
                if display:
                    frame = detection.video_stream.read()
                    cv2.circle(frame, target_point, 5, YELLOW, -1)
                    cv2.putText(frame, str(edge_movement_direction), target_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 2)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                if bot:
                    bot.updatePosition()
                    bot.move(target_point)
                    time.sleep(SLEEP_AFTER_MOVEMENT)
                    if edge_movement_direction in ["right","left"]:
                        bot.makeMovement(edge_movement_direction, {"delay": EDGE_ROTATION_DELAY},edge_rotation=True)
                    else:
                        bot.move(closest_ball)
                        bot.updatePosition()
            else:
                print("No possible shots found")
        elif strategy == "e":
            print("go to default location")
            bot.updatePosition()
            bot.move(detection.default_point)
            edge_counter = 0
        
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
