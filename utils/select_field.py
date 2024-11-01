import cv2
import numpy as np
import math

# Initialize a list to store the corners and a variable to track the mouse position
corners = []
mouse_position = None

# Real-world field dimensions in centimeters (6 feet x 8 feet)
FIELD_WIDTH_CM = 244
FIELD_HEIGHT_CM = 183

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
                calculate_and_save_pixel_to_cm_ratio(corners)
                print("Corners and pixel-to-cm ratio saved to field_corners.py")

# Function to draw the rectangle based on selected corners
def draw_rectangle(frame, corners):
    if len(corners) == 4:
        cv2.polylines(frame, [np.array(corners)], isClosed=True, color=(0, 255, 0), thickness=2)

# Function to trace mouse movement
def trace_mouse(frame, mouse_position):
    if mouse_position is not None:
        # Draw a circle at the mouse position
        cv2.circle(frame, mouse_position, 5, (255, 0, 0), -1)

# Function to calculate distance between two points
def distance_between_points(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Function to calculate pixel-to-cm ratio and save it to file
def calculate_and_save_pixel_to_cm_ratio(corners):
    # Calculate pixel distances
    width_px = distance_between_points(corners[0], corners[1])
    height_px = distance_between_points(corners[1], corners[2])
    
    # Calculate pixel-to-cm conversion factors
    pixel_to_cm_width = FIELD_WIDTH_CM / width_px
    pixel_to_cm_height = FIELD_HEIGHT_CM / height_px
    
    # Print and save the conversion factors
    print(f"Pixel-to-CM (Width): {pixel_to_cm_width:.4f} cm/pixel")
    print(f"Pixel-to-CM (Height): {pixel_to_cm_height:.4f} cm/pixel")
    
    with open("field_corners.py", "w") as file:
        file.write(f"corner1 = {corners[0]}\n")
        file.write(f"corner2 = {corners[1]}\n")
        file.write(f"corner3 = {corners[2]}\n")
        file.write(f"corner4 = {corners[3]}\n")
        file.write(f"pixel_to_cm_width = {pixel_to_cm_width:.4f}\n")
        file.write(f"pixel_to_cm_height = {pixel_to_cm_height:.4f}\n")

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
