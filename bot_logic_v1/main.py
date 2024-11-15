import time
import cv2

from detection import Detection
from bot import Bot
from algorithm import algorithm


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
    bot = Bot(bot_center_point, bot_angle)

    print("Initializing completed!")

    # Wait for start key
    try:
        # Start Algorithm
        algorithm(detection, bot)



    except KeyboardInterrupt:
        detection.destroy()
        print("Exiting...")

if __name__ == "__main__":
    main()
