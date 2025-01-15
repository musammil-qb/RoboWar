import time
import cv2

from targetDetection import filter_balls, choose_next_target_point
from util import draw_polygons, calculate_distance
from edge_logic_new import find_target_and_direction
from random_movement_points import random_movement_algorithm, get_defense_points
from score_goal import score_goal
from defense import calculate_blocking_point
from sweep_corners import find_sweep_corner_points, sweep
from const import BLUE, GREEN, RED,  YELLOW, \
    SLEEP_AFTER_MOVEMENT, SLEEP_FOR_KEY_PRESS, SLEEP_BALL_NOT_FOUND, \
    EXTENDED_POINT_OFFSET, EDGE_BALL_ROTATION_DISTANCE, SLEEP_AFTER_DISPLAYING,\
    EDGE_BALL_MOVEMENT_DISTANCE, SLEEP_AFTER_DEFENSE, \
    NO_DEFENSE_MOVE_WITH_NO_TARGET_BALLS, DEFENSE_MODE, \
    EDGE_ROTATION_DELAY


target_point,selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)

def algorithm(detection, bot, display=True, test=False, image=False, disable_algorithm=False):
    global target_point,selected_point
    edge_movement_direction = None
    sweep_movements = find_sweep_corner_points(detection)
    sweep_position = 0

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
    random_movement_algorithm(detection, bot, strategy,defense_point_1,defense_point_2, defense_center)
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
        bot_center_point, balls = \
            detection_object['aruco']['bot_center_point'], detection_object['yolo']['balls']    
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

        if display and test and not disable_algorithm:
            for ball in filtered_balls:
                cv2.circle(frame, ball, 3, GREEN, -1)
            for possible_movement in intersection_points:
                cv2.circle(frame, possible_movement['target_point'], 5, RED, -1)
                cv2.circle(frame, possible_movement['goal_point'], 5, YELLOW, -1)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        if not disable_algorithm and next_target_point is not None:
            if not score_goal(next_target_point, detection, bot, bot_center_point, bot_movement_trimmed_field, goal_center_point, display=True):
                continue
        elif strategy == 'c':
            if DEFENSE_MODE == 2:
                bot.move(detection.default_point)
                frame = detection.video_stream.read()
                defense_point_1, defense_point_2, defense_center = get_defense_points(detection)
                cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
                cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
                cv2.imshow('Feed', frame)
                cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                for _ in range(NO_DEFENSE_MOVE_WITH_NO_TARGET_BALLS):
                    bot.updatePosition()
                    bot.move(defense_point_1, acquire_target=False)
                    bot.updatePosition()
                    bot.move(defense_point_2, acquire_target=False)
                    bot.updatePosition()
                    bot.move(defense_center, acquire_target=False)
                    time.sleep(SLEEP_AFTER_DEFENSE)
            else:
                opponent_bot = detection_object['aruco']['opponent_bot']
                if not opponent_bot:
                    print("opponent bot not found")
                    continue
                frame = detection.video_stream.read()
                # detection_object = detection.process_frame()

                point_of_intercept = calculate_blocking_point(
                opponent_bot, self_goal_center_point, detection.cm_to_pixel_rate)
                if not point_of_intercept:
                    bot.updatePosition()
                    bot.move(defense_point_1, acquire_target=False)
                    point_of_intercept = detection.default_point
                print("intercepting...")
                cv2.circle(frame, point_of_intercept, 5, YELLOW, -1)
                cv2.imshow('Feed', frame)
                cv2.waitKey(1)
                bot.updatePosition()
                bot.move(point_of_intercept, acquire_target=False)
        elif strategy == 's':
            sweep(detection,sweep_movements[sweep_position],bot,display)
            if sweep_position<5:
                sweep_position+=1
            else:
                sweep_position = 0
            
        elif not disable_algorithm and next_target_point is None and edge_counter <=5:
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
                        bot.makeMovement(edge_movement_direction, EDGE_ROTATION_DELAY,edge_rotation=True)
                    else:
                        bot.move(closest_ball)
                        bot.updatePosition()
            else:
                print("No possible shots found")
        else:
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
