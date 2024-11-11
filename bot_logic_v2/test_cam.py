from detection import Detection
from const import RED
import cv2
import time
import random
 
detection = Detection()

width, height = detection.video_stream.frame_height,detection.video_stream.frame_width
pressed_key = None
while True:
    print(f"waiting for key press previous key:{pressed_key}")
    time.sleep(0.01)
    frame = detection.video_stream.read()
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
