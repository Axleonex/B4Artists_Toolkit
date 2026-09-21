"""Reference-mixture Transformer for constrained motion inbetweening.

SPDX-License-Identifier: GPL-2.0-or-later
Untrained construction is research code, not a functional animation model.
"""
import torch
from torch import nn

from sequence_transformer_model_v1 import Block, LAYERS, WIDTH


CONDITION = 853
OUTPUT = 157


class MixtureTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.input = nn.Linear(CONDITION, WIDTH)
        self.blocks = nn.ModuleList([Block() for _ in range(LAYERS)])
        self.norm = nn.LayerNorm(WIDTH)
        self.output = nn.Linear(WIDTH, OUTPUT)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)
        with torch.no_grad():
            self.output.bias[153] = -2.0
            self.output.bias[154:] = torch.tensor([0.0, 0.0, 2.0])

    def forward(self, condition):
        values = self.input(condition)
        for block in self.blocks:
            values = block(values)
        return self.output(self.norm(values))

