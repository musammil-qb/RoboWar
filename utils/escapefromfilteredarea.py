import cv2
import numpy as np
import math
import os

cap = cv2.imread("/home/qburst/ctf/hacknight/imagedetection/hacknight-pythoncodes/utils/aruco/new_images_withour_bot/output_image9.jpg")
# Initialize a list to store the corners and a variable to track the mouse position
corners = []
mouse_position = None
points = []

Green = (0, 255, 0)
Red = (0, 0, 255)
Blue = (255, 0, 0)

# Mouse callback function to capture the corner points and mouse position
def select_corners(event, x, y, flags, param):
    global corners, mouse_position
    mouse_position = (x, y)  # Update the mouse position
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 4:  # Limit to 4 corners
            corners.append((x, y))
            print(f"Corner {len(corners)}: ({x}, {y})")
            
            # Save corners to file once four corners are selected
            if len(corners) == 4:
                # save_corners_to_file(corners)
                print("Corners saved to field_corners.py")
        else:
            points.append((x,y))


# Function to draw the rectangle based on selected corners
def draw_rectangle(frame, corners, color):
    if len(corners) == 4:
        cv2.polylines(frame, [np.array(corners)], isClosed=True, color=color, thickness=2)

# Function to trace mouse movement
def trace_mouse(frame, mouse_position):
    if mouse_position is not None:
        # Draw a circle at the mouse position
        cv2.circle(frame, mouse_position, 1, (255, 0, 0), 1)

def define_trimmed_field(corners):
        field_corners = corners
        trim_factor = 0.06
        trim_length = calculate_distance(field_corners[0], field_corners[1])*trim_factor
        
        p1, p2, p3, p4 = np.array(field_corners)
        trimmed_field = [
            (int(p1[0] + trim_length), int(p1[1] + trim_length)),
            (int(p2[0] - trim_length), int(p2[1] + trim_length)),
            (int(p3[0] - trim_length), int(p3[1] - trim_length)),
            (int(p4[0] + trim_length), int(p4[1] - trim_length))
        ]
        # trimmed_field = [
        #     (int(p1[0] + trim_length), int(p1[1] + trim_length)),
        #     (int(p2[0]), int(p2[1] + trim_length)),
        #     (int(p3[0] - trim_length), int(p3[1] - trim_length)),
        #     (int(p4[0] + trim_length), int(p4[1] - trim_length))
        # ]
        trimmed_field = trimmed_field
        return trimmed_field

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

extension_factor_before = 0.1
extension_factor_after = 0.1

def calculate_extended_points(ball_pos,goal_center, buffer_distance=20):
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

def is_point_inside_border_v2(point, border_points):
    # Test if the point is inside, on, or outside the polygon
    result = cv2.pointPolygonTest(border_points, point, False)
    return result >= 0  # >=0 means inside or on the border, -1 means outside

# Function to find a parallel point inside the border
# def find_parallel_point_inside_border(given_point, border_points, offset=40):
#     # Define the top border as the line segment between the first two points
#     top_start, top_end = border_points[0], border_points[1]
    
#     # Calculate the direction vector of the top border
#     top_vector = top_end - top_start
    
#     # Normalize the top vector to find the perpendicular offset
#     top_length = np.linalg.norm(top_vector)
#     top_unit_vector = top_vector / top_length
    
#     # Calculate the perpendicular vector (90 degrees to the right)
#     perpendicular_vector = np.array([-top_unit_vector[1], top_unit_vector[0]])
    
#     # Shift the given point parallel and down (inside the border)
#     inside_point = given_point - offset * perpendicular_vector
#     is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0
    
#     # If point is outside, adjust the offset inward until it's inside
#     while not is_inside:
#         offset -= 10
#         inside_point = given_point + offset * perpendicular_vector
#         is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0

#     return tuple(map(int, inside_point))

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

# Create a window for selecting corners
cv2.namedWindow("Select Rectangle")
cv2.setMouseCallback("Select Rectangle", select_corners)
bot_offset = 1

while True:
    
    # ret, frame = cap.read()
    # Draw rectangle on the frame
    draw_rectangle(cap, corners, Green)
    if len(corners) == 4:
        trimmed_field = define_trimmed_field(corners)
        draw_rectangle(cap, trimmed_field, Blue)

        if len(points) >= 2:
            e1, e2 = calculate_extended_points(points[0], points[1])
            cv2.circle(cap, e1, 2, Red, 2)
            trimmed_field = np.array(trimmed_field)

            if not is_point_inside_border_v2(e1, trimmed_field):
                next_viable_point, side_name = find_parallel_point_inside_border(e1,np.array(corners))
                if side_name != "right" or side_name != "left":
                    # closest_side, _ = closest_border_top_or_bottom(next_viable_point, np.array(corners))
                    midpoint = (int((next_viable_point[0] + points[0][0]) / 2), int((next_viable_point[1] + points[0][1]) / 2))
                    midpoint = next_viable_point + bot_offset * np.array([1,1])
                    # print(midpoint)
                    cv2.circle(cap, midpoint, 2, Green, 2)
                    if side_name == "top":
                        print("Anti-Clockwise")
                    if side_name == "bottom":
                        print("Clockwise")

    # Trace mouse movement
    # trace_mouse(cap, mouse_position)

    # Display the video frame
    cv2.imshow("Select Rectangle", cap)

    # Exit the stream on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()