from pathlib import Path
from Initialize import Initialize
from YOLOV12 import YOLOV12
from Objects import Objects , IdBag
from Models import ModelLoader , BoxPredictor , Matcher
from Tracking import ObjectTracker
import torch

class ProcessFrame:
    def __init__(self , FOLDER_PATH , TIME_SERIES):
        folder = Path(FOLDER_PATH)
        self.image_paths = list(folder.glob("*.jpg"))  # sadece jpg

        # Tüm yaygın uzantılar için:
        self.image_paths = [p for p in folder.iterdir() if p.suffix.lower() in [".jpg", ".png", ".jpeg"]]
        self.initialize = Initialize(self.image_paths[0] , time_series=TIME_SERIES)
        self.frame_idx = 1
    def process_frame(self):
        if self.frame_idx >= len(self.image_paths):
            return False
        yolov12 = self.initialize.yolov12
        detections_list = yolov12.predict_image(self.image_paths[self.frame_idx] , CONFIDENCE_THRESHOLD= 0.5)
        tracker = self.initialize.tracker


        tracker.match_objects(detections_list, match_threshold=0.5)
        self.frame_idx += 1
        return 

        




