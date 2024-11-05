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
    print(e1)
    
    return e1, e2

def is_point_inside_border_v2(point, border_points):
    # Test if the point is inside, on, or outside the polygon
    result = cv2.pointPolygonTest(border_points, point, False)
    return result >= 0  # >=0 means inside or on the border, -1 means outside

# Function to find a parallel point inside the border
def find_parallel_point_inside_border(given_point, border_points, offset=1000, inward_margin=10):
    # Define the top border as the line segment between the first two points
    top_start, top_end = border_points[0], border_points[1]
    
    # Calculate the direction vector of the top border
    top_vector = top_end - top_start
    
    # Normalize the top vector to find the perpendicular offset
    top_length = np.linalg.norm(top_vector)
    top_unit_vector = top_vector / top_length
    
    # Calculate the perpendicular vector (90 degrees to the right)
    perpendicular_vector = np.array([-top_unit_vector[1], top_unit_vector[0]])
    
    # Shift the given point parallel and down (inside the border)
    inside_point = given_point - 20000 * perpendicular_vector
    is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0
    
    # If point is outside, adjust the offset inward until it's inside
    # while not is_inside:
    #     offset -= 10
    #     inside_point = given_point + offset * perpendicular_vector
    #     is_inside = cv2.pointPolygonTest(border_points, tuple(inside_point), False) >= 0
    
    # inside_point = inside_point + inward_margin * perpendicular_vector

    return inside_point

# Create a window for selecting corners
cv2.namedWindow("Select Rectangle")
cv2.setMouseCallback("Select Rectangle", select_corners)

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
                next_viable_point = find_parallel_point_inside_border(e1,np.array(corners))
                cv2.circle(cap, e1, 2, Green, 2)



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