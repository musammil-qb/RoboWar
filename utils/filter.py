import cv2
import numpy as np

def is_point_in_polygon(point, polygon):
    """Check if a point is within a given polygon using OpenCV."""
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def filter_balls(balls, trimmed_field, goal_post, buffer_distance=20):
    """
    Filter out balls based on their extended points' position relative to the trimmed field.
    
    Parameters:
    - balls: List of tuples (x, y) positions of balls.
    - trimmed_field: List of tuples representing the trimmed rectangle corners.
    - goal_post: Tuple representing the goal post position.
    - buffer_distance: Minimum distance from the ball to consider it kickable.
    
    Returns:
    - filtered_balls: List of balls that are within bounds and kickable.
    """
    filtered_balls = []

    for ball in balls:
        # Calculate aligned extended points for the ball in a line toward the goal
        e1, e2 = calculate_extended_points(ball, goal_post, buffer_distance)

        # Check if both E1 and E2 points are within the trimmed field area
        if is_point_in_polygon(e1, trimmed_field) and is_point_in_polygon(e2, trimmed_field):
            # Only add the ball if both extended points are within the field
            filtered_balls.append(ball)
        else:
            print(f"Ball at {ball} has an extended point outside the field; not targeted.")

    return filtered_balls

def calculate_extended_points(ball_pos, goal_post, buffer_distance):
    """Calculate E1 and E2 extended points for the ball toward the goal post."""
    dx, dy = goal_post[0] - ball_pos[0], goal_post[1] - ball_pos[1]
    length = np.hypot(dx, dy)
    
    # Normalize direction vector
    dx, dy = dx / length, dy / length

    # Calculate positions for E1 and E2 based on buffer distance
    e1 = (int(ball_pos[0] - buffer_distance * dx), int(ball_pos[1] - buffer_distance * dy))
    e2 = (int(ball_pos[0] + buffer_distance * dx), int(ball_pos[1] + buffer_distance * dy))

    return e1, e2


