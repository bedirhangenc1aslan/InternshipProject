from pathlib import Path
from Initialize import Initialize
from OCR import OCRProcessor
from YOLOV12 import YOLOV12
from Objects import Objects 
from Models import ModelLoader , BoxPredictor , Matcher
import torch
from YOLOV12 import YOLOV12
from Initialize import Initialize
import cv2
from pathlib import Path
from .UpdateObjectsAttributes import UpdateObjectsAttributes
from .PrepareLogs import PrepareLogs
from Video import ImageCreator

class ProcessFrame:
    def __init__(self, video_path, time_series , initialize):
        # BU FONKSİYONA DOKUNULMADI (İsteğiniz üzerine)
        self.time_series = time_series
        self.yolov12 = initialize.get_yolo()
        self.objects = initialize.get_objects()
        self.cls_names = initialize.get_cls_names()
        self.box_predictor = BoxPredictor(self.time_series)
        self.updater = UpdateObjectsAttributes(self.cls_names , self.box_predictor)
        self.ocr_processor = OCRProcessor(languages=['tr', 'en'], use_gpu=True)

        self.video_path = video_path
        self.results_generator = self.yolov12.predict_video(VIDEO_PATH=video_path)
        self.logs = PrepareLogs()
        self.current_frame_index = 0

    def process_frame(self):
        if self.results_generator is None:
            self.results_generator = self.yolov12.predict_video(VIDEO_PATH=self.video_path)
        
        result = next(self.results_generator)
        self.objects = self.updater.update_attributes(result, self.objects)

        original_frame = result.orig_img
        frame_with_ocr,self.objects  = self.ocr_processor.process_image(self.objects,original_frame)
        print(self.get_objects()[1].get_name())
        self.logs.write_logs(self.get_objects() , self.current_frame_index)
        
        frame_to_return = self.current_frame_index
        self.current_frame_index += 1

        last_processed_frame_with_ocr = frame_with_ocr

        return frame_to_return , last_processed_frame_with_ocr
    
    def get_objects(self):
        return self.objects.get_objects()
        




