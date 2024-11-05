import time
import cv2
import numpy as np


from const import BLUE, GREEN, RED, DELAY_AFTER_GOAL, YELLOW, DELAY_AFTER_MOVEMENT
from targetDetection import filter_balls, choose_next_target_point
from util import draw_rectangle
from edge_handling import is_point_inside_border_v2,find_parallel_point_inside_border


target_point,selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)
        

def algorithm(detection, bot, display=True, test=False, image=False):
    global target_point,selected_point
    rotation_direction = None

    print("Algorithm started!")
    if display:
        cv2.namedWindow("Feed" )
        cv2.setMouseCallback("Feed",select_point)  
    balls = None
    completed = False
    while True:
        trimmed_field = detection.trimmed_field
        field_corners = detection.field_corners
        if display and test:
            frame = detection.video_stream.read() 
            draw_rectangle(frame, trimmed_field, BLUE)
            draw_rectangle(frame, field_corners, GREEN)
            cv2.imshow('Feed', frame)
        if completed and image:
            cv2.waitKey(1)
            time.sleep(2)
            continue
        if selected_point is not None:
            if display:
                cv2.circle(frame,selected_point,5,RED,5)
                cv2.imshow('Feed', frame)
            detection_object = detection.process_frame()
            bot_angle, bot_center_point, goal_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point'], detection_object['aruco']['goal_center_point']
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue
            if bot:
                bot.updatePosition(bot_center_point, bot_angle)
                bot.setSpeed(4)
                bot.move(selected_point)
                time.sleep(DELAY_AFTER_MOVEMENT)
                bot.setSpeed(6)
                bot.makeMovement('right', 2000)
            selected_point = None

        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('i'):
            input("waiting for interrupt")


        detection_object = detection.process_frame()
        bot_center_point, balls, goal_center_point =  \
            detection_object['aruco']['bot_center_point'], detection_object['yolo']['balls'],\
                detection_object['aruco']['goal_center_point']
        if any([balls == [] , goal_center_point is None , bot_center_point is None]):
            print(f"Detection failed goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")
            time.sleep(1)
            continue
        
        if display:
            frame =  detection.video_stream.read()
            for ball in balls:
                cv2.circle(frame, ball,10, BLUE, 2)
            cv2.imshow('Feed', frame)
            cv2.waitKey(1)
        print(f"Detection results goal post: {goal_center_point}, bot center point: {bot_center_point} no of balls:{len(balls)}")

        filtered_balls, intersection_points = filter_balls(trimmed_field,balls, goal_center_point ,buffer_distance=50)
        next_target_point = choose_next_target_point(intersection_points, bot_center_point)
        if display and test:
            for ball in filtered_balls:
                cv2.circle(frame, ball, 3, GREEN, -1)
            for possible_movement in intersection_points:
                cv2.circle(frame, possible_movement['target_point'], 5, RED, -1)
                cv2.circle(frame, possible_movement['goal_point'], 5, YELLOW, -1)
            cv2.imshow('Feed', frame)
            cv2.waitKey(1)
        next_target_point = None
        if next_target_point is not None:
            print('target locked')
            target_point = next_target_point['target_point']
            goal_point = next_target_point['goal_point']
            frame = detection.video_stream.latest_frame
            if display:
                cv2.circle(frame, target_point, 5, BLUE, -1)
                cv2.circle(frame, goal_point, 5, GREEN, -1)
                cv2.circle(frame, target_point, 5, BLUE, -1)
                cv2.circle(frame, goal_point, 5, GREEN, -1)
                cv2.imshow('Feed', frame)
            time.sleep(0.5)
            detection_object = detection.process_frame()
            bot_center_point , bot_angle = detection.detection_object['aruco']['bot_center_point'], detection.detection_object['aruco']['bot_angle']
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue

            if bot:
                bot.updatePosition(bot_center_point, bot_angle)
                bot.move(target_point)
            time.sleep(0.5)

            bot_angle, bot_center_point, goal_center_point, _ = detection.detect_aruco()
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue
            if bot:
                bot.updatePosition(bot_center_point, bot_angle)
                bot.move(goal_point)
            print("Goal reached!")
            time.sleep(0.5)

            bot_angle, bot_center_point, goal_center_point, _ = detection.detect_aruco()
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue
            if bot:
                bot.updatePosition(bot_center_point, bot_angle)
                bot.move(target_point)
            target_point, goal_point = None, None
            time.sleep(DELAY_AFTER_GOAL)
        else:
            # print(            print("No extended points found within the trimmed field.")
            trimmed_field = np.array(detection.trimmed_field)
            field_corners = np.array(detection.field_corners)
            bot_offset = 1
            filtered_balls, intersection_points = filter_balls(trimmed_field,balls, goal_center_point ,buffer_distance=50, disable_filter=True)
            next_target_point = choose_next_target_point(intersection_points, bot_center_point)
            if next_target_point is not None:
                target_point = next_target_point['target_point']
                ball = next_target_point['ball']
                next_viable_point, side_name = find_parallel_point_inside_border(target_point,field_corners)
                if side_name != "right" or side_name != "left":
                    midpoint = (int((next_viable_point[0] + ball[0])/2), int((next_viable_point[1] + ball[1])/2))
                    midpoint = next_viable_point + bot_offset * np.array([1,1])
                    selected_point = midpoint
                    rotation_direction = 'right' if side_name=='bottom' else 'left'
                    cv2.circle(frame,midpoint,3,YELLOW,-1)
                    cv2.putText(frame, rotation_direction, (midpoint[0], midpoint[1]-30), cv2.FONT_HERSHEY_SIMPLEX,
                                1, GREEN, 1, cv2.LINE_AA)
                    cv2.imshow('Feed',frame)


        completed = True