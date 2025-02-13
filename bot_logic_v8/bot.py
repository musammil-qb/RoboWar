import os
import json
import time
import requests

from util import *
from const import *

"""
Bot control module for robot soccer system.

This module contains the Bot class which handles all robot movement, calibration,
and position tracking functionality. It interfaces with the physical robot via
HTTP requests and uses computer vision data for navigation.

Classes:
    Bot: Main robot control class that handles movement, calibration, and positioning.
"""

class Bot:
    """
    Main robot control class.

    Handles all robot movement, calibration, and position tracking functionality.
    Interfaces with physical robot via HTTP requests and uses computer vision data.

    Attributes:
        bot_ip (str): IP address of the robot
        position (tuple): Current position of the robot (x,y)
        angle (float): Current orientation angle of the robot
        movement (str): Current movement state
        speed (int): Current movement speed
        detection (Detection): Computer vision detection object
        command (dict): Current movement command parameters
        rate_of_movement (dict): Calibration data for movement rates

    Methods:
        __init__: Initialize bot with position, angle and detection
        goto_initial_position: Move bot to default starting position
        calibrate: Calibrate bot movement parameters
        caliberateMovement: Calibrate movement in specific direction
        getPositionAndAngle: Get current position and angle from detection
        updatePosition: Update bot's position and angle
        makeMovement: Send movement command to bot
        setSpeed: Set bot's movement speed
        move: Move bot to target point with optional parameters
        calculate_rotation_needed: Calculate required rotation to face target
        calculateMovement: Calculate movement parameters to reach target
        get_closest_rate: Get closest calibration rate for given target
    """
    def __init__(self, position, angle, detection, calibrate=True):
        # todo
        self.bot_ip = input("Enter Bot ip: ")
        if not self.bot_ip:
            self.bot_ip = "192.168.226.103"  # TODO ip from input
        self.position = position  # bot center point
        self.angle = angle
        self.movement = 'stop'
        self.speed = None
        self.setSpeed(MOVEMENT_SPEED)
        self.detection = detection
        self.command = {
            'direction': None,
            'interval': None,
            'time_of_command': None
        }
        if calibrate:
            self.calibrate()

    def goto_initial_postion(self):
        # input("reset to default location")
        # return
        self.move(self.detection.default_point, acquire_target=True)
        time.sleep(SLEEP_AFTER_MOVEMENT)
        self.move(self.detection.goal_posts['opponent']['post_center_point'],
                   orient_only=True,orientation='forward')
        time.sleep(0.3)

    def calibrate(self):
        calibrate_file = "calibrated_speed.json"
        rate_of_movement = {'forward': {}, 'backward': {}, 'right': {}, 'left': {}}
        if not os.path.exists(calibrate_file):
            calibrate_temp_file = "calibrated_speed_temp.json"
            if os.path.exists(calibrate_temp_file):
                with open(calibrate_temp_file, "r") as calibrationfile:
                    self.rate_of_movement = json.load(calibrationfile)
            else:
                print("temporary calibration not found exiting")
                exit(0)
            # todo find offset values (angle difference for example)
            # for sample_ms in range(*BOT_CALIBRATION_ROTATION_MS_SAMPLES):
            #     rate_of_movement['right'].update(self.caliberateMovement('right', sample_ms))
            #     rate_of_movement['left'].update(self.caliberateMovement('left', sample_ms))
            # with open(calibrate_file, "w") as calibrationfile:
            #     json.dump(rate_of_movement, calibrationfile)
            self.goto_initial_postion()
            counter = 0
            for sample_ms in range(*BOT_CALIBRATION_MOVEMENT_MS_SAMPLES):
                counter += 1
                rate_of_movement['forward'].update(self.caliberateMovement('forward', sample_ms))
                rate_of_movement['backward'].update(self.caliberateMovement('backward', sample_ms))
                if counter % 5 == 0:
                    self.goto_initial_postion()
            with open(calibrate_file, "w") as calibrationfile:
                json.dump(rate_of_movement, calibrationfile)
        else:
            with open(calibrate_file, "r") as calibrationfile:
                rate_of_movement = json.load(calibrationfile)
        print("Max left angle:", max(rate_of_movement['left'].keys()))
        print("Max right angle:", max(rate_of_movement['right'].keys()))
        print("Max forward distance:", max(rate_of_movement['forward'].keys()))
        print("Max backward distance:", max(rate_of_movement['backward'].keys()))
        self.rate_of_movement = rate_of_movement
        return rate_of_movement

    def caliberateMovement(self, direction, interval):
        if direction in ['forward', 'backward']:
            initial_position, _ = self.getPositionAndAngle()

            self.makeMovement(direction, {"delay": interval})
            time.sleep(SLEEP_AFTER_CALIBRATION_MOVEMENT)

            final_position, _ = self.getPositionAndAngle()
            print(f"initial position: {initial_position} Final position:{final_position}")
            # Calculate distance traveled per millisecond
            if initial_position is not None and final_position is not None:
                distance_traveled = calculate_distance(initial_position, final_position)
            else:
                print(f"Initial position: {initial_position} final position: {final_position} please restart")
                exit(0)
            rate = interval / distance_traveled if distance_traveled > 0 else 0

            return {distance_traveled: rate}

        else:
            _, initial_angle = self.getPositionAndAngle()

            self.makeMovement(direction, {"delay": interval})
            time.sleep(SLEEP_AFTER_CALIBRATION_MOVEMENT)

            _, final_angle = self.getPositionAndAngle()

            # Calculate angle change per millisecond
            angle_traveled = abs(final_angle - initial_angle)
            print(f"initial angle: {initial_angle} Final angle: {final_angle} angle traveled: {angle_traveled}")
            rate = interval / angle_traveled if angle_traveled > 0 else 0

            return {angle_traveled: rate}

    def getPositionAndAngle(self):
        bot_center_point = None
        counter = 0
        while bot_center_point is None:
            bot_angle, bot_center_point, _, _ = self.detection.detect_aruco()
            if bot_center_point is None:
                print("Bot position not found recalculating")
                time.sleep(SLEEP_ARUCO_NOT_FOUND_RECALCULATE)
                counter += 1
                if counter % 10 == 0:
                    # reverse last action to detect bot
                    self.makeMovement(
                        MOVEMENT_REVERSE_DICT[self.movement], {"delay": 50}, update_movement=False)
        return bot_center_point, bot_angle

    def updatePosition(self,bot_center_point=None, bot_angle=None):
        if bot_center_point is None:
            bot_center_point, bot_angle = self.getPositionAndAngle()
        self.position = bot_center_point
        self.angle = bot_angle

    def makeMovement(self, movement, params, edge_rotation=False, update_movement=True):
        if movement in ['right', 'left'] and not edge_rotation: 
            self.setSpeed(ROTATION_SPEED)
        else:
            self.setSpeed(MOVEMENT_SPEED)
    
        res = requests.get(f"http://{self.bot_ip}/{movement}", params=params)

        if movement in ['right', 'left'] and not edge_rotation :
            self.setSpeed(MOVEMENT_SPEED)

        if res.status_code == 200:
            # TODO update only forward and backward?
            if update_movement and movement not in [ 'right', 'left']:
                self.movement = movement
        else:
            print(f"http request failed {res.status_code}")
            print(f"http://{self.bot_ip}/{movement}", params)

    def setSpeed(self, speed):
        self.speed = speed
        res = requests.get(f"http://{self.bot_ip}/speed", params={"speed": speed})
        if res.status_code != 200:
            print("Bot movement failed communication issue")

    def move(self, target_point, acquire_target=True, orient_only=False, ram=False, allowed_rotation_error=0, orientation=None,weighted_movement=True, ball=None, check_ball_movement=False):
        """
        Move the bot to a target point with various movement options.

        Args:
            target_point (tuple): The (x,y) coordinates of the target point to move to
            acquire_target (bool, optional): Whether to perform target acquisition and correction. 
                Defaults to True. When False, bot moves directly to target without corrections.
            orient_only (bool, optional): Whether to only orient the bot towards the target 
                without moving forward/backward. Defaults to False.
            ram (bool, optional): Whether to perform a direct movement without corrections.
                Defaults to False. When True, bot moves directly to target at full speed.
            allowed_rotation_error (int, optional): Allowed error in degrees for orientation.
                Defaults to 0. Higher values allow less precise orientation.
            orientation (str, optional): Specific orientation to face ('forward' or 'backward').
                Defaults to None, which calculates optimal orientation.
            weighted_movement (bool, optional): Whether to use weighted movement corrections.
                Defaults to True. When True, applies multiple correction steps.
            ball (tuple, optional): (x,y) coordinates of ball to check for movement.
                Defaults to None. Used with check_ball_movement.
            check_ball_movement (bool, optional): Whether to check if ball has moved during movement.
                Defaults to False. When True, aborts movement if ball moves.

        Returns:
            str: Movement status ("Completed" or "Ball moved" if check_ball_movement is True)
        """
        if target_point is None or self.position is None:
            print(
                f"target point or position failed target point:{target_point}  bot center point:{self.position}")
            return False
        if orient_only:
            rotation_time_ms, rotation_direction, _, _, rotation_needed, distance_to_target=\
                self.calculateMovement(target_point,orientation=orientation)
            distance_to_target_in_cm = distance_to_target / self.detection.cm_to_pixel_rate
            if not allowed_rotation_error:
                allowed_rotation_error = map_rotation_range(
                    distance_to_target_in_cm,0,MIN_DISTANCE_FOR_ONE_DEGREE_CORRECTION,
                    *ORIENT_ROTATION_ERROR_ALLOWED)
            print(f"Allowed rotation error: {allowed_rotation_error}\tDistance: {distance_to_target_in_cm} distance in pixel: {distance_to_target}\t rate:{self.detection.cm_to_pixel_rate}")
            correction_count=0
            if IS_USING_GYRO:
                self.makeMovement("rotate", {"angle": rotation_needed, "direction": rotation_direction, "angle_tolerance": allowed_rotation_error})
            else:
                while rotation_needed > allowed_rotation_error and correction_count < CORRECTION_LIMIT:
                    self.makeMovement(rotation_direction, {"delay": rotation_time_ms})
                    time.sleep(MOVEMENT_CORRECTION_SLEEP)
                    self.updatePosition()
                    rotation_time_ms, rotation_direction, _, _, rotation_needed, distance_to_target=\
                    self.calculateMovement(target_point,orientation=orientation)
                    correction_count+=1
            return "Completed"
        elif ram:
            _, _, travel_direction, travel_time_ms, _, _ =\
        self.calculateMovement(target_point)
            self.makeMovement(travel_direction, {"delay": travel_time_ms})
            time.sleep(MOVEMENT_CORRECTION_SLEEP)
            self.updatePosition()
            return "Completed"
        elif acquire_target and weighted_movement:
            # Calculate distance to target in cm
            _, _, _, _, _, distance_to_target = self.calculateMovement(target_point)
            distance_to_target_in_cm = distance_to_target / self.detection.cm_to_pixel_rate
            
            # Select appropriate correction percentages based on distance
            correction_percentages = None
            for threshold in sorted(MOVEMENT_CORRECTION_PERCENTAGES_MAP.keys()):
                if distance_to_target_in_cm <= threshold:
                    correction_percentages = MOVEMENT_CORRECTION_PERCENTAGES_MAP[threshold]
                    break
            # Use the highest threshold percentages if distance exceeds all thresholds
            if correction_percentages is None:
                correction_percentages = MOVEMENT_CORRECTION_PERCENTAGES_MAP[max(MOVEMENT_CORRECTION_PERCENTAGES_MAP.keys())]
            
            print(f"weighted movement distance: {round(distance_to_target_in_cm)} percentages: {correction_percentages}")
            for  percentage in correction_percentages:
                rotation_time_ms, rotation_direction, travel_direction, travel_time_ms, rotation_needed, _ =\
                      self.calculateMovement(target_point)
                if IS_USING_GYRO:
                    self.makeMovement("rotate", {"angle": rotation_needed, "direction": rotation_direction, "angle_tolerance": ALLOWED_ROTATION_ERROR})
                else:
                    self.makeMovement(rotation_direction, {"delay": rotation_time_ms})
                self.makeMovement(travel_direction, {"delay": travel_time_ms*percentage})
                time.sleep(MOVEMENT_CORRECTION_SLEEP)
                self.updatePosition()
                
                # Check for ball movement if requested
                if check_ball_movement and ball is not None:
                    detection_object = self.detection.process_frame()
                    if is_ball_moved(detection_object['yolo']['balls'], ball, self.detection.cm_to_pixel_rate):
                        print("ball moved during weighted movement")
                        return "Ball moved"
            return "Completed"
        elif acquire_target:
            print("go until found")
            rotation_time_ms, rotation_direction, travel_direction, travel_time_ms, rotation_needed, _ =\
                  self.calculateMovement(target_point)
            if IS_USING_GYRO:
                self.makeMovement("rotate", {"angle": rotation_needed, "direction": rotation_direction, "angle_tolerance": ALLOWED_ROTATION_ERROR})
                # time.sleep(1)
            else:
                self.makeMovement(rotation_direction, {"delay": rotation_time_ms})
            self.makeMovement(travel_direction, {"delay": travel_time_ms})
            time.sleep(MOVEMENT_CORRECTION_SLEEP)
            self.updatePosition()
            distance = calculate_distance(self.position, target_point)
            correction_count = 0
            while distance > MOVEMENT_ERROR_ALLOWED and acquire_target and correction_count < CORRECTION_LIMIT:
                rotation_time_ms, rotation_direction, travel_direction, travel_time_ms, rotation_needed, _ = \
                    self.calculateMovement(target_point)
                if IS_USING_GYRO:
                    self.makeMovement("rotate", {"angle": rotation_needed, "direction": rotation_direction, "angle_tolerance": ALLOWED_ROTATION_ERROR})
                    # time.sleep(1)
                else:
                    self.makeMovement(rotation_direction, {"delay": rotation_time_ms})
                self.makeMovement(travel_direction, {"delay": travel_time_ms})
                time.sleep(MOVEMENT_CORRECTION_SLEEP)
                self.updatePosition()
                distance = calculate_distance(self.position, target_point)
                print(f"Distance diffrence: {distance} correcting")
                correction_count+=1
        else:
            rotation_time_ms, rotation_direction, travel_direction, travel_time_ms, rotation_needed, _ =\
                  self.calculateMovement(target_point)
            if IS_USING_GYRO:
                self.makeMovement("rotate", {"angle": rotation_needed, "direction": rotation_direction, "angle_tolerance": ALLOWED_ROTATION_ERROR})
            else:
                self.makeMovement(rotation_direction, {"delay": rotation_time_ms})
            self.makeMovement(travel_direction, {"delay": travel_time_ms})
        return "Completed"

    def calculate_rotation_needed(self,bot_position,bot_angle,target_point,orientation=None):
        angle_to_target = calculate_angle_to_point(bot_position, target_point)

        # Calculate rotation and travel directions
        rotation_needed = (angle_to_target - bot_angle) % 360
        if orientation is None:
            if rotation_needed < 90:
                rotation_direction = "right"
                travel_direction = "forward"
            elif rotation_needed > 90 and rotation_needed < 180:
                rotation_direction = "left"
                travel_direction = "backward"
                rotation_needed = 180 - rotation_needed
            elif rotation_needed > 180 and rotation_needed < 270:
                rotation_direction = "right"
                travel_direction = "backward"
                rotation_needed = rotation_needed - 180
            else:
                rotation_direction = "left"
                travel_direction = "forward"
                rotation_needed = 360 - rotation_needed
        elif orientation == 'forward':
            rotation_direction = "right" if rotation_needed < 180 else "left"
            rotation_needed = rotation_needed if rotation_needed < 180 else (360 - rotation_needed)
            travel_direction = "forward"
        elif orientation == 'backward':
            rotation_direction = "left" if rotation_needed < 180 else "right"
            rotation_needed = (180 - rotation_needed) if rotation_needed < 180 else (rotation_needed - 180)
            travel_direction = "backward"
        return rotation_needed, rotation_direction, travel_direction

    def calculateMovement(self, target_point,orientation=None):
        bot_position, bot_angle = self.position, self.angle
        # Calculate distance and angle to target
        distance_to_target = calculate_distance(bot_position, target_point)
        rotation_needed, rotation_direction, travel_direction = self.calculate_rotation_needed(bot_position,bot_angle,target_point,orientation)
        # Calculate rotation and travel time
        rotation_time_ms = abs(rotation_needed) * self.get_closest_rate(
            rotation_needed, self.rate_of_movement[rotation_direction])
        travel_time_ms = distance_to_target * \
            self.get_closest_rate(distance_to_target, self.rate_of_movement[travel_direction])
        # Display the movement steps
        # print(
        #     f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        # print(
        #     f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")
        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms, rotation_needed, distance_to_target

    def get_closest_rate(self, target, rate_dict):
        # Find the key in rate closest to the target value
        closest_sample = min(rate_dict.keys(), key=lambda k: abs(int(float(k)) - target))
        return rate_dict[closest_sample]


if __name__ == '__main__':
    pass
