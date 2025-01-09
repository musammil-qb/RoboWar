

import cv2
from detection import Detection



detection = Detection()
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
    except Exception as e:
        print(f"Error with dictionary {aruco_dict_name}: {e}")

# Print results
if matched_dictionaries:
    print("Matched Dictionaries and IDs:")
    for dict_name, ids in matched_dictionaries.items():
        print(f"Dictionary: {dict_name}, IDs: {ids}")
else:
    print("No matches found in any dictionaries.")