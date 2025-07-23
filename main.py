# main.py dosyanızın tamamı

import cv2
from tqdm import tqdm
from Converter import ImageCreator
from Initialize import Initialize
from Run import ProcessFrame

def draw_objects_on_frame(frame, objects_dict):
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

def main():
    video_path = "/home/nyenice/Desktop/Project Hiearchy/senaryo_48.mp4"
    output_video_path = "output_tracked_video.avi"
    time_series = 30
    image_creator = ImageCreator()

    image_creator.split_frames(video_path)
    
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))


    initialize = Initialize(time_series=time_series)
    process_frame_handler = ProcessFrame(video_path , time_series , initialize)
    
    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    # --- Ana İşleme Döngüsü (Orijinal haliyle) ---
    for _ in tqdm(range(total_frames), desc="Video İşleniyor"):
        # `process_frame` her çağrıldığında bir sonraki kareyi işler ve nesneleri günceller.
        processed_data = process_frame_handler.process_frame()
        
        if processed_data is None: # Video bitti
            break

        frame_idx = processed_data
        
        # Güncellenmiş nesneleri al
        objects = process_frame_handler.get_objects()
        
        # İlgili kareyi diskten oku
        current_frame_path = f"{image_creator.image_folder_path}/frame_{int(frame_idx):05d}.jpg"
        frame_to_write = cv2.imread(current_frame_path)

        if frame_to_write is None:
            continue

        # Güncel nesneleri kare üzerine çiz
        display_frame = draw_objects_on_frame(frame_to_write, objects)
        video_writer.write(display_frame)

    # --- Kapanış ---
    video_writer.release()
    print(f"\nİşlem tamamlandı. Sonuç videosu '{output_video_path}' olarak kaydedildi.")

if __name__ == '__main__':
    main()