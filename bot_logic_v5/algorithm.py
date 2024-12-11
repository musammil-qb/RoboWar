import time
import cv2
from random import randint

from targetDetection import filter_balls, choose_next_target_point
from util import draw_polygons, calculate_distance, is_ball_moved
from edge_logic_new import find_target_and_direction
from random_movement_points import get_forward_goal_point, get_defense_points
from collision_avoidance import find_pit_stop_to_avoid_ball, is_collision_chance_closest_point

from const import BLUE, GREEN, RED, SLEEP_AFTER_GOAL, YELLOW, SLEEP_AFTER_EACH_LOOP, \
    SLEEP_AFTER_MOVEMENT, SLEEP_FOR_KEY_PRESS, SLEEP_BALL_NOT_FOUND, SLEEP_BEFORE_GOAL,\
    EXTENDED_POINT_OFFSET, EDGE_BALL_ROTATION_DISTANCE, SLEEP_AFTER_DISPLAYING,\
    EDGE_BALL_MOVEMENT_DISTANCE, SLEEP_AFTER_DEFENSE,RANDOM_MOVEMENT_DELAY_RANGE,\
    RANDOM_MOVEMENT_SPEED, RANDOM_MOVEMENT_DIRECTIONS, GREY, FORWARD_MOVEMENT_DELAY,\
    IS_ARUCO_WORKING, DEFENCE_INITIAL_MOVEMENTS, DEFENCE_LOOP_MOVEMENTS,\
    NO_DEFENCE_MOVE_WITH_NO_TARGET_BALLS


target_point,selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)
        

