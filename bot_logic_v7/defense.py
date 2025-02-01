from util import calculate_distance, point_at_distance_in_a_line
from const import DEFENSE_INTERCEPTION_DISTANCE


def calculate_blocking_point(opponent_bot, opponent_goal_post,cm_to_pixel_rate):
    distance_of_interception = cm_to_pixel_rate * DEFENSE_INTERCEPTION_DISTANCE
    opponent_distance_from_post = calculate_distance(opponent_bot, opponent_goal_post)
    if opponent_distance_from_post < distance_of_interception:
        return False
    return point_at_distance_in_a_line(opponent_goal_post, opponent_bot, distance_of_interception)