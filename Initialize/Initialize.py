# Initialize.py dosyanızın güncellenmiş hali

from OCR import OCRProcessor
from YOLOV12 import YOLOV12
from Objects import Objects
from Models import ModelLoader, BoxPredictor, Matcher
import torch
from pathlib import Path

class Initialize:
    def __init__(self, time_series):
        self.time_series = time_series
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.yolov12 = YOLOV12(self.device) 
        self.model_loader = ModelLoader()
        
        # Model yolları
        boxmodel_path = Path(__file__).parent.parent / 'Models/BestBoxPredictor.pth'
        matchmodel_path = Path(__file__).parent.parent / 'Models/Matcher.pth'
        
        # Modelleri yükle
        self.boxPredictor = self.model_loader.load_model(boxmodel_path, "BoxPredictor", self.device)
        self.matcher = self.model_loader.load_model(matchmodel_path, "Matcher", self.device)
        self.ocr_processor = OCRProcessor(languages=['tr', 'en'], use_gpu=True)

        # Gerekli ayarları ve nesneleri başlat
        self.cls_types = self.__get_cls_types__()
        self.objects = Objects(self.cls_types, self.time_series)

    def __get_cls_types__(self):
        cls_types = {
        0: "Weapon", 1: "Weapon", 2: "Weapon", 3: "Weapon",
        4: "Plane", 5: "Plane", 6: "Plane", 7: "Plane",
        8: "Plane", 9: "Plane", 10: "Plane", 11: "Plane",
        12: "Plane", 13: "Plane", 14: "Plane"
        }
        return cls_types

    def get_cls_names(self):
        cls_names = {
        0: "Müttefik Portatif Tim",
        1: "Müttefik Atış Kontrol Merkezi Bt AKM",
        2: "Müttefik Komuta Kontrol Aracı KKA",
        3: "Müttefik Portatif Tim2",
        4: "Bilinmeyen IHA",
        5: "Düşman IHA",
        6: "Bilinmeyen Sabit Kanat",
        7: "Düşman Sabit Kanat",
        8: "Bilinmeyen Döner Kanat",
        9: "Düşman Döner Kanat",
        10: "Bilinmeyen Füze",
        11: "Düşman Füze",
        12: "Müttefik Fighter",
        13: "Şüpheli Sabit Kanat",
        14: "Düşman Sabit Kanat2"
        }
        return cls_names


    def get_objects(self):
        return self.objects
    def get_yolo(self):
        return self.yolov12
    def get_box_predictor(self):
        return self.boxPredictor