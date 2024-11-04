import time
import cv2


from const import BLUE, GREEN, RED
from targetDetection import filter_balls, choose_next_target_point
from util import draw_rectangle


target_point,selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)


def algorithm(detection, bot):
    global target_point,selected_point

    print("Algorithm started!")
    cv2.namedWindow("Feed" )
    cv2.setMouseCallback("Feed",select_point)  
    balls = None
    while True:

        frame = detection.video_stream.read() # remove

        if target_point is not None:
            cv2.circle(frame, target_point, 5, BLUE, -1)
            cv2.circle(frame, goal_point, 5, GREEN, -1)

        if balls is not None:
            for ball in balls:
                cv2.circle(frame, ball, 5, RED, -1)
        if selected_point is not None:
            detection_object = detection.process_frame()
            bot_angle, bot_center_point, goal_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point'], detection_object['aruco']['goal_center_point']

            bot.updatePosition(bot_center_point, bot_angle)
            time.sleep(0.1)
            bot.move(selected_point)
            selected_point =None

        draw_rectangle(frame, detection.trimmed_field,BLUE)
        draw_rectangle(frame, detection.field_corners,GREEN)

        cv2.imshow('Feed', frame)
        pressed_key = cv2.waitKey(1)

        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('t'):
            detection_object = detection.process_frame()
            trimmed_field = detection.trimmed_field
            filtered_balls, intersection_points = filter_balls(trimmed_field, detection_object['yolo']['balls'],detection_object['aruco']['goal_center_point'],buffer_distance=20)
            next_target_point = choose_next_target_point(intersection_points, detection_object['aruco']['bot_center_point'])
            
            target_point = next_target_point['target_point']
            goal_point = next_target_point['goal_point']
        elif pressed_key == ord('g'):
            bot_center_point , bot_angle = detection.detection_object['aruco']['bot_center_point'], detection.detection_object['aruco']['bot_angle']
            bot.updatePosition(bot_center_point, bot_angle)
            bot.move(target_point)
            time.sleep(1)
            bot_angle, bot_center_point, goal_center_point, _ = detection.detect_aruco()
            bot.updatePosition(bot_center_point, bot_angle)
            bot.move(goal_point)
            print("Goal reached!")
            target_point, goal_point = None, None
