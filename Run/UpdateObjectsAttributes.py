from Objects import Objects
from Models import  BoxPredictor

class UpdateObjectsAttributes:
    def __init__(self , cls_names , box_predictor):
        self.box_predictor = box_predictor
        self.cls_names = cls_names
    def update_attributes(self , result , objects):
        objects = self.__find_lost_objects__(result , objects)
        objects , is_used= self.__assign_boxes__(result , objects)
        objects = self.__predict_boxes__(objects , is_used)

        return objects

    def __find_lost_objects__(self , result , objects):
        if result.boxes is None or result.boxes.id is None:
            active_ids_from_tracker = set()
        else:
            active_ids_from_tracker = set(result.boxes.id.int().cpu().tolist())

        my_current_ids = set(objects.get_objects().keys())
        
        ids_to_delete = my_current_ids - active_ids_from_tracker
        for track_id in ids_to_delete:
            objects.delete_object(track_id)
        return objects

    def __predict_boxes__(self , objects , is_used):
        for id , value in is_used.items():
            if value:
                continue
            object = objects.get_single_object(id)
            conf = object.get_conf()
            cls = object.get_cls()
            if conf > 0.0:#tamamlancak
                condition = "Obje tespit edilirken sorun yaşanıyor. Tahmini bulunduğu konum ve hız gösteriliyor."
                bbox = self.box_predictor(objects.get_box())
                objects.update(id,bbox , cls , conf ,condition) # Güvenli değil güvenli forma sokulcak
            else: #doldurulcak
                pass
        return objects

    def __assign_boxes__(self , result , objects):
        is_used = {}
        for id , object in objects.get_objects().items():
            is_used[id] = False

        for box_data in result.boxes.data.cpu().numpy():
            x_min, y_min, x_max, y_max, track_id, conf, cls_id = box_data
            track_id = int(track_id)
            is_exists = objects.is_object_present(track_id)

            w = x_max - x_min
            h = y_max - y_min
            bbox_for_object = [x_min + w / 2, y_min + h / 2, w, h]
            class_name = self.cls_names[int(cls_id)]

            if is_exists:
                is_used[track_id] = True
                objects.update_object(
                    id = track_id,
                    bbox=bbox_for_object,
                    cls=int(cls_id),
                    conf=float(conf)
                )
            else:
                objects.add_object(
                    track_id=track_id,
                    cls_name=class_name,
                    cls_id=int(cls_id),
                    bbox=bbox_for_object,
                    conf=float(conf)
                )
        return objects , is_used
