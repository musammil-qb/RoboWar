import cv2
import numpy as np
import sys

from aruco.arucodetect import detectarucomarker
from yolo.findall import findall
import math

def getnearestball(balls, bot_pos):
    # Calculate the distance of each point in 'points' to the reference point
    closest = min(balls, key=lambda ball: math.sqrt((ball[0] - bot_pos[0])**2 + (ball[1] - bot_pos[1])**2))
    return closest

def calculate_angle(p1, p2):
    # Convert points to numpy arrays if they aren't already
    point1 = np.array(p1, dtype=np.float32)
    point2 = np.array(p2, dtype=np.float32)
    
    # Calculate the angle in radians
    angle_radians = np.arctan2(point2[1] - point1[1], point2[0] - point1[0])
    
    # Convert angle to degrees
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees

def process_frame(frame):
    corners = detectarucomarker(frame)
    bot_corners = corners[69]
    post_corners = corners[92]
    x_total_bot = 0
    y_total_bot = 0
    x_total_post = 0
    y_total_post = 0

    for i in range(4):
        x_total_bot += bot_corners[i][0]
        y_total_bot += bot_corners[i][1]
        x_total_post += post_corners[i][0]
        y_total_post += post_corners[i][1]

    
    bot_mid_point = (int(x_total_bot/4), int(y_total_bot/4))
    post_mid_point = (int(x_total_post/4), int(y_total_post/4))

    findvirtualpoint(frame, bot_mid_point, post_mid_point)

    for i in range(4):
        p1 = bot_corners[i]
        p2 = bot_corners[(i + 1) % 4]
        color = (0, 255, 0) if i == 0 else (0, 0, 255) if i == 1 else (255, 0, 0) if i == 2 else (255, 255, 0)
        cv2.line(frame, tuple(p1), tuple(p2), color, 2)

        if i == 0:
            # Define the points of the triangle
            p3 = bot_corners[2]
            point1 = np.array([p1[0], p1[1]], dtype=np.float32)
            point2 = np.array([p2[0], p2[1]], dtype=np.float32)
            point3 = np.array([p3[0], p3[1]], dtype=np.float32)

            # Calculate midpoint and perpendicular direction
            midpoint = (point1 + point2) / 2
            direction = point2 - point1
            perpendicular_direction = np.array([-direction[1], direction[0]])
            perpendicular_direction = perpendicular_direction / np.linalg.norm(perpendicular_direction)

            # Determine if p3 is in the same direction as perpendicular vector
            vector_to_p3 = point3 - midpoint
            if np.dot(vector_to_p3, perpendicular_direction) > 0:
                d = -50  # Move away from p3
            else:
                d = 50  # Move towards the opposite side of p3

            # Calculate the new perpendicular point for the triangle
            perpendicular_point = midpoint + d * perpendicular_direction
            triangle_points = np.array([
                p1,
                p2,
                perpendicular_point
            ], dtype=np.int32)
            
            cv2.drawContours(frame, [triangle_points], 0, color, -1)
            angle = calculate_angle(p1, p2)
            print(angle)

    return frame

def findvirtualpoint(frame, bot_pos, post_pos):
    balls, _, _ = findall(frame)

    extension_factor=0.2

    closest_ball = getnearestball(balls, bot_pos)
    print(closest_ball, post_pos)
    dx = closest_ball[0] - post_pos[0]
    dy = closest_ball[1] - post_pos[1]

    x_extended = closest_ball[0] + extension_factor * dx
    y_extended = closest_ball[1] + extension_factor * dy

    cv2.line(frame, (int(x_extended),int(y_extended)), post_pos, (0,255,0), 2)

    return x_extended, y_extended


if __name__ == "__main__":
    image_path =  sys.argv[1]   
    if not image_path:
        image_path='output_images/output_image40.jpg'
    cap = cv2.imread(image_path)
    frame=process_frame(cap)
    cv2.imshow("Frame", frame)
    # cv2.imwrite('save_image4.jpg', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()