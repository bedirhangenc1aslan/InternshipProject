from Objects import Objects

class UpdateObjectsAttributes:
    def __init__(self , cls_names):
        self.cls_names = cls_names



    def update_attributes(self , result , objects):
        for box_data in result.boxes.data.cpu().numpy():
            x_min, y_min, x_max, y_max, track_id, conf, cls_id = box_data
            track_id = int(track_id)
            
            existing_object = objects.get_single_object(track_id)
            
            w = x_max - x_min
            h = y_max - y_min
            bbox_for_object = [x_min + w / 2, y_min + h / 2, w, h]
            class_name = self.cls_names[int(cls_id)]

            if existing_object:
                existing_object.take_frame(
                    bbox=bbox_for_object,
                    cls_=int(cls_id),
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
        return objects
