import requests
from util import *
from const import *


class Bot:
    def __init__(self, position, angle,detection):
        #to do
        self.bot_ip = '10.42.0.202'
        self.position = position #bot center point
        self.angle = angle
        self.direction = 'stop'
        self.speed = None
        self.rate_of_movement = self.calliberate(detection)
        self.command = {
            'direction' : None,
            'interval': None, 
            'time_of_command': None
        }
        self.setSpeed(4)

    def calliberate(self,detection):
        return {'forward': FRONT_TRAVEL_PIXELS_PER_MS, 'backward': BACK_TRAVEL_PIXELS_PER_MS, 
                'left': ROTATION_TIME_PER_DEGREE,
                'right': ROTATION_TIME_PER_DEGREE,
                }
        caliberation_speed = {}
        caliberation_speed['forward'] = self.caliberateMovement('forward', 500,detection)
        caliberation_speed['backward'] = self.caliberateMovement('backward', 500,detection)
        caliberation_speed['right'] = self.caliberateMovement('right', 100,detection)
        caliberation_speed['left'] = self.caliberateMovement('left', 100,detection)

        return caliberation_speed

    def caliberateMovement(self, direction, interval,detection):
        if direction == 'forward' or direction == 'backward':
            initial_position = self.getPositionAndAngle(detection)[0]
            self.makeMovement(direction, interval)
            final_position = self.getPositionAndAngle(detection)[0]
            return calculate_distance(initial_position, final_position) / interval
        else:
            initial_angle = self.getPositionAndAngle(detection)[1]
            self.makeMovement(direction, interval)
            final_angle = self.getPositionAndAngle(detection)[1]
            return calculate_angle_to_point(initial_angle, final_angle) / interval


    def getPositionAndAngle(self,detection):
        
        detection_object = detection.process_frame()
        return detection_object['aruco']['bot_center_point'], detection_object['aruco']['bot_angle']



    def updatePosition(self, position, angle):
        self.position = position
        self.angle = angle

    def makeMovement(self, movement, interval):
        res = requests.get(f"http://{self.bot_ip}/{movement}", params={"delay": interval})
        print(res.status_code)
    
    def setSpeed(self, speed):
        self.speed = speed
        res = requests.get(f"http://{self.bot_ip}/speed", params={"speed": speed})
        print(res.status_code)

    def move(self, target_point):
        x, y = target_point
        rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = self.calculateMovement((x, y))
        self.makeMovement(rotation_direction, rotation_time_ms)
        self.makeMovement(travel_direction, travel_time_ms)

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
        rotation_time_ms = abs(rotation_needed) * self.rate_of_movement['right'] if rotation_direction == "right" else abs(rotation_needed) * self.rate_of_movement['left']
        travel_time_ms = distance_to_target / self.rate_of_movement['forward'] if travel_direction == "forward" else distance_to_target / self.rate_of_movement['backward']
        
        # Display the movement steps
        print(f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        print(f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")

        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms


if __name__ == '__main__':
    pass