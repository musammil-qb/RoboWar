import requests
from util import *
from const import *

class Bot:
    def __init__(self, position, angle):
        #to do
        self.bot_ip = '10.42.0.202'
        self.position = position #bot center point
        self.angle = angle
        self.direction = 'stop'
        self.speed = 8
        self.command = {
            'direction' : None,
            'interval': None, 
            'time_of_command': None
        }

    def updatePosition(self, position, angle):
        self.position = position
        self.angle = angle

    def move(self, movement, interval):
        res = requests.get(f"http://{self.bot_ip}/{movement}", params={"delay": interval})
        print(res.status_code)

    def makeCommand(self, x, y):
        rotation_time_ms, rotation_direction, travel_direction, travel_time_ms = self.calculateMovement(self.position, self.angle, (x, y))
        self.move(rotation_direction, rotation_time_ms)
        self.move(travel_direction, travel_time_ms)

    def calculateMovement(bot_position, bot_angle, target_point):
        # Calculate distance and angle to target
        distance_to_target = calculate_distance(bot_position, target_point)
        angle_to_target = calculate_angle_to_point(bot_position, target_point)
        
        # Calculate rotation and travel directions
        rotation_needed = (angle_to_target - bot_angle) % 360
        if rotation_needed < 90:
            rotation_direction = "Right"
            travel_direction = "Forward"
        elif rotation_needed > 90 and rotation_needed < 180:
            rotation_direction = "Left"
            travel_direction = "Backward"
        elif rotation_needed > 180 and rotation_needed < 270:
            rotation_direction = "Right"
            travel_direction = "Backward"
        else:
            rotation_direction = "Left"
            travel_direction = "Forward"

        # Calculate rotation and travel time
        rotation_time_ms = abs(rotation_needed) * ROTATION_TIME_PER_DEGREE
        travel_time_ms = distance_to_target / FRONT_TRAVEL_PIXELS_PER_MS if travel_direction == "Forward" else distance_to_target / BACK_TRAVEL_PIXELS_PER_MS
        
        # Display the movement steps
        print(f"Rotation needed: {rotation_needed:.2f} degrees ({rotation_direction}), Time: {rotation_time_ms:.2f} ms")
        print(f"Move {travel_direction} to target, Distance: {distance_to_target:.2f} pixels, Time: {travel_time_ms:.2f} ms")

        return rotation_time_ms, rotation_direction, travel_direction, travel_time_ms

        


