from utils import calculate_distance, calculate_angle_to_point
from bot_logic_v1.bot import makeMovement
from detection import process_frame

def calliberate(self):
    caliberation_speed = {}
    caliberation_speed['forward'] = self.caliberateMovement('forward', 500)
    caliberation_speed['backward'] = self.caliberateMovement('backward', 500)
    caliberation_speed['right'] = self.caliberateMovement('right', 100)
    caliberation_speed['left'] = self.caliberateMovement('left', 100)

    return caliberation_speed

def caliberateMovement(self, direction, interval):
    if direction == 'forward' or direction == 'backward':
        initial_position = getPositionAndAngle()[0]
        makeMovement(direction, interval)
        final_position = getPositionAndAngle()[0]
        return calculate_distance(initial_position, final_position) / interval
    else:
        initial_angle = getPositionAndAngle()[1]
        makeMovement(direction, interval)
        final_angle = getPositionAndAngle()[1]
        return calculate_angle_to_point(initial_angle, final_angle) / interval


def getPositionAndAngle(self):
    detection_object = process_frame()
    return detection_object['aruco']['bot_center_point'], detection_object['aruco']['bot_angle']
