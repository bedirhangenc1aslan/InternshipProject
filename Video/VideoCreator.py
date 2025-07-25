import cv2


class VideoCreator:
    def __init__(self , VIDEO_PATH , OUPUT_PATH , image_creator):
        self.video_path = VIDEO_PATH
        self.output_path = OUPUT_PATH
        self.image_creator = image_creator
        cap = cv2.VideoCapture(self.video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(OUPUT_PATH, fourcc, fps, (frame_width, frame_height))

    def add_frame_to_video(self , frame_idx, objects , frame = None):
        frame_to_write = frame
        if frame is None:
            current_frame_path = f"{self.image_creator.image_folder_path}/frame_{int(frame_idx):05d}.jpg"
            frame_to_write = cv2.imread(current_frame_path)

        if frame_to_write is None:
            return

        # Güncel nesneleri kare üzerine çiz
        display_frame = self.__draw_objects_on_frame__(frame_to_write, objects)
        self.video_writer.write(display_frame)

    def __draw_objects_on_frame__(self ,frame, objects_dict):
        h, w, _ = frame.shape
        for obj_id, obj_instance in objects_dict.items():
            try:
                bbox = obj_instance.get_box()
                if not bbox: continue
                x_center, y_center, box_w, box_h = bbox
                x_min = int(x_center - box_w / 2)
                y_min = int(y_center - box_h / 2)
                x_max = int(x_center + box_w / 2)
                y_max = int(y_center + box_h / 2)
                
                # Varsayım 2: [x_min, y_min, x_max, y_max] dönüyorsa
                # x_min, y_min, x_max, y_max = map(int, bbox)

                # Çizim işlemleri
                color = (0, 255, 0)
                thickness = 2
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
                
                label = f"ID: {obj_id}"
                # ... geri kalan çizim kodları ...
                cv2.putText(frame, label, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            except Exception:
                continue
                
        return frame
    def release_video(self):
        self.video_writer.release()
        print(f"\nİşlem tamamlandı. Sonuç videosu '{self.output_path}' olarak kaydedildi.")
    def get_total_frames(self):
        return self.total_frames