import cv2

from video import resize_to_max_dimensions

def save_or_show_image(cap):
    image_no = 0
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        success, frame = cap.read()
        if not success:
            break  # Exit if the video feed is not available
        resized_frame = resize_to_max_dimensions(original_width, original_height,1500,800,frame=frame)
        cv2.imshow('Webcam', resized_frame)
        pressed_key = cv2.waitKey(1)
        
        if pressed_key == ord('s'):
            # Save the current frame
            cv2.imwrite('output_image' + str(image_no) + '.jpg', frame)
            print(f"Image saved as output_image{image_no}.jpg")
            image_no += 1
        elif pressed_key == ord('q'):
            # Quit if 'q' is pressed
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    # cap = cv2.VideoCapture("http://192.168.90.87:8080/video")
    cap = cv2.VideoCapture('Data/green_arena/20241023_162704.mp4' )
    cap.set(3, 640)
    cap.set(4, 480)
    save_or_show_image(cap)