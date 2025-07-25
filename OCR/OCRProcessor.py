import math
import re
import cv2
import easyocr
import numpy as np

class OCRProcessor:
    def __init__(self, languages=['tr', 'en'], use_gpu=True):
        # BU METODDA DEĞİŞİKLİK YOK
        print("OCRProcessor başlatılıyor, EasyOCR modeli yükleniyor...")
        try:
            self.reader = easyocr.Reader(languages, gpu=use_gpu)
            print("EasyOCR modeli başarıyla yüklendi.")
        except Exception as e:
            print(f"HATA: EasyOCR modeli yüklenemedi. Lütfen kurulumu kontrol edin. Hata: {e}")
            self.reader = None

    def process_image(self, objects, image: np.ndarray):
        """
        Her bir nesnenin altındaki belirli bir alanda OCR yapar.
        Kutu formatı işleme mantığı, sağlanan doğru çalışan koda göre güncellenmiştir.
        """
        if self.reader is None:
            print("Uyarı: OCR modeli yüklenemediği için işlem atlanıyor.")
            return image, objects

        processed_image = image.copy()
        h_img, w_img, _ = image.shape

        objects_ = objects.get_objects()
        
        for id, obj in objects_.items():
            # 1. ADIM: Nesnenin Bounding Box'ını al ([x_center, y_center, width, height] formatında)
            obj_bbox_yolo = obj.get_box()
            
            if not obj_bbox_yolo or len(obj_bbox_yolo) != 4:
                continue

            # 2. ADIM: YOLO formatını (x_min, y_min, x_max, y_max) formatına çevir
            # --- BU BÖLÜM SENİN KODUNDAN BİREBİR ALINDI ---
            try:
                x_center, y_center, box_w, box_h = obj_bbox_yolo
                
                # Koordinatları ve boyutları int'e çevirerek daha güvenli hale getir
                x_center, y_center, box_w, box_h = int(x_center), int(y_center), int(box_w), int(box_h)

                ox1 = int(x_center - box_w / 2) # x_min
                oy1 = int(y_center - box_h / 2) # y_min
                ox2 = int(x_center + box_w / 2) # x_max
                oy2 = int(y_center + box_h / 2) # y_max
            except (ValueError, TypeError):
                # Eğer gelen veri float/int'e çevrilemezse, bu nesneyi atla
                continue
            # ------------------------------------------------

            # 3. ADIM: Genişlik ve Yüksekliği KONTROL ET
            # Artık box_w ve box_h doğrudan elimizde olduğu için daha basit
            if box_w <= 0 or box_h <= 0:
                continue

            # 4. ADIM: Hedef OCR bölgesini hesapla
            # Bu kısım artık doğru (ox1, oy1, ox2, oy2) ve (box_w, box_h) değerleriyle çalışacak
            search_area_w = box_w * 8
            search_area_h = box_h * 0.60
            
            # Arama bölgesinin yatay merkezini nesnenin merkeziyle aynı yap
            # center_x zaten elimizde
            
            search_x1 = int(x_center - search_area_w / 2)
            search_y1 = int(oy2) # Nesnenin alt sınırından başla
            
            search_x2 = int(search_x1 + search_area_w)
            search_y2 = int(search_y1 + search_area_h)
            
            # Resim sınırları dışına taşmayı engelle
            search_x1 = max(0, search_x1)
            search_y1 = max(0, search_y1)
            search_x2 = min(w_img, search_x2)
            search_y2 = min(h_img, search_y2)
            
            # Arama bölgesini görselleştir
            cv2.rectangle(processed_image, (search_x1, search_y1), (search_x2, search_y2), (255, 0, 0), 1)

            # 5. ADIM: OCR yap ve sonuçları ata
            if search_x2 > search_x1 and search_y2 > search_y1:
                roi = image[search_y1:search_y2, search_x1:search_x2]
                results = self.reader.readtext(roi, detail=1)

                if results:
                    full_text = " ".join([res[1] for res in results])
                    parsed_string = self.__parse_info__(full_text , obj.type_())
                    
                    if parsed_string:
                        obj.set_name(parsed_string)
                        # Başarılı sonucu, nesnenin kendi kutusunun altına yazdır
                        cv2.putText(processed_image, parsed_string, (ox1, oy2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        return processed_image, objects

    def __parse_info__(self, text: str, type=0):
        if type == 0:
            only_numbers_and_spaces = re.sub(r'[^\d]', ' ', text)
            number_list = only_numbers_and_spaces.split()
            if len(number_list) < 3:
                return None
            return f"Sınıf Kodu:{number_list[0]} Alt Sınıf Kodu:{number_list[1]} Obje Kodu:{number_list[2]}"

        elif type == 1:
            parts = text.split('-')
            if len(parts) < 2:
                return None

            # Sol taraf ID, sağ taraf model ve değerler
            id_part = parts[0].strip()
            right_part = parts[1].strip()

            # Model adını harf olarak al (örnek: "mg")
            model_match = re.match(r'([a-zA-Z]+)', right_part)
            model = model_match.group(1) if model_match else "bilinmeyen model"

            # Sağ taraftaki tüm sayıları bul
            numbers = re.findall(r'\d+', right_part)
            if len(numbers) < 2:
                return None

            altitude = numbers[0]
            speed = numbers[1]

            return f"{id_part} ID'li {model} modelindeki obje {altitude}m irtifada {speed} m/s hızla uçuyor."

        else:
            return None
