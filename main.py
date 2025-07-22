import cv2
import numpy as np
from Converter import ImageCreator
from Run import ProcessFrame

def draw_objects_on_frame(frame, objects_dict):
    """
    Verilen bir kare (frame) üzerine, objects sözlüğündeki tüm nesneleri
    sınırlayıcı kutu ve ID'leri ile birlikte çizer.
    
    Args:
        frame (np.ndarray): Üzerine çizim yapılacak olan görüntü (OpenCV formatında).
        objects_dict (dict): ID'lerin nesne örneklerine map'lendiği sözlük.
    
    Returns:
        np.ndarray: Üzerine çizim yapılmış olan görüntü.
    """
    # Görüntünün boyutlarını al
    h, w, _ = frame.shape

    # Nesneler sözlüğündeki her bir nesne için döngüye gir
    for obj_id, obj_instance in objects_dict.items():
        # Nesnenin en son sınırlayıcı kutusunu al
        # Nesne sınıflarınızda 'get_last_box' gibi bir metod olduğunu varsayıyoruz.
        # Eğer yoksa, 'get_box()'[-1] gibi bir yapı kullanabilirsiniz.
        try:
            # Varsayım: Nesne sınıfınızın en son kutuyu veren bir metodu var.
            # get_box() tüm geçmişi veriyorsa, sonuncusunu alın.
            bbox = obj_instance.get_box()[-1] 
            
            # Kutu formatı [x_center, y_center, width, height] (normalize) ise
            # OpenCV'nin istediği [x_min, y_min, x_max, y_max] (pixel) formatına çevir
            x_center, y_center, box_w, box_h = bbox
            x_min = int((x_center - box_w / 2) * w)
            y_min = int((y_center - box_h / 2) * h)
            x_max = int((x_center + box_w / 2) * w)
            y_max = int((y_center + box_h / 2) * h)
            
            # Kutuyu çiz
            # Renk (B, G, R formatında) ve kalınlık belirle
            color = (255, 0, 0) # Mavi renk
            thickness = 2
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
            
            # ID'yi kutunun yakınına yazdır
            label = f"ID: {obj_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            font_color = (255, 255, 255) # Beyaz renk
            font_thickness = 2
            
            # Metin için bir arka plan kutusu çiz (daha okunaklı olması için)
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            cv2.rectangle(frame, (x_min, y_min - text_h - 5), (x_min + text_w, y_min - 5), color, -1)
            cv2.putText(frame, label, (x_min, y_min - 5), font, font_scale, font_color, font_thickness)

        except (IndexError, AttributeError) as e:
            # Nesnenin henüz bir kutusu yoksa veya metod bulunamazsa atla
            print(f"Uyarı: Nesne ID {obj_id} için kutu çizilemedi. Hata: {e}")
            continue
            
    return frame


def main():
    image_creator = ImageCreator()
    time_series = 30
    video_path = "senaryo_48.mp4"
    image_creator.split_frames(video_path)
    
    process_frame = ProcessFrame(image_creator.image_folder_path, time_series)
    
    # Video hakkında bilgi almak için (kare boyutu vb.)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Hata: Video dosyası açılamadı.")
        return

    # Görselleştirme penceresi oluştur
    cv2.namedWindow("Nesne Takibi", cv2.WINDOW_NORMAL)

    while True:
        # Sonraki kareyi işle
        processed_data = process_frame.process_frame()

        # Eğer process_frame False veya None dönerse döngüyü kır
        if not processed_data:
            print("Video işleme tamamlandı veya bir hata oluştu.")
            break

        # İşlenen karenin ID'sini ve nesneleri al
        frame_idx = processed_data
        objects = process_frame.get_objects() # Bu, ID -> nesne_instance sözlüğünü döndürür
        
        # O anki orijinal kareyi diskten oku
        current_frame_path = f"{image_creator.image_folder_path}/frame_{frame_idx}.jpg"
        frame_to_display = cv2.imread(current_frame_path)

        if frame_to_display is None:
            print(f"Uyarı: {current_frame_path} okunamadı.")
            continue

        # Nesneleri karenin üzerine çiz
        display_frame = draw_objects_on_frame(frame_to_display, objects)

        # Sonucu ekranda göster
        cv2.imshow("Nesne Takibi", display_frame)

        # 'q' tuşuna basılırsa döngüden çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kapanış işlemleri
    cap.release()
    cv2.destroyAllWindows()
    print("Program sonlandırıldı.")

# Programı çalıştırmak için
if __name__ == '__main__':
    main()