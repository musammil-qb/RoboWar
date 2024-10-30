import cv2
from threading import Thread
import time 

class VideoCapture:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

cap = VideoCapture().start()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    print("processing frames")
    # Process the latest frame
    cv2.imshow('Latest Frame', frame)
    time.sleep(5)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.stop()
cv2.destroyAllWindows()
