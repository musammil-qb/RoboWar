import cv2
import time
import sys
import threading
import os
import json

import numpy as np 
from ultralytics import YOLO

from util import calculate_angle_to_point,calculate_distance,point_at_distance_in_a_line,\
    find_closest_edge, find_perpendicular_point_from_point_on_line, find_closest_corner,\
    is_point_inside_border
from const import BOT_ID, POST_ID, FIELD_LENGTH, FIELD_WIDTH, \
    TRIM_LENGTH, CORNER_TO_POST_LENGTH, BOT_MOVEMENT_TRIM_LENGTH,\
        DEFAULT_POSITION_TO_POST_LENGTH, SLEEP_CORNER_SELECTION_LOOP, \
        SLEEP_ARUCO_NOT_FOUND_RECALCULATE, SLEEP_BEFORE_TAKING_FRAME

class Detection:
    def __init__(self,image_path=None, video_path=None):
        print("Initializing detection...")
        self.model = YOLO("model.pt")
        self.detection_object = {}
        # start video stream
        if image_path:
            self.video_stream = VideoStream(image_path=image_path)
        elif video_path:
            self.video_stream = VideoStream(video_path=video_path, target_fps=30)
        else:
            cam_ip = input("Enter camera ip: ")
            if not cam_ip:
                cam_ip = "192.168.32.247"

            stream_url = f'http://{cam_ip}:8080/video'
            self.video_stream = VideoStream(stream_url)

            while True:
                if self.video_stream.read() is not None:
                    break
            print("Video stream started!")
        self.field_corners = []
        self.edge_line  = None
        self.goal_posts = []
        self.select_field()
        self.calculate_cm_pixel_rate()
        self.find_interested_points()
        self.define_trimmed_fields()
        print("Detection initialized!")


    def process_frame(self):
        if SLEEP_BEFORE_TAKING_FRAME:
            time.sleep(SLEEP_BEFORE_TAKING_FRAME)
        frame = self.video_stream.read()
        balls, bots, arena = self.detect_yolo(frame)
        bot_angle, bot_center_point, goal_center_point, other_aruco_codes = self.detect_aruco(frame)
        detection_object = {
            'yolo' : {'balls': balls, 'bots': bots, 'arena': arena},
            'aruco': {'bot_angle': bot_angle, 'bot_center_point': bot_center_point,
                       'goal_center_point': goal_center_point, 'other_aruco codes': other_aruco_codes}}
        return detection_object


    def detect_yolo(self, frame=None):
        if frame is None:
            if SLEEP_BEFORE_TAKING_FRAME:
                time.sleep(SLEEP_BEFORE_TAKING_FRAME)
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
                    if is_point_inside_border(center_point_ball, self.field_corners):
                        balls.append(center_point_ball)

                if int(box.cls[0]) == 1: # Detect bot
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    center_point_bot = (int((x1+x2)/2), int((y1+y2)/2))

                    bot = center_point_bot

                if int(box.cls[0]) == 2: # Detect arena
                    x1, y1, x2, y2 = box.xyxy[0]
                    arena = [int(i) for i in [x1, y1, x2, y2]]
        self.detection_object['yolo'] = {'balls': balls, 'bots': bot, 'arena': arena}
        return balls, bot, arena


    def detect_aruco(self, frame=None):
        if frame is None:
            if SLEEP_BEFORE_TAKING_FRAME:
                time.sleep(SLEEP_BEFORE_TAKING_FRAME)
            frame = self.video_stream.read()
        markers_dict_np, markers_dict_integer = self.detect_aruco_markers(frame)
        bot_angle, bot_center_point = self.find_bot(markers_dict_integer.pop(BOT_ID)) if markers_dict_integer.get(BOT_ID) else (None,None)
        _, goal_center_point = self.find_bot(markers_dict_integer.pop(POST_ID)) if markers_dict_integer.get(POST_ID) else (None,None)
        self.detection_object['aruco'] = {'bot_angle': bot_angle, 'bot_center_point': bot_center_point,
                       'goal_center_point': goal_center_point, 'other_aruco codes': markers_dict_integer}
        return bot_angle, bot_center_point, goal_center_point, markers_dict_integer

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
        bot_center_point = ((bot_corners[0]+bot_corners[1]+bot_corners[2]+bot_corners[3])/4).tolist()
        bot_angle = calculate_angle_to_point(bot_center_point, mid_point)        
        return bot_angle, (int(bot_center_point[0]), int(bot_center_point[1]))

    def select_field(self):
        file_path = 'corners.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.field_corners = json.load(f)
                
        else:
            cv2.namedWindow("Feed")
            cv2.setMouseCallback("Feed", self.select_corners)
            print("Select 4 corners of the field")

            while True:
                if SLEEP_BEFORE_TAKING_FRAME:
                    time.sleep(SLEEP_BEFORE_TAKING_FRAME)
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
                time.sleep(SLEEP_CORNER_SELECTION_LOOP)


        # Release the video capture and close all windows
        # cv2.destroyAllWindows()

    def select_corners(self,event, x, y, flags, param):        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.field_corners) < 4:
                self.field_corners.append((x, y))

    def calculate_cm_pixel_rate(self):
        field_length = (calculate_distance(
            self.field_corners[0], self.field_corners[1]) + \
                calculate_distance(self.field_corners[2], self.field_corners[3]))/2
        field_width = (calculate_distance(self.field_corners[1], self.field_corners[2]) + \
                       calculate_distance(self.field_corners[0], self.field_corners[3])) / 2
        self.cm_pixel_rate = ((field_length/FIELD_LENGTH) + (field_width/FIELD_WIDTH))/2


    def define_trimmed_fields(self):
        field_corners = self.field_corners
        trim_length = TRIM_LENGTH * self.cm_pixel_rate
        
        goal_post_points = self.goal_posts['opponent']['edge_points']
        closest_corner_index = [find_closest_corner(field_corners,goal_post_points[0]),
                         find_closest_corner(field_corners,goal_post_points[1])]
        p1, p2, p3, p4 = np.array(field_corners)
        if min(closest_corner_index) == 0:
            trimmed_field = [
                goal_post_points[closest_corner_index.index(3)],
                goal_post_points[closest_corner_index.index(0)],
                (int(p1[0] + trim_length), int(p1[1] + trim_length)),
                (int(p2[0] - trim_length), int(p2[1] + trim_length)),
                (int(p3[0] - trim_length), int(p3[1] - trim_length)),
                (int(p4[0] + trim_length), int(p4[1] - trim_length))
                ]
        else:
            trimmed_field = [
                (int(p1[0] + trim_length), int(p1[1] + trim_length)),
                (int(p2[0] - trim_length), int(p2[1] + trim_length)),
                goal_post_points[closest_corner_index.index(1)],
                goal_post_points[closest_corner_index.index(2)],
                (int(p3[0] - trim_length), int(p3[1] - trim_length)),
                (int(p4[0] + trim_length), int(p4[1] - trim_length))
                ]

        self.trimmed_field = trimmed_field
        trim_length = BOT_MOVEMENT_TRIM_LENGTH * self.cm_pixel_rate
        
        p1, p2, p3, p4 = np.array(field_corners)
        bot_movement_trimmed_field = [
            (int(p1[0] + trim_length), int(p1[1] + trim_length)),
            (int(p2[0] - trim_length), int(p2[1] + trim_length)),
            (int(p3[0] - trim_length), int(p3[1] - trim_length)),
            (int(p4[0] + trim_length), int(p4[1] - trim_length))
        ]
        self.bot_movement_trimmed_field = bot_movement_trimmed_field


    def find_interested_points(self):
        length_from_corner_to_post = self.cm_pixel_rate * CORNER_TO_POST_LENGTH
        side_edge_and_midpoint = [
            {'post_center_point': (np.array(self.field_corners[1])+np.array(self.field_corners[2]))/2,
             'edge': [self.field_corners[1], self.field_corners[2]]},
            {'post_center_point': (np.array(self.field_corners[0])+np.array(self.field_corners[3]))/2,
             'edge': [self.field_corners[0], self.field_corners[3]]}
        ]

        goal_aruco_center = None
        while goal_aruco_center is None:
            print("getting goal center point")
            _, _, goal_aruco_center, _ = self.detect_aruco()
            time.sleep(SLEEP_ARUCO_NOT_FOUND_RECALCULATE)

        closest_edge, _, _ = find_closest_edge(goal_aruco_center, list(
            map(lambda x: x['edge'], side_edge_and_midpoint)))
        if closest_edge[0] == side_edge_and_midpoint[0]['edge']:
            opponent_edge = 0
            self_edge = 1
        else:
            opponent_edge = 1
            self_edge = 0

        self.goal_posts = {
            'self':  {
                'post_center_point': list(map(int, side_edge_and_midpoint[self_edge]['post_center_point'])),
                'edge_points': [
                    point_at_distance_in_a_line(
                        side_edge_and_midpoint[self_edge]['edge'][0],
                        side_edge_and_midpoint[self_edge]['edge'][1], length_from_corner_to_post),
                    point_at_distance_in_a_line(
                        side_edge_and_midpoint[self_edge]['edge'][1],
                        side_edge_and_midpoint[self_edge]['edge'][0], length_from_corner_to_post)
                ]
            }, 'opponent': {
                'post_center_point': list(map(int, side_edge_and_midpoint[opponent_edge]['post_center_point'])),
                'edge_points': [
                    point_at_distance_in_a_line(
                        side_edge_and_midpoint[opponent_edge]['edge'][0],
                        side_edge_and_midpoint[opponent_edge]['edge'][1], length_from_corner_to_post),
                    point_at_distance_in_a_line(
                        side_edge_and_midpoint[opponent_edge]['edge'][1],
                        side_edge_and_midpoint[opponent_edge]['edge'][0], length_from_corner_to_post)
                ]
            }}

        default_point_distance = self.cm_pixel_rate * DEFAULT_POSITION_TO_POST_LENGTH
        self.default_point = find_perpendicular_point_from_point_on_line(
            self.goal_posts['self']['edge_points'], self.goal_posts['self']['post_center_point'], default_point_distance, self.goal_posts['opponent']['post_center_point'])
        center_point = (side_edge_and_midpoint[self_edge]['post_center_point'] +
                        side_edge_and_midpoint[opponent_edge]['post_center_point'])/2
        self.center_point = list(map(int, center_point))
        self.default_point = find_perpendicular_point_from_point_on_line(
            self.goal_posts['self']['edge_points'], self.goal_posts['self']['post_center_point'], default_point_distance, self.goal_posts['opponent']['post_center_point'])


    def __del__(self):
        self.video_stream.stop()

class VideoStream:
    def __init__(self, url=None, image_path=None, video_path=None, target_fps=30):
        self.url = url
        self.image_path = image_path
        self.video_path = video_path
        self.latest_frame = None
        self.stopped = False
        self.lock = threading.Lock()  # Initialize a lock
        self.cap = None
        if image_path is None:
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

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # with self.lock:  # Lock access before updating
                    self.latest_frame = frame
                else:
                    print("Failed to grab frame.")
                    self.stop()
                    break
            else:
                print("Failed to open video stream.")
                self.stop()
                break

    def read(self):
        frame = self.latest_frame
        return frame.copy() if frame is not None else None

    def stop(self):
        self.stopped = True
        if self.cap:
            self.cap.release()

