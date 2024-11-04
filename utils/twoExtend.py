import cv2
import numpy as np
import math

# Global variables
corners = []
outer_trimmed_field = []
inner_trimmed_field = []
balls = []  # Store detected balls
bot_position = (320, 240)  # Initial bot position for testing
goal_post_pos = (600, 240)  # Static goal post position for testing
extension_factor_before = 0.1  # Percentage for point before the ball
extension_factor_after = 0.15  # Percentage for point after the ball
buffer_distance = 20  # Minimum buffer to maintain from the ball for E1 and E2

def find_aligned_extended_points(ball_pos):
    """Calculate aligned extended points E1 (before ball) and E2 (after ball) in a straight line to the goal post."""
    dx, dy = goal_post_pos[0] - ball_pos[0], goal_post_pos[1] - ball_pos[1]
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return ball_pos, ball_pos  # Avoid division by zero

    # Normalize direction vector
    dx, dy = dx / length, dy / length  

    # Calculate the distances for E1 and E2
    dist_e1 = max(extension_factor_before * length, buffer_distance)
    dist_e2 = max(extension_factor_after * length, buffer_distance)

    # E1: Extended point before the ball
    x_e1 = int(ball_pos[0] - dist_e1 * dx)
    y_e1 = int(ball_pos[1] - dist_e1 * dy)
    e1 = (x_e1, y_e1)

    # E2: Extended point after the ball
    x_e2 = int(ball_pos[0] + dist_e2 * dx)
    y_e2 = int(ball_pos[1] + dist_e2 * dy)
    e2 = (x_e2, y_e2)

    # Print E1 and E2 coordinates for tracking
    print(f"E1 (before ball): {e1}")
    print(f"E2 (after ball): {e2}")
    
    return e1, e2

def is_point_in_polygon(point, polygon):
    """Check if a point is within a given polygon using OpenCV."""
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def select_corners(event, x, y, flags, param):
    global corners
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
        corners.append((x, y))
        print(f"Corner {len(corners)}: ({x}, {y})")
        if len(corners) == 4:
            define_trimmed_field(corners)

    # Right-click to set bot position
    if event == cv2.EVENT_RBUTTONDOWN:
        global bot_position
        bot_position = (x, y)
        print(f"Bot position set to: {bot_position}")

def define_trimmed_field(field_corners, trim_factor=30):  # Adjust trim factor to scale in pixels
    """Define outer and inner trimmed fields inside the selected corners."""
    global outer_trimmed_field, inner_trimmed_field
    p1, p2, p3, p4 = np.array(field_corners)
    outer_trimmed_field = [
        (int(p1[0] + trim_factor), int(p1[1] + trim_factor)),
        (int(p2[0] - trim_factor), int(p2[1] + trim_factor)),
        (int(p3[0] - trim_factor), int(p3[1] - trim_factor)),
        (int(p4[0] + trim_factor), int(p4[1] - trim_factor))
    ]
    # Inner rectangle further trimmed by the same trim factor
    inner_trimmed_field = [
        (int(outer_trimmed_field[0][0] + trim_factor), int(outer_trimmed_field[0][1] + trim_factor)),
        (int(outer_trimmed_field[1][0] - trim_factor), int(outer_trimmed_field[1][1] + trim_factor)),
        (int(outer_trimmed_field[2][0] - trim_factor), int(outer_trimmed_field[2][1] - trim_factor)),
        (int(outer_trimmed_field[3][0] + trim_factor), int(outer_trimmed_field[3][1] - trim_factor))
    ]
    print(f"Outer trimmed field corners: {outer_trimmed_field}")
    print(f"Inner trimmed field corners: {inner_trimmed_field}")

def draw_trimmed_fields(frame):
    """Draw both outer and inner trimmed fields on the frame."""
    if len(outer_trimmed_field) == 4:
        cv2.polylines(frame, [np.array(outer_trimmed_field)], isClosed=True, color=(255, 0, 255), thickness=2)
    if len(inner_trimmed_field) == 4:
        cv2.polylines(frame, [np.array(inner_trimmed_field)], isClosed=True, color=(0, 255, 255), thickness=2)

def simulate_balls(num_balls=5):
    """Simulate ball positions for testing. Replace with YOLO detection in real code."""
    global balls
    balls = [(np.random.randint(100, 500), np.random.randint(100, 400)) for _ in range(num_balls)]
    print(f"Simulated ball positions: {balls}")

def process_frame(frame):
    """Process each frame to draw balls, extended points, and connecting lines."""
    nearest_e1 = None
    min_distance_to_bot = float('inf')

    if len(outer_trimmed_field) == 4 and len(inner_trimmed_field) == 4:
        for ball in balls:
            if is_point_in_polygon(ball, outer_trimmed_field):
                e1, e2 = find_aligned_extended_points(ball)

                # Draw the ball
                cv2.circle(frame, ball, 10, (0, 0, 255), -1)  # Red circle for balls

                # Draw extended points
                cv2.circle(frame, e1, 5, (255, 0, 0), -1)  # Blue for point before ball (E1)
                cv2.circle(frame, e2, 5, (0, 255, 0), -1)  # Green for point after ball (E2)

                # Draw line from E1 to ball, ball to E2, and E2 to goal post
                cv2.line(frame, e1, ball, (255, 0, 0), 1)
                cv2.line(frame, ball, e2, (0, 255, 0), 1)
                cv2.line(frame, e2, goal_post_pos, (0, 255, 255), 1)

                # Calculate the distance from bot to E1 to find the nearest point
                distance_to_bot = math.sqrt((e1[0] - bot_position[0])**2 + (e1[1] - bot_position[1])**2)
                if distance_to_bot < min_distance_to_bot:
                    min_distance_to_bot = distance_to_bot
                    nearest_e1 = e1

    # Draw the bot and nearest E1 point if available
    cv2.circle(frame, bot_position, 8, (0, 255, 255), -1)  # Yellow for bot
    if nearest_e1:
        cv2.putText(frame, f"Nearest E1: {nearest_e1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def main():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Field", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Field", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("Field", select_corners)
    simulate_balls()  # Simulate balls at the start

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Display outer and inner trimmed fields
        draw_trimmed_fields(frame)

        # Process frame for extended points and display
        process_frame(frame)

        # Show the frame
        cv2.imshow("Field", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
