import time
import cv2
import json

from const import BLUE, GREEN, RED, SLEEP_AFTER_GOAL, YELLOW, SLEEP_AFTER_MOVEMENT, SLEEP_AFTER_EACH_LOOP
from util import calculate_distance
from detection import Detection
from bot import Bot


movement_dict = { 'f': 'forward', 'b': 'backward', 'l': 'left', 'r': 'right' }


selected_point = None
def select_point(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_point = (x, y)
        

def main():
    detection= Detection()

    detection_object = detection.process_frame()
    bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
        detection_object['aruco']['bot_center_point']
    cv2.namedWindow("Feed" )
    cv2.setMouseCallback("Feed",select_point)  
    bot = Bot(bot_center_point, bot_angle, detection,calibrate=True)
    global selected_point
    data = []
    pressed_key = None
    while True:
        frame = detection.video_stream.read()
        if selected_point is not None:
            cv2.circle(frame,selected_point,3,RED,-1)
            cv2.imshow('Feed', frame)
            if not pressed_key:
                pressed_key = cv2.waitKey(1)
            detection_object = detection.process_frame()
            bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point']
            if bot_center_point is None:
                print("Bot not found interrupt")
                continue
            bot.updatePosition()
            bot.move(selected_point,acquire_target=True)
            # rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = bot.calculateMovement(selected_point)
            # bot.makeMovement(rotation_direction,rotation_time_ms)
            time.sleep(SLEEP_AFTER_MOVEMENT)
            bot_angle,bot_center_point ,goal_center_point, _ = detection.detect_aruco()
            bot.updatePosition()
            bot.move(goal_center_point,acquire_target=False,orient_only=True)
            time.sleep(SLEEP_AFTER_MOVEMENT)
            detection_object = detection.process_frame()
            bot_angle, bot_center_point = detection_object['aruco']['bot_angle'], \
                detection_object['aruco']['bot_center_point']
            print("Bot position: ", bot_center_point)
            if bot_center_point is not None:
                bot.calculateMovement(selected_point)
            else:
                print(f"Bot center point:{bot_center_point}")
            selected_point = None
        frame = detection.video_stream.read()
        cv2.imshow('Feed', frame)
        if not pressed_key:
            pressed_key = cv2.waitKey(1)

        if pressed_key == ord('q'):
            print("Exiting...")
            break
        elif pressed_key == ord('d'):
            bot_angle, bot_center_point, _, _ = detection.detect_aruco()
            # cv2.circle(frame,bot_center_point,3,GREEN,-1)
            print(bot_angle, bot_center_point)
        elif pressed_key == ord('c'):
            print("Calibrating...")
            bot.calibrate(detection)
        elif pressed_key == ord('i'):
            initial_bot_angle, initial_bot_center_point, _, _ = detection.detect_aruco()
            movement = input("Enter movement: ")
            value = int(input("Enter value: "))
            if movement in ['r','l']:
                delay = abs(value) * bot.get_closest_rate(
                value, bot.rate_of_movement[movement_dict[movement]])
            else:
                delay = value * bot.get_closest_rate(value,
                                  bot.rate_of_movement[movement_dict[movement]])
            bot.makeMovement(movement_dict[movement], delay)
            time.sleep(SLEEP_AFTER_MOVEMENT)
            finale_bot_angle, final_bot_center_point, _, _ = detection.detect_aruco()
            if initial_bot_center_point is not None and final_bot_center_point is not None:
                distance_difference =calculate_distance(final_bot_center_point,initial_bot_center_point)
            else:
                distance_difference = None
            print("Initial bot position: ", initial_bot_center_point)
            print("Initial bot angle: ", initial_bot_angle)
            print("Current bot position: ", final_bot_center_point)
            print("Current bot angle: ", finale_bot_angle)
            print("Angle difference: ", finale_bot_angle - initial_bot_angle)
            print("Distance difference: ", distance_difference)
            data.append({
                'initial_bot_angle': initial_bot_angle, 'initial_bot_center_point': initial_bot_center_point,
                'final_bot_angle': finale_bot_angle, 'final_bot_center_point': final_bot_center_point,
                'movement': movement, 'delay': delay, 'angle_difference': finale_bot_angle - initial_bot_angle,
                'distance_difference': distance_difference
                })
            with open('data.json', 'a') as f:
                f.write(json.dumps({
                'initial_bot_angle': initial_bot_angle, 'initial_bot_center_point': initial_bot_center_point,
                'final_bot_angle': finale_bot_angle, 'final_bot_center_point': final_bot_center_point,
                'movement': movement, 'delay': delay, 'angle_difference': finale_bot_angle - initial_bot_angle,
                'distance_difference': distance_difference
                }))
                f.write('\n')
        elif pressed_key == ord('s'):
            print("Saving...")
            with open('data.json', 'w') as f:
                json.dump(data, f)
        if pressed_key:
            pressed_key = None
    
        time.sleep(SLEEP_AFTER_EACH_LOOP)

if __name__ == "__main__":
    main()