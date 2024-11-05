import os, json
import time
import requests

from util import *
from const import *

class Bot:
    def __init__(self, position, angle,detection):
        #todo
        self.bot_ip = '10.42.0.202'
        self.position = position # bot center point
        self.angle = angle
        self.direction = 'stop'
        self.speed = None
        self.setSpeed(6)
        self.rate_of_movement = self.calliberate(detection)
        self.command = {
            'direction' : None,
            'interval': None, 
            'time_of_command': None
        }

    def calliberate(self, detection):
        calibrate_file = "calibrated_speed.json"
        caliberation_speed = {}
        
        if not os.path.exists(calibrate_file):
            caliberation_speed['forward'] = self.caliberateMovement('forward', 500, detection)
            caliberation_speed['backward'] = self.caliberateMovement('backward', 500, detection)
            caliberation_speed['right'] = self.caliberateMovement('right', 200, detection)
            caliberation_speed['left'] = self.caliberateMovement('left', 200, detection)
            
            with open(calibrate_file, "w") as calibrationfile:
                json.dump(caliberation_speed, calibrationfile)
        else:
            with open(calibrate_file, "r") as calibrationfile:
                caliberation_speed = json.load(calibrationfile)

        return caliberation_speed


    def caliberateMovement(self, direction, interval, detection):
        if direction in ['forward', 'backward']:
            initial_position, _ = self.getPositionAndAngle(detection)

            self.makeMovement(direction, interval)
            time.sleep(3)

            final_position, _ = self.getPositionAndAngle(detection)

            # Calculate distance traveled per millisecond
            distance_traveled = calculate_distance(initial_position, final_position)
            
            return distance_traveled / interval if distance_traveled > 0 else 0

        else:
            _, initial_angle = self.getPositionAndAngle(detection)

            self.makeMovement(direction, interval)
            time.sleep(3)

            _ ,final_angle = self.getPositionAndAngle(detection)

            # Calculate angle change per millisecond
            angle_traveled = abs(final_angle - initial_angle)
            return angle_traveled / interval if angle_traveled > 0 else 0



    def getPositionAndAngle(self,detection):
        bot_angle, bot_center_point, goal_center_point, other_aruco_codes = detection.detect_aruco()
        return bot_center_point, bot_angle


    def updatePosition(self, position, angle):
        self.position = position
        self.angle = angle

    def makeMovement(self, movement, interval):
        res = requests.get(f"http://{self.bot_ip}/{movement}", params={"delay": interval})
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
        time.sleep(rotation_time_ms/1000)
        self.makeMovement(travel_direction, travel_time_ms)
        return rotation_time_ms + travel_time_ms

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
        rotation_time_ms = abs(rotation_needed) / self.rate_of_movement['right'] if rotation_direction == "right" else abs(rotation_needed) / self.rate_of_movement['left']
        travel_time_ms = distance_to_target / self.rate_of_movement['forward'] if travel_direction == "forward" else distance_to_target / self.rate_of_movement['backward']
        
        # Display the movement steps
        print(f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        print(f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")

        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms


if __name__ == '__main__':
    pass