import cv2
import time
import threading
from ultralytics import YOLO



class Detection:
    def __init__(self):
        # select corners
        self.model = YOLO("model.pt")

        # start video stream
        cam_ip = "10.7.110.35"  #TODO ip from input

        stream_url = f'http://{cam_ip}:8080/video'
        self.video_stream = VideoStream(stream_url)

        while True:
            if self.video_stream.read() is not None:
                break
        print("Video stream started!")

    def process_frame(self, frame):
        pass

    def detect_arucode(self, frame):
        pass

    def detect_yolo(self, frame):
        pass

    def destroy(self):
        self.video_stream.stop()
        self.destroy()

class VideoStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.latest_frame = None
        self.stopped = False

        # Start the thread to read frames
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
    
    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.latest_frame = frame
                else:
                    print("Failed to grab frame.")
                    self.stop()
                    break
            else:
                print("Failed to open video stream.")
                self.stop()
                break
            # time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def read(self):
        return self.latest_frame

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()

