import cv2
import time
import sys
import threading

import numpy as np 
from ultralytics import YOLO

from util import calculate_angle_to_point
from const import BOT_ID, POST_ID

class Detection:
    def __init__(self):
        #TODO select field
        self.model = YOLO("model.pt")
        self.detection_object = None
        # start video stream
        cam_ip = "10.42.0.66"  #TODO ip from input

        stream_url = f'http://{cam_ip}:8080/video'
        self.video_stream = VideoStream(stream_url)

        while True:
            if self.video_stream.read() is not None:
                break
        print("Video stream started!")

    def process_frame(self):
        frame = self.video_stream.read()
        balls, bots, arena = self.detect_yolo(frame)
        bot_angle, bot_center_point, goal_center_point, other_aruco_codes = self.detect_aruco()
        detection_object = {'yolo' :{'balls': balls, 'bots': bots, 'arena': arena},'aruco': {'bot_angle': bot_angle,
                            'bot_center_point': bot_center_point, 'goal_center_point': goal_center_point,
                            'other_aruco codes': other_aruco_codes}}
        self.detection_object = detection_object
        return detection_object


    def detect_yolo(self, frame):
        model = self.model
        result = model.predict(frame, conf=0.5)
        balls = []
        bot = None
        arena = None

        for r in result:
            boxes = r.boxes

            for box in boxes:
                if int(box.cls[0]) == 0: # Detect balls
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    center_point_ball = (int((x1+x2)/2), int((y1+y2)/2))

                    balls.append(center_point_ball)

                if int(box.cls[0]) == 1: # Detect bot
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    center_point_bot = (int((x1+x2)/2), int((y1+y2)/2))

                    bot = center_point_bot

                if int(box.cls[0]) == 2: # Detect arena
                    x1, y1, x2, y2 = box.xyxy[0]
                    arena = [int(i) for i in [x1, y1, x2, y2]]

        return balls, bot, arena


    def detect_aruco(self):
        frame = self.video_stream.read()
        markers_dict_np, markers_dict_integer = self.detect_aruco_markers(frame)
        bot_angle, bot_center_point = self.find_bot(markers_dict_integer.pop(BOT_ID)) if markers_dict_integer.get(BOT_ID) else (None,None)
        _, goal_center_point = self.find_bot(markers_dict_integer.pop(POST_ID)) if markers_dict_integer.get(POST_ID) else (None,None)
        return bot_angle, bot_center_point, goal_center_point, markers_dict_integer


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
            corners, ids, _ = detector.detectMarkers(frame)

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