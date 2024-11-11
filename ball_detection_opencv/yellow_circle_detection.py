import cv2
import numpy as np

lower_yellow = np.array([22, 150, 140])
upper_yellow = np.array([33, 255, 255])
# Function to detect yellow circles in a frame or image
def detect_yellow_circle(frame
                         ,  corners, lower_yellow=lower_yellow, upper_yellow=upper_yellow):
    # Convert the image to HSV (hue, saturation, value) color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    kernel = np.ones((3, 3), np.uint8) 
    erode = cv2.erode(mask,kernel)
    kernel = np.ones((1000, 1000), np.uint8) 
    # dilate = cv2.dilate(erode,kernel)
    # Perform a bitwise AND to keep only the yellow parts of the image
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return mask

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
                               param1=100, param2=30, minRadius=5, maxRadius=100)
    # If circles are detected, draw them on the frame (only inside the rectangle)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Explicitly cast x and y to float for pointPolygonTest
            if cv2.pointPolygonTest(points, (float(x), float(y)), False) >= 0:
                # Draw the outer circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                # Draw the center of the circle
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

    return frame

if __name__ == '__main__':
    # Load the image from file
    images = [
        {'image_path': 'Data/droidcam-20241022-211211.jpg',
            'corners': [[82, 37], [85, 424], [586, 434], [598,  38]]},
        {'image_path': 'Data/droidcam-20241022-211204.jpg', 'corners': [[82, 38], [85, 424], [588, 431], [596, 38]]}]
    image=images[0]
    image_frame = cv2.imread(image['image_path'])

    # # Check if image is loaded properly
    if image is None:
        print("Error: Could not open or find the image.")
    else:
        # Detect yellow circles in the image
        output_image = detect_yellow_circle(image_frame,image['corners'])

        # Display the image with detected circles
        cv2.imshow("Yellow Circle Detection", output_image)

        # Wait for a key press and close the window
        cv2.waitKey(0)
    #     cv2.destroyAllWindows()