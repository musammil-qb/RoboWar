import cv2
import time
import sys
import threading
import os
import json

import numpy as np 
from ultralytics import YOLO

from util import calculate_angle_to_point,calculate_distance
from const import BOT_ID, POST_ID, BLUE

class Detection:
    def __init__(self,image_path=None, video_path=None):
        print("Initializing detection...")
        self.model = YOLO("model.pt")
        self.detection_object = None
        # start video stream
        if image_path:
            self.video_stream = VideoStream(image_path=image_path)
        elif video_path:
            self.video_stream = VideoStream(video_path=video_path, target_fps=30)
        else:
            cam_ip = input("Enter camera ip: ")
            if not cam_ip:
                cam_ip = "192.168.123.64"  #TODO ip from input

            stream_url = f'http://{cam_ip}:8080/video'
            self.video_stream = VideoStream(stream_url)

            while True:
                if self.video_stream.read() is not None:
                    break
            print("Video stream started!")
        #TODO select field
        self.field_corners = []
        self.edge_line  = None
        self.select_field()
        self.define_trimmed_field()
        print("Detection initialized!")


    def process_frame(self):
        frame = self.video_stream.read()
        balls, bots, arena = self.detect_yolo(frame)
        bot_angle, bot_center_point, goal_center_point, other_aruco_codes = self.detect_aruco(frame)
        detection_object = {
            'yolo' : {'balls': balls, 'bots': bots, 'arena': arena},
            'aruco': {'bot_angle': bot_angle, 'bot_center_point': bot_center_point,
                       'goal_center_point': goal_center_point, 'other_aruco codes': other_aruco_codes}}
        self.detection_object = detection_object
        return detection_object


    def detect_yolo(self, frame=None):
        if frame is None:
            frame = self.video_stream.read()
        model = self.model
        result = model.predict(frame, conf=0.5, verbose=False)
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


    def detect_aruco(self, frame=None):
        if frame is None:
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

    def select_field(self):
        file_path = 'corners.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.field_corners = json.load(f)
                
        else:
            cv2.namedWindow("Feed")
            cv2.setMouseCallback("Feed", self.select_corners)

            while True:
                frame = self.video_stream.read()
                # Trace mouse movement

                # Display the video frame
                cv2.imshow("Feed", frame)

                # Break the loop on 'q' key press
                if len(self.field_corners) == 4:
                    with open(file_path, 'w') as f:
                        json.dump(self.field_corners, f)
                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.5)


        # Release the video capture and close all windows
        # cv2.destroyAllWindows()

    def select_corners(self,event, x, y, flags, param):        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.field_corners) < 4:
                self.field_corners.append((x, y))
            # else:
            #     self.



    def define_trimmed_field(self):
        field_corners = self.field_corners
        trim_factor = 0.03
        trim_length = calculate_distance(field_corners[0], field_corners[1])*trim_factor
        
        p1, p2, p3, p4 = np.array(field_corners)
        trimmed_field = [
            (int(p1[0] + trim_length), int(p1[1] + trim_length)),
            (int(p2[0] - trim_length), int(p2[1] + trim_length)),
            (int(p3[0] - trim_length), int(p3[1] - trim_length)),
            (int(p4[0] + trim_length), int(p4[1] - trim_length))
        ]
        self.trimmed_field = trimmed_field

class VideoStream:
    def __init__(self, url=None,image_path=None,video_path=None,target_fps=30):
        self.url = url
        self.image_path = image_path
        self.video_path = video_path
        self.latest_frame = None
        self.stopped = False
        if image_path is None :
            if video_path is None:
                self.cap = cv2.VideoCapture(self.url)
            elif os.path.exists(video_path):
                self.cap = cv2.VideoCapture(self.video_path)
            else:
                print("Video file does not exist.")
                exit(0)
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.thread = threading.Thread(target=self.update, daemon=True)
            self.thread.start()

        elif os.path.exists(image_path):
            self.latest_frame = cv2.imread(self.image_path)
            self.frame_width = self.latest_frame.shape[1]
            self.frame_height = self.latest_frame.shape[0]

        else:
            print("Image file does not exist.")
            exit(0)

        # Start the thread to read frames
    
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
            # time.sleep(1)  # Small delay to prevent excessive CPU usage

    def read(self):
        return self.latest_frame
    
    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()
