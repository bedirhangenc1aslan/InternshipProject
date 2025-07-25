from fpdf import FPDF
import os
from Objects import Objects
from collections import defaultdict
from fpdf import FPDF
from collections import defaultdict
import copy

class PrepareLogs:
    def __init__(self, initialize, output_filename="olay_raporu_anlik.pdf"):
        """
        PERFORMANS UYARISI: Bu sınıf, her frame'de PDF'i baştan sona yeniden
        oluşturur. Kısa videolar veya testler için uygundur ancak uzun işlemlerde
        video ilerledikçe önemli ölçüde yavaşlamaya neden olacaktır.
        """
        self.output_filename = output_filename
        self.initialize = initialize
        self.cls_names_map = self.initialize.get_cls_names()
        
        # Her frame'in verisini saklamak için bir liste
        self.frame_data_history = []
        
        # Renk paletleri
        self.BORDER_COLORS = {
            "Takip Edilen": (0, 128, 0),
            "Gorus Alanindan Cikan": (255, 193, 7),
            "Kaybolan": (220, 53, 69)
        }
        self.FILL_COLORS = {
            "Muttefik": (173, 216, 230),
            "Bilinmeyen": (255, 255, 204),
            "Dusman": (255, 192, 203),
            "Supheli": (255, 218, 185)
        }

    def _sanitize_text(self, text):
        replacements = {'ş':'s', 'Ş':'S', 'ğ':'g', 'Ğ':'G', 'ı':'i', 'İ':'I', 'ö':'o', 'Ö':'O', 'ü':'u', 'Ü':'U', 'ç':'c', 'Ç':'C'}
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _get_attitude(self, cls_name_str):
        cls_name_str_clean = self._sanitize_text(cls_name_str)
        if cls_name_str_clean.startswith("Muttefik"): return "Muttefik"
        elif cls_name_str_clean.startswith("Dusman"): return "Dusman"
        elif cls_name_str_clean.startswith("Bilinmeyen"): return "Bilinmeyen"
        elif cls_name_str_clean.startswith("Supheli"): return "Supheli"
        return "Bilinmeyen"

    def _draw_table(self, pdf_object, title, border_color, fill_color, data):
        # Bu metod artık hangi pdf nesnesine çizeceğini parametre olarak alıyor
        if not data: return
        pdf_object.set_font('Arial', 'B', 12)
        pdf_object.set_text_color(*border_color)
        pdf_object.cell(w=0, h=8, txt=self._sanitize_text(title), ln=1, align="L")
        pdf_object.set_text_color(0, 0, 0)
        pdf_object.set_font('Arial', 'B', 10)
        pdf_object.set_draw_color(*border_color)
        pdf_object.set_fill_color(220, 220, 220)
        col_widths = (15, 85, 40, 40)
        headers = ("ID", "Isim", "Hiz (Dummy)", "Irtifa (Dummy)")
        for i, header in enumerate(headers):
            pdf_object.cell(col_widths[i], 7, self._sanitize_text(header), 1, 0, 'C', 1)
        pdf_object.ln()
        pdf_object.set_font('Arial', '', 9)
        pdf_object.set_fill_color(*fill_color)
        for row in data:
            for i, item in enumerate(row):
                pdf_object.cell(col_widths[i], 6, self._sanitize_text(str(item)), 1, 0, 'L', 1)
            pdf_object.ln()
        pdf_object.ln(5)

    @staticmethod
    def __is_out__(velocity, angle, bbox, frame_width, frame_height, out_th=10):
        # Bu metodda değişiklik yok
        if not bbox or len(bbox) != 4: return None
        try:
            x_center, y_center, box_w, box_h = bbox
            x_min, y_min = x_center - box_w / 2, y_center - box_h / 2
            x_max, y_max = x_center + box_w / 2, y_center + box_h / 2
        except (ValueError, TypeError): return None
        if velocity == 0.0: return None
        if (x_min <= out_th) and (90 < angle < 270): return "Bati'dan cikti"
        if (x_max >= frame_width - out_th) and (angle < 90 or angle > 270): return "Dogu'dan cikti"
        if (y_max >= frame_height - out_th) and (180 < angle < 360): return "Guney'den cikti"
        if (y_min <= out_th) and (0 < angle < 180): return "Kuzey'den cikti"
        return None

    def _draw_single_frame_page(self, pdf_object, objects, frame_idx, frame_width, frame_height):
        # Sadece tek bir frame'in sayfasını ve tablolarını çizen yardımcı metod
        if not objects:
            return

        categorized_data = defaultdict(lambda: defaultdict(list))
        for obj_id, obj in objects.items():
            cls_name = self.cls_names_map.get(obj.get_cls(), "Tanimsiz Sinif")
            attitude = self._get_attitude(cls_name)
            event_type = "Takip Edilen"
            if obj.get_cond() == "Obje suanda kayboldu":
                velocity, angle = obj.get_velocity()
                bbox = obj.get_box()
                if self.__is_out__(velocity, angle, bbox, frame_width, frame_height):
                    event_type = "Gorus Alanindan Cikan"
                else:
                    event_type = "Kaybolan"
            row_data = [obj_id, obj.get_name() , "1200 km/s", "10000 m"]
            categorized_data[event_type][attitude].append(row_data)

        if not categorized_data:
            return

        pdf_object.add_page()
        pdf_object.set_font('Arial', 'B', 14)
        page_title = self._sanitize_text(f"Saniye: {frame_idx} Raporu")
        pdf_object.cell(w=0, h=10, txt=page_title, ln=1, align="C")
        pdf_object.ln(5)

        event_order = ["Takip Edilen", "Gorus Alanindan Cikan", "Kaybolan"]
        attitude_order = ["Muttefik", "Dusman", "Supheli", "Bilinmeyen"]
        for event_type in event_order:
            for attitude in attitude_order:
                data = categorized_data[event_type][attitude]
                if data:
                    border_color = self.BORDER_COLORS[event_type]
                    fill_color = self.FILL_COLORS[attitude]
                    title = f"{event_type} - {attitude}"
                    self._draw_table(pdf_object, title, border_color, fill_color, data)

    def write_logs(self, objects, frame_idx, frame_width=1920, frame_height=1080):
        """
        Bu metod her çağrıldığında:
        1. Mevcut frame'in verisini geçmiş listesine ekler.
        2. PDF'i sıfırdan oluşturur, tüm geçmiş frameleri yazar.
        3. Dosyayı diske kaydeder/üzerine yazar.
        """
        # 1. Mevcut frame'in verisini geçmiş listesine ekle.
        # deepcopy, 'objects' sözlüğünün o anki halini kopyalamak için önemlidir.
        self.frame_data_history.append((copy.deepcopy(objects), frame_idx, frame_width, frame_height))

        # 2. PDF'i her seferinde sıfırdan oluştur.
        pdf = FPDF()

        # Ana başlık sayfasını ekle
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        title = self._sanitize_text("Olay Kayıt Raporu")
        pdf.cell(w=0, h=10, txt=title, ln=1, align="C")
        pdf.ln(10)

        # 3. Geçmişteki tüm frameler için sayfaları yeniden çiz.
        for saved_objects, saved_frame_idx, saved_fw, saved_fh in self.frame_data_history:
            self._draw_single_frame_page(pdf, saved_objects, saved_frame_idx, saved_fw, saved_fh)

        # 4. Son halini diske kaydet.
        try:
            pdf.output(self.output_filename, 'F')
        except Exception as e:
            print(f"PDF kaydedilirken bir hata oluştu: {e}")