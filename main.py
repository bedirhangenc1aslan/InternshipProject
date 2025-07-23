import cv2
import numpy as np
from tqdm import tqdm

from Converter import ImageCreator
from Run import ProcessFrame

def draw_objects_on_frame(frame, objects_dict):
    h, w, _ = frame.shape
    for obj_id, obj_instance in objects_dict.items():
        try:
            bbox = obj_instance.get_box()[-1]
            if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
                continue

            x_center, y_center, box_w, box_h = bbox
            x_min = int((x_center - box_w / 2) * w)
            y_min = int((y_center - box_h / 2) * h)
            x_max = int((x_center + box_w / 2) * w)
            y_max = int((y_center + box_h / 2) * h)
            
            color = (0, 255, 0) # Parlak Yeşil
            thickness = 2
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
            
            label = f"ID: {obj_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_color = (255, 255, 255)
            font_thickness = 1
            
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            cv2.rectangle(frame, (x_min, y_min - text_h - 5), (x_min + text_w, y_min), color, -1)
            cv2.putText(frame, label, (x_min, y_min - 5), font, font_scale, font_color, font_thickness)
        except (IndexError, AttributeError, TypeError):
            continue
    return frame

def main():
    # --- Ayarlar ---
    image_creator = ImageCreator()
    time_series = 30
    video_path = "senaryo_48.mp4"
    output_video_path = "output_tracked_video.avi"

    # --- Video İşleme Öncesi Hazırlık ---
    print(f"Orijinal video karelere ayrılıyor: {video_path}")
    image_creator.split_frames(video_path)
    
    process_frame_handler = ProcessFrame(image_creator.image_folder_path, time_series)
    
    # --- Video ve Yazıcı Bilgileri ---
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Hata: Orijinal video dosyası açılamadı: {video_path}")
        return
        
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    if not video_writer.isOpened():
        print(f"Hata: Video yazıcı oluşturulamadı: {output_video_path}")
        return

    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    # --- Ana İşleme Döngüsü ---
    # Döngüyü `total_frames` yerine `total_frames - 1` veya daha güvenli bir yapıda kurabiliriz.
    # Ancak asıl sorun `process_frame` den gelen index. Onu kontrol edelim.
    for i in tqdm(range(total_frames), desc="Video İşleniyor"):
        processed_data = process_frame_handler.process_frame()
        
        if not processed_data:
            break

        frame_idx = processed_data
        
        # --- YENİ EKLENEN KONTROL ---
        # Gelen frame_idx'in geçerli bir aralıkta olup olmadığını kontrol et.
        # Eğer video 1000 kare ise, en yüksek index 999 olabilir.
        if frame_idx >= total_frames:
            print(f"Uyarı: Geçersiz kare indeksi ({frame_idx}) alındı. Döngü durduruluyor.")
            break
        # --- KONTROL SONU ---

        objects = process_frame_handler.get_objects()
        
        current_frame_path = f"{image_creator.image_folder_path}/frame_{int(frame_idx):05d}.jpg"
        frame_to_write = cv2.imread(current_frame_path)

        if frame_to_write is None:
            continue

        display_frame = draw_objects_on_frame(frame_to_write, objects)
        video_writer.write(display_frame)

    # --- Kapanış ---
    video_writer.release()
    print(f"\nİşlem tamamlandı. Sonuç videosu '{output_video_path}' olarak kaydedildi.")

if __name__ == '__main__':
    main()