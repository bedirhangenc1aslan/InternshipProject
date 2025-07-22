from pathlib import Path
from Initialize import Initialize
from YOLOV12 import YOLOV12
from Objects import Objects , IdBag
from Models import ModelLoader , BoxPredictor , Matcher
from Tracking import ObjectTracker
import torch

class ProcessFrame:
    def __init__(self , FOLDER_PATH , TIME_SERIES):
        self.image_paths = list(FOLDER_PATH.glob("*.jpg"))  # sadece jpg

        # Tüm yaygın uzantılar için:
        self.image_paths = [p for p in FOLDER_PATH.iterdir() if p.suffix.lower() in [".jpg", ".png", ".jpeg"]]
        self.initialize = Initialize(self.image_paths[0] , time_series=TIME_SERIES)
        self.frame_idx = 1
    def process_frame(self):
        if self.frame_idx >= len(self.image_paths):
            return False
        yolov12 = self.initialize.yolov12
        detections_list = yolov12.predict_image(self.image_paths[self.frame_idx] , CONFIDENCE_THRESHOLD= 0.5)
        tracker = self.initialize.tracker
        bboxes = []
        clss = []
        confs = []

        for detection in detections_list:
            bboxes.append(detection["coordinates"])
            clss.append(detection["class_id"])
            confs.append(detection["confidence"])

        tracker.match_objects(bboxes=bboxes , clss=clss , confs=confs , match_threshold=0.5)
        self.frame_idx += 1
        return self.frame_idx
    def get_objects(self):
        return self.initialize.objects

        




