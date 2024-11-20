import time
import cv2

from detection import Detection
from bot import Bot
from algorithm import algorithm
from util import draw_polygons
from const import BLUE, GREEN, SLEEP_ARUCO_NOT_FOUND_RECALCULATE


def main():
    detection = Detection()
    # Wait for initial bot detection
    print("Waiting for initial bot detection...")
    while True:
        bot_angle, bot_center_point, _, _ = detection.detect_aruco()
        if bot_angle is not None:
            print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
            break
        time.sleep(SLEEP_ARUCO_NOT_FOUND_RECALCULATE)
    bot = Bot(bot_center_point, bot_angle,detection)
    print("Initializing completed!")

    # Wait for start key
    try:
        # Start Algorithm
        algorithm(detection, bot)

    except Exception as e:
        detection.destroy()
        print("Exiting...")

from multiprocessing import Process, Queue, Manager 
from display_video import display_video

def main_v2():
    frame_queue = Queue()
    # with Manager() as manager:
    if frame_queue:
        # frame_queue = manager.dict()  # Shared dictionary
        cam_ip = input("Enter camera ip: ")
        if not cam_ip:
            cam_ip = "10.7.110.39"
        detection = Detection(cam_ip)
        # Start processes
        p1 = Process(target=detection.process_video, args=(frame_queue,))
        p2 = Process(target=display_video, args=(frame_queue,))

        try:
            p1.start()
            p2.start()   

        finally:
            del detection
            p1.join()
            p2.join()
    


if __name__ == "__main__":
    main_v2()
