import cv2
from time import time


def resize_to_max_dimensions(current_width, current_height, max_width, max_height, frame):
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

    return cv2.resize(frame, (new_width, new_height))

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
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
    
        resized_frame = resize_to_max_dimensions(original_width, original_height,1500,800,frame=frame)

        cv2.imshow('Video', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
