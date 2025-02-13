import numpy as np
import cv2
import math
from detection import Detection
from util import calculate_distance, distance_to_line
from const import GREEN, RED, BLUE, YELLOW

from util import calculate_distance, distance_to_line
# extension_factor_before = 0.2  # Percentage for point before the ball
# extension_factor_after = 0.1


def filter_balls(trimmed_field, balls, goal_center_point, buffer_distance=20, disable_filter=False):
    filtered_balls = []
    intersection_points = []
    for ball in balls:
        e1, e2 = calculate_extended_points(ball,goal_center_point, buffer_distance,extension_factor_after=0.3)

        if is_point_in_polygon(e1, trimmed_field) and is_point_in_polygon(e2, trimmed_field):
            filtered_balls.append(ball)
            intersection_points.append({'target_point':e1, 'goal_point':e2,'ball':ball})
        elif disable_filter:
            filtered_balls.append(ball)
            intersection_points.append({'target_point':e1, 'goal_point':e2,'ball':ball})
        # else:
            # print(f"Ball at {ball} has an extended point outside the field; not targeted.")


    return filtered_balls, intersection_points


def calculate_extended_points(ball_pos,goal_center, buffer_distance=50,extension_factor_before=0.2, extension_factor_after=0.15):
    dx, dy = goal_center[0] - ball_pos[0], goal_center[1] - ball_pos[1]
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return ball_pos, ball_pos  # Avoid division by zero

    # Normalize direction vector
    dx, dy = dx / length, dy / length  

    # Calculate the distances for E1 and E2
    dist_e1 = max(extension_factor_before * length, buffer_distance)
    dist_e2 = extension_factor_after * length

    # E1: Extended point before the ball
    x_e1 = int(ball_pos[0] - dist_e1 * dx)
    y_e1 = int(ball_pos[1] - dist_e1 * dy)
    e1 = (x_e1, y_e1)

    # E2: Extended point after the ball
    x_e2 = int(ball_pos[0] + dist_e2 * dx)
    y_e2 = int(ball_pos[1] + dist_e2 * dy)
    e2 = (x_e2, y_e2)
    
    return e1, e2

def is_point_in_polygon(point, polygon):
    #Check if a point is within a given polygon using OpenCV.
    return cv2.pointPolygonTest(np.array(polygon), point, False) >= 0

