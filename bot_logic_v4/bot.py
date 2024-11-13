import os
import json
import time
import requests

from util import *
from const import *


class Bot:
    def __init__(self, position, angle, detection, calibrate=True):
        # todo
        self.bot_ip = input("Enter Bot ip: ")
        if not self.bot_ip:
            self.bot_ip = "192.168.32.103"  # TODO ip from input
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
            self.calibrate(detection)

    def goto_initial_postion(self):
        self.move(self.detection.default_point, acquire_target=False)
        time.sleep(SLEEP_AFTER_MOVEMENT)
        self.move(self.detection.goal_posts['opponent']['post_center_point'],
                   orient_only=True)

    def calibrate(self):
        calibrate_file = "calibrated_speed.json"
        rate_of_movement = {'forward': {}, 'backward': {}, 'right': {}, 'left': {}}
        if not os.path.exists(calibrate_file):
            calibrate_temp_file = "calibrated_speed_temp.json"
            if os.path.exists(calibrate_temp_file):
                with open(calibrate_temp_file, "r") as calibrationfile:
                    rate_of_movement = json.load(calibrationfile)
                    self.rate_of_movement = rate_of_movement
            else:
                print("temporary calibration not found exiting")
                exit(0)
            # todo find offset values (angle difference for example)
            for sample_ms in range(*BOT_CALIBRATION_ROTATION_MS_SAMPLES):
                rate_of_movement['right'].update(self.caliberateMovement('right', sample_ms))
                rate_of_movement['left'].update(self.caliberateMovement('left', sample_ms))
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

        self.rate_of_movement = rate_of_movement
        return rate_of_movement

    def caliberateMovement(self, direction, interval):
        if direction in ['forward', 'backward']:
            initial_position, _ = self.getPositionAndAngle()

            self.makeMovement(direction, interval)
            time.sleep(interval)
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

            self.makeMovement(direction, interval)
            time.sleep(SLEEP_AFTER_CALIBRATION_MOVEMENT)

            _, final_angle = self.getPositionAndAngle()
            print(f"initial angle: {initial_angle} Final angle: {final_angle}")

            # Calculate angle change per millisecond
            angle_traveled = abs(final_angle - initial_angle)
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
                # TODO do inverse movement if not found for 10 sec
                counter += 1
                if counter % 10:
                    # reverse last action to detect bot
                    self.makeMovement(
                        MOVEMENT_REVERSE_DICT[self.movement], 50, update_movement=False)
        return bot_center_point, bot_angle

    def updatePosition(self):
        bot_center_point, bot_angle = self.getPositionAndAngle()
        self.position = bot_center_point
        self.angle = bot_angle

    def makeMovement(self, movement, interval, edge_rotation=False, update_movement=True):
        if movement in ['right', 'left'] and not edge_rotation:
            self.setSpeed(ROTATION_SPEED)

        res = requests.get(f"http://{self.bot_ip}/{movement}", params={"delay": interval})

        if movement in ['right', 'left'] and not edge_rotation:
            self.setSpeed(MOVEMENT_SPEED)

        if res.status_code == 200:
            print(f"moved {movement} time:{interval}")
            # TODO update only forward and backward?
            if update_movement:
                self.movement = movement

    def setSpeed(self, speed):
        self.speed = speed
        res = requests.get(f"http://{self.bot_ip}/speed", params={"speed": speed})
        if res.status_code != 200:
            print("Bot movement failed communication issue")

    def move(self, target_point, acquire_target=True, orient_only=False):
        if target_point is None or self.position is None:
            print(
                f"target point or position failed target point:{target_point}  bot center point:{self.position}")
            return False
        # rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = self.calculateMovement(target_point)
        if orient_only:
            rotation_time_ms, rotation_direction, travel_direction, travel_time_ms =\
                  self.calculateMovement(target_point)
            self.makeMovement(rotation_direction, rotation_time_ms)
            pass
            # time.sleep(MOVEMENT_CORRECTION_SLEEP)
            # self.updatePosition()
            # correction in angle
        elif MOVEMENT_CORRECTION_PERCENTAGES:
            for percentage in MOVEMENT_CORRECTION_PERCENTAGES:
                rotation_time_ms, rotation_direction, travel_direction, travel_time_ms =\
                      self.calculateMovement(target_point)
                self.makeMovement(rotation_direction, rotation_time_ms)
                self.makeMovement(travel_direction, travel_time_ms*percentage)
                time.sleep(MOVEMENT_CORRECTION_SLEEP)
                self.updatePosition()
        else:
            rotation_time_ms, rotation_direction, travel_direction, travel_time_ms =\
                  self.calculateMovement(target_point)
            self.makeMovement(rotation_direction, rotation_time_ms)
            self.makeMovement(travel_direction, travel_time_ms)
            time.sleep(MOVEMENT_CORRECTION_SLEEP)
            self.updatePosition()
            distance = calculate_distance(self.position, target_point)

            while distance > 15 and acquire_target:
                rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = \
                    self.calculateMovement(target_point)
                self.makeMovement(rotation_direction, rotation_time_ms)
                self.makeMovement(travel_direction, travel_time_ms)
                self.updatePosition()
                time.sleep(MOVEMENT_CORRECTION_SLEEP)
                distance = calculate_distance(self.position, target_point)
                print(f"Distance diffrence: {distance} correcting")

        return "Completed"

    def calculateMovement(self, target_point):
        bot_position, bot_angle = self.position, self.angle
        # Calculate distance and angle to target
        distance_to_target = calculate_distance(bot_position, target_point)
        angle_to_target = calculate_angle_to_point(bot_position, target_point)

        # Calculate rotation and travel directions
        rotation_needed = (angle_to_target - bot_angle) % 360
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

        # Calculate rotation and travel time
        rotation_time_ms = abs(rotation_needed) * self.get_closest_rate(
            rotation_needed, self.rate_of_movement[rotation_direction])
        travel_time_ms = distance_to_target * \
            self.get_closest_rate(distance_to_target, self.rate_of_movement[travel_direction])
        # Display the movement steps
        print(
            f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        print(
            f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")

        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms

    def get_closest_rate(self, target, rate_dict):
        # Find the key in rate closest to the target value
        closest_sample = min(rate_dict.keys(), key=lambda k: abs(int(float(k)) - target))
        return rate_dict[closest_sample]


if __name__ == '__main__':
    pass
