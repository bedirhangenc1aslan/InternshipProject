import torch
from Models import BoxPredictor , Matcher
class ObjectTracker:
    def __init__(self, box_predictor, objects, matcher, conf_th = 0.5):
        self.box_predictor = box_predictor
        self.Objects = objects
        self.matcher = matcher
        self.conf_th = conf_th

    def __is_match__(self, bbox, cls, conf, object_instance):
        history_bboxes = object_instance.get_box()[:]
        history_clss = object_instance.get_cls()[:]
        history_confs = object_instance.get_conf()[:]

        history_bboxes.append(bbox)
        history_clss.append(cls)
        history_confs.append(conf)

        t_bboxes = torch.tensor([history_bboxes], dtype=torch.float32)
        t_clss = torch.tensor([history_clss], dtype=torch.long)
        t_confs = torch.tensor([history_confs], dtype=torch.float32)
        
        self.matcher.eval()
        with torch.no_grad():
            logits = self.matcher(t_bboxes, t_clss, t_confs)
            probabilities = torch.softmax(logits, dim=-1)
            match_score = probabilities[0, 1].item()
        
        return match_score

    def match_objects(self, detections_list, match_threshold = 0.5):
        tracked_objects = self.Objects.get_objects()

        is_used_box = [False] * len(detections_list)

        for obj_id, track in tracked_objects.items():
            best_match_score = match_threshold
            best_match_idx = None
            
            for i, detection in enumerate(detections_list):

                class_name , class_id , confidence , coordinates = self.__get_detection__(detection)

                if not is_used_box[i]:
                    score = self.__is_match__(coordinates, class_id, confidence, track)
                    if score > best_match_score:
                        best_match_score = score
                        best_match_idx = i
            
            if best_match_idx is not None:
                is_used_box[best_match_idx] = True
                class_name , class_id , confidence , coordinates = self.__get_detection__(detections_list[best_match_idx])
                track.take_frame(coordinates, class_id, confidence)
            else:
                track.take_frame(None, None, 0)
        for i in range(len(detections_list)):
            if not is_used_box[i]:
                class_name , class_id , confidence , coordinates = self.__get_detection__(detections_list[i])
                if conf > self.conf_th:
                    self.Objects.add_object(class_name, class_id , coordinates , confidence)
        return
    
    def __get_detection__(self , detection):                
        class_name = detection["class_name"]
        class_id = detection["class_id"]
        confidence = detection["confidence"]
        coordinates = detection["coordinates"]
        return class_name , class_id , confidence , coordinates