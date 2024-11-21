import cv2
import numpy as np

# Initialize lists to store the corners, goal post points, and a variable to track the mouse position
corners = []
goal_post_points = []
mouse_position = None

# Mouse callback function to capture the corner points, goal post points, and mouse position
def select_points(event, x, y, flags, param):
    global corners, goal_post_points, mouse_position
    mouse_position = (x, y)  # Update the mouse position

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 4:  # Limit to 4 corners for the field
            corners.append((x, y))
            print(f"Field Corner {len(corners)}: ({x}, {y})")
        
        # After selecting the field, allow for goal post selection (2 points)
        if len(corners) == 4 and len(goal_post_points) < 2:
            goal_post_points.append((x, y))
            print(f"Goal Post Point {len(goal_post_points)}: ({x}, {y})")

            # Once 2 goal post points are selected, create the 8-sided polygon
            if len(goal_post_points) == 2:
                create_polygon()

# Function to draw the rectangle (field) and goal post connections
def draw_polygon(frame, corners, goal_post_points):
    if len(corners) == 4:
        cv2.polylines(frame, [np.array(corners)], isClosed=True, color=(0, 255, 0), thickness=2)  # Field rectangle
        
    if len(goal_post_points) == 2:
        # Goal post lines connecting the rectangle (field) to the goal post points
        cv2.line(frame, corners[0], goal_post_points[0], (255, 0, 0), 2)  # Top left goal post connection
        cv2.line(frame, corners[3], goal_post_points[1], (255, 0, 0), 2)  # Bottom right goal post connection

        # Draw the goal posts
        cv2.circle(frame, goal_post_points[0], 5, (0, 0, 255), -1)  # First goal post point
        cv2.circle(frame, goal_post_points[1], 5, (0, 0, 255), -1)  # Second goal post point

# Function to create the 8-sided polygon (connected rectangle with goal posts)
def create_polygon():
    global corners, goal_post_points

    # Assuming goal post points are connected at the left and right goal post locations
    field_width = np.linalg.norm(np.array(corners[0]) - np.array(corners[3]))
    field_height = np.linalg.norm(np.array(corners[0]) - np.array(corners[1]))

    # Calculate the goal post corners (top and bottom) to form an 8-sided polygon
    top_left_goal_post = goal_post_points[0]
    bottom_right_goal_post = goal_post_points[1]

    # Create the 8-point polygon by connecting goal posts to the field rectangle
    extended_corners = [
        corners[0], corners[1], corners[2], corners[3],
        top_left_goal_post, bottom_right_goal_post
    ]
    extended_corners = np.array(extended_corners, dtype=np.int32)
    extended_corners = extended_corners.reshape((-1, 1, 2))

    # Draw the polygon (8-sided shape)
    cv2.polylines(frame, [extended_corners], isClosed=True, color=(0, 255, 255), thickness=2)

# Function to trace mouse movement
def trace_mouse(frame, mouse_position):
    if mouse_position is not None:
        # Draw a circle at the mouse position
        cv2.circle(frame, mouse_position, 5, (255, 0, 0), -1)

# Main function to capture video and select rectangle
def main():
    global corners, goal_post_points, mouse_position, frame

    # Open video capture
    cap = cv2.VideoCapture(0)  # Change 0 to a video file path if needed

    # Create a window for selecting points
    cv2.namedWindow("Select Rectangle and Goal Post")
    cv2.setMouseCallback("Select Rectangle and Goal Post", select_points)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break

        # Draw the rectangle (field) and goal post connections
        draw_polygon(frame, corners, goal_post_points)

        # Trace mouse movement
        trace_mouse(frame, mouse_position)

        # Display the video frame
        cv2.imshow("Select Rectangle and Goal Post", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
