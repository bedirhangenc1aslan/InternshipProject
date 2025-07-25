from Entities import Object,Plane, Helicopter, Weapon

class Objects:
    def __init__(self, cls_types, time_series):
        self.objects = {}
        self.cls_types = cls_types
        self.time_series = time_series

    # --- BU METOT DEĞİŞTİRİLDİ ---
    # Artık 'id_' parametresini ilk sıraya alıyor.
    def add_object(self, track_id, cls_name, cls_id, bbox, conf, attitude="Neutral"):
        if track_id in self.objects:
            return False
        type_ = self.cls_types.get(cls_id)
        new_object = None
        if type_ == "Helicopter":
            new_object = Helicopter(track_id,cls_name, cls_id, bbox, conf, self.time_series, attitude=attitude)
        elif type_ == "Plane":
            new_object = Plane(track_id,cls_name, cls_id, bbox, conf, self.time_series, attitude=attitude)
        elif type_ == "Weapon":
            new_object = Weapon(track_id,cls_name, cls_id, bbox, conf, self.time_series, attitude=attitude)
        else:
            print("Obje hiçbir sınıf ile uyuşmuyor")
        
        if new_object:
            self.objects[track_id] = new_object
            return True
            
        return False
    def update_object(self, id ,bbox , cls , conf, is_lost = False):
        if self.is_object_present(id):
            object = self.objects.get(id)
            if is_lost:
                object.update(None , None , 0)
                if object.get_lost_time() >= self.time_series:
                    self.delete_object(id)
                    return True , True
                return True , False
            object.update(bbox , cls , conf)
            return False , False
        return False , True
        
    def delete_object(self, id_):
        if id_ in self.objects:
            self.objects.pop(id_)

    def get_single_object(self, id_):
        return self.objects.get(id_)

    def is_object_present(self , id ):
        object = self.objects.get(id)
        if object:
            return True
        return False

    def get_objects(self):
        return self.objects
    
    def get_object_lost_time(self , id):
        return self.objects[id].get_lost_time()
    
    def get_object_history(self , id):
        return self.objects[id].get_history()
    
    def set_object_condition(self , id , condition):
        self.objects[id].set_condition(condition)
