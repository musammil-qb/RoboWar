"""
Constants module for robot soccer system.

This module contains all system-wide constants including:
- Aruco marker IDs
- Movement parameters
- Color definitions
- Timing constants
- Field dimensions
- Configuration flags
"""

import cv2.aruco as aruco
# Arucode Ids
BOT_ID = 69
POST_ID  = 92

OPPONENT_ARUCO_ID = 92
OPPONENT_ARUCO_TYPE = aruco.DICT_4X4_100

# OPPONENT_ARUCO_ID = 43
# OPPONENT_ARUCO_TYPE = aruco.DICT_4X4_100

IS_USING_GYRO = False

DEFENSE_INTERCEPTION_DISTANCE = 30
OPPONENT_BALL_DISTANCE = 80
ORIENT_ROTATION_ERROR_ALLOWED = [8,1] # Rotation error range

MOVEMENT_CORRECTION_PERCENTAGES_MAP = {
    20:[1],
    30:  [0.8, 1],      # Short distances
    90:  [0.8, 0.5, 1],
    120:  [0.8, 0.5, 0.5, 1],
    200: [0.8, 0.5, 0.5, 0.5, 1]  # Long distances
}
CORRECTION_LIMIT = 5
DEFENSE_COOLDOWN = 8  # 5 seconds cooldown for defense mode

MOVEMENT_SPEED = 10
ROTATION_SPEED = 4

#  colors
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
ORANGE = (15,56,100)
YELLOW = (0, 165, 255)
GREY = (128, 128, 128)


EDGE_ROTATION_DELAY = 1500
BALL_COOLOFF_DISTANCE = 20

IS_ARUCO_WORKING = True 
DEFENSE_MODE = 1  # 1 Razal mode 2 Defense point movement

# Sample ms to set calibration        [start, stop, step]
BOT_CALIBRATION_MOVEMENT_MS_SAMPLES = [50, 1400, 50]
BOT_CALIBRATION_ROTATION_MS_SAMPLES = [20, 450, 10]

# Sleep constants
SLEEP_BEFORE_GOAL = 0.1
SLEEP_AFTER_GOAL = 0.2
SLEEP_AFTER_MOVEMENT = 0.01
SLEEP_BALL_NOT_FOUND = 1 # sleep when bot center or ball not found
SLEEP_AFTER_EACH_LOOP = 0.1
SLEEP_FOR_KEY_PRESS = 1 # in ms
SLEEP_AFTER_CALIBRATION_MOVEMENT = 1
SLEEP_CORNER_SELECTION_LOOP = 0.5
SLEEP_ARUCO_NOT_FOUND_RECALCULATE = 0.2
MOVEMENT_CORRECTION_SLEEP = 0.1
SLEEP_AFTER_DEFENSE = 0.3
# cv2.waitKey wait
SLEEP_AFTER_DISPLAYING = 1 # in ms
SLEEP_BEFORE_TAKING_FRAME = 0


# measurement constants
FIELD_LENGTH = 239
FIELD_WIDTH = 182
CORNER_TO_POST_LENGTH = 68
POST_LENGTH = 45
DEFAULT_POSITION_TO_POST_LENGTH = 23
TRIM_LENGTH = 8
BOT_MOVEMENT_TRIM_LENGTH = 4
EXTENDED_POINT_OFFSET = 25
EDGE_BALL_ROTATION_DISTANCE = 8
EDGE_BALL_MOVEMENT_DISTANCE = 15
EDGE_BALL_MOVEMENT_BUFFER = 12


FORWARD_OFFENCE_POINT_DISTANCE_AFTER_CENTER = 20
DEFENSE_POINT_DISTANCE_FROM_DEFAULT_POINT = 25

AVOIDANCE_DISTANCE = 15
PIT_STOP_DISTANCE = 35
BALL_MOVEMENT_BUFFER = 8

MOVEMENT_REVERSE_DICT = {
    'left': 'right', 'right': 'left', 'forward': 'backward',
    'backward': 'forward','stop':'stop'}

# flags
RANDOM_MOVEMENT_SPEED = 3
RANDOM_MOVEMENT_DELAY_RANGE = [100, 800]
RANDOM_MOVEMENT_DIRECTIONS = ['forward', 'backward', 'left', 'right']
FORWARD_MOVEMENT_DELAY = 1000

# each value percentageis a percentage
MOVEMENT_ERROR_ALLOWED = 15
MIN_DISTANCE_FOR_ONE_DEGREE_CORRECTION = 200 #error?



DEFENSE_INITIAL_MOVEMENTS = [['right',{"delay": 278}],['backward',{"delay": 270}]]
DEFENSE_LOOP_MOVEMENTS = [['forward',{"delay": 442}],['backward',{"delay": 442}]]
NO_DEFENSE_MOVE_WITH_NO_TARGET_BALLS = 5 #no of iterations of defense to move before

# Distance thresholds (in units) mapped to correction percentages
# Higher distances need more granular corrections

# Remove old constants
# MOVEMENT_CORRECTION_PERCENTAGES = [0.8, 0.5, 0.5, 1]
# SWEEP_MOVEMENT_CORRECTION_PERCENTAGES = [0.05, 0.1,0.15,0.2,0.3,0.5, 0.5, 1]
# SWEEP_MOVEMENT_CORRECTION_PERCENTAGES_2 = [0.3, 0.4, 0.5, 1]

ALLOWED_ROTATION_ERROR = 3