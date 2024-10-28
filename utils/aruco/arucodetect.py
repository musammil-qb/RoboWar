import cv2
import numpy as np # Import Numpy library

size_of_marker = 400  # size of marker. 

def detectarucomarker(frame):
    arucoType = cv2.aruco.DICT_4X4_100                                                                                                                                                                             
    dictionary = cv2.aruco.getPredefinedDictionary(arucoType)                                                                                                                                                      
    parameters = cv2.aruco.DetectorParameters()                                                                                                                                                                    
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)   
    try:                                                                                                                                                  
        corners, ids, rejected = detector.detectMarkers(frame)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        corners=corners[0].tolist()
        print(corners[0])
        print(type(corners[0]))

        # if int(ids) == 69:
        #     # Estimate pose of each marker
        #     # print(corners)
        # rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
        # print(rvecs, tvecs)
        processed_corners =  list(map(lambda row: tuple(map(int, row)), corners[0]))
        return processed_corners

    except:
        return

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
frame_rate = 1

while True:
    success, img = cap.read()
    skip_rate = 1
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    if frame_rate % skip_rate == 0:    

        corners = detectarucomarker(img)
        print(corners)
    if corners:
        ppcm = 50
        radius = int(1 * ppcm)
        print(corners[0][0])
        # cv2.circle(img,corners[0], radius, (255,0,255), 2)
        # cv2.circle(img,corners[1], radius, (0,255,255), 2)
        cv2.circle(img,corners[2], radius, (0,0,255), 2)
        # cv2.circle(img,corners[3], radius, (255,0,0), 2)
    frame_rate += 1

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()