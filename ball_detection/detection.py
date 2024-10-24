import cv2
from time import time

from field_detection import detect_field, draw_field
from yellow_circle_detection import detect_yellow_circle

# Load the image from file
image_paths = ['Data/droidcam-20241022-211204.jpg',
               'Data/droidcam-20241022-211202.jpg',
              'Data/droidcam-20241022-211211.jpg']


    # Detect the largest greenish rectangle and find its corners
for image_path in image_paths:
    start_time = time()

    image = cv2.imread(image_path)
    green_field = detect_field(image)
    corners = green_field.reshape(4, 2)
    image = detect_yellow_circle(image,corners)

    # image = draw_field(image, green_field,corners)
    cv2.imshow("Green Field"+image_path, image)

    end_time = time()
    print(f"Time taken: {end_time-start_time}")
    # Wait for a key press and close the window
cv2.waitKey(0)
cv2.destroyAllWindows()