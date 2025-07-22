from collections import deque
class Helicopter:
    def __init__(self, id_, name, cls_, bbox, conf, time_serial, attitude="Neutral"):
        self.id = id_
        self.name = name
        self.cls = cls_
        self.bbox = bbox
        self.conf = conf
        self.time_serial = time_serial
        self.attitude = attitude

        self.history = deque(maxlen=self.time_serial)
        initial_condition = [self.bbox, self.cls, self.conf]
        history_padding = [[0, 0, 0, 0], "0", 0]

        for _ in range(self.time_serial):
            self.history.append(history_padding)

        self.history.append(initial_condition)

    def take_frame(self, bbox, cls_, conf):
        if conf == 0:
            self.history.append(self.history_padding)
            return
        self.bbox = bbox
        self.cls = cls_
        self.conf = conf
        self.history.append([self.bbox, self.cls, self.conf])
    def get_box(self):
        return self.bbox
    def get_cls(self):
        return self.cls
    def get_conf(self):
        return self.cls
    def get_history(self):
        return self.history
    

        
