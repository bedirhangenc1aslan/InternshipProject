import cv2
import numpy as np
from tqdm import tqdm
import traceback  # <-- YENİ: Hatanın detayını yazdırmak için

from Converter import ImageCreator
from Run import ProcessFrame

# main.py

import cv2
import numpy as np
# ... diğer importlar ...

def draw_objects_on_frame(frame, objects_dict):
    h, w, _ = frame.shape
    for obj_id, obj_instance in objects_dict.items():
        try:
            bbox = obj_instance.get_box()[-1]
            
            # --- YENİ EKLENEN KONTROL ---
            # bbox'un içinde gerçekten 4 eleman olup olmadığını kontrol et. Değilse, bu nesneyi atla.
            if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
                # print(f"Uyarı: Nesne ID {obj_id} için geçersiz bbox formatı. Atlanıyor. Gelen veri: {bbox}")
                continue
            # --- KONTROL SONU ---

            # Artık bbox'un (x, y, w, h) formatında olduğundan eminiz.
            x_center, y_center, box_w, box_h = bbox
            
            # Geri kalan kodunuz aynı...
            x_min = int((x_center - box_w / 2) * w)
            y_min = int((y_center - box_h / 2) * h)
            x_max = int((x_center + box_w / 2) * w)
            y_max = int((y_center + box_h / 2) * h)
            
            color = (255, 0, 0)
            thickness = 2
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
            
            label = f"ID: {obj_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            font_color = (255, 255, 255)
            font_thickness = 2
            
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            cv2.rectangle(frame, (x_min, y_min - text_h - 5), (x_min + text_w, y_min - 5), color, -1)
            cv2.putText(frame, label, (x_min, y_min - 5), font, font_scale, font_color, font_thickness)
            
        except (IndexError, AttributeError) as e:
            # Bu except bloğu, get_box() hiç liste döndürmezse diye kalabilir.
            continue
            
    return frame


def main():
    # --- Ayarlarınız olduğu gibi kalıyor ---
    image_creator = ImageCreator()
    time_series = 30
    video_path = "senaryo_48.mp4"
    output_video_path = "output_tracked_video.mp4"

    # --- Video İşleme Öncesi Hazırlık (Sizin Mantığınızla) ---
    print(f"Orijinal video karelere ayrılıyor: {video_path}")
    image_creator.split_frames(video_path)
    
    process_frame_handler = ProcessFrame(image_creator.image_folder_path, time_series)
    
    # --- Video ve Yazıcı Bilgileri (Sizin Mantığınızla) ---
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Hata: Orijinal video dosyası açılamadı: {video_path}")
        return
        
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    if not video_writer.isOpened():
        print(f"Hata: Video yazıcı oluşturulamadı: {output_video_path}")
        return

    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    # --- Ana İşleme Döngüsü ---
    # <<< YENİ: Hata yakalama için 'try' bloğu ekleniyor >>>
    try:
        for i in tqdm(range(total_frames), desc="Video İşleniyor"):
            # SİZİN KODUNUZUN ÇEKİRDEĞİ BURADA
            processed_data = process_frame_handler.process_frame()
            
            # Eğer process_frame bir şey döndürmezse döngüden çık (mevcut mantık)
            if not processed_data:
                print(f"Bilgi: {i}. karede process_frame() bir sonuç döndürmedi. İşlem durduruluyor.")
                break

            frame_idx = processed_data
            objects = process_frame_handler.get_objects()
            
            # Diskteki ilgili kare dosyasını oku
            current_frame_path = f"{image_creator.image_folder_path}/frame_{int(frame_idx):05d}.jpg"
            frame_to_write = cv2.imread(current_frame_path)

            # Eğer dosya okunamadıysa (silinmiş, bozuk vb.), bu adımı atla
            if frame_to_write is None:
                print(f"Uyarı: {current_frame_path} dosyası okunamadı veya bulunamadı. Bu kare atlanıyor.")
                continue

            # Nesneleri çiz ve videoya yaz
            display_frame = draw_objects_on_frame(frame_to_write, objects)
            video_writer.write(display_frame)

    # <<< YENİ: Hata yakalama için 'except' bloğu >>>
    except Exception as e:
        print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! PROGRAM BİR HATA NEDENİYLE ANİDEN DURDU !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        print(f"Hatanın Tipi: {type(e).__name__}")
        print(f"Hata Mesajı: {e}\n")
        print("--- Hatanın Oluştuğu Kod Satırı (Traceback) ---")
        traceback.print_exc() # Hatanın tam olarak nerede ve nasıl olduğunu gösterir
        print("---------------------------------------------")
        print("\nHatanın kaynağını bulmak için yukarıdaki traceback'i inceleyin.")

    # <<< YENİ: Hata olsa da olmasa da çalışacak 'finally' bloğu >>>
    finally:
        # --- Kapanış ---
        video_writer.release()
        print(f"\nİşlem tamamlandı veya bir hata ile sonlandı. Sonuç videosu '{output_video_path}' olarak kaydedildi.")


if __name__ == '__main__':
    main()