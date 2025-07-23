import cv2
import numpy as np
from tqdm import tqdm  # İlerleme çubuğu için
from Converter import ImageCreator
from Run import ProcessFrame

def draw_objects_on_frame(frame, objects_dict):
    """
    Verilen bir kare (frame) üzerine, objects sözlüğündeki tüm nesneleri
    sınırlayıcı kutu ve ID'leri ile birlikte çizer.
    (Bu fonksiyon değiştirilmedi)
    """
    h, w, _ = frame.shape
    for obj_id, obj_instance in objects_dict.items():
        try:
            bbox = obj_instance.get_box()[-1] 
            x_center, y_center, box_w, box_h = bbox
            x_min = int((x_center - box_w / 2) * w)
            y_min = int((y_center - box_h / 2) * h)
            x_max = int((x_center + box_w / 2) * w)
            y_max = int((y_center + box_h / 2) * h)
            
            color = (255, 0, 0) # Mavi
            thickness = 2
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
            
            label = f"ID: {obj_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            font_color = (255, 255, 255) # Beyaz
            font_thickness = 2
            
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            cv2.rectangle(frame, (x_min, y_min - text_h - 5), (x_min + text_w, y_min - 5), color, -1)
            cv2.putText(frame, label, (x_min, y_min - 5), font, font_scale, font_color, font_thickness)
        except (IndexError, AttributeError) as e:
            # print(f"Uyarı: Nesne ID {obj_id} için kutu çizilemedi. Hata: {e}")
            continue
            
    return frame


def main():
    # --- Ayarlar ---
    image_creator = ImageCreator()
    time_series = 30
    video_path = "senaryo_48.mp4"
    output_video_path = "output_tracked_video.mp4"

    # --- Video İşleme Öncesi Hazırlık ---
    print(f"Orijinal video karelere ayrılıyor: {video_path}")
    image_creator.split_frames(video_path)
    
    process_frame_handler = ProcessFrame(image_creator.image_folder_path, time_series)
    
    # Orijinal video hakkında bilgi al (boyut, FPS)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Hata: Orijinal video dosyası açılamadı: {video_path}")
        return
        
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # --- Çıktı Videosu Yazıcısını Oluşturma ---
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    if not video_writer.isOpened():
        print(f"Hata: Video yazıcı oluşturulamadı: {output_video_path}")
        return

    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    # --- Ana İşleme Döngüsü ---
    for _ in tqdm(range(total_frames), desc="Video İşleniyor"):
        processed_data = process_frame_handler.process_frame()

        if not processed_data:
            break

        frame_idx = processed_data
        objects = process_frame_handler.get_objects()
        
        current_frame_path = f"{image_creator.image_folder_path}/frame_{frame_idx}.jpg"
        frame_to_write = cv2.imread(current_frame_path)

        if frame_to_write is None:
            continue

        display_frame = draw_objects_on_frame(frame_to_write, objects)

        video_writer.write(display_frame)

    # --- Kapanış ---
    video_writer.release()
    print(f"\nİşlem tamamlandı. Sonuç videosu '{output_video_path}' olarak kaydedildi.")


# Programı çalıştırmak için
if __name__ == '__main__':
    main()