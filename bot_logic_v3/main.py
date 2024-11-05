import time
import cv2

from detection import Detection
from bot import Bot
from algorithm import algorithm
from util import draw_rectangle
from const import BLUE, GREEN


def main():
    detection = Detection()
    # Wait for initial bot detection
    print("Waiting for initial bot detection...")
    while True:
        bot_angle, bot_center_point, _, _ = detection.detect_aruco()
        if bot_angle is not None:
            print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
            break
        time.sleep(0.5)
    bot = Bot(bot_center_point, bot_angle,detection)
    # bot = None
    print("Initializing completed!")

    # Wait for start key
    try:
        # Start Algorithm
        algorithm(detection, bot)
        # while True:
        #     image = detection.video_stream.read()

        #     cv2.imshow('Feed', image)
        #     pressed_key = cv2.waitKey(1)
        #     if pressed_key == ord('q'):
        #         print("Exiting...")
        #         break
        #     elif pressed_key == ord('i'):
        #         bot_angle, bot_center_point, _, _ = detection.detect_aruco()
        #         print("initial point")
        #         print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
        #         movement = input("movement: ")
        #         interval = input("interval: ")
        #         print("final point")
        #         bot.makeMovement(movement, interval)
        #         time.sleep(1)
        #         bot_angle_2, bot_center_point_2, _, _ = detection.detect_aruco()
        #         print(f"Bot angle:{bot_angle_2}, bot center point: {bot_center_point_2}")
        #     elif pressed_key == ord('d'):
        #         bot_angle_2, bot_center_point_2, _, _ = detection.detect_aruco()
        #         # print("initial point")
        #         print(f"Bot angle:{bot_angle_2}, bot center point: {bot_center_point_2}")


        #     time.sleep(0.01)

    except KeyboardInterrupt:
        detection.destroy()
        print("Exiting...")

if __name__ == "__main__":
    main()
