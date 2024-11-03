from detection import Detection
from bot import Bot
import time
import cv2

target_point = None
def select_point(event, x, y, flags, param):
    global frame, bot_center_point, bot_angle
    if event == cv2.EVENT_LBUTTONDOWN:
        target_point = (x, y)
        print("point selected", x, y)

def main():
    global target_point
    detection = Detection()
    # Wait for initial bot detection
    print("Waiting for initial bot detection...")
    while True:
        bot_angle, bot_center_point = detection.detect_aruco()
        if bot_angle is not None:
            print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
            break
        time.sleep(0.5)
    bot = Bot(bot_center_point, bot_angle)

    print("Initializing completed!")

    # Wait for start key
    try:
        # Start Algorithm
        print("Algorithm started!")
        cv2.namedWindow("Feed" )
        cv2.setMouseCallback("Feed",select_point )
        while True:
            frame = detection.video_stream.read()
            cv2.imshow('Feed', frame)
            if target_point is not None:
                bot.move(target_point)
                target_point = None

            pressed_key = cv2.waitKey(1)
            if pressed_key == ord('q'):
                print("Exiting...")
                break



    except KeyboardInterrupt:
        detection.destroy()
        print("Exiting...")

if __name__ == "__main__":
    main()
