from .BoxPredictor import BoxPredictor
from .Matcher import Matcher
import torch
class ModelLoader:
    def __init__(self):
        self.model_dict = {}

    def load_model(self , MODEL_PATH , TYPE , DEVICE):
        if TYPE == "BoxPredictor":
            model = BoxPredictor()
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        elif TYPE == "Matcher":
            model = Matcher()
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.model_dict[MODEL_PATH] = model
        return model