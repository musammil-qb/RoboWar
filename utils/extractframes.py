import cv2
import os

def extract_frames(video_path, output_folder, frame_count):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Check if video file opened successfully
    if not video.isOpened():
        print("Error: Could not open video.")
        return
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    while True:
        # Read frame-by-frame
        ret, frame = video.read()
        
        # If there are no more frames, break the loop
        if not ret:
            break
        
        # Save frame as a file
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.png")
        cv2.imwrite(frame_filename, frame)
        
        print(f"Saved: {frame_filename}")
        frame_count += 1
    
    # Release the video capture object
    video.release()
    print("Frame extraction completed.")
    return frame_count

# Example usage\
Video_arr = ["PXL_20241010_123010396.mp4","PXL_20241010_123628133.mp4","PXL_20241010_124023491.mp4","PXL_20241010_124323369.mp4","PXL_20241010_124816944.mp4","PXL_20241010_125020727-001.mp4"]
video_dir = "Data"  # Path to your MP4 video
output_folder = 'extracted_frames'  # Folder where frames will be saved
frame_count = 0
for video in Video_arr:
    video_path = video_dir+"/"+video
    frame_count = extract_frames(video_path, output_folder,frame_count)