import math
import cv2
import numpy as np

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to calculate the angle between two points
def calculate_angle_to_point(bot_position, target_position):
    dx = target_position[0] - bot_position[0]
    dy = target_position[1] - bot_position[1]
    angle_to_target = math.degrees(math.atan2(dy, dx)) % 360
    return angle_to_target

def draw_rectangle(frame, corners):
    if len(corners) == 4:
        cv2.polylines(frame, [np.array(corners)], isClosed=True, color=(0, 255, 0), thickness=2)
