import numpy as np
import cv2


from const import BOT_MOVEMENT_TRIM_LENGTH, GREEN, BLUE,\
    SWEEP_MOVEMENT_CORRECTION_PERCENTAGES, SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2, \
    EDGE_ROTATION_DELAY
from util import point_at_distance_in_a_line

def find_sweep_corner_points(detection):
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
        print("post is on left")
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
        print("post is on right")
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

        {'start_point':points[1],'end_point':points[2],'idx':1
         'rotation':'right' if direction == 'clockwise' else 'left'},
        
        {'start_point':points[2],'end_point':points[3],'idx':2
         'rotation':'right' if direction == 'clockwise' else 'left'},
    ]    


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
        bot.makeMovement(sweep_movement['rotation'], EDGE_ROTATION_DELAY,edge_rotation=True)
        
    bot.updatePosition()
    movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES if sweep_movement['idx'] == 2 else SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2
    bot.move(sweep_movement['end_point'],movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2)
    bot.makeMovement(sweep_movement['rotation'], EDGE_ROTATION_DELAY,edge_rotation=True)
    