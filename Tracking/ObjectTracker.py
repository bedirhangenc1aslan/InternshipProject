import torch

class ObjectTracker:
    def __init__(self, box_predictor, objects, matcher, conf_th):
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

    def match_objects(self, bboxes, clss, confs, match_threshold):
        tracked_objects = self.Objects.get_objects()
        
        if not bboxes:
            for obj_id, track in tracked_objects.items():
                track.take_frame(None, None, 0)
            return

        is_used_box = [False] * len(bboxes)
        detection_data = list(zip(bboxes, clss, confs))

        for obj_id, track in tracked_objects.items():
            best_match_score = match_threshold
            best_match_idx = None
            
            for i, (bbox, cls, conf) in enumerate(detection_data):
                if not is_used_box[i]:
                    score = self.__is_match__(bbox, cls, conf, track)
                    if score > best_match_score:
                        best_match_score = score
                        best_match_idx = i
            
            if best_match_idx is not None:
                is_used_box[best_match_idx] = True
                matched_bbox, matched_cls, matched_conf = detection_data[best_match_idx]
                track.take_frame(matched_bbox, matched_cls, matched_conf)
            else:
                track.take_frame(None, None, 0)
        # Buraya bakılcak
        for i in range(len(detection_data)):
            if not is_used_box[i]:
                new_bbox, new_cls, new_conf = detection_data[i]
                if new_conf.max() > self.conf_th:
                    self.Objects.add_object(new_bbox, new_cls, new_conf)

        return