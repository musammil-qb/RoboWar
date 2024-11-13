import time
import cv2
import numpy as np


from const import BLUE, GREEN, RED, SLEEP_AFTER_GOAL, YELLOW, SLEEP_AFTER_EACH_LOOP, \
    SLEEP_AFTER_MOVEMENT, SLEEP_FOR_KEY_PRESS, SLEEP_BALL_NOT_FOUND, SLEEP_BEFORE_GOAL
from targetDetection import filter_balls, choose_next_target_point
from util import draw_polygons
from edge_handling import is_point_inside_border,find_parallel_point_inside_border


target_point,selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)
        

def algorithm(detection, bot, display=True, test=False, image=False, disable_algorithm=False):
    global target_point,selected_point
    rotation_direction = None

    if display:
        cv2.namedWindow("Feed" )
        cv2.setMouseCallback("Feed",select_point)  
    goal_center_point=None
    while goal_center_point is None:
        print("getting goal center point")
        _, _, goal_center_point, _ = detection.detect_aruco()
    balls, pressed_key = None, None
    completed = False

    trimmed_field = detection.trimmed_field
    field_corners = detection.field_corners
    bot_movement_trimmed_field = detection.bot_movement_trimmed_field

    while True:
        start_time = time.time()
        if display and test:
            frame = detection.video_stream.read() 
            draw_polygons(frame, trimmed_field, BLUE)
            draw_polygons(frame, field_corners, GREEN)
            draw_polygons(frame, bot_movement_trimmed_field, RED)
            cv2.circle(frame, detection.default_point,5, GREEN, -1)
            cv2.circle(frame, detection.goal_posts['self']['post_center_point'],10, BLUE, 2)
            cv2.circle(frame, detection.goal_posts['opponent']['post_center_point'],10, BLUE, 2)
            cv2.circle(frame, detection.center_point,5, RED, -1)
            cv2.line(frame, detection.goal_posts['self']['edge_points'][0],detection.goal_posts['self']['edge_points'][1],RED, 2)
            cv2.line(frame, detection.goal_posts['opponent']['edge_points'][0],detection.goal_posts['opponent']['edge_points'][1],YELLOW, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(1)
        if completed and image:
            pressed_key = cv2.waitKey(0)
            
        if selected_point is not None:
            if display:
                cv2.circle(frame,selected_point,5,RED,5)
                cv2.imshow('Feed', frame)
                cv2.waitKey(1)
            if bot:
                bot.updatePosition()
                bot.move(selected_point)
                time.sleep(SLEEP_AFTER_MOVEMENT)
                bot.makeMovement(rotation_direction, 2000,edge_rotation=True)
            selected_point = None
    
        detection_object = detection.process_frame()
        bot_center_point, balls =  \
            detection_object['aruco']['bot_center_point'], detection_object['yolo']['balls']    
        if any([balls == [] , goal_center_point is None , bot_center_point is None]) and not disable_algorithm:
            print(f"Detection failed goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")
            time.sleep(SLEEP_BALL_NOT_FOUND)
            continue
        
        if display:
            frame =  detection.video_stream.read()
            for ball in balls:
                cv2.circle(frame, ball,10, BLUE, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(1)
        print(f"Detection results goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")

        if not disable_algorithm:
            filtered_balls, intersection_points = filter_balls(trimmed_field,balls, goal_center_point ,buffer_distance=50)
            next_target_point = choose_next_target_point(intersection_points, bot_center_point)

        if display and test and not disable_algorithm:
            for ball in filtered_balls:
                cv2.circle(frame, ball, 3, GREEN, -1)
            for possible_movement in intersection_points:
                cv2.circle(frame, possible_movement['target_point'], 5, RED, -1)
                cv2.circle(frame, possible_movement['goal_point'], 5, YELLOW, -1)
            cv2.imshow('Feed', frame)
            cv2.waitKey(1)
        if not disable_algorithm and next_target_point is not None:
            print('target locked')
            target_point = next_target_point['target_point']
            goal_point = next_target_point['goal_point']
            frame = detection.video_stream.read()
            if display:
                cv2.circle(frame, target_point, 5, BLUE, -1)
                cv2.circle(frame, goal_point, 5, GREEN, -1)
                cv2.circle(frame, target_point, 5, BLUE, -1)
                cv2.circle(frame, goal_point, 5, GREEN, -1)
                cv2.imshow('Feed', frame)
                cv2.waitKey(1)
            time.sleep(SLEEP_BEFORE_GOAL)

            if bot:
                bot.updatePosition()
                bot.move(target_point,acquire_target=True)
            time.sleep(SLEEP_AFTER_MOVEMENT)

            print("Goal reached!")
            if bot:
                bot.updatePosition()
                bot.move(goal_point,acquire_target=False)
            time.sleep(SLEEP_AFTER_MOVEMENT)

            if bot:
                bot.updatePosition()
                bot.move(target_point,acquire_target=False)
                time.sleep(SLEEP_AFTER_MOVEMENT)
            target_point, goal_point = None, None
            time.sleep(SLEEP_AFTER_GOAL)
        elif not disable_algorithm:
            # print("No extended points found within the trimmed field.")
            trimmed_field = np.array(detection.trimmed_field)
            field_corners = np.array(detection.field_corners)
            bot_offset = 1
            filtered_balls, intersection_points = filter_balls(trimmed_field,balls, goal_center_point ,buffer_distance=50, disable_filter=True)
            next_target_point = choose_next_target_point(intersection_points, bot_center_point)
            if next_target_point is not None:
                target_point = next_target_point['target_point']
                ball = next_target_point['ball']
                next_viable_point, side_name = find_parallel_point_inside_border(target_point,field_corners)
                if side_name == "right" or side_name == "left":
                    midpoint = (int((next_viable_point[0] + ball[0])/2), int((next_viable_point[1] + ball[1])/2))
                    midpoint = next_viable_point + bot_offset * np.array([1,1])
                    edge_point = (int(midpoint[0]), int(midpoint[1]))
                    rotation_direction = 'right' if side_name=='bottom' else 'left'
                    if display:
                        frame = detection.video_stream.read()
                        cv2.circle(frame, edge_point, 5, RED, -1)
                        cv2.imshow('Feed',frame)
                        cv2.waitKey(1)
                    if bot_center_point is None:
                        print("Bot not found interrupt")
                        continue
                    if bot:
                        bot.updatePosition()
                        bot.move(edge_point)
                        time.sleep(SLEEP_AFTER_MOVEMENT)
                        bot.makeMovement(rotation_direction, 2000,edge_rotation=True)
                else:
                    print("No possible shots found")

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
                    cv2.waitKey(1)

                elif display:
                    print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
                    frame = detection.video_stream.read()
                    cv2.circle(frame,bot_center_point,5,GREEN,-1)
                    cv2.imshow('Feed',frame)
                    cv2.waitKey(1)
                time.sleep(SLEEP_AFTER_EACH_LOOP)

            

        completed = True