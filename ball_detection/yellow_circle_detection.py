import cv2
import numpy as np

lower_yellow = np.array([22, 150, 140])
upper_yellow = np.array([33, 255, 255])
# Function to detect yellow circles in a frame or image
def detect_yellow_circle(frame
                         , corners):
    # Convert the image to HSV (hue, saturation, value) color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Perform a bitwise AND to keep only the yellow parts of the image
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Create a mask with the rectangular region defined by the four corners
    rect_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    points = np.array([corners], dtype=np.int32)  # Convert the corners to a NumPy array
    cv2.fillPoly(rect_mask, points, 255)  # Fill the polygon (rectangle) with white

    # Apply the rectangle mask to the yellow result
    result_masked = cv2.bitwise_and(result, result, mask=rect_mask)
    # Convert the result to grayscale for circle detection
    gray = cv2.cvtColor(result_masked, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    # TODO configure
    # Detect circles using the Hough Circle Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                               param1=100, param2=30, minRadius=1, maxRadius=100)
    # If circles are detected, draw them on the frame (only inside the rectangle)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Check if the circle's center (x, y) is inside the rectangular region
            if cv2.pointPolygonTest(points, (x, y), False) >= 0:  # Point inside the polygon
                # Draw the outer circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                # Draw the center of the circle
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

    return frame

# Load the image from file
# image_path = 'Data/droidcam-20241022-211204.jpg'  # Replace with your image path
# image = cv2.imread(image_path)

# # Check if image is loaded properly
# if image is None:
#     print("Error: Could not open or find the image.")
# else:
#     # Detect yellow circles in the image
#     output_image = detect_yellow_circle(image)

#     # Display the image with detected circles
#     cv2.imshow("Yellow Circle Detection", output_image)

#     # Wait for a key press and close the window
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
