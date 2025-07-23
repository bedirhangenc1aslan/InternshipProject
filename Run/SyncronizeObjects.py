from Objects import Objects
class SyncronizeObjects:
    def __init__(self):
        pass
    def syncronize(self , result , objects):
        if result.boxes is None or result.boxes.id is None:
            active_ids_from_tracker = set()
        else:
            active_ids_from_tracker = set(result.boxes.id.int().cpu().tolist())

        my_current_ids = set(objects.get_objects().keys())
        
        ids_to_delete = my_current_ids - active_ids_from_tracker
        for track_id in ids_to_delete:
            objects.delete_object(track_id)
        return objects