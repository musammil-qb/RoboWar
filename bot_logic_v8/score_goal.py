import cv2
from const import SLEEP_AFTER_DISPLAYING, BLUE, GREEN, YELLOW, SLEEP_AFTER_GOAL, \
    RED,SLEEP_AFTER_MOVEMENT,SLEEP_BEFORE_GOAL
from collision_avoidance import find_pit_stop_to_avoid_ball, is_collision_chance_closest_point
import time
from util import  is_ball_moved, draw_bot_location

"""
Goal scoring module for robot soccer system.

This module contains functions for scoring goals and
handling goal-related movement strategies.

Functions:
    score_goal: Execute goal scoring strategy
"""

def score_goal(next_target_point, detection, bot, bot_center_point, bot_movement_trimmed_field, goal_center_point, opponent_bot, display=True):
    print('target locked')
    target_point = next_target_point['target_point']
    goal_point = next_target_point['goal_point']
    ball = next_target_point['ball']
    if display:
        frame = detection.video_stream.read()
        cv2.circle(frame, target_point, 5, BLUE, -1)
        cv2.circle(frame, goal_point, 5, GREEN, -1)
        draw_bot_location(frame, bot_center_point, opponent_bot, detection.cm_to_pixel_rate)
        cv2.imshow('Feed', frame)
        cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    time.sleep(SLEEP_BEFORE_GOAL)
    # check if there is a collision chance
    is_collision_chance, closest_point_on_line = is_collision_chance_closest_point(
        bot_center_point, target_point, ball, detection.cm_to_pixel_rate)
    if is_collision_chance:
        # find the pit stop to avoid the ball
        pit_stop = find_pit_stop_to_avoid_ball(
            bot_center_point, target_point, closest_point_on_line, bot_movement_trimmed_field, detection.cm_to_pixel_rate)
    if is_collision_chance:
            cv2.circle(frame, (int(pit_stop[0]),int(pit_stop[1])), 5, RED, -1)
            cv2.circle(frame, target_point, 5, YELLOW, -1)
            draw_bot_location(frame, bot_center_point, opponent_bot, detection.cm_to_pixel_rate)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    if bot and not is_collision_chance:
        if display:
            cv2.circle(frame, target_point, 5, YELLOW, -1)
            draw_bot_location(frame, bot_center_point, opponent_bot, detection.cm_to_pixel_rate)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        bot.updatePosition()
        # Move to target with ball movement check
        movement_result = bot.move(target_point, acquire_target=True, ball=ball, check_ball_movement=True)
        if movement_result == "Ball moved":
            return False
    elif bot:
        bot.updatePosition()
        bot.move(pit_stop, acquire_target=False)
        time.sleep(SLEEP_AFTER_MOVEMENT)
        bot.updatePosition()
        movement_result = bot.move(target_point, acquire_target=True, ball=ball, check_ball_movement=True)
        if movement_result == "Ball moved":
            return False
    time.sleep(SLEEP_AFTER_MOVEMENT)

    detection_object = detection.process_frame()
    if is_ball_moved(detection_object['yolo']['balls'], ball,detection.cm_to_pixel_rate):
        # abort
        print("ball moved")
        return False
    if bot:
        if display:
            # frame = detection.video_stream.read()
            cv2.circle(frame, target_point, 5, YELLOW, -1)
            draw_bot_location(frame, bot_center_point, opponent_bot, detection.cm_to_pixel_rate)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        bot.updatePosition(detection_object['aruco']['bot_center_point'],
                        detection_object['aruco']['bot_angle'])
        bot.move(goal_center_point,orient_only=True)
    time.sleep(SLEEP_AFTER_MOVEMENT)
    # input("test ball movement:")
    detection_object = detection.process_frame()
    if is_ball_moved(detection_object['yolo']['balls'], ball,detection.cm_to_pixel_rate):
        # abort
        print("ball moved")
        return False
    if bot:
        if display:
            # frame = detection.video_stream.read()
            cv2.circle(frame, goal_point, 5, YELLOW, -1)
            draw_bot_location(frame, bot_center_point, opponent_bot, detection.cm_to_pixel_rate)
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
        bot.updatePosition(detection_object['aruco']['bot_center_point'],
                        detection_object['aruco']['bot_angle'])
        bot.move(goal_point,ram=True)
    time.sleep(SLEEP_AFTER_MOVEMENT)
    print("Goal reached!")

    # Coming back to target point to avoid self goal
    # if bot:
    #     if display:
    #         # frame = detection.video_stream.read()
    #         cv2.circle(frame, target_point, 5, YELLOW, -1)
    #         cv2.imshow('Feed', frame)
    #         cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    #     bot.updatePosition()
    #     bot.move(target_point,acquire_target=False)
    #     time.sleep(SLEEP_AFTER_MOVEMENT)
    target_point, goal_point = None, None
    time.sleep(SLEEP_AFTER_GOAL)
    edge_counter = 0
    # Completed successfully
    return True
