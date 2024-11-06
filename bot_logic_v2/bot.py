import os, json
import time
import requests

from util import *
from const import *

class Bot:
    def __init__(self, position, angle,detection,calibrate=True):
        #todo
        self.bot_ip = input("Enter Bot ip: ")
        if not self.bot_ip:
            self.bot_ip = "192.168.123.103"  #TODO ip from input
        self.position = position # bot center point
        self.angle = angle
        self.direction = 'stop'
        self.speed = None
        self.setSpeed(MOVEMENT_SPEED)
        self.command = {
            'direction' : None,
            'interval': None, 
            'time_of_command': None
        }
        if calibrate:
            self.calibrate(detection)

    def calibrate(self, detection):
        calibrate_file = "calibrated_speed.json"
        caliberation_speed = {'forward': {}, 'backward': {}, 'right': {}, 'left': {}}
        
        if not os.path.exists(calibrate_file):
            # todo find offset values (angle difference for example)
            for sample_ms in BOT_CALIBRATION_MOVEMENT__MS_SAMPLES:
                caliberation_speed['forward'].update(self.caliberateMovement('forward', sample_ms, detection))
                caliberation_speed['backward'].update(self.caliberateMovement('backward', sample_ms, detection))

            for sample_ms in BOT_CALIBRATION_ROTATION_MS_SAMPLES:
                caliberation_speed['right'].update(self.caliberateMovement('right', sample_ms, detection))
                caliberation_speed['left'].update(self.caliberateMovement('left', sample_ms, detection))
            
            with open(calibrate_file, "w") as calibrationfile:
                json.dump(caliberation_speed, calibrationfile)
        else:
            with open(calibrate_file, "r") as calibrationfile:
                caliberation_speed = json.load(calibrationfile)
        self.rate_of_movement = caliberation_speed
        return caliberation_speed


    def caliberateMovement(self, direction, interval, detection):
        if direction in ['forward', 'backward']:
            initial_position, _ = self.getPositionAndAngle(detection)

            self.makeMovement(direction, interval)
            time.sleep(3)

            final_position, _ = self.getPositionAndAngle(detection)
            print(f"initial position: {initial_position} Final position:{final_position}")
            # Calculate distance traveled per millisecond
            distance_traveled = calculate_distance(initial_position, final_position)
            rate = interval / distance_traveled  if distance_traveled > 0 else 0
            
            return {distance_traveled: rate}

        else:
            _, initial_angle = self.getPositionAndAngle(detection)

            self.makeMovement(direction, interval)
            time.sleep(3)

            _ ,final_angle = self.getPositionAndAngle(detection)
            print(f"initial angle: {initial_angle} Final angle: {final_angle}")

            # Calculate angle change per millisecond
            angle_traveled = abs(final_angle - initial_angle)
            rate =  interval / angle_traveled  if angle_traveled > 0 else 0

            return {angle_traveled: rate}



    def getPositionAndAngle(self,detection):
        bot_angle, bot_center_point, goal_center_point, other_aruco_codes = detection.detect_aruco()
        return bot_center_point, bot_angle


    def updatePosition(self, position, angle):
        self.position = position
        self.angle = angle

    def makeMovement(self, movement, interval, edge_rotation=False):
        if movement in ['right', 'left'] and not edge_rotation:
            self.setSpeed(ROTATION_SPEED)

        res = requests.get(f"http://{self.bot_ip}/{movement}", params={"delay": interval})
        if movement in ['right', 'left'] and not edge_rotation:
            self.setSpeed(MOVEMENT_SPEED)

        if res.status_code ==200:
            print(f"moved {movement} time:{interval}")
    
    def setSpeed(self, speed):
        self.speed = speed
        res = requests.get(f"http://{self.bot_ip}/speed", params={"speed": speed})
        print(res.status_code)

    def move(self, target_point):
        x, y = target_point
        rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = self.calculateMovement((x, y))
        self.makeMovement(rotation_direction, rotation_time_ms)
        time.sleep((rotation_time_ms/1000)+0.05)
        self.makeMovement(travel_direction, travel_time_ms)
        time.sleep((travel_time_ms/1000)+0.05)
        
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
        travel_time_ms = distance_to_target * self.get_closest_rate(distance_to_target,
                                  self.rate_of_movement[travel_direction])
        # Display the movement steps
        print(f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        print(f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")

        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms
 
    def get_closest_rate(target, rate_dict):
        # Find the key in rate closest to the target value
        closest_sample = min(rate_dict.keys(), key=lambda k: abs(k- target))
        return rate_dict[closest_sample]




if __name__ == '__main__':
    pass