import cv2
import numpy as np

# Define checkerboard dimensions (adjust based on your printout)
chessboard_size = (9, 6) 
# Arrays to store object points and image points
objpoints = []
imgpoints = []

# Function to detect checkerboard corners in an image
def find_checkerboard_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    return ret, corners

# Specify webcam number
cap = cv2.VideoCapture(0)

# Define termination criteria for calibration
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

# Capture frames until 'q' key is pressed
while True:
    ret, frame = cap.read()
    ret, corners = find_checkerboard_corners(frame)

    # If corners found, draw on frame and add points
    if ret:
        cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
        objpoints.append(objp)
        imgpoints.append(corners)

    # Display the frame with corners (optional)
    cv2.imshow('Calibration', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("exit")
        break

# Release capture and close windows
cap.release()
cv2.destroyAllWindows()

# Calibrate the camera
print("calibration start")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame.shape[:2], None, None)

# Print calibration results
if ret:
    print("Calibration successful!")
    print("Camera matrix:")
    print(mtx)
    print("Distortion coefficients:")
    print(dist)
else:
    print("Calibration failed!")