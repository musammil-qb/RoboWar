import numpy as np
import cv2


from const import BOT_MOVEMENT_TRIM_LENGTH, GREEN, BLUE,\
    SWEEP_MOVEMENT_CORRECTION_PERCENTAGES, SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2
from util import point_at_distance_in_a_line

def find_sweep_corner_points(detection):
    sweep_corners = detection.bot_movement_trimmed_field
    sweep_points = generate_sweep_points(
        my_posts=detection.goal_posts['self']['goal_post_end_points'],
        opponent_posts=detection.goal_posts['opponent']['goal_post_end_points'],
          corners=sweep_corners, sweep_distance = BOT_MOVEMENT_TRIM_LENGTH*detection.cm_to_pixel_rate)
    return sweep_points


def generate_sweep_points(my_posts, opponent_posts, corners, sweep_distance):

    # Find the center x-coordinate of each goal
    my_center_x = np.mean([p[0] for p in my_posts])
    opponent_center_x = np.mean([p[0] for p in opponent_posts])
    
    # Separate corners into my_corners and opponent_corners
    my_corners = sorted(corners, key=lambda p: abs(p[0] - my_center_x))[:2]
    opponent_corners = sorted(corners, key=lambda p: abs(p[0] - opponent_center_x))[:2]

    # Sort my posts and corners by x-coordinate
    my_posts = sorted(my_posts, key=lambda p: p[0])
    my_corners = sorted(my_corners, key=lambda p: p[0])

    # Sort opponent posts and corners by x-coordinate
    opponent_posts = sorted(opponent_posts, key=lambda p: p[0])
    opponent_corners = sorted(opponent_corners, key=lambda p: p[0])

    # Determine if the field needs flipping
    flip = my_center_x > opponent_center_x

    # Assign right/left labels (flip if my posts are on the right)
    if flip:
        points = [
            [
                point_at_distance_in_a_line(my_posts[1],opponent_posts[1],sweep_distance),
                my_corners[1],
                opponent_corners[1],
                point_at_distance_in_a_line(opponent_posts[1], my_posts[1],sweep_distance),
                ],
            [
                point_at_distance_in_a_line(my_posts[0],opponent_posts[0],sweep_distance),
                my_corners[0],
                opponent_corners[0],
                point_at_distance_in_a_line(opponent_posts[0], my_posts[0],sweep_distance),
                ]
                ]
    else:
        points = [
            [
            point_at_distance_in_a_line(my_posts[0],opponent_posts[0],sweep_distance),
            my_corners[0], 
            opponent_corners[0], 
            point_at_distance_in_a_line(opponent_posts[0],my_posts[0],sweep_distance),
            ],
            [
            point_at_distance_in_a_line(my_posts[1],opponent_posts[1],sweep_distance),
            my_corners[1], 
            opponent_corners[1], 
            point_at_distance_in_a_line(opponent_posts[1],my_posts[1],sweep_distance),
            ]
        ]
    return points


def sweep_movements(detection,sweep_position,sweep_points,bot):
    frame = detection.video_stream.read()
    if sweep_position == 0:
        cv2.circle(frame, sweep_points[0][0], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[0][1], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[0][0])
        bot.updatePosition()
        bot.move(sweep_points[0][1],movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2)
        bot.makeMovement('left', 2000,edge_rotation=True)
    elif sweep_position == 1:
        cv2.circle(frame, sweep_points[0][1], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[0][2], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[0][1])
        bot.updatePosition()
        bot.move(sweep_points[0][2],movement_correction_percent=SWEEP_MOVEMENT_CORRECTION_PERCENTAGES)
        bot.makeMovement('left', 2000,edge_rotation=True)
    elif sweep_position ==2:
        cv2.circle(frame, sweep_points[0][2], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[0][3], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[0][2],)
        bot.updatePosition()
        bot.move(sweep_points[0][3],movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2)
    elif sweep_position ==3:
        cv2.circle(frame, sweep_points[1][0], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[1][1], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[1][0])
        bot.updatePosition()
        bot.move(sweep_points[1][1],movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2)  
        bot.makeMovement('right', 2000,edge_rotation=True)            
    elif sweep_position ==4:
        cv2.circle(frame, sweep_points[1][1], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[1][2], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[1][1])
        bot.updatePosition()
        bot.move(sweep_points[1][2],movement_correction_percent=SWEEP_MOVEMENT_CORRECTION_PERCENTAGES)
        bot.makeMovement('right', 2000,edge_rotation=True)
    elif sweep_position ==5:
        cv2.circle(frame, sweep_points[1][2], 5, BLUE, -1)
        cv2.circle(frame, sweep_points[1][3], 5, GREEN, -1)
        cv2.imshow('Feed',frame)
        cv2.waitKey(1)
        bot.updatePosition()
        bot.move(sweep_points[1][2])
        bot.updatePosition()
        bot.move(sweep_points[1][3],movement_correction_percent = SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2)
