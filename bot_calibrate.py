import cv2
import requests

from utils.video import resize_to_max_dimensions
from utils.find_bot import find_bot,find_distance
from utils.aruco.arucodetect import detectarucomarker
from utils.clickAndMove import select_target,calculate_distance,calculate_angle_to_point,move_bot_to_target


# from utils.select_field import trace_mouse,select_corners
mouse_position = None
frame= None
bot_center_point,bot_angle = None,None

def select_corners(event, x, y, flags, param):
    global corners, mouse_position
    mouse_position = (x, y)  # Update the mouse position
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 4:  # Limit to 4 corners
            corners.append((x, y))
            print(f"Corner {len(corners)}: ({x}, {y})")
            
# video_ip = input("ipcam ip: ")
# bot_ip = input("Bot Ip: ")
BOT_CODE = 69
video_ip = '10.42.0.66'
bot_ip = '10.42.0.202'

def trace_mouse(frame, mouse_position):
    if mouse_position is not None:
        # Draw a circle at the mouse position
        cv2.circle(frame, mouse_position, 5, (255, 0, 0), -1)
        
def select_point(event, x, y, flags, param):
    global frame, bot_center_point, bot_angle
    if event == cv2.EVENT_LBUTTONDOWN:

        print("point selected", x, y)
        corners = detectarucomarker(frame)
        # print("corners:",corners,'\n\n')
        bot_angle, bot_center_point = find_bot(corners[BOT_CODE]) if corners.get(BOT_CODE) else (None,None)
        # print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
        rotation_time_ms, rotation_direction, rotation_time_ms, travel_direction, travel_time_ms = move_bot_to_target(
            bot_center_point, bot_angle, (x, y))
        if rotation_direction == "Left":
            send_movement('a', rotation_time_ms)
        elif rotation_direction == "Right":
            send_movement('d', rotation_time_ms)    
        send_movement('w', travel_time_ms)

def send_movement(movement,delay):
    print(movement,delay)
    if movement_dictionary.get(movement):
        res = requests.get(f"http://{bot_ip}/{movement_dictionary[movement]}", params={"delay": delay})
    print(res.status_code)

movement_dictionary = {'w':'forward', 'a':'left', 's':'backward', 'd':'right' ,'b':'stop'} 

def process_image(cap):
    global frame, bot_center_point, bot_angle
    current_bot_angle = None
    current_center_point = None
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Starting")
    cv2.namedWindow("Webcam")
    cv2.setMouseCallback("Webcam", select_point)

    while True:
        success, frame = cap.read()
        if not success:
            print("exiting")
            break  # Exit if the video feed is not available
        resized_frame = resize_to_max_dimensions(original_width, original_height,1500,800,frame=frame)
        cv2.imshow('Webcam', resized_frame)
        trace_mouse(frame, mouse_position)

        pressed_key = cv2.waitKey(1)

        if pressed_key == ord('i'):
            movement = input("movement: ")
            delay = input("delay: ")
            send_movement(movement,delay)
        elif pressed_key == ord('p'):
            corners = detectarucomarker(frame)
            print("corners:",corners,'\n\n')
            bot_angle, bot_center_point = find_bot(corners[BOT_CODE]) if corners.get(BOT_CODE) else (None,None)
            print(f"Bot angle:{bot_angle}, bot center point: {bot_center_point}")
            if current_bot_angle and bot_angle:
                print(f"Angle deference:{bot_angle-current_bot_angle} \tdistance travelled:{find_distance(current_center_point,bot_center_point)}")
            current_bot_angle , current_center_point = bot_angle, bot_center_point
        if pressed_key == ord('q'):
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