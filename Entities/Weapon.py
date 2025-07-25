from collections import deque
from .Object import Object
class Weapon(Object):
    def __init__(self, id_, name, cls_, bbox, conf, time_serial, attitude="Neutral"):
        super().__init__(id_, name, cls_, bbox, conf, time_serial, attitude)
    
    def get_velocity(self):
        return 0 , 0
    def type_(self):
        return False