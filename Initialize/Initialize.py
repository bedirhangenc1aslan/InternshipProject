from YOLOV12 import YOLOV12
from Objects import Objects , IdBag
from Models import ModelLoader , BoxPredictor , Matcher
from Tracking import ObjectTracker
import torch
from pathlib import Path
class Initialize:
    def __init__(self , IMAGE_PATH , time_series):
        self.time_series = time_series
        self.yolov12 = YOLOV12()
        self.detections_list = self.yolov12.predict_image(IMAGE_PATH=IMAGE_PATH , CONFIDENCE_THRESHOLD=0.5)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_loader = ModelLoader()
        boxmodel_path = Path(__file__).parent.parent/ 'Models/BestBoxPredictor.pth'
        matchmodel_path = Path(__file__).parent.parent/ 'Models/Matcher.pth'
        self.boxPredictor = self.model_loader.load_model(boxmodel_path,"BoxPredictor",self.device)
        self.matcher = self.model_loader.load_model(matchmodel_path,"Matcher",self.device)

        self.cls_types = self.__get_cls_types__()
        self.idbag = IdBag(length=100)
        self.objects = Objects(self.idbag , self.cls_types , self.time_series)

        self.__create_objects__()
        self.tracker = ObjectTracker(self.boxPredictor ,self.objects , self.matcher , conf_th=0.5)

    def __create_objects__(self):
        for object in self.detections_list:
            self.objects.add_object(object["class_name"], object["class_id"] , object["coordinates"] , object["confidence"])

    def __get_cls_types__(self):
        cls_types = {"ikon_0" : "Weapon",
                     "ikon_1" : "Weapon",
                     "ikon_2" : "Weapon",
                     "ikon_3" : "Weapon",
                     "ikon_4" : "Plane",
                     "ikon_5" : "Plane",
                     "ikon_6" : "Plane",
                     "ikon_7" : "Plane",
                     "ikon_8" : "Plane",
                     "ikon_9" : "Plane",
                     "ikon_10" : "Plane",
                     "ikon_11" : "Plane",
                     "ikon_12" : "Plane",
                     "ikon_13" : "Plane",
                     "ikon_14" : "Plane"
                     }
        return cls_types
    
    def get_objects(self):
        return self.objects