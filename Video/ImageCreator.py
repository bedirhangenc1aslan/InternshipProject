import cv2
import os
class ImageCreator:
    def __init__(self):
        self.image_folder_path = 'frames/'
    def split_frames(self , VIDEO_PATH):
        output_folder = self.image_folder_path
        os.makedirs(output_folder, exist_ok=True)
        cap = cv2.VideoCapture(VIDEO_PATH)
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_filename = os.path.join(output_folder, f"frame_{frame_count:05d}.jpg")
            cv2.imwrite(frame_filename, frame)

            frame_count += 1

        cap.release()