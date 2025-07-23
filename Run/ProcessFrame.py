from pathlib import Path
from Initialize import Initialize
from YOLOV12 import YOLOV12
from Objects import Objects 
from Models import ModelLoader , BoxPredictor , Matcher
import torch
from YOLOV12 import YOLOV12
from Initialize import Initialize
import cv2
from pathlib import Path
from .SyncronizeObjects import SyncronizeObjects
from .UpdateObjectsAttributes import UpdateObjectsAttributes
class ProcessFrame:
    def __init__(self, video_path, time_series , initialize):
        # BU FONKSİYONA DOKUNULMADI (İsteğiniz üzerine)
        self.time_series = time_series
        self.yolov12 = initialize.get_yolo()
        self.objects = initialize.get_objects()
        self.cls_names = initialize.get_cls_names()

        self.syncronizer = SyncronizeObjects()
        self.updater = UpdateObjectsAttributes(self.cls_names)

        self.video_path = video_path
        self.results_generator = self.yolov12.predict_video(VIDEO_PATH=video_path)

        self.current_frame_index = 0

    def process_frame(self):
        if self.results_generator is None:
            self.results_generator = self.yolov12.predict_video(VIDEO_PATH=self.video_path)
        
        result = next(self.results_generator)

        self.objects = self.syncronizer.syncronize(result , self.objects)
        self.objects = self.updater.update_attributes(result, self.objects)
        
        frame_to_return = self.current_frame_index
        self.current_frame_index += 1
        return frame_to_return
    
    def get_objects(self):
        return self.objects.get_objects()
        




