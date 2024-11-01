import cv2
import math

# Constants for bot movement (based on given specifications)
FRONT_TRAVEL_PIXELS_PER_MS = 393 / 1000  # pixels per ms for forward movement
BACK_TRAVEL_PIXELS_PER_MS = 386 / 1000   # pixels per ms for backward movement
ROTATION_TIME_PER_DEGREE = 203 / 90      # ms per degree rotation

# Temporary values for bot's current state
bot_angle = 45  # Initial bot orientation in degrees
bot_center_point = (320, 240)  # Starting bot position at the center of the frame (example)

target_point = None  # Will be set when user clicks

# Function to calculate the angle between two points
def calculate_angle_to_point(bot_position, target_position):
    dx = target_position[0] - bot_position[0]
    dy = target_position[1] - bot_position[1]
    angle_to_target = math.degrees(math.atan2(dy, dx)) % 360
    return angle_to_target

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to move bot to the target point
def move_bot_to_target(bot_position, bot_angle, target_point):
    # Calculate distance and angle to target
    distance_to_target = calculate_distance(bot_position, target_point)
    angle_to_target = calculate_angle_to_point(bot_position, target_point)
    
    # Calculate rotation needed
    rotation_needed = (angle_to_target - bot_angle) % 360
    if rotation_needed > 180:
        rotation_needed -= 360  # Simplify rotation to the shortest path
    
    # Calculate rotation time
    rotation_time_ms = abs(rotation_needed) * ROTATION_TIME_PER_DEGREE
    
    # Determine movement direction
    if rotation_needed < 0:
        rotation_direction = "Left"
    else:
        rotation_direction = "Right"
    
    # Calculate travel time
    forward_travel_time_ms = distance_to_target / FRONT_TRAVEL_PIXELS_PER_MS
    backward_travel_time_ms = distance_to_target / BACK_TRAVEL_PIXELS_PER_MS
    travel_direction, travel_time_ms = ("Forward", forward_travel_time_ms) if forward_travel_time_ms < backward_travel_time_ms else ("Backward", backward_travel_time_ms)
    
    # Display the movement steps
    print(f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
    print(f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")
    return rotation_time_ms,rotation_direction,rotation_time_ms,travel_direction,travel_time_ms


# Mouse callback function to select the target point
def select_target(event, x, y, flags, param):
    global target_point
    if event == cv2.EVENT_LBUTTONDOWN:
        target_point = (x, y)
        print(f"Target selected at: {target_point}")

# Main function to capture video, select point, and calculate movement
def main():
    global bot_center_point, bot_angle, target_point
    
    # Open webcam capture
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Select Target Point")
    cv2.setMouseCallback("Select Target Point", select_target)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break

        # Draw bot center point
        cv2.circle(frame, bot_center_point, 5, (0, 255, 0), -1)
        cv2.putText(frame, "Bot Position", bot_center_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw target point if set
        if target_point is not None:
            cv2.circle(frame, target_point, 5, (0, 0, 255), -1)
            cv2.putText(frame, "Target Point", target_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Calculate movement instructions
            move_bot_to_target(bot_center_point, bot_angle, target_point)
            
            # Reset target point after calculation to avoid repeated prints
            target_point = None

        # Show the frame
        cv2.imshow("Select Target Point", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
