from fpdf import FPDF
import os
from Objects import Objects
class PrepareLogs:
    def __init__(self, output_filename="olay_raporu.pdf"):
        """
        Sinif baslatildiginda gerekli degiskenleri ayarlar.
        'objects' parametresini alarak daha tutarli hale getirildi.
        """
        self.output_filename = output_filename
        self.log_entries = []  # Tum loglari hafizada tutmak icin liste
        
        # Font adini dogrudan 'Arial' olarak ayarlayalim.
        self.font_name = 'Arial'
        
        # PDF'in basligini en basta bir kere yazdiralim
        self._initialize_pdf_with_title()

    def _initialize_pdf_with_title(self):
        """PDF'i sadece baslik ile olusturur. Henuz log yazilmaz."""
        pdf = FPDF()
        pdf.add_page()
        
        # Fontu dogrudan Arial olarak ayarla. Font dosyasi arama islemi kaldirildi.
        pdf.set_font(self.font_name, 'B', 16) # Basligi kalin yapalim
        
        # Turkce karakterler kaldirildi
        pdf.cell(w=0, h=10, txt="Olay Kayit Raporu", ln=1, align="C")
        pdf.ln(10)
        pdf.output(self.output_filename)

    @staticmethod
    def __is_out__(velocity, angle, bbox, out_th=0.005):
        # Metinlerdeki Turkce karakterler kaldirildi
        top, bottom, right, left = bbox[1], bbox[3], bbox[2], bbox[0]
        if velocity == 0.0: return "Hata"
        if (left <= out_th) and (90 < angle < 270): return "Bati'dan cikti"
        if (right >= 1-out_th) and (angle < 90 or angle > 270): return "Dogu'dan cikti"
        if (bottom >= 1-out_th) and (180 < angle < 360): return "Guney'den cikti"
        if (top <= out_th) and (0 < angle < 180): return "Kuzey'den cikti"
        return "Hata"

    def write_logs(self, objects ,frame_idx, frame_ratio=1, lost=None):
        """
        Her cagrildiginda yeni loglari bulur, hafizadaki listeye ekler
        ve PDF dosyasini bu guncel liste ile yeniden olusturur.
        """
        new_logs_this_frame = []
        # 'objects' parametresi yerine __init__'te alinan 'self.objects' kullanildi.

        for id, obj in objects.items():
            velocity, angle = obj.get_velocity()
            bbox = obj.get_box()
            status = self.__is_out__(velocity, angle, bbox)
            if status != "Hata":
                # Turkce karakterler kaldirildi
                log_message = f"ID-{id}: Nesne {frame_idx * frame_ratio:.2f}. saniyede gorus alanindan ({status})."
                new_logs_this_frame.append(log_message)

        if lost is not None:
            for id in lost:
                # Turkce karakterler kaldirildi
                log_message = f"ID-{id}: Nesne {frame_idx * frame_ratio:.2f}. saniyede kayboldu."
                new_logs_this_frame.append(log_message)
        
        if not new_logs_this_frame:
            return

        self.log_entries.extend(new_logs_this_frame)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Fontu dogrudan Arial olarak ayarla
        pdf.set_font(self.font_name, 'B', 16)

        # Basligi tekrar yaz
        pdf.cell(w=0, h=10, txt="Olay Kayit Raporu", ln=1, align="C")
        pdf.ln(5)
        
        # Tum loglari yazdir
        pdf.set_font(self.font_name, '', 12) # Loglar icin normal boyut
        for entry in self.log_entries:
            # unidecode'a gerek yok cunku metinler zaten ASCII
            pdf.multi_cell(w=0, h=8, txt=entry, ln=1)
            
        pdf.output(self.output_filename)
