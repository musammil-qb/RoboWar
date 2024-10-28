import cv2
from time import time

from field_detection import detect_field, draw_field
from yellow_circle_detection import detect_yellow_circle

# Load the image from file
video_paths = [
  'Data/green_arena/20241023_162704.mp4','Data/green_arena/20241023_163240.mp4','Data/green_arena/20241023_164256.mp4',
  'Data/green_arena/PXL_20241023_115208820.mp4','Data/green_arena/20241023_162718.mp4',
  'Data/green_arena/20241023_163455.mp4','Data/green_arena/PXL_20241023_114723402.mp4',
    ]


    # Detect the largest greenish rectangle and find its corners
for video_path in video_paths:
    vs = cv2.VideoCapture(video_path)
    while True:
    # grab the current frame
        grabbed, image = vs.read()
        if image is None:
            break

        start_time = time()
        green_field = detect_field(image)
        corners = green_field.reshape(4, 2)
        image = detect_yellow_circle(image,corners)

        image = draw_field(image, green_field,corners)
        cv2.imshow("Video", image)

        end_time = time()
        print(f"Time taken: {end_time-start_time}")
    # Wait for a key press and close the window

cv2.waitKey(0)
cv2.destroyAllWindows()