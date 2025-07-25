from collections import deque
import math
from .Object import Object
class Plane(Object):
    def __init__(self, id_, name, cls_, bbox, conf, time_serial, attitude="Neutral"):
        super().__init__(id_, name, cls_, bbox, conf, time_serial, attitude)
    
    def get_velocity(self):
        x1 , y1 = (self.history[-1][0][0] + self.history[-1][0][2])/2 , (self.history[-1][0][1] + self.history[-1][0][3])/2
        x2 , y2 = (self.history[-2][0][0] + self.history[-2][0][2])/2 , (self.history[-2][0][1] + self.history[-2][0][3])/2

        dx = x2 - x1
        dy = y2 - y1
        velocity = math.sqrt((dx)**2 + (dy)**2)

        angle_rad = math.atan2(dx, -dy)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg + 360) % 360

        return velocity , angle_deg