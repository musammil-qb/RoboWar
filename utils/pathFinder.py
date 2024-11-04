import cv2
import numpy as np
import math

# Global variables
corners = []
trimmed_field = []
extended_points = []  # Store the extended points for each ball
balls = []  # Store the simulated ball positions
goal_post_pos = (500, 240)  # Static goal post position within the field for testing
bot_position = (320, 240)  # Initial bot position, can change with clicks


def find_extended_points(ball_pos, extension_factor_before=0.1, extension_factor_after=0.15):
    """Calculate extended points on either side of the ball along a straight line to the goal post."""
    dx, dy = goal_post_pos[0] - ball_pos[0], goal_post_pos[1] - ball_pos[1]
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return ball_pos, ball_pos  # Avoid division by zero
    dx, dy = dx / length, dy / length  # Normalize direction

    # Calculate E1 (before ball) and E2 (after ball)
    x_e1 = int(ball_pos[0] - extension_factor_before * dx * length)
    y_e1 = int(ball_pos[1] - extension_factor_before * dy * length)
    x_e2 = int(ball_pos[0] + extension_factor_after * dx * length)
    y_e2 = int(ball_pos[1] + extension_factor_after * dy * length)
    
    return (x_e1, y_e1), (x_e2, y_e2)

def is_point_in_polygon(point, polygon):
    """Check if a point is within a given polygon using OpenCV."""
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def select_corners(event, x, y, flags, param):
    """Mouse callback to select field corners or update bot position."""
    global corners, bot_position
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
        corners.append((x, y))
        if len(corners) == 4:
            define_trimmed_field(corners)

    # Set the bot position on right-click
    if event == cv2.EVENT_RBUTTONDOWN:
        bot_position = (x, y)

def define_trimmed_field(field_corners, trim_factor=30):
    """Define a trimmed field area."""
    global trimmed_field
    p1, p2, p3, p4 = np.array(field_corners)
    trimmed_field = [
        (int(p1[0] + trim_factor), int(p1[1] + trim_factor)),
        (int(p2[0] - trim_factor), int(p2[1] + trim_factor)),
        (int(p3[0] - trim_factor), int(p3[1] - trim_factor)),
        (int(p4[0] + trim_factor), int(p4[1] - trim_factor))
    ]

def draw_trimmed_field(frame):
    """Draw the trimmed field on the frame."""
    if len(trimmed_field) == 4:
        cv2.polylines(frame, [np.array(trimmed_field)], isClosed=True, color=(255, 0, 255), thickness=2)

def simulate_balls(num_balls=10):
    """Simulate ball positions for testing."""
    global balls
    balls = [(np.random.randint(100, 400), np.random.randint(100, 400)) for _ in range(num_balls)]

def draw_travel_path(frame, path_points):
    """Draw the travel path on the frame with pit stops."""
    for i in range(len(path_points) - 1):
        cv2.line(frame, path_points[i], path_points[i + 1], (0, 255, 255), 1)
        cv2.circle(frame, path_points[i], 5, (255, 255, 0), -1)  # Pit stop points

def calculate_path_to_extended_point(bot_pos, e1, obstacles, buffer=20):
    """Calculate a path to E1 while avoiding obstacles and ensuring the path does not touch the buffer."""
    path_points = [bot_pos]
    current_pos = bot_pos

    # Check the distance to the target extended point (E1)
    dx, dy = e1[0] - current_pos[0], e1[1] - current_pos[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Normalize direction
    if distance != 0:
        dx, dy = dx / distance, dy / distance

    # Define the number of checks along the path
    num_checks = int(distance // buffer)
    for i in range(num_checks):
        check_pos = (int(current_pos[0] + dx * i * buffer), int(current_pos[1] + dy * i * buffer))
        
        # If check position is within the field
        if is_point_in_polygon(check_pos, trimmed_field):
            for obstacle in obstacles:
                if math.sqrt((check_pos[0] - obstacle[0])**2 + (check_pos[1] - obstacle[1])**2) < buffer:
                    # If an obstacle is detected, find a new direction to avoid it
                    new_dx, new_dy = dy, -dx  # Rotate direction to find a new path
                    current_pos = (int(current_pos[0] + new_dx * buffer), int(current_pos[1] + new_dy * buffer))
                    path_points.append(current_pos)  # Update path points to include the new position
                    break
            else:
                # No obstacles found, continue moving towards E1
                current_pos = (int(current_pos[0] + dx * buffer), int(current_pos[1] + dy * buffer))
                path_points.append(current_pos)  # Add to path points
        else:
            # Break if the check position is out of polygon
            break

    # Finally, move to E1 directly
    path_points.append(e1)

    return path_points

def process_frame(frame):
    """Process each frame to visualize paths, balls, and extended points."""
    global extended_points

    # Draw balls and calculate extended points
    extended_points.clear()
    for ball in balls:
        cv2.circle(frame, ball, 10, (0, 0, 255), -1)  # Draw ball in red
        if is_point_in_polygon(ball, trimmed_field):
            e1, e2 = find_extended_points(ball)
            extended_points.append((ball, e1, e2))
            cv2.circle(frame, e1, 5, (255, 0, 0), -1)  # E1 in blue
            cv2.circle(frame, e2, 5, (0, 255, 0), -1)  # E2 in green
            cv2.line(frame, ball, goal_post_pos, (0, 255, 255), 1)  # Line to goal post

    # Find the ball closest to the goal post
    nearest_goal_ball = None
    nearest_goal_distance = float('inf')
    for ball, e1, e2 in extended_points:
        distance_to_goal = math.sqrt((goal_post_pos[0] - ball[0])**2 + (goal_post_pos[1] - ball[1])**2)
        if distance_to_goal < nearest_goal_distance:
            nearest_goal_distance = distance_to_goal
            nearest_goal_ball = (ball, e1, e2)

    # Draw the travel path from bot to nearest extended point (E1) of the nearest ball to the goal
    if nearest_goal_ball:
        _, nearest_point, _ = nearest_goal_ball
        obstacles = [ball for ball, _, _ in extended_points]
        path_to_E1 = calculate_path_to_extended_point(bot_position, nearest_point, obstacles)
        draw_travel_path(frame, path_to_E1)

def main():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Path Planning", cv2.WND_PROP_FULLSCREEN)
    cv2.setMouseCallback("Path Planning", select_corners)
    simulate_balls()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Draw the field and process path visualization
        draw_trimmed_field(frame)
        if len(trimmed_field) == 4:
            process_frame(frame)

        cv2.imshow("Path Planning", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
