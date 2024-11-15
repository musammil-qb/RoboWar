import cv2
import time


stream_url = 'http://10.42.0.66:8080/video'


import cv2
import time
import threading


class VideoStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.latest_frame = None
        self.stopped = False
        self.fps = 0  # FPS counter

        # Start the thread to read frames
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
    
    def update(self):
        frame_count = 0
        start_time = time.time()
        
        while not self.stopped:
            if self.cap.isOpened():
                # Grab and retrieve the latest frame
                ret, frame = self.cap.read()
                if ret:
                    self.latest_frame = frame
                    frame_count += 1
                    
                    # Calculate and print FPS every second
                    if time.time() - start_time >= 1:
                        self.fps = frame_count
                        print("FPS:", self.fps)
                        frame_count = 0
                        start_time = time.time()
                else:
                    print("Failed to grab frame.")
                    self.stop()
                    break
            else:
                print("Failed to open video stream.")
                self.stop()
                break
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def read(self):
        # Return the latest frame
        return self.latest_frame

    def stop(self):
        # Stop the video stream
        self.stopped = True
        self.thread.join()
        self.cap.release()


if __name__ == "__main__":  
    # Initialize the video stream
    video_stream = VideoStream(stream_url)
    # get the first frame
    while True:
        frame = video_stream.read()
        if frame is not None:
            break

    # Display the first frame
    cv2.imshow("Live Stream", frame)
    print("Displayed a new frame at:", time.strftime("%H:%M:%S"))
    while True:
        # Request the latest frame from the video stream
        
        key_press = cv2.waitKey(1) & 0xFF
        key_press = ord('d')
        # Break on 'q' key press
        if key_press == ord('q'):
            break
        elif key_press == ord('d'):
            # read a new frame
            frame = video_stream.read()
            if frame is not None:
                # Display the frame
                cv2.imshow("Live Stream", frame)
                
                # Print the time for display
                print("Displayed a new frame at:", time.strftime("%H:%M:%S"))

    # Stop the video stream and close windows
    video_stream.stop()
    cv2.destroyAllWindows()
