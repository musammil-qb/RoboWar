import cv2
import numpy as np

# Initialize a list to store the corners and a variable to track the mouse position
corners = []
mouse_position = None

# Mouse callback function to capture the corner points and mouse position
def select_corners(event, x, y, flags, param):
    global corners, mouse_position
    mouse_position = (x, y)  # Update the mouse position
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 4:  # Limit to 4 corners
            corners.append((x, y))
            print(f"Corner {len(corners)}: ({x}, {y})")
            if len(corners) == 4:  # Draw rectangle after selecting 4 corners
                cv2.destroyWindow("Select Rectangle")

# Function to draw the rectangle based on selected corners
def draw_rectangle(frame, corners):
    if len(corners) == 4:
        cv2.polylines(frame, [np.array(corners)], isClosed=True, color=(0, 255, 0), thickness=2)

# Function to trace mouse movement
def trace_mouse(frame, mouse_position):
    if mouse_position is not None:
        # Draw a circle at the mouse position
        cv2.circle(frame, mouse_position, 5, (255, 0, 0), -1)

# Main function to capture video and select rectangle
def main():
    global corners, mouse_position
    
    # Open video capture
    cap = cv2.VideoCapture(0)  # Change 0 to a video file path if needed

    # Create a window for selecting corners
    cv2.namedWindow("Select Rectangle")
    cv2.setMouseCallback("Select Rectangle", select_corners)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break

        # Draw rectangle on the frame
        draw_rectangle(frame, corners)

        # Trace mouse movement
        trace_mouse(frame, mouse_position)

        # Display the video frame
        cv2.imshow("Select Rectangle", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
