from Entities import Plane , Helicopter , Weapon
from .IdBag import IdBag
class Objects:
    def __init__(self, IdBag, cls_types,time_series):
        self.IdBag = IdBag
        self.objects = {}
        self.cls_types = cls_types
        self.time_series = time_series
    def add_object(self, cls_name ,cls_id, bbox, conf, attitude="Neutral"):
        id_ = self.IdBag.get_id()
        if id_ is False:
            return False
        type_ = self.cls_types.get(cls_name)
        if type_ == "Helicopter":
            self.objects[id_] = Helicopter(id_, cls_name, cls_id, bbox, conf, self.time_series, attitude)
        elif type_ == "Plane":
            self.objects[id_] = Plane(id_, cls_name, cls_id, bbox, conf, self.time_series, attitude)
        elif type_ == "Weapon":
            self.objects[id_] = Weapon(id_,cls_name, cls_id, bbox, conf, self.time_series, attitude)
        
        return True

    def delete_object(self, id_):
        self.objects.pop(id_, None)
        self.IdBag.allocate_id(id_)

    def get_single_object(self, id_):
        return self.objects.get(id_)

    def get_objects(self):
        return self.objects


