import numpy as np

from const import AVOIDANCE_DISTANCE, PIT_STOP_DISTANCE
from util import distance_to_line,is_point_inside_border,\
    perpendicular_points_from_point_on_line_with_a_distance


def is_collision_chance_closest_point(bot_center_point, target_point, ball, cm_to_pixel_rate):
    distance_from_ball_to_line, closest_point= distance_to_line(ball, np.array(bot_center_point), np.array(target_point))
    return distance_from_ball_to_line < (AVOIDANCE_DISTANCE*cm_to_pixel_rate), closest_point


def find_pit_stop_to_avoid_ball(bot_center_point, target_point, closest_point, bot_movement_trimmed_field,cm_to_pixel_rate):
    print(bot_movement_trimmed_field)
    secondary_point1, secondary_point2 = perpendicular_points_from_point_on_line_with_a_distance([bot_center_point,target_point,], closest_point, cm_to_pixel_rate*PIT_STOP_DISTANCE)
    if is_point_inside_border(secondary_point1, np.array(bot_movement_trimmed_field)):
        return secondary_point1
    return secondary_point2


"""
Collision avoidance module for robot soccer system.

This module contains functions for detecting and avoiding
collisions with balls and other objects.

    is_collision_chance_closest_point: Check if collision is likely
 and return the closest point of collision
    find_pit_stop_to_avoid_ball: Find safe point to avoid collision
"""

