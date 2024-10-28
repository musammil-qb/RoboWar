from ultralytics import YOLO
import cv2
import math 

cap = cv2.VideoCapture("http://192.168.90.87:8080/video")
cap.set(3, 640)
cap.set(4, 480)
image_no = 0

while True:
    success, img = cap.read()
    if not success:
        break  # Exit if the video feed is not available

    cv2.imshow('Webcam', img)
    pressed_key = cv2.waitKey(1)
    
    if pressed_key == ord('s'):
        # Save the current frame
        cv2.imwrite('output_image' + str(image_no) + '.jpg', img)
        print(f"Image saved as output_image{image_no}.jpg")
        image_no += 1
    elif pressed_key == ord('q'):
        # Quit if 'q' is pressed
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
