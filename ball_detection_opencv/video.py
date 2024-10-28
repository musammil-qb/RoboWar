import cv2
from time import time
import numpy as np


from field_detection import detect_field, draw_field
from yellow_circle_detection import detect_yellow_circle

# Open the video file
video_path = 'Data/green_arena/20241023_162704.mp4'  # Replace with the path to your video file
cap = cv2.VideoCapture(video_path)

def resize_to_max_dimensions(current_width, current_height, max_width, max_height):
    aspect_ratio = current_width / current_height
    if current_width > max_width or current_height > max_height:
        if (max_width / aspect_ratio) <= max_height:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
    else:
        new_width = current_width
        new_height = current_height

    return new_width, new_height


original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
desired_width, desired_height = resize_to_max_dimensions(original_width, original_height,1500,800)
print(desired_height,  desired_width)
# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    success, frame = cap.read()  
    # Break the loop if there are no frames left
    if not success:
        print("End of video.")
        break
    old_image = frame.copy()
    start_time = time()
    lower_green, upper_green = np.array([36, 0, 43]), np.array([[114, 129, 215]])
    green_field = detect_field(frame,lower_green, upper_green)
    corners = green_field.reshape(4, 2)
    lower_yellow, upper_yellow =  np.array([ 22,  87 ,157]), np.array([ 46 ,245 ,255])
    frame = detect_yellow_circle(frame,corners,lower_yellow, upper_yellow)

    frame = draw_field(frame, green_field,corners)
    resized_frame = cv2.resize(frame, (desired_width, desired_height))
    old_image = cv2.resize(old_image, (desired_width, desired_height))

    cv2.imshow('Video', resized_frame)
    cv2.imshow('old Video', old_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
