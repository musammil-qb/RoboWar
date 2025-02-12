import time

from util import calculate_distance, point_at_distance_in_a_line
from const import DEFENSE_INTERCEPTION_DISTANCE, DEFENSE_COOLDOWN


def calculate_blocking_point(opponent_bot, opponent_goal_post,cm_to_pixel_rate):
    distance_of_interception = cm_to_pixel_rate * DEFENSE_INTERCEPTION_DISTANCE
    opponent_distance_from_post = calculate_distance(opponent_bot, opponent_goal_post)
    if opponent_distance_from_post < distance_of_interception:
        return False
    return point_at_distance_in_a_line(opponent_goal_post, opponent_bot, distance_of_interception)

def check_defense_needed(opponent_bot, balls, detection, defense_start_time):
    defense_needed = False
    balls_near_opponent, defense_ball = False, None
    if opponent_bot:
        # Check if any balls are within 50cm of opponent bot
        for ball in balls:
            if calculate_distance(opponent_bot, ball) < 50 * detection.cm_to_pixel_rate:
                balls_near_opponent = True
                defense_needed = True
                defense_ball = ball
                break
        
        # Only maintain cooldown if balls are near opponent
        current_time = time.time()
        print(f"current_time: {current_time} defense_start_time: {defense_start_time} cooldown: {DEFENSE_COOLDOWN}")
        if current_time and defense_start_time:
            print(f" diff :{current_time - defense_start_time}")
        if defense_start_time is not None and current_time - defense_start_time <= DEFENSE_COOLDOWN:
            print("between defense continung")
            if balls_near_opponent:
                defense_needed = True
            else:
                defense_start_time = None  # Reset cooldown if no balls near opponent
        else:
            print("exiying defense cooldown is finished")
            defense_start_time = None
    else:
        print("no opponent bot")
    return defense_needed, defense_ball, defense_start_time