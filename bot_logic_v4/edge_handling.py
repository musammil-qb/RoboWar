import cv2
import numpy as np
import math

def is_point_inside_border_v2(point, border_points):
    # Test if the point is inside, on, or outside the polygon
    
    result = cv2.pointPolygonTest(border_points, point, False)
    return result >= 0 

# Function to find the closest side and return an inside point along it
def find_parallel_point_inside_border(given_point, border_points, offset=40):
    # Define each side as a line segment
    sides = [
        ("top", border_points[0], border_points[1]),
        ("right", border_points[1], border_points[2]),
        ("bottom", border_points[2], border_points[3]),
        ("left", border_points[3], border_points[0])
    ]

    # Find the closest side to the given point
    min_distance = float('inf')
    closest_side = None
    for side_name, start, end in sides:
        distance = point_to_line_distance(given_point, start, end)
        if distance < min_distance:
            min_distance = distance
            closest_side = (side_name, start, end)

    # Now calculate the inside point along the closest side
    side_name, side_start, side_end = closest_side
    side_vector = side_end - side_start
    side_length = np.linalg.norm(side_vector)
    side_unit_vector = side_vector / side_length

    # Find perpendicular vector to move inside the border
    if side_name in ["top", "bottom"]:
        # perpendicular_vector = np.array([0, -1 if side_name == "top" else 1])
        perpendicular_vector = np.array([-side_unit_vector[1], side_unit_vector[0]])
    else:
        # perpendicular_vector = np.array([-1 if side_name == "left" else 1, 0])
        perpendicular_vector = np.array([-side_unit_vector[1], side_unit_vector[0]])
        
    if side_name == "right":
        offset = 100
    # Calculate the inside point by shifting along the perpendicular vector
    inside_point = given_point + offset * perpendicular_vector

    # Ensure the point is inside the polygon using cv2.pointPolygonTest
    is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0

    # If the calculated inside point is outside, decrease offset until it's inside
    while not is_inside and offset > 0 and offset < 200:
        if side_name == "right":
            offset += 10
        else:
            offset -= 10
        inside_point = given_point + offset * perpendicular_vector
        is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0
    return tuple(map(int, inside_point)), side_name


# Define a function to calculate the distance from a point to a line segment
def point_to_line_distance(point, line_start, line_end):
    line_vec = line_end - line_start
    point_vec = point - line_start
    line_length_squared = np.dot(line_vec, line_vec)
    
    # If the line length is zero (rare edge case), return distance to line_start
    if line_length_squared == 0:
        return np.linalg.norm(point - line_start)

    # Projection factor for the point onto the line
    projection_factor = np.dot(point_vec, line_vec) / line_length_squared
    projection_factor = max(0, min(1, projection_factor))  # Clamp between 0 and 1 for segment

    # Closest point on the line segment
    closest_point = line_start + projection_factor * line_vec
    distance = np.linalg.norm(point - closest_point)
    return distance


def closest_border_top_or_bottom(point, border_points):
    sides = [
        ("top", border_points[0], border_points[1]),
        ("bottom", border_points[2], border_points[3])
    ]

    # Calculate the distance to each side
    distances = {side_name: point_to_line_distance(point, start, end) for side_name, start, end in sides}
    
    # Find the side with the minimum distance
    closest_side = min(distances, key=distances.get)
    return closest_side, distances[closest_side]
