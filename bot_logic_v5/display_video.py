import cv2
import time

def display_video(shared_data):
    while True:
        frame = shared_data.get()
        if frame:
            cv2.imshow('Display', frame)
            print(frame)
        time.sleep(0.01)
