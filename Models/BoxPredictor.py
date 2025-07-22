import torch
import torch.nn as nn
import torch.nn.functional as F

class BoxPredictor(nn.Module):
    def __init__(self , time_series=30):
        super(BoxPredictor, self).__init__()
        self.decoder = nn.Linear(4 , time_series)
        self.act1 = nn.ReLU()
        self.encoder = nn.Linear(time_series , 1)
        self.act2 = nn.Sigmoid()
        self.out = nn.Linear(time_series , 4)
    def forward(self , bbox_sequence):
        decode = self.decoder(bbox_sequence)
        act1 = self.act1(decode)
        encoded = self.encoder(act1)
        act2 = self.act2(encoded)
        act2 = act2.squeeze(-1)
        out = self.out(act2)
        return out