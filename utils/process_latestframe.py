import cv2
import time
cap = cv2.VideoCapture(0)  # Use 0 for the default camera
print("Starting video capture")
while True:
    # Clear frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
    print("Geting frames")
    # Process the latest frame
    ret, latest_frame = cap.read()
    if not ret:
        break
    print("processing frames")
    time.sleep(5)
    # Processing code here
    cv2.imshow('Latest Frame', latest_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
