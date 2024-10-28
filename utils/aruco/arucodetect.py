import cv2
import numpy as np # Import Numpy library

size_of_marker = 400  # size of marker. 

def detectarucomarker(frame):
    arucoType = cv2.aruco.DICT_4X4_100
    dictionary = cv2.aruco.getPredefinedDictionary(arucoType)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    # Initialize an empty dictionary to store IDs and their corresponding corners
    markers_dict = {}

    try:
        # Detect markers
        corners, ids, rejected = detector.detectMarkers(frame)

        # Draw detected markers on the frame (optional)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Loop through each detected marker and add its ID and corners to the dictionary
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                # Convert corners to a simple list of integer tuples
                processed_corners = [tuple(map(int, corner)) for corner in corners[i][0]]
                markers_dict[marker_id] = processed_corners
        
        return markers_dict

    except Exception as e:
        print(f"Error detecting markers: {e}")
        return {}

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    frame_rate = 1
    image_path = 'output_images/output_image33.jpg'
    while True:
        success, img = cap.read()
        # img=cv2.imread(image_path)
        skip_rate = 1
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        if frame_rate % skip_rate == 0:    

            corners = detectarucomarker(img)
            corners = corners[69]
            print(corners)
        if corners:
            ppcm = 5
            radius = int(1 * ppcm)
            print(corners[0][0])
            cv2.circle(img,corners[0], radius, (255,0,255), 2)
            cv2.circle(img,corners[1], radius, (0,255,255), 2)
            cv2.circle(img,corners[2], radius, (0,0,255), 2)
            cv2.circle(img,corners[3], radius, (255,0,0), 2)
        frame_rate += 1

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
