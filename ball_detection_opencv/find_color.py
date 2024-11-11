import cv2
import numpy as np
import sys

def nothing(x):
    pass

# Create a window for the trackbars
cv2.namedWindow("Trackbars")

# Create trackbars for yellow
def create_yellow_trackbars():
    cv2.createTrackbar("Lower Hue", "Trackbars", 20, 179, nothing)  
    cv2.createTrackbar("Lower Saturation", "Trackbars", 100, 255, nothing)
    cv2.createTrackbar("Lower Value", "Trackbars", 100, 255, nothing)

    cv2.createTrackbar("Upper Hue", "Trackbars", 30, 179, nothing)
    cv2.createTrackbar("Upper Saturation", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Upper Value", "Trackbars", 255, 255, nothing)

# Create trackbars for green
def create_green_trackbars():
    cv2.createTrackbar("Lower Hue (Green)", "Trackbars", 0, 179, nothing)
    cv2.createTrackbar("Lower Saturation (Green)", "Trackbars", 100, 255, nothing)
    cv2.createTrackbar("Lower Value (Green)", "Trackbars", 100, 255, nothing)

    cv2.createTrackbar("Upper Hue (Green)", "Trackbars", 60, 179, nothing)
    cv2.createTrackbar("Upper Saturation (Green)", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Upper Value (Green)", "Trackbars", 255, 255, nothing)

# Function to get HSV range from trackbars
def get_hsv_range(prefix=''):
    lower_hue = cv2.getTrackbarPos(f"Lower Hue{prefix}", "Trackbars")
    lower_saturation = cv2.getTrackbarPos(f"Lower Saturation{prefix}", "Trackbars")
    lower_value = cv2.getTrackbarPos(f"Lower Value{prefix}", "Trackbars")

    upper_hue = cv2.getTrackbarPos(f"Upper Hue{prefix}", "Trackbars")
    upper_saturation = cv2.getTrackbarPos(f"Upper Saturation{prefix}", "Trackbars")
    upper_value = cv2.getTrackbarPos(f"Upper Value{prefix}", "Trackbars")

    lower_bound = np.array([lower_hue, lower_saturation, lower_value])
    upper_bound = np.array([upper_hue, upper_saturation, upper_value])

    return lower_bound, upper_bound

# Main loop for calibration
def calibrate_color(color_name, create_trackbars_fn, image):

    print(f"Calibrate {color_name}")
    create_trackbars_fn()

    while True:
        # Convert the image to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = image.shape[:2]
        # Get the current positions of the trackbars
        lower_bound, upper_bound = get_hsv_range('' if color_name == 'Yellow' else ' (Green)')

        # Create a mask with the current HSV range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # Apply the mask to the original image
        result = cv2.bitwise_and(image, image, mask=mask)

        # Display the result
        cv2.imshow("Masked Image",  result)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return lower_bound,upper_bound

def calibrate_colors(image_path):
    image = cv2.imread(image_path)
    # Calibrate yellow first
    lower_yellow, upper_yellow = calibrate_color("Yellow", create_yellow_trackbars,image)

    # Clear the trackbars and create them for green
    cv2.destroyAllWindows()
    cv2.namedWindow("Trackbars")
    lower_green, upper_green = calibrate_color("Green", create_green_trackbars,image)

    # Close all windows
    cv2.destroyAllWindows()

    print(f"Yellow Lower HSV: {lower_yellow}")
    print(f"Yellow Upper HSV: {upper_yellow}")
    print(f"Green Lower HSV: {lower_green}")
    print(f"Green Upper HSV: {upper_green}")
    return lower_yellow, upper_yellow, lower_green, upper_green

if __name__ == '__main__':
    image_path = sys.argv[1]
    print(image_path)
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not open or find the image.")
        exit()

    calibrate_colors(image_path)