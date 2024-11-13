import time
import cv2
import argparse

from detection import Detection
from bot import Bot
from algorithm import algorithm
from util import draw_polygons
from const import BLUE, GREEN, SLEEP_ARUCO_NOT_FOUND_RECALCULATE

def main(image_path=None, video_path=None, disable_bot=True,disable_algorithm=False):

    # Handle image or video input
    if image_path:
        print(f"Processing image: {image_path}")
        detection = Detection(image_path = image_path)
    elif video_path:
        print(f"Processing video: {video_path}")
        detection = Detection(video_path = video_path)
    else:
        print("Using droidcam for video input...")
        detection = Detection()

    # If bot is not disabled, wait for initial bot detection
    if not disable_bot:
        print("Waiting for initial bot detection...")
        while True:
            bot_angle, bot_center_point, _, _ = detection.detect_aruco()
            if bot_angle is not None:
                print(f"Bot angle: {bot_angle}, bot center point: {bot_center_point}")
                break
            time.sleep(SLEEP_ARUCO_NOT_FOUND_RECALCULATE)
        bot = Bot(bot_center_point, bot_angle, detection)
    else:
        print("Bot functionality is disabled.")
        bot = None
    print("Initialization completed!")

    try:
        algorithm(detection, bot,test=True,image=bool(image_path),disable_algorithm=disable_algorithm)
    except KeyboardInterrupt:
        detection.__del__()
        print("Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run bot detection and algorithm.")
    parser.add_argument("--image_path", type=str, help="Path to an image file.")
    parser.add_argument("--video_path", type=str, help="Path to a video file.")
    parser.add_argument("--disable_bot", action="store_true", help="Disable bot initialization.")
    parser.add_argument("--disable_algorithm", action="store_true", help="Disable algorithm movements.")
    args = parser.parse_args()

    main(image_path=args.image_path, video_path=args.video_path, disable_bot=args.disable_bot, 
          disable_algorithm=args.disable_algorithm)