def choose_next_target_point(intersection_points, bot_center_point, opponent_bot, goal_center_point,detection, test=False):
    cm_to_pixel_rate = detection.cm_to_pixel_rate
    if not intersection_points or not bot_center_point:
        return None
        
    # Constants for scoring (in pixels based on cm conversion)
    OPPONENT_DANGER_RADIUS = int(40*cm_to_pixel_rate)  # 40cm danger radius around opponent
    OPPONENT_PATH_DANGER_RADIUS = int(30*cm_to_pixel_rate)  # 30cm danger radius for path checking
    
    def calculate_ball_score(point_data):
        ball_pos = point_data['ball']
        
        # Calculate distances
        distance_to_bot = calculate_distance(point_data['target_point'], bot_center_point)
        distance_to_goal = calculate_distance(ball_pos, goal_center_point)
        
        # Initialize score and score components dictionary for detailed output
        score = 0
        score_components = {
            'bot_proximity': 0,
            'goal_proximity': 0,
            'opponent_penalty': 0,
            'path_penalty': 0
        }
        
        # Positive factors
        # Bot proximity score (closer is better)
        bot_proximity_score = 1000 / (distance_to_bot + 1)  # Add 1 to avoid division by zero
        score += bot_proximity_score
        score_components['bot_proximity'] = bot_proximity_score
        
        # Goal proximity score (closer is better)
        goal_proximity_score = 800 / (distance_to_goal + 1)
        score += goal_proximity_score
        score_components['goal_proximity'] = goal_proximity_score
        
        if opponent_bot:
            # Negative factors
            # Opponent proximity penalty
            distance_to_opponent = calculate_distance(ball_pos, opponent_bot)
            opponent_penalty = 0
            if distance_to_opponent < OPPONENT_DANGER_RADIUS:
                opponent_penalty = -1500 * (1 - distance_to_opponent/OPPONENT_DANGER_RADIUS)
                score += opponent_penalty
            score_components['opponent_penalty'] = opponent_penalty
            
            # Check if opponent is near the ball's path to goal
            # Convert points to numpy arrays for distance_to_line function
            ball_np = np.array(ball_pos)
            goal_np = np.array(goal_center_point)
            opponent_np = np.array(opponent_bot)
            
            path_distance, closest_point = distance_to_line(opponent_np, ball_np, goal_np)
            path_penalty = 0
            if path_distance < OPPONENT_PATH_DANGER_RADIUS:
                # Calculate how far along the path the opponent is
                path_penalty = -1200 * (1 - path_distance/OPPONENT_PATH_DANGER_RADIUS)
                score += path_penalty
            score_components['path_penalty'] = path_penalty

        if test:
            # Visualization - Create a copy of the frame if it exists
            frame = detection.video_stream.read()
            
            # Draw ball position
            cv2.circle(frame, ball_pos, 5, BLUE, -1)
            
            # Draw line from ball to goal
            cv2.line(frame, ball_pos, goal_center_point, GREEN, 1)
            
            # Draw circles showing danger radius around opponent
            if opponent_bot:
                cv2.circle(frame, opponent_bot, OPPONENT_DANGER_RADIUS, RED, 1)
                cv2.circle(frame, opponent_bot, OPPONENT_PATH_DANGER_RADIUS, YELLOW, 1)
                
                # If opponent is affecting the score, draw the closest point on path
                if path_penalty != 0:
                    closest_point_tuple = (int(closest_point[0]), int(closest_point[1]))
                    cv2.circle(frame, closest_point_tuple, 3, RED, -1)
                    cv2.line(frame, opponent_bot, closest_point_tuple, RED, 1)

            # Draw distance to bot
            cv2.putText(frame, f"Bot: {distance_to_bot:.1f}px", 
                        (ball_pos[0] - 30, ball_pos[1] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 1)
            
            # Draw distance to goal
            cv2.putText(frame, f"Goal: {distance_to_goal:.1f}px", 
                        (ball_pos[0] - 30, ball_pos[1] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1)
            
            # Draw line from bot to target point
            if bot_center_point:
                cv2.line(frame, bot_center_point, point_data['target_point'], (0, 255, 255), 1)
            # Add score text above the ball
            score_text = f"Score: {score:.1f}"
            cv2.putText(frame, score_text, 
                        (ball_pos[0] - 30, ball_pos[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 1)
                
            cv2.imshow('Ball Scoring Visual/ization', frame)

            # Print detailed scoring information
            print("\nBall Score Details:")
            print(f"Ball position: {ball_pos}")
            print(f"Distance to bot: {distance_to_bot:.1f} pixels")
            print(f"Distance to goal: {distance_to_goal:.1f} pixels")
            print("\nScore Components:")
            print(f"Bot proximity score: {score_components['bot_proximity']:.1f}")
            print(f"Goal proximity score: {score_components['goal_proximity']:.1f}")
            if opponent_bot:
                print(f"Distance to opponent: {distance_to_opponent:.1f} pixels")
                print(f"Opponent penalty: {score_components['opponent_penalty']:.1f}")
                print(f"Path distance from opponent: {path_distance:.1f} pixels")
                print(f"Path penalty: {score_components['path_penalty']:.1f}")
            print(f"Total score: {score:.1f}")
            print("-" * 50)
            print(test)
            cv2.waitKey(0)
        return score
    
    # Calculate scores for all intersection points and return the one with highest score
    scored_points = [(point, calculate_ball_score(point)) for point in intersection_points]
    best_point = max(scored_points, key=lambda x: x[1])[0]
    return best_point