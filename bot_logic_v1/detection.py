import cv2
import time
import sys
import threading

import numpy as np 
from ultralytics import YOLO

from util import calculate_angle_to_point


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


    def detect_yolo(self, frame):
        pass

    def detect_aruco(self):
        frame = self.video_stream.read()
        markers_dict_np, markers_dict_integer = self.detect_aruco_markers(frame)
        bot_angle, bot_center_point = self.find_bot(markers_dict_integer[69]) if markers_dict_integer.get(69) else (None,None)
        return bot_angle, bot_center_point


    def destroy(self):
        self.video_stream.stop()
        self.destroy()

    def detect_aruco_markers(self,frame, draw_corners=False):
        aruco_type = cv2.aruco.DICT_4X4_100
        dictionary = cv2.aruco.getPredefinedDictionary(aruco_type)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        
        markers_dict_np = {}
        markers_dict_integer = {}

        try:
            corners, ids, rejected = detector.detectMarkers(frame)

            if draw_corners:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            if ids is not None:
                for i, marker_id in enumerate(ids.flatten()):
                    processed_corners = corners[i][0]
                    markers_dict_np[marker_id] = processed_corners
                    processed_corners = [corner.tolist() for corner in corners[i][0]]
                    markers_dict_integer[marker_id] = processed_corners

            return markers_dict_np, markers_dict_integer

        except Exception as e:
            print(f"Error detecting markers: {e}")
            return {}, {}

    def find_bot(self, bot_corners):
        bot_corners = np.array(bot_corners)
        mid_point = (bot_corners[0]+bot_corners[1])/2
        bot_center_point = (bot_corners[0]+bot_corners[1]+bot_corners[2]+bot_corners[3])/4
        bot_angle = calculate_angle_to_point(bot_center_point, mid_point)        
        return bot_angle, bot_center_point


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