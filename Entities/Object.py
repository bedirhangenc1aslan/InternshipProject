from collections import deque

class Object:
    def __init__(self, id_, name, cls_, bbox, conf ,time_series, attitude="Neutral"):
        self.id = id_
        self.name = name
        self.cls = cls_
        self.bbox = bbox
        self.conf = conf
        self.attitude = attitude
        self.condition = "Tespit Edildi"

        self.lost_time = 0

        self.time_series = time_series
        self.history = deque(maxlen=self.time_series)
        initial_condition = [self.bbox, self.cls, self.conf]
        self.history_padding = [[0, 0, 0, 0], 0, 0]

        for _ in range(self.time_series):
            self.history.append(self.history_padding)
        self.history.append(initial_condition)

    def update(self, bbox, cls_, conf , cond = "Tespit Edildi"):
        if conf == 0:
            self.condition = cond
            self.history.append(self.history_padding)
            self.lost_time += 1
            return
        self.lost_time = 0
        self.condition = cond
        self.bbox = bbox
        self.cls = cls_
        self.conf = conf
        self.history.append([self.bbox, self.cls, self.conf])
    
    def set_condition(self , condition):
        self.condition = condition

    def get_box(self):
        return self.bbox
    def get_cls(self):
        return self.cls
    def get_conf(self):
        return self.cls
    def get_cond(self):
        return self.condition
    def get_history(self):
        return self.history
    def get_lost_time(self):
        return self.lost_time
    def get_name(self):
        return self.name
    def set_name(self , name):
        self.name = name