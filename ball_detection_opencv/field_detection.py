import cv2
import numpy as np
import time
import sys

# Define the range for green color in HSV (adjust these values if needed)
lower_green = np.array([50, 0, 44]) 
upper_green = np.array([83, 220, 227])
lower_green = np.array([80,50,68])
upper_green= np.array([179 ,255, 255])

# Function to detect the largest greenish rectangle and find its corners
def detect_field(frame,lower_green=lower_green, upper_green=upper_green):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)
    cv2.imshow("Mask", mask)
    cv2.waitKey(0)
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    green_field = None
    max_area = 0

    # Loop over the contours to find the largest rectangular shape (the field)
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # If the contour has 4 corners and its area is larger than the current max area
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > max_area:
                max_area = area
                green_field = approx

    # If a largest rectangle is found, draw it and mark the corners
    return green_field


def draw_field(image,corners):

   # Draw the largest rectangle on the original image
    cv2.drawContours(image, np.array([corners]), -1, (0, 255, 0), 3)
    # Mark each corner with a circle
    for (x, y) in corners:
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
    return image

if __name__ == "__main__":
    image_path = sys.argv[1]
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not open or find the image.")
        exit()

    green_field = detect_field(image)
    corners = green_field.reshape(4, 2)
    image = draw_field(image, green_field,corners)
    cv2.imshow("Green Field", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()