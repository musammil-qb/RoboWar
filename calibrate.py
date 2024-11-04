import cv2
import math
import numpy as np

# Calibration constants (temporary placeholders)
EXPECTED_MOVE_DISTANCE_PIXELS = 200  # The bot is supposed to move this distance in pixels
EXPECTED_ROTATION_DEGREES = 90      # The bot is supposed to rotate this many degrees

# Correction factors initialized to 1 (no correction initially)
distance_correction_factor = 1.0
rotation_correction_factor = 1.0

# Temporary initial bot position and angle
bot_center_point = (320, 240)
bot_angle = 0  # Assume the bot starts facing right (0 degrees)

# Mouse click to set new bot position after a move
new_position = None

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Mouse callback to set the bot's new position
def set_new_position(event, x, y, flags, param):
    global new_position
    if event == cv2.EVENT_LBUTTONDOWN:
        new_position = (x, y)
        print(f"New position set at: {new_position}")

def calibrate_movement():
    global distance_correction_factor, bot_center_point, new_position

    # Display instruction to move the bot by a known distance
    print("Move the bot by a known distance (200 pixels) and click on the bot's new position.")

    # Wait for user to click on bot's new position
    while new_position is None:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break

        # Draw original and new positions if available
        cv2.circle(frame, bot_center_point, 5, (0, 255, 0), -1)
        if new_position is not None:
            cv2.circle(frame, new_position, 5, (0, 0, 255), -1)
        
        cv2.imshow("Calibration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Calculate actual distance moved
    actual_distance_moved = calculate_distance(bot_center_point, new_position)
    print(f"Actual distance moved: {actual_distance_moved} pixels")

    # Calculate correction factor
    distance_correction_factor = EXPECTED_MOVE_DISTANCE_PIXELS / actual_distance_moved
    print(f"Distance correction factor: {distance_correction_factor}")

    # Reset position for next calibration
    bot_center_point = new_position

def calibrate_rotation():
    global rotation_correction_factor, bot_angle

    # Assume bot rotated 90 degrees, prompt user to verify the new angle
    print("Rotate the bot by 90 degrees and click on the bot's new direction.")

    # Wait for the user to click the new position to determine the rotation angle
    while new_position is None:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break

        # Draw original position and mark new position if available
        cv2.circle(frame, bot_center_point, 5, (0, 255, 0), -1)
        if new_position is not None:
            cv2.circle(frame, new_position, 5, (0, 0, 255), -1)
        
        cv2.imshow("Calibration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Calculate the actual rotation angle
    dx = new_position[0] - bot_center_point[0]
    dy = new_position[1] - bot_center_point[1]
    actual_rotation_angle = (math.degrees(math.atan2(dy, dx)) - bot_angle) % 360

    # Calculate correction factor for rotation
    rotation_correction_factor = EXPECTED_ROTATION_DEGREES / actual_rotation_angle
    print(f"Actual rotation angle: {actual_rotation_angle} degrees")
    print(f"Rotation correction factor: {rotation_correction_factor}")

    # Reset for future use
    bot_angle += EXPECTED_ROTATION_DEGREES * rotation_correction_factor
    if bot_angle >= 360:
        bot_angle -= 360

# Initialize webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow("Calibration")
cv2.setMouseCallback("Calibration", set_new_position)

try:
    # Calibrate movement
    calibrate_movement()
    
    # Reset new_position for rotation calibration
    new_position = None

    # Calibrate rotation
    calibrate_rotation()

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
