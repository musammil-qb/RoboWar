import numpy as np
import cv2
import math
from detection import Detection

extension_factor_before = 0.1  # Percentage for point before the ball
extension_factor_after = 0.15 

def filter_balls(trimmed_field,balls, goal_center_point,buffer_distance=20):
    filtered_balls = []
    intersection_points = []
    for ball in balls:
        e1, e2 = calculate_extended_points(ball,goal_center_point, buffer_distance)

        if is_point_in_polygon(e1, trimmed_field) and is_point_in_polygon(e2, trimmed_field):
            filtered_balls.append(ball)
            intersection_points.append({'target_point':e1, 'goal_point':e2})
        else:
            print(f"Ball at {ball} has an extended point outside the field; not targeted.")

    return filtered_balls, intersection_points


def calculate_extended_points(ball_pos,goal_center, buffer_distance):
    dx, dy = goal_center[0] - ball_pos[0], goal_center[1] - ball_pos[1]
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return ball_pos, ball_pos  # Avoid division by zero

    # Normalize direction vector
    dx, dy = dx / length, dy / length  

    # Calculate the distances for E1 and E2
    dist_e1 = max(extension_factor_before * length, buffer_distance)
    dist_e2 = max(extension_factor_after * length, buffer_distance)

    # E1: Extended point before the ball
    x_e1 = int(ball_pos[0] - dist_e1 * dx)
    y_e1 = int(ball_pos[1] - dist_e1 * dy)
    e1 = (x_e1, y_e1)

    # E2: Extended point after the ball
    x_e2 = int(ball_pos[0] + dist_e2 * dx)
    y_e2 = int(ball_pos[1] + dist_e2 * dy)
    e2 = (x_e2, y_e2)
    
    return e1, e2

def is_point_in_polygon(point, polygon):
    #Check if a point is within a given polygon using OpenCV.
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def choose_next_target_point(intersection_points, bot_center_point):
    return min(intersection_points, key=lambda point: math.sqrt((point['target_point'][0] - bot_center_point[0])**2 + (point['target_point'][1] - bot_center_point[1])**2))

if __name__ == '__main__':
    define_trimmed_field()
    detection = Detection()
    detection_object = detection.process_frame()
    filtered_balls, intersection_points = filter_balls()
    next_target_point = min(intersection_points, key=lambda point: math.sqrt((point['target_point'][0] - bot_center_point[0])**2 + (point['target_point'][1] - bot_center_point[1])**2))
    print(next_target_point)
