from detection import VideoStream
from const import RED
import cv2
import time
import random
 

pressed_key = None
cam_ip = input("Enter camera ip: ")
if not cam_ip:
    cam_ip = "192.168.187.44"
stream_url = f'http://{cam_ip}:8080/video'
video_stream = VideoStream(stream_url)

while True:
    if video_stream.read() is not None:
        break
print("Video stream started!")

width, height = video_stream.frame_height,video_stream.frame_width
while True:
    print(f"waiting for key press previous key:{pressed_key}")
    time.sleep(0.01)
    frame = video_stream.read()
    cv2.imshow("Feed", frame)
    cv2.waitKey(1)
    pressed_key = cv2.waitKey(1)
    if pressed_key == ord('q'):
        break
    elif pressed_key == ord('s'):
        frame = detection.video_stream.read()
        print("new frame")
        start_time = time.time()
        cv2.imshow("Feed", frame)
        cv2.waitKey(1)
        while True:
            random_point = (random.randint(0, width), random.randint(0, height))
            cv2.circle(frame,random_point,5,RED,5)
            cv2.imshow("Feed", frame)
            pressed_key = cv2.waitKey(10)
            if time.time() - start_time > 3:
                break
        frame = detection.video_stream.read()
        cv2.imshow("Feed", frame)
        cv2.waitKey(1)
        

        
        # time.sleep(0.1)
cv2.destroyAllWindows()
# detection.destroy()
