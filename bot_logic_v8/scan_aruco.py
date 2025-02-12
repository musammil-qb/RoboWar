import cv2
from detection import Detection
import numpy as np
from const import *

# Define triangle_side constant
triangle_side = 30  # You can adjust this value to change the triangle size

detection = Detection()
while True:
    # List all available ArUco dictionaries
    aruco_dictionaries = [name for name in dir(cv2.aruco) if name.startswith("DICT_")]

    # Initialize a dictionary to store matches
    matched_dictionaries = {}

    frame = detection.video_stream.read()

    # Iterate over all ArUco dictionaries
    for aruco_dict_name in aruco_dictionaries:
        try:
            # Get the dictionary object
            aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, aruco_dict_name))
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            
            # Detect markers using this dictionary
            corners, ids, _ = detector.detectMarkers(frame)
            
            # If markers are detected, store the dictionary name and IDs
            if ids is not None:
                matched_dictionaries[aruco_dict_name] = ids.flatten().tolist()
                
                # Draw detected markers
                for corner, marker_id in zip(corners, ids.flatten()):
                    # Reshape corner to a 4x2 array
                    corner = corner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corner
                    
                    # Convert each corner coordinate to integer
                    topLeft = tuple(map(int, topLeft))
                    topRight = tuple(map(int, topRight))
                    bottomRight = tuple(map(int, bottomRight))
                    bottomLeft = tuple(map(int, bottomLeft))
                    
                    # Draw the ArUco border
                    cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    
                    # Calculate the center for the label
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    
                    # Put the label near the center
                    label = f"{aruco_dict_name}: {marker_id}"
                    # Position label above the marker box with some padding
                    label_position = (cX - 50, topLeft[1] - 20)
                    cv2.putText(frame, label, label_position,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 2)
                    
                    # Draw a triangle on one side for face detection
                    # Calculate the midpoint between topLeft and topRight
                    midpoint_x = int((topLeft[0] + topRight[0]) / 2)
                    midpoint_y = int((topLeft[1] + topRight[1]) / 2)
                    
                    # Calculate the direction vector from the center to the midpoint (reversed from before)
                    direction_x = midpoint_x - cX
                    direction_y = midpoint_y - cY
                    
                    # Normalize and scale the direction vector
                    length = np.sqrt(direction_x**2 + direction_y**2)
                    if length > 0:
                        direction_x = direction_x / length * triangle_side
                        direction_y = direction_y / length * triangle_side
                    
                    # Calculate the third point of the triangle (pointing outward)
                    pt3 = (midpoint_x + int(direction_x), midpoint_y + int(direction_y))
                    pts = np.array([topLeft, topRight, pt3], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                    
        except Exception as e:
            print(f"Error with dictionary {aruco_dict_name}: {e}")

    # Print results
    if matched_dictionaries:
        print("Matched Dictionaries and IDs:")
        for dict_name, ids in matched_dictionaries.items():
            print(f"Dictionary: {dict_name}, IDs: {ids}")
    else:
        print("No matches found in any dictionaries.")

    # Display the frame with annotations
    cv2.imshow('ArUco Detection', frame)
    if  cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
