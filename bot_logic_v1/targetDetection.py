import numpy as np
import cv2
import math
from detection import Detection

extension_factor_before = 0.1  # Percentage for point before the ball
extension_factor_after = 0.15 
target_points = []
goal_points = []
nearest_extented_point = None

def define_trimmed_field(trim_factor=30):
    global trimmed_field
    # detection_object.field_corners instead of field_corners
    field_corners = [(12, 16), (626, 16), (626, 464), (12, 464)]
    p1, p2, p3, p4 = np.array(field_corners)
    trimmed_field = [
        (int(p1[0] + trim_factor), int(p1[1] + trim_factor)),
        (int(p2[0] - trim_factor), int(p2[1] + trim_factor)),
        (int(p3[0] - trim_factor), int(p3[1] - trim_factor)),
        (int(p4[0] + trim_factor), int(p4[1] - trim_factor))
    ]

def filter_balls(buffer_distance=20):
    filtered_balls = []

    for ball in detection_object['yolo'].balls:
        e1, e2 = calculate_extended_points(ball, detection_object['aruco'].goal_center_point, buffer_distance)

        if is_point_in_polygon(e1, trimmed_field) and is_point_in_polygon(e2, trimmed_field):
            filtered_balls.append(ball)
            target_points.append(e1)
            goal_points.append(e2)
        else:
            print(f"Ball at {ball} has an extended point outside the field; not targeted.")

    return filtered_balls, target_points, goal_points


def calculate_extended_points(ball_pos, buffer_distance):
    goal_center = detection_object['aruco'].goal_center_point
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

    # Print E1 and E2 coordinates for tracking
    print(f"E1 (before ball): {e1}")
    print(f"E2 (after ball): {e2}")
    
    return e1, e2

def is_point_in_polygon(point, polygon):
    #Check if a point is within a given polygon using OpenCV.
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def get_nearest_extended_point(points):
    bot_pos = detection_object['aruco'].bot_center_point
    closest = min(points, key=lambda point: math.sqrt((point[0] - bot_pos[0])**2 + (point[1] - bot_pos[1])**2))
    return closest

if __name__ == '__main__':
    define_trimmed_field()
    detection = Detection()
    detection_object = detection.process_frame()
    filtered_balls, target_points, goal_points = filter_balls()
    next_target_point = get_nearest_extended_point(target_points)
    print(next_target_point)
