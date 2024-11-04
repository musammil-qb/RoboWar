import time
import cv2


from const import BLUE, GREEN, RED

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
            bot.move(selected_point)
            selected_point =None

        cv2.imshow('Feed', frame)
        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('t'):
            detection_object = detection.process_frame()
            bot_angle, bot_center_point, goal_center_point = detection_object['aruco']['bot_angle'],\
                  detection_object['aruco']['bot_center_point'], detection_object['aruco']['goal_center_point']
            balls = detection_object['yolo']['balls'] 
            target_point = findvirtualpoint(frame, bot_center_point, goal_center_point, balls)
            goal_point = (int((target_point[0]+goal_center_point[0])/2),int((target_point[1]+goal_center_point[1])/2))
        elif pressed_key == ord('g'):
            bot.updatePosition(bot_center_point, bot_angle)
            bot.move(target_point)
            time.sleep(1)
            bot_angle, bot_center_point, goal_center_point = detection.detect_aruco()
            bot.updatePosition(bot_center_point, bot_angle)
            bot.move(goal_point)
            print("Goal reached!")
            target_point, goal_point = None, None
