import math
import cv2
import numpy as np
from const import GREEN

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to calculate the angle between two points
def calculate_angle_to_point(bot_position, target_position):
    dx = target_position[0] - bot_position[0]
    dy = target_position[1] - bot_position[1]
    angle_to_target = math.degrees(math.atan2(dy, dx)) % 360
    return angle_to_target

def draw_polygons(frame, corners,color=GREEN):
    cv2.polylines(frame, [np.array(corners)], isClosed=True, color=color, thickness=2)

def point_at_distance_in_a_line(p1, p2, distance_from_p1):
    x1, y1 = p1
    x2, y2 = p2
    total_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    # Calculate the unit direction vector from P1 to P2
    ux = (x2 - x1) / total_distance
    uy = (y2 - y1) / total_distance
    
    # Calculate the coordinates of the point at the specified distance from P1
    x = int(x1 + distance_from_p1 * ux)
    y = int(y1 + distance_from_p1 * uy)
    
    return (x, y)

def distance_to_segment(px, py, x1, y1, x2, y2):
    # Vector from A to B
    dx, dy = x2 - x1, y2 - y1
    # Vector from A to P
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    # Clamp t to the range [0, 1] to find the closest point within the segment
    t = max(0, min(1, t))
    # Calculate the projection point on the segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    # Calculate the distance from P to the closest point on the segment
    distance = math.sqrt((closest_x - px) ** 2 + (closest_y - py) ** 2)
    return distance, (closest_x, closest_y)

def find_closest_edge(point, edges):
    px, py = point
    min_distance = float('inf')
    closest_edge = None
    closest_point_on_edge = None

    for ((x1, y1), (x2, y2)) in edges:
        distance, closest_point = distance_to_segment(px, py, x1, y1, x2, y2)
        if distance < min_distance:
            min_distance = distance
            closest_edge = (x1, y1, x2, y2)
            closest_point_on_edge = closest_point

    return closest_edge, min_distance, closest_point_on_edge


def find_perpendicular_point_from_point_on_line(edges, point_on_line, distance, external_point):
    x3, y3 = point_on_line
    (x1, y1), (x2, y2) = edges

    # Calculate direction vector of the line
    dx = x2 - x1
    dy = y2 - y1
    
    # Calculate the magnitude of the direction vector
    magnitude = math.sqrt(dx**2 + dy**2)
    
    # Calculate the unit perpendicular vector
    ux_perpendicular = -dy / magnitude
    uy_perpendicular = dx / magnitude
    
    # Calculate the two perpendicular points at distance d
    p1_x = x3 + distance * ux_perpendicular
    p1_y = y3 + distance * uy_perpendicular
    p2_x = x3 - distance * ux_perpendicular
    p2_y = y3 - distance * uy_perpendicular

    # Calculate distances to the reference point
    ref_x,ref_y =  external_point
    distance_p1 = math.sqrt((p1_x - ref_x) ** 2 + (p1_y - ref_y) ** 2)
    distance_p2 = math.sqrt((p2_x - ref_x) ** 2 + (p2_y - ref_y) ** 2)
    
    # Return the point closer to the reference point
    if distance_p1 < distance_p2:
        return (int(p1_x), int(p1_y))
    else:
        return (int(p2_x), int(p2_y))

def find_closest_corner(polygon_corners, point):
    closest_corners = []

    for i, corner in enumerate(polygon_corners):
        dist_to_point = calculate_distance(corner, point)
        closest_corners.append((i, dist_to_point))

    closest_corners.sort(key=lambda x: x[1])
    return closest_corners[0][0]

def is_point_inside_border(point, border_points):
    # Test if the point is inside, on, or outside the polygon    
    result = cv2.pointPolygonTest(border_points, point, False)
    return result >= 0 