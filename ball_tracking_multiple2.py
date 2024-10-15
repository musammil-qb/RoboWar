# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "yellow" ball in the HSV color space
yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)

# Store points for each ball
balls = {}

# if a video path was not supplied, grab the reference to the webcam
if not args.get("video", False):
    vs = cv2.VideoCapture(0)  # Webcam
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    grabbed, frame = vs.read()
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "yellow"
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)

    # perform a series of dilations and erosions to remove any small blobs left in the mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # only proceed if at least one contour was found
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 200:  # Minimum area to consider it as a ball
            continue

        # Compute the bounding box and aspect ratio
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h

        # Check for circularity
        perimeter = cv2.arcLength(c, True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        # Filter based on aspect ratio and circularity to ensure it is a ball
        if 0.9 < aspect_ratio < 1.1 and circularity > 0.8:  # Strict thresholds for round shapes
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # Assign a unique ID for each detected ball
            ball_id = f"ball_{len(balls) + 1}"
            if ball_id not in balls:
                balls[ball_id] = deque(maxlen=args["buffer"])

            # Append the center to the corresponding ball's deque
            balls[ball_id].append(center)

            # Draw the circle and centroid on the frame
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # Draw the tracked paths for each ball
    for ball_id, tracked_points in balls.items():
        for i in range(1, len(tracked_points)):
            if tracked_points[i - 1] is None or tracked_points[i] is None:
                continue

            # Draw the connecting lines for each ball's path
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, tracked_points[i - 1], tracked_points[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
vs.release()

# close all windows
cv2.destroyAllWindows()
