import cv2
import time


cam_ip = 'http://10.7.110.35:8080/video'


import cv2
import time
import threading

class VideoStream:
    def __init__(self, url):
        
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.latest_frame = None
        self.stopped = False
        # Start the thread to read frames
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
        print("Video stream started.")
    
    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                # Grab and retrieve the latest frame
                ret, frame = self.cap.read()
                if ret:
                    self.latest_frame = frame
                else:
                    print("Failed to grab frame.")
                    self.stop()
                    break
            else:
                print("Failed to open video stream.")
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    def read(self):
        # Return the latest frame
        return self.latest_frame

    def stop(self):
        # Stop the video stream
        self.stopped = True
        self.thread.join()
        self.cap.release()


# URL of the video stream
stream_url = cam_ip

# Initialize the video stream
video_stream = VideoStream(stream_url)

while True:
    # Request the latest frame from the video stream
    frame = video_stream.read()
    
    if frame is not None:
        # Display the frame
        cv2.imshow("Live Stream", frame)
        
        # Print the time for display
        print("Displayed a new frame at:", time.strftime("%H:%M:%S"))
    
    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # Simulate a processing delay (e.g., 1 second)
    time.sleep(5)

# Stop the video stream and close windows
video_stream.stop()
cv2.destroyAllWindows()
