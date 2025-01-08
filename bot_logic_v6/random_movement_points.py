import cv2
import math
import time
import numpy as np
from random import randint

from const import FORWARD_OFFENCE_POINT_DISTANCE_AFTER_CENTER, IS_ARUCO_WORKING, \
    DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT, FORWARD_MOVEMENT_DELAY, SLEEP_AFTER_DISPLAYING, \
    SLEEP_AFTER_DEFENSE, YELLOW, DEFENCE_LOOP_MOVEMENTS, DEFENCE_INITIAL_MOVEMENTS, \
    RANDOM_MOVEMENT_DELAY_RANGE, RANDOM_MOVEMENT_DIRECTIONS, RANDOM_MOVEMENT_SPEED, SLEEP_AFTER_MOVEMENT


def get_forward_goal_point(detection):
    start_point = detection.default_point
    end_point = detection.center_point 
    dx =  end_point[0] - start_point[0]  
    dy =  end_point[1] - start_point[1]  
    magnitude = math.sqrt(dx**2 + dy**2)
    line_vector = np.array( [dx / magnitude, dy / magnitude])

    initial_movement_point = detection.center_point + (detection.cm_to_pixel_rate* FORWARD_OFFENCE_POINT_DISTANCE_AFTER_CENTER)* line_vector
    initial_movement_point = (int(initial_movement_point[0]), int(initial_movement_point[1]))
    return initial_movement_point

def get_defense_points(detection):
    start_point = detection.goal_posts['self']['edge'][0]
    end_point = detection.goal_posts['self']['edge'][1]
    dx =  end_point[0] - start_point[0]  
    dy =  end_point[1] - start_point[1]  
    magnitude = math.sqrt(dx**2 + dy**2)
    line_vector = np.array( [dx / magnitude, dy / magnitude])
    
    defense_point_1 = detection.default_point + (detection.cm_to_pixel_rate * DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT)* line_vector
    defense_point_1 = (int(defense_point_1[0]), int(defense_point_1[1]))

    defense_point_2 = detection.default_point - (detection.cm_to_pixel_rate * DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT)* line_vector
    defense_point_2 = (int(defense_point_2[0]), int(defense_point_2[1]))
    
    return defense_point_1, defense_point_2

def random_movement_algorithm(detection, bot, strategy,defense_point_1,defense_point_2):
    if strategy =='f':
        frame = detection.video_stream.read()
        # if arucode works
        if IS_ARUCO_WORKING:
            initial_movement_point = get_forward_goal_point(detection)
            bot.updatePosition()
            bot.move(initial_movement_point,acquire_target=False)
            bot.updatePosition()
            bot.move(detection.default_point,acquire_target=False)
        else:
            # bot
            bot.makeMovement('forward',FORWARD_MOVEMENT_DELAY)
            bot.makeMovement('backward',FORWARD_MOVEMENT_DELAY)
        cv2.imshow('Feed', frame)
        cv2.waitKey(SLEEP_AFTER_DISPLAYING)
    elif strategy == 'd':
        if IS_ARUCO_WORKING:
            frame = detection.video_stream.read()
            cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
            cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            while True:
                bot.updatePosition()
                bot.move(defense_point_1, acquire_target=False)
                bot.updatePosition()
                bot.move(defense_point_2, acquire_target=False)
                bot.updatePosition()
                bot.move(detection.default_point, acquire_target=False)
                bot.updatePosition()
                time.sleep(SLEEP_AFTER_DEFENSE)
        else:
            frame = detection.video_stream.read()
            cv2.circle(frame, defense_point_1,5, YELLOW, -1)  
            cv2.circle(frame, defense_point_2,5, YELLOW, -1)  
            cv2.imshow('Feed', frame)
            cv2.waitKey(SLEEP_AFTER_DISPLAYING)
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[0])
            bot.makeMovement(*DEFENCE_INITIAL_MOVEMENTS[1])
            while True:
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[0])
                bot.makeMovement(*DEFENCE_LOOP_MOVEMENTS[1])
                bot.move(detection.default_point)      
                time.sleep(SLEEP_AFTER_DEFENSE)

    elif strategy == 'r':
        bot.setSpeed(RANDOM_MOVEMENT_SPEED)
        while True:
            random_movement = RANDOM_MOVEMENT_DIRECTIONS[randint(0,len(RANDOM_MOVEMENT_DIRECTIONS)-1)]
            random_delay = randint(*RANDOM_MOVEMENT_DELAY_RANGE)
            bot.makeMovement(random_movement, random_delay)
            time.sleep(SLEEP_AFTER_MOVEMENT)
