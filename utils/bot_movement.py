import sys
import cv2

from aruco.arucodetect import detectarucomarker
from find_bot import calculate_angle, find_bot, find_distance
from constants import RED, GREEN, BLUE

destination_point = (790, 116)

def move_bot(angle=None,distance=None):
    if angle is not None:
        print("angle")
    if distance is not None:
        print("distance")

def bot_movement(bot_corners,destination_point=destination_point):
    bot_angle, bot_center = find_bot(bot_corners)
    destination_point_angle = calculate_angle(bot_center, destination_point)
    angle_difference = destination_point_angle - bot_angle
    # move_bot(angle =angle_difference)
    distance = find_distance(bot_center, destination_point)
    # move_bot(distance = distance)
    print(bot_angle, destination_point_angle, angle_difference, distance) 
    print(bot_center, destination_point)

def main(frame):
    corners = detectarucomarker(frame)
    bot_movement(corners[69])
    return frame
if __name__ == "__main__":
    image_path =  sys.argv[1] if len(sys.argv) > 1 else None
    if not image_path:
        image_path='output_images/output_image9.jpg'
    cap = cv2.imread(image_path)
    frame = main(cap)
    cv2.line(frame, (100,0), (460,0),RED, -1)
    cv2.circle(frame, destination_point, 5, GREEN, -1)
    cv2.circle(frame, (665,450), 5, BLUE, -1)
    cv2.imshow("Frame", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