def algorithm(detection, bot, display=True, test=False, image=False, disable_algorithm=False):
    global target_point,selected_point
    edge_movement_direction = None

    if display:
        cv2.namedWindow("Feed" )
        cv2.setMouseCallback("Feed",select_point)  
    goal_center_point = detection.goal_posts['opponent']['post_center_point']
    self_goal_center_point = detection.goal_posts['self']['post_center_point']
    opponent_edge = detection.goal_posts['opponent']['edge']
    self_edge = detection.goal_posts['self']['edge']

    balls, pressed_key = None, None

    trimmed_field = detection.trimmed_field
    field_corners = detection.field_corners
    bot_movement_trimmed_field = detection.bot_movement_trimmed_field
    strategy = input("Enter staring strategy to start: ")
    if strategy =='f':
        frame = detection.video_stream.read()
        # if arucode works
        if IS_ARUCO_WORKING:
            initial_movement_point = get_forward_goal_point(detection)
            bot.updatePosition()
            bot.move(initial_movement_point,acquire_target=False)
            bot.updatePosition()
            bot.move(detection.default_point,acquire_target=False)
        else:
            # bot
            bot.makeMovement('forward',FORWARD_MOVEMENT_DELAY)
            bot.makeMovement('backward',FORWARD_MOVEMENT_DELAY)
        cv2.imshow('Feed', frame)
        cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    elif strategy == 'd':
        if IS_ARUCO_WORKING:
            frame = detection.video_stream.read()
            defense_point_1, defense_point_2 = get_defense_points(detection)
            cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
            cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            while True:
                bot.updatePosition()
                bot.move(defense_point_1, acquire_target=False)
                bot.updatePosition()
                bot.move(defense_point_2, acquire_target=False)
                bot.updatePosition()
                bot.move(detection.default_point, acquire_target=False)
                bot.updatePosition()
                time.sleep(SLEEP_AFTER_DEFENSE)
        else:
            frame = detection.video_stream.read()
            defense_point_1, defense_point_2 = get_defense_points(detection)
            cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
            cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[0])
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[1])
            while True:
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[0])
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[1])
                bot.move(detection.default_point)      
                time.sleep(SLEEP_AFTER_DEFENSE)

    elif strategy == 'r':
        bot.setSpeed(RANDOM_MOVEMENT_SPEED)
        while True:
            random_movement = RANDOM_MOVEMENT_DIRECTIONS[randint(0,len(RANDOM_MOVEMENT_DIRECTIONS)-1)]
            random_delay = randint(*RANDOM_MOVEMENT_DELAY_RANGE)
            bot.makeMovement(random_movement, random_delay)
            time.sleep(SLEEP_AFTER_MOVEMENT)

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
                buffer_distance=int(EXTENDED_POINT_OFFSET*detection.cm_pixel_rate))
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
            print('target locked')
            target_point = next_target_point['target_point']
            goal_point = next_target_point['goal_point']
            ball = next_target_point['ball']
            if display:
                frame = detection.video_stream.read()
                cv2.circle(frame, target_point, 5, BLUE, -1)
                cv2.circle(frame, goal_point, 5, GREEN, -1)
                cv2.imshow('Feed', frame)
                cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            time.sleep(SLEEP_BEFORE_GOAL)
            is_collision_chance, closest_point_on_line = is_collision_chance_closest_point(
                bot_center_point, target_point, ball, detection.cm_pixel_rate)
            if is_collision_chance:
                pit_stop = find_pit_stop_to_avoid_ball(
                    bot_center_point, target_point, closest_point_on_line, bot_movement_trimmed_field, detection.cm_pixel_rate)
            if is_collision_chance:
                    cv2.circle(frame, (int(pit_stop[0]),int(pit_stop[1])), 5, RED, -1)
                    cv2.circle(frame, target_point, 5, YELLOW, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            if bot and not is_collision_chance:
                if display:
                    cv2.circle(frame, target_point, 5, YELLOW, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                bot.updatePosition()
                bot.move(target_point,acquire_target=True)
            elif bot:
                bot.updatePosition()
                bot.move(pit_stop,acquire_target=False)
                time.sleep(SLEEP_AFTER_MOVEMENT)
                bot.updatePosition()
                bot.move(target_point,acquire_target=True)
            time.sleep(SLEEP_AFTER_MOVEMENT)

            # input("test ball movement:")
            detection_object = detection.process_frame()
            if is_ball_moved(detection_object['yolo']['balls'], ball,detection.cm_pixel_rate):
                # abort
                print("ball moved")
                continue
            if bot:
                if display:
                    # frame = detection.video_stream.read()
                    cv2.circle(frame, target_point, 5, YELLOW, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                bot.updatePosition(detection_object['aruco']['bot_center_point'],
                               detection_object['aruco']['bot_angle'])
                bot.move(goal_center_point,orient_only=True)
            time.sleep(SLEEP_AFTER_MOVEMENT)
            # input("test ball movement:")
            detection_object = detection.process_frame()
            if is_ball_moved(detection_object['yolo']['balls'], ball,detection.cm_pixel_rate):
                # abort
                print("ball moved")
                continue
            if bot:
                if display:
                    # frame = detection.video_stream.read()
                    cv2.circle(frame, goal_point, 5, YELLOW, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                bot.updatePosition(detection_object['aruco']['bot_center_point'],
                               detection_object['aruco']['bot_angle'])
                bot.move(goal_point,ram=True)
            time.sleep(SLEEP_AFTER_MOVEMENT)
            print("Goal reached!")

            # Coming back to target point to avoid self goal
            if bot:
                if display:
                    # frame = detection.video_stream.read()
                    cv2.circle(frame, target_point, 5, YELLOW, -1)
                    cv2.imshow('Feed', frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                bot.updatePosition()
                bot.move(target_point,acquire_target=False)
                time.sleep(SLEEP_AFTER_MOVEMENT)
            target_point, goal_point = None, None
            time.sleep(SLEEP_AFTER_GOAL)
            edge_counter = 0
        elif strategy == 'c':
            bot.move(detection.default_point)
            frame = detection.video_stream.read()
            defense_point_1, defense_point_2 = get_defense_points(detection)
            cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
            cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[0])
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[1])
            for _ in range(NO_DEFENCE_MOVE_WITH_NO_TARGET_BALLS):
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[0])
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[1])
                bot.move(detection.default_point, acquire_target=False)
                time.sleep(SLEEP_AFTER_DEFENSE)
        elif not disable_algorithm and next_target_point is None and edge_counter <=5:
            edge_counter += 1
            print("Targeting edge ball")
            if balls and bot_center_point:
                closest_ball = min(balls, key=lambda ball: calculate_distance(ball, bot_center_point))
                target_point, edge_movement_direction = find_target_and_direction(
                    field_corners, closest_ball, goal_center_point,self_goal_center_point, self_edge, opponent_edge,
                    detection.cm_pixel_rate * EDGE_BALL_ROTATION_DISTANCE, detection.cm_pixel_rate * EDGE_BALL_MOVEMENT_DISTANCE
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
                        bot.makeMovement(edge_movement_direction, 2000,edge_rotation=True)
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
        elif pressed_key == ord('f'):
            print("finding bot")
            bot_angle =None
            while True:
                bot_angle, bot_center_point, _, _ = detection.detect_aruco()
                if bot_angle is None and display:
                    print("Bot not found retrying")
                    cv2.circle(frame,bot_center_point,5,RED,-1)
                    cv2.imshow('Feed',frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                elif display:
                    print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
                    frame = detection.video_stream.read()
                    cv2.circle(frame,bot_center_point,5,GREEN,-1)
                    cv2.imshow('Feed',frame)
                    cv2.waitKey(SLEEP_AFTER_DISPLAYING)
                time.sleep(SLEEP_AFTER_EACH_LOOP)

