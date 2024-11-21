import math
import numpy as np

from const import FORWARD_OFFENCE_POINT_DISTANCE_AFTER_CENTER, DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT


def get_forward_goal_point(detection):
    start_point = detection.default_point
    end_point = detection.center_point 
    dx =  end_point[0] - start_point[0]  
    dy =  end_point[1] - start_point[1]  
    magnitude = math.sqrt(dx**2 + dy**2)
    line_vector = np.array( [dx / magnitude, dy / magnitude])

    initial_movement_point = detection.center_point + (detection.cm_pixel_rate* FORWARD_OFFENCE_POINT_DISTANCE_AFTER_CENTER)* line_vector
    initial_movement_point = (int(initial_movement_point[0]), int(initial_movement_point[1]))
    return initial_movement_point

def get_defense_points(detection):
    start_point = detection.goal_posts['self']['edge'][0]
    end_point = detection.goal_posts['self']['edge'][1]
    dx =  end_point[0] - start_point[0]  
    dy =  end_point[1] - start_point[1]  
    magnitude = math.sqrt(dx**2 + dy**2)
    line_vector = np.array( [dx / magnitude, dy / magnitude])
    
    defense_point_1 = detection.default_point + (detection.cm_pixel_rate * DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT)* line_vector
    defense_point_1 = (int(defense_point_1[0]), int(defense_point_1[1]))

    defense_point_2 = detection.default_point - (detection.cm_pixel_rate * DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT)* line_vector
    defense_point_2 = (int(defense_point_2[0]), int(defense_point_2[1]))
    
    return defense_point_1, defense_point_2