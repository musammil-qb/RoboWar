from ultralytics import YOLO
import os, sys
import math
import cv2

model = YOLO("best.pt")

image = cv2.imread(sys.argv[1])

result = model.predict(image, conf=0.5)

def getnearestball(balls, bot_pos):
    # Calculate the distance of each point in 'points' to the reference point
    closest = min(balls, key=lambda ball: math.sqrt((ball[0] - bot_pos[0])**2 + (ball[1] - bot_pos[1])**2))
    return closest

def detectarucomarker(frame):
    arucoType = cv2.aruco.DICT_4X4_100
    dictionary = cv2.aruco.getPredefinedDictionary(arucoType)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    corners, ids, rejected = detector.detectMarkers(frame)

    if int(ids) == 69:
        return
        
balls = []
bot_pos =  None
for r in result:
    boxes = r.boxes

    for box in boxes:
        if int(box.cls[0]) == 0: # Detect balls
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            center_point_ball = (int((x1+x2)/2), int((y1+y2)/2))

            ppcm = 50
            radius = int(1 * ppcm)

            # cv2.circle(image,center_point_ball, radius, (255,0,255), 4)

            balls.append(center_point_ball)
            
            # cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
            # cv2.circle(image, (x1, y1), 5,(255,0,255), 2)
            # cv2.circle(image, (x2, y2), 5, (0,25,0), 2)
        
        if int(box.cls[0]) == 1: # Detect bot
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            center_point_bot = (int((x1+x2)/2), int((y1+y2)/2))

            bot_pos = center_point_bot

            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        

nearestball = getnearestball(balls, bot_pos)

cv2.circle(image, nearestball, radius, (255,0,255), 4)
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()