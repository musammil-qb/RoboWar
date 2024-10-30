import cv2
import requests

from utils.video import resize_to_max_dimensions
from utils.find_bot import find_bot,find_distance
from utils.aruco.arucodetect import detectarucomarker


# video_ip = input("ipcam ip: ")
# bot_ip = input("Bot Ip: ")
BOT_CODE = 69
video_ip = '10.42.0.66'
bot_ip = '10.42.0.202'

movement_dictionary = {'w':'forward', 'a':'left', 's':'backward', 'd':'right' ,'b':'stop'} 

def process_image(cap):
    current_bot_angle = None
    current_center_point = None
    image_no = 0
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Starting")
    while True:
        success, frame = cap.read()
        if not success:
            print("exiting")
            break  # Exit if the video feed is not available
        resized_frame = resize_to_max_dimensions(original_width, original_height,1500,800,frame=frame)
        cv2.imshow('Webcam', resized_frame)
        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('i'):
            movement = input("movement: ")
            delay = input("delay: ")
            print(movement,delay)
            if movement_dictionary.get(movement):
                res = requests.get(f"http://{bot_ip}/{movement_dictionary[movement]}", params={"delay": delay})
            print(res.raw,res.status_code)
        elif pressed_key == ord('p'):
            corners = detectarucomarker(frame)
            print("corners:",corners,'\n\n')
            bot_angle, bot_center_point = find_bot(corners[BOT_CODE]) if corners.get(BOT_CODE) else (None,None)
            print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
            if current_bot_angle and bot_angle:
                print(f"Angle deference:{bot_angle-current_bot_angle} \tdistance travelled:{find_distance(current_center_point,bot_center_point)}")
            current_bot_angle , current_center_point = bot_angle, bot_center_point
        elif pressed_key == ord('q'):
            # Quit if 'q' is pressed
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    video_url = 'http://'+video_ip+':8080/video'
    print(f"Video URL:{video_url}")
    cap = cv2.VideoCapture(video_url)
    cap.set(3, 640)
    cap.set(4, 480)
    process_image(cap)