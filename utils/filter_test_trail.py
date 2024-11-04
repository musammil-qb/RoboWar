import cv2
import numpy as np
from filter import filter_balls, calculate_extended_points

# Simulation parameters
FIELD_CORNERS = [(50, 50), (500, 50), (500, 400), (50, 400)]
TRIMMED_MARGIN = 20  # Distance in pixels to trim the field
GOAL_POST = (600, 240)  # Goal post position for testing
BUFFER_DISTANCE = 30  # Buffer for extended points, to ensure kickable balls have space
NUM_BALLS = 8  # Number of balls to simulate

def generate_trimmed_field(corners, margin):
    """Generate a trimmed field rectangle with a specified margin inside the field corners."""
    trimmed_field = [
        (corners[0][0] + margin, corners[0][1] + margin),
        (corners[1][0] - margin, corners[1][1] + margin),
        (corners[2][0] - margin, corners[2][1] - margin),
        (corners[3][0] + margin, corners[3][1] - margin)
    ]
    return trimmed_field

def simulate_balls(num_balls, field_corners):
    """Randomly simulate ball positions within the field for testing."""
    x_min, y_min = field_corners[0]
    x_max, y_max = field_corners[2]
    return [(np.random.randint(x_min, x_max), np.random.randint(y_min, y_max)) for _ in range(num_balls)]

def main():
    # Create a blank frame to visualize the test
    frame = np.zeros((500, 700, 3), dtype=np.uint8)

    # Draw the main field and trimmed field
    field_corners = FIELD_CORNERS
    trimmed_field = generate_trimmed_field(FIELD_CORNERS, TRIMMED_MARGIN)
    
    cv2.polylines(frame, [np.array(field_corners)], isClosed=True, color=(255, 0, 0), thickness=2)  # Main field
    cv2.polylines(frame, [np.array(trimmed_field)], isClosed=True, color=(0, 255, 0), thickness=2)  # Trimmed field

    # Draw the goal post
    cv2.circle(frame, GOAL_POST, 10, (0, 0, 255), -1)
    cv2.putText(frame, "Goal Post", (GOAL_POST[0] - 20, GOAL_POST[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Simulate balls and apply the filter
    balls = simulate_balls(NUM_BALLS, field_corners)
    filtered_balls = filter_balls(balls, trimmed_field, GOAL_POST, buffer_distance=BUFFER_DISTANCE)

    # Display the balls and extended points
    for ball in balls:
        color = (0, 0, 255) if ball in filtered_balls else (100, 100, 100)  # Red for targetable balls, grey for others
        cv2.circle(frame, ball, 10, color, -1)
        cv2.putText(frame, f"Ball {ball}", (ball[0] + 5, ball[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Draw extended points for filtered balls only
        if ball in filtered_balls:
            e1, e2 = calculate_extended_points(ball, GOAL_POST, BUFFER_DISTANCE)
            cv2.circle(frame, e1, 5, (255, 255, 0), -1)  # Blue for E1
            cv2.circle(frame, e2, 5, (0, 255, 255), -1)  # Yellow for E2
            cv2.line(frame, e1, e2, (200, 200, 0), 1)
            cv2.line(frame, e2, GOAL_POST, (0, 255, 255), 1)
            print(f"Ball at {ball} -> E1: {e1}, E2: {e2}")

    # Display the result
    cv2.imshow("Field Test", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
