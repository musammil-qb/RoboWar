import time
import cv2
from util import calculate_distance, point_at_distance_in_a_line, draw_bot_location
from const import DEFENSE_INTERCEPTION_DISTANCE, DEFENSE_COOLDOWN, RED, \
    BLUE, SLEEP_AFTER_DISPLAYING,SLEEP_AFTER_MOVEMENT, OPPONENT_BALL_DISTANCE, ORANGE


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
            if calculate_distance(opponent_bot, ball) < OPPONENT_BALL_DISTANCE * detection.cm_to_pixel_rate:
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
            print("exiting defense cooldown is finished")
            defense_start_time = None
    else:
        print("no opponent bot")
    return defense_needed, defense_ball, defense_start_time


def execute_defense(bot, opponent_bot, balls, defense_ball, self_goal_center_point, defense_point_1, detection, display=True, message="defending"):
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
    point_of_intercept = calculate_blocking_point(
        opponent_bot, self_goal_center_point, detection.cm_to_pixel_rate)
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
    
    bot.move(point_of_intercept, acquire_target=False)