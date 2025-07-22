from collections import deque

class IdBag:
    def __init__(self, length=100):
        self.ids = deque(range(length))

    def get_id(self):
        if not self.ids:
            return False
        return self.ids.pop()

    def allocate_id(self, id_):
        self.ids.append(id_)
