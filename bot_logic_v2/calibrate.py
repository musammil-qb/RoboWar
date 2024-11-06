import time
import cv2


from const import BLUE, GREEN, RED, DELAY_AFTER_GOAL, YELLOW, DELAY_AFTER_MOVEMENT
from util import calculate_distance
from detection import Detection
from bot import Bot


selected_point = None, None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)
        

def main():
    detection= Detection()

    detection_object = detection.process_frame()
    bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
        detection_object['aruco']['bot_center_point']

    bot = Bot(bot_center_point, bot_angle, detection,calibrate=False)
    global selected_point
    while True:
        pressed_key = cv2.waitKey(1)
        frame = detection.video_stream.read()
        if selected_point is not None:
            cv2.circle(frame,selected_point,3,RED,-1)
            cv2.imshow('Feed', frame)
            detection_object = detection.process_frame()
            bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point']
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue
            bot.updatePosition(bot_center_point, bot_angle)
            bot.move(selected_point)
            time.sleep(DELAY_AFTER_MOVEMENT)
            detection_object = detection.process_frame()
            bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point']
            print("Bot position: ", bot_center_point)
            bot.calculateMovement(selected_point)
            selected_point = None
        frame = detection.video_stream.read()
        cv2.imshow('Feed', frame)
        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('d'):
            _, bot_center_point, _, _ = detection.detect_aruco()
            cv2.circle(frame,bot_center_point,3,GREEN,-1)
        elif pressed_key == ord('c'):
            print("Calibrating...")
            bot.calibrate()
            time.sleep(5)
        elif pressed_key == ord('i'):
            initial_bot_angle, initial_bot_center_point, _, _ = detection.detect_aruco()
            movement = input("Enter movement: ")
            delay = int(input("Enter delay: "))
            bot.makeMovement(movement, delay)
            time.sleep(DELAY_AFTER_MOVEMENT)
            finale_bot_angle, final_bot_center_point, _, _ = detection.detect_aruco()
            print("Initial bot position: ", initial_bot_center_point)
            print("Initial bot angle: ", initial_bot_angle)
            print("Current bot position: ", final_bot_center_point)
            print("Current bot angle: ", finale_bot_angle)
            print("Angle difference: ", finale_bot_angle - initial_bot_angle)
            print("Distance difference: ", calculate_distance(final_bot_center_point - initial_bot_center_point))
        time.sleep(0.1)

if __name__ == "__main__":
    main()