import time
import cv2
import math
import numpy as np
from util import calculate_distance, point_at_distance_in_a_line, draw_bot_location, line_intersection
from const import DEFENSE_INTERCEPTION_DISTANCE, DEFENSE_COOLDOWN, RED, \
    BLUE, SLEEP_AFTER_DISPLAYING,SLEEP_AFTER_MOVEMENT, OPPONENT_BALL_DISTANCE, ORANGE


def calculate_blocking_point(opponent_bot, opponent_goal_post, defense_line):
    intersection_point = line_intersection(defense_line[0], defense_line[1], opponent_bot, opponent_goal_post)

    if intersection_point:
        return intersection_point
    return False

def check_defense_needed(opponent_bot, balls, detection, defense_start_time):
    defense_needed = False
    balls_near_opponent, defense_ball = False, None
    if opponent_bot:
        # Check if any balls are within 50cm of opponent bot
        for ball in balls:
            if calculate_distance(opponent_bot, ball) < OPPONENT_BALL_DISTANCE * detection.cm_to_pixel_rate:
                balls_near_opponent = True
                defense_needed = True
                defense_ball = ball
                break
        
        # Only maintain cooldown if balls are near opponent
        current_time = time.time()
        if current_time and defense_start_time:
            print(f" cooldown ends in {DEFENSE_COOLDOWN - (current_time - defense_start_time)} seconds")
        if defense_start_time is not None and current_time - defense_start_time <= DEFENSE_COOLDOWN:
            if balls_near_opponent:
                defense_needed = True
            else:
                defense_start_time = None  # Reset cooldown if no balls near opponent
        else:
            print("exiting defense cooldown is finished")
            defense_start_time = None
    else:
        print("no opponent bot")
    return defense_needed, defense_ball, defense_start_time

last_defense_time = None

def execute_defense(bot, opponent_bot, balls, defense_ball, self_goal_center_point, defense_point_1, detection, defense_line,display=True, message="defending"):
    """
    Execute defense movement for the bot.
    
    Args:
        bot: Bot object to control movement
        opponent_bot: Position of opponent bot
        balls: List of all balls on field
        defense_ball: Ball that triggered defense
        self_goal_center_point: Center point of our goal
        defense_point_1: Primary defense position
        detection: Detection object for field parameters
        display: Whether to display visual feedback
        message: Message to print during defense
    """
    global last_defense_time
    point_of_intercept = calculate_blocking_point(
        opponent_bot, self_goal_center_point, defense_line)
    if not point_of_intercept:
        bot.move(defense_point_1, acquire_target=False)
        time.sleep(SLEEP_AFTER_MOVEMENT)
        point_of_intercept = detection.default_point
        bot.updatePosition()
    if display:
        frame = detection.video_stream.read()
        for ball in balls:
            if ball == defense_ball:
                cv2.circle(frame, ball, 5, RED, -1)
            else:
                cv2.circle(frame, ball, 5, BLUE, -1)
        draw_bot_location(frame, bot.position, opponent_bot, detection.cm_to_pixel_rate)
        cv2.circle(frame, point_of_intercept, 5, ORANGE, -1)
        cv2.imshow('Feed', frame)
        cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    
    print(message)
    if last_defense_time is None or time.time() - last_defense_time > 1.2:
        bot.move(point_of_intercept, acquire_target=True)
        last_defense_time = time.time()
        time.sleep(SLEEP_AFTER_MOVEMENT)
    bot.updatePosition()
    bot.move(defense_line[0], orientation='forward',orient_only=True)
    

def generate_defense_line(detection):
    self_goal_center = detection.goal_posts['self']['post_center_point']
    opponent_goal_center = detection.goal_posts['opponent']['post_center_point']
    dx = opponent_goal_center[0] - self_goal_center[0]
    dy = opponent_goal_center[1] - self_goal_center[1]
    magnitude = math.sqrt(dx**2 + dy**2)
    direction_vector = [dx/magnitude, dy/magnitude]
    
    # Calculate defense line points pushed in direction of opponent goal
    push_distance_to_opponent_goal_post = 10 * detection.cm_to_pixel_rate
    push_distance_for_extension = -8 * detection.cm_to_pixel_rate
    
    defense_line = [
        (int(detection.goal_posts['self']['goal_post_end_points'][0][0] + push_distance_to_opponent_goal_post * direction_vector[0]),
         int(detection.goal_posts['self']['goal_post_end_points'][0][1] + push_distance_to_opponent_goal_post * direction_vector[1])),
        (int(detection.goal_posts['self']['goal_post_end_points'][1][0] + push_distance_to_opponent_goal_post * direction_vector[0]),
         int(detection.goal_posts['self']['goal_post_end_points'][1][1] + push_distance_to_opponent_goal_post * direction_vector[1]))
    ]
    defense_line = [point_at_distance_in_a_line(defense_line[1],defense_line[0],push_distance_for_extension),point_at_distance_in_a_line(defense_line[0],defense_line[1],push_distance_for_extension)]
    return defense_line