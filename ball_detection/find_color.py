import cv2
import numpy as np

# Callback function for the trackbars (it does nothing, but is required for the trackbars to work)
def nothing(x):
    pass

# Load the image
image_path = 'Data/droidcam-20241022-211204.jpg'  # Replace with your image path
image = cv2.imread(image_path)

if image is None:
    print("Error: Could not open or find the image.")
    exit()

# Create a window for the trackbars
cv2.namedWindow("Trackbars")
color='yellow'
if color == 'green':
    # Create trackbars for lower and upper HSV values
    cv2.createTrackbar("Lower Hue", "Trackbars", 0, 179, nothing)
    cv2.createTrackbar("Lower Saturation", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("Lower Value", "Trackbars", 0, 255, nothing)

    cv2.createTrackbar("Upper Hue", "Trackbars", 179, 179, nothing)
    cv2.createTrackbar("Upper Saturation", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Upper Value", "Trackbars", 255, 255, nothing)
elif color=='yellow':
    cv2.createTrackbar("Lower Hue", "Trackbars", 20, 179, nothing)  
    cv2.createTrackbar("Lower Saturation", "Trackbars", 100, 255, nothing)
    cv2.createTrackbar("Lower Value", "Trackbars", 100, 255, nothing)

    cv2.createTrackbar("Upper Hue", "Trackbars", 30, 179, nothing)
    cv2.createTrackbar("Upper Saturation", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Upper Value", "Trackbars", 255, 255, nothing)


# Function to get HSV range from trackbars

def get_hsv_range():
    lower_hue = cv2.getTrackbarPos("Lower Hue", "Trackbars")
    lower_saturation = cv2.getTrackbarPos("Lower Saturation", "Trackbars")
    lower_value = cv2.getTrackbarPos("Lower Value", "Trackbars")

    upper_hue = cv2.getTrackbarPos("Upper Hue", "Trackbars")
    upper_saturation = cv2.getTrackbarPos("Upper Saturation", "Trackbars")
    upper_value = cv2.getTrackbarPos("Upper Value", "Trackbars")

    lower_bound = np.array([lower_hue, lower_saturation, lower_value])
    upper_bound = np.array([upper_hue, upper_saturation, upper_value])

    return lower_bound, upper_bound

while True:
    # Convert the image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Get the current positions of the trackbars
    lower_bound, upper_bound = get_hsv_range()

    # Create a mask with the current HSV range
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply the mask to the original image
    result = cv2.bitwise_and(image, image, mask=mask)

    # Display the result
    cv2.imshow("Masked Image", result)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"Selected lower HSV: {lower_bound}")
        print(f"Selected upper HSV: {upper_bound}")
        break

# Close all windows
cv2.destroyAllWindows()
