"""Compact deterministic Transformer baseline for motion inbetweening.

SPDX-License-Identifier: GPL-2.0-or-later
Untrained construction is research code, not a functional animation model.
"""
import math

import torch
from torch import nn


CONDITION = 547
POSE_CHANNELS = 153
WIDTH = 128
HEADS = 4
HEAD_WIDTH = WIDTH // HEADS
LAYERS = 4
FF_WIDTH = 256


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1 = nn.LayerNorm(WIDTH)
        self.qkv = nn.Linear(WIDTH, WIDTH * 3)
        self.attention_output = nn.Linear(WIDTH, WIDTH)
        self.norm2 = nn.LayerNorm(WIDTH)
        self.ff1 = nn.Linear(WIDTH, FF_WIDTH)
        self.ff2 = nn.Linear(FF_WIDTH, WIDTH)

    def forward(self, values):
        batch, time, _ = values.shape
        query, key, value = self.qkv(self.norm1(values)).chunk(3, dim=-1)
        query = query.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(1, 2)
        key = key.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(1, 2)
        value = value.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(1, 2)
        weights = torch.softmax(query @ key.transpose(-1, -2) / math.sqrt(HEAD_WIDTH), dim=-1)
        attended = (weights @ value).transpose(1, 2).reshape(batch, time, WIDTH)
        values = values + self.attention_output(attended)
        hidden = torch.nn.functional.gelu(self.ff1(self.norm2(values)), approximate="tanh")
        return values + self.ff2(hidden)


class SequenceTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.input = nn.Linear(CONDITION, WIDTH)
        self.blocks = nn.ModuleList([Block() for _ in range(LAYERS)])
        self.norm = nn.LayerNorm(WIDTH)
        self.output = nn.Linear(WIDTH, POSE_CHANNELS + 1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)
        with torch.no_grad():
            self.output.bias[-1] = -2.0

    def forward(self, condition):
        values = self.input(condition)
        for block in self.blocks:
            values = block(values)
        return self.output(self.norm(values))

