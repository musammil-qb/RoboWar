import math
import numpy as np
import time
import cv2


from util import calculate_distance, distance_to_line
from const import EDGE_BALL_MOVEMENT_DISTANCE,EDGE_ROTATION_DELAY,EDGE_BALL_ROTATION_DISTANCE,\
    SLEEP_AFTER_DISPLAYING,SLEEP_AFTER_MOVEMENT,BLUE,YELLOW

def find_target_and_direction(corners, ball, goal_point, self_goal_point,  self_edge, goal_edge, rotation_distance, movement_distance):

    # Convert inputs to numpy arrays for easier vector operations
    corners = [np.array(corner) for corner in corners]
    ball = np.array(ball)
    goal_point = np.array(goal_point)

    # Determine the closest edge to the ball
    min_distance = float('inf')

    for i in range(len(corners)):
        line_start = corners[i]
        line_end = corners[(i + 1) % len(corners)]
        dist, _ = distance_to_line(ball, line_start, line_end)
        if dist < min_distance:
            min_distance = dist
            closest_edge = (line_start, line_end)

    closest_edge_array = [tuple(closest_edge[0]),tuple(closest_edge[1])]
    if closest_edge_array == goal_edge:
        if calculate_distance(closest_edge[0], ball) > calculate_distance(closest_edge[1], ball):
            closer_corner = closest_edge[1]
        else:
            closer_corner = closest_edge[0]
        start_point = closer_corner 
        end_point = goal_point 
        dx =  start_point[0]-end_point[0]  
        dy =  start_point[1]-end_point[1]  
        magnitude = math.sqrt(dx**2 + dy**2)
        line_vector = np.array( [dx / magnitude, dy / magnitude])

        target_point = ball + movement_distance * line_vector
        movement_direction = 'forward'
    elif closest_edge_array == self_edge:
        if calculate_distance(closest_edge[0], ball) > calculate_distance(closest_edge[1], ball):
            closer_corner = closest_edge[1]
        else:
            closer_corner = closest_edge[0]
        start_point = self_goal_point 
        end_point = closer_corner 
        dx =  start_point[0] - end_point[0]  
        dy =  start_point[1] - end_point[1]  
        magnitude = math.sqrt(dx**2 + dy**2)
        line_vector = np.array( [dx / magnitude, dy / magnitude])

        target_point = ball + movement_distance * line_vector
        movement_direction = 'forward'
    else:
        if calculate_distance(closest_edge[0], goal_point) > calculate_distance(closest_edge[1], goal_point):
            end_point = closest_edge[1]
            start_point = closest_edge[0] 

        else:
            start_point = closest_edge[1] 
            end_point = closest_edge[0] 

        dx =  start_point[0] - end_point[0]  
        dy =  start_point[1] - end_point[1]  
        magnitude = math.sqrt(dx**2 + dy**2)
        line_vector = np.array( [dx / magnitude, dy / magnitude])

        target_point = ball + rotation_distance * line_vector

        # Determine the rotation direction to bring the ball closer to the goal post
        ball_to_target = target_point - ball
        ball_to_goal = goal_point - ball
        cross_product = np.cross(ball_to_target, ball_to_goal)
        movement_direction = "right" if cross_product < 0 else "left"
    return (int(target_point[0]),int(target_point[1])), movement_direction


def edge_move(balls, bot_center_point, field_corners, 
              goal_center_point, self_goal_center_point, self_edge, opponent_edge,detection,bot,display=True):
    closest_ball = min(balls, key=lambda ball: calculate_distance(ball, bot_center_point))
    target_point, edge_movement_direction = find_target_and_direction(
        field_corners, closest_ball, goal_center_point,self_goal_center_point, self_edge, opponent_edge,
        detection.cm_to_pixel_rate * EDGE_BALL_ROTATION_DISTANCE, detection.cm_to_pixel_rate * EDGE_BALL_MOVEMENT_DISTANCE
    )
    if display:
        frame = detection.video_stream.read()
        cv2.circle(frame, target_point, 5, YELLOW, -1)
        cv2.putText(frame, str(edge_movement_direction), target_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 2)
        cv2.imshow('Feed', frame)
        cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    if bot:
        bot.updatePosition()
        bot.move(target_point)
        time.sleep(SLEEP_AFTER_MOVEMENT)
        if edge_movement_direction in ["right","left"]:
            bot.makeMovement(edge_movement_direction, {"delay": EDGE_ROTATION_DELAY},edge_rotation=True)
        else:
            bot.updatePosition()
            bot.move(closest_ball)