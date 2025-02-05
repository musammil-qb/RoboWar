import numpy as np
import cv2
import time

from const import BOT_MOVEMENT_TRIM_LENGTH, GREEN, BLUE,\
    SWEEP_MOVEMENT_CORRECTION_PERCENTAGES, SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2, \
    EDGE_ROTATION_DELAY
from util import point_at_distance_in_a_line,\
      distance_to_line, calculate_distance

def find_sweep_movements(detection):
    sweep_corners = detection.bot_movement_trimmed_field
    sweep_movements = generate_sweep_points(
        my_posts=detection.goal_posts['self']['goal_post_end_points'],
        opponent_posts=detection.goal_posts['opponent']['goal_post_end_points'],
          corners=sweep_corners, sweep_distance = BOT_MOVEMENT_TRIM_LENGTH*detection.cm_to_pixel_rate)
    return sweep_movements


def generate_sweep_points(my_posts, opponent_posts, corners, sweep_distance):
    # Extract the four corners in order: top-left, top-right, bottom-right, bottom-left
    top_left, top_right, bottom_right, bottom_left = corners
    
    if my_posts[0][1] < my_posts[1][1]:
        my_post_top,my_post_bottom = my_posts[::]
    else:
        my_post_top,my_post_bottom = my_posts[::-1]

    if opponent_posts[0][1] < opponent_posts[1][1]:
        opponent_post_top,opponent_post_bottom = opponent_posts[::]
    else:
        opponent_post_top,opponent_post_bottom = opponent_posts[::-1]
    # Determine if the self post is on the left or right side
    if my_posts[0][0] < opponent_posts[0][0]:  # Self post is on the left
        clockwise_points = [
            point_at_distance_in_a_line(my_post_top,opponent_post_top,sweep_distance),
            top_left, 
            top_right, 
            point_at_distance_in_a_line(opponent_post_top,my_post_top,sweep_distance)
        ]
        anti_clockwise_points = [
            point_at_distance_in_a_line(my_post_bottom,opponent_post_bottom,sweep_distance),
            bottom_left,
            bottom_right,
            point_at_distance_in_a_line(opponent_post_bottom,my_post_bottom,sweep_distance)
        ]
    else:  # Self post is on the right
        clockwise_points = [
            point_at_distance_in_a_line(my_post_bottom,opponent_post_bottom,sweep_distance),
                bottom_right,
            bottom_left,
            point_at_distance_in_a_line(opponent_post_bottom,my_post_bottom,sweep_distance)
        ]
        anti_clockwise_points = [
            point_at_distance_in_a_line(my_post_top,opponent_post_top,sweep_distance),
            top_right,
            top_left,
            point_at_distance_in_a_line(opponent_post_top,my_post_top,sweep_distance)
        ]
    # Combine both sets of points
    sweep_movements = [
        *generate_sweep_movements(clockwise_points,'clockwise'),
        *generate_sweep_movements(anti_clockwise_points,'anti_clockwise')
        ]
    sweep_points = [clockwise_points , anti_clockwise_points]
    return sweep_movements

def generate_sweep_movements(points, direction):
    return [
        {'start_point':points[0],'end_point':points[1],'idx':0,
         'rotation':'right' if direction == 'clockwise' else 'left'},

        {'start_point':points[1],'end_point':points[2],'idx':1,
         'rotation':'right' if direction == 'clockwise' else 'left'},
        
        {'start_point':points[2],'end_point':points[3],'idx':2,
         'rotation':'right' if direction == 'clockwise' else 'left'},
    ]


def find_best_sweep_movement(sweep_movements, balls, cm_to_pixel_rate):
    sweep_movement_score =[]
    for sweep_movement in sweep_movements:
        ball_count = 0
        for ball in balls:
            distance, _ = distance_to_line(
                ball,np.array(sweep_movement['start_point']),
                np.array(sweep_movement['end_point']))
            if distance <= 15*cm_to_pixel_rate:
                ball_count += 1
            # if ball_count > 2:
            #     return sweep_movement
        sweep_movement_score.append({'ball_count':ball_count,'sweep_movement':sweep_movement})
    sorted_sweep_movements = sorted(sweep_movement_score,key=lambda x:x['ball_count'],reverse=True)
    return sorted_sweep_movements[0]['sweep_movement']


def sweep(detection,sweep_movement,bot,display):
    frame = detection.video_stream.read()
    if display:
        cv2.circle(frame, sweep_movement['start_point'], 5, BLUE, -1)
        cv2.circle(frame, sweep_movement['end_point'], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
    bot.updatePosition()
    bot.move(sweep_movement['start_point'])
    if sweep_movement['idx']!=0:
        bot.updatePosition()
        bot.makeMovement(sweep_movement['rotation'], {"delay": EDGE_ROTATION_DELAY}, edge_rotation=True)
        time.sleep(0.2)
        bot.move(sweep_movement['start_point'],acquire_target=False)

    points = find_points_between(sweep_movement['start_point'], sweep_movement['end_point'],max_length=detection.cm_to_pixel_rate * 20)
    for point in points:
        bot.updatePosition()
        bot.move(point, acquire_target=False)

    bot.makeMovement(sweep_movement['rotation'], {"delay": EDGE_ROTATION_DELAY}, edge_rotation=True)


def find_points_between(start_point, end_point, max_length):
    points = [start_point]
    current_point = start_point
    while calculate_distance(current_point, end_point) > max_length:
        current_point = point_at_distance_in_a_line(current_point, end_point, max_length)
        points.append(current_point)
    if current_point != end_point:
        points.append(end_point)
    return points
    