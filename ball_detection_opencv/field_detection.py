import cv2
import numpy as np
import time
# Define the range for green color in HSV (adjust these values if needed)
lower_green = np.array([50, 0, 44]) 
upper_green = np.array([83, 220, 227])

# Function to detect the largest greenish rectangle and find its corners
def detect_field(frame,lower_green=lower_green, upper_green=upper_green):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

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


def draw_field(image, green_field,corners):

   # Draw the largest rectangle on the original image
    cv2.drawContours(image, [green_field], -1, (0, 255, 0), 3)
    # Mark each corner with a circle
    for (x, y) in corners:
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
    return image