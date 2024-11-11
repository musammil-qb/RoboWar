import cv2
import numpy as np
from time import time

from field_detection import detect_field, draw_field
from yellow_circle_detection import detect_yellow_circle
from find_color import calibrate_colors
from field_selection import select_field
# Load the image from file
image_paths = [
    # 'output_image13.jpg',
    # 'output_image23.jpg',
    # 'output_image33.jpg',
    # 'output_image3.jpg',
    'output_image43.jpg',
    # 'output_image9.jpg'
    ]
lower_yellow = np.array([0, 34, 231])
upper_yellow = np.array([58, 235, 255])
def main():
    corners = select_field(image_paths[0])    # Detect the largest greenish rectangle and find its corners
    for image_path in image_paths:
        start_time = time()
        image = cv2.imread(image_path)
        image = detect_yellow_circle(image,corners,lower_yellow=lower_yellow, upper_yellow= upper_yellow)

        image = draw_field(image,corners)
        cv2.namedWindow("Green Field"+image_path,cv2.WINDOW_NORMAL)
        cv2.imshow("Green Field"+image_path, image)

        end_time = time()
        print(f"Time taken: {end_time-start_time}")
        # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()