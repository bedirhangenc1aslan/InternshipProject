from Objects import Objects
from Models import  BoxPredictor

class UpdateObjectsAttributes:
    def __init__(self , cls_names , box_predictor ):
        self.box_predictor = box_predictor
        self.cls_names = cls_names

        self.conf_th = 0.3
    def update_attributes(self , result , objects):
        objects = self.__find_lost_objects__(result , objects)
        objects = self.__assign_boxes__(result , objects)
        return objects

    def __find_lost_objects__(self , result , objects):
        if result.boxes is None or result.boxes.id is None:
            active_ids_from_tracker = set()
        else:
            active_ids_from_tracker = set(result.boxes.id.int().cpu().tolist())

        my_current_ids = set(objects.get_objects().keys())
        
        ids_to_delete = my_current_ids - active_ids_from_tracker
        for track_id in ids_to_delete:
            objects.update_object(track_id , None , None , 0 , True)
        return objects

    def __assign_boxes__(self , result , objects):
        for box_data in result.boxes.data.cpu().numpy():
            try:
                x_min, y_min, x_max, y_max, track_id, conf, cls_id = box_data
            except ValueError as e:
                continue

            track_id = int(track_id)
            is_exists = objects.is_object_present(track_id)

            w = x_max - x_min
            h = y_max - y_min
            bbox_for_object = [x_min + w / 2, y_min + h / 2, w, h]
            class_name = self.cls_names[int(cls_id)]

            if is_exists:
                condition = None
                if conf < self.conf_th:
                    bbox_history = [objects.get_object_history(track_id)[i][0] for i in range(len(objects.get_object_history(track_id)))]
                    bbox_for_object = self.box_predictor.run_model(bbox_history)
                    condition = "Obje tespit edilirken sorun yasaniyor. Tahmini bulundugu konum ve hiz gosteriliyor."
                objects.update_object(
                    id = track_id,
                    bbox=bbox_for_object,
                    cls=int(cls_id),
                    conf=float(conf),
                )
                if condition is not None:
                    objects.set_object_condition(track_id , condition)
            else:
                objects.add_object(
                    track_id=track_id,
                    cls_name=class_name,
                    cls_id=int(cls_id),
                    bbox=bbox_for_object,
                    conf=float(conf)
                )
        return objects
