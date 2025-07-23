# Initialize.py dosyanızın güncellenmiş hali

from YOLOV12 import YOLOV12
from Objects import Objects
from Models import ModelLoader, BoxPredictor, Matcher
import torch
from pathlib import Path

class Initialize:
    def __init__(self, time_series):
        self.time_series = time_series
        self.yolov12 = YOLOV12() 
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_loader = ModelLoader()
        
        # Model yolları
        boxmodel_path = Path(__file__).parent.parent / 'Models/BestBoxPredictor.pth'
        matchmodel_path = Path(__file__).parent.parent / 'Models/Matcher.pth'
        
        # Modelleri yükle
        self.boxPredictor = self.model_loader.load_model(boxmodel_path, "BoxPredictor", self.device)
        self.matcher = self.model_loader.load_model(matchmodel_path, "Matcher", self.device)

        # Gerekli ayarları ve nesneleri başlat
        self.cls_types = self.__get_cls_types__()
        self.objects = Objects(self.cls_types, self.time_series)

    def __get_cls_types__(self):
        cls_types = {
            "ikon_0": "Weapon", "ikon_1": "Weapon", "ikon_2": "Weapon", "ikon_3": "Weapon",
            "ikon_4": "Plane", "ikon_5": "Plane", "ikon_6": "Plane", "ikon_7": "Plane",
            "ikon_8": "Plane", "ikon_9": "Plane", "ikon_10": "Plane", "ikon_11": "Plane",
            "ikon_12": "Plane", "ikon_13": "Plane", "ikon_14": "Plane"
        }
        return cls_types
    
    def get_cls_names(self):
        cls_names = {
            0: "ikon_0",
            1: "ikon_1",
            2: "ikon_2",
            3: "ikon_3",
            4: "ikon_4",
            5: "ikon_5",
            6: "ikon_6",
            7: "ikon_7",
            8: "ikon_8",
            9: "ikon_9",
            10: "ikon_10",
            11: "ikon_11",
            12: "ikon_12",
            13: "ikon_13",
            14: "ikon_14"
        }
        return cls_names


    def get_objects(self):
        return self.objects
    def get_yolo(self):
        return self.yolov12
    def get_box_predictor(self):
        return self.boxPredictor