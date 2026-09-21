"""Masked residual temporal-convolution candidate for full-hierarchy motion.

SPDX-License-Identifier: GPL-2.0-or-later
Training dependency only.  Deployment must use a separately verified export.
"""
import torch
from torch import nn
from torch.nn import functional as F


INPUT_WIDTH = 766
STATE_WIDTH = 141
JOINTS = 23


class ResidualTemporalBlock(nn.Module):
    def __init__(self, width, dilation, dropout):
        super().__init__()
        padding = dilation
        self.norm1 = nn.GroupNorm(8, width)
        self.conv1 = nn.Conv1d(width, width, 3, padding=padding, dilation=dilation)
        self.norm2 = nn.GroupNorm(8, width)
        self.conv2 = nn.Conv1d(width, width, 3, padding=padding, dilation=dilation)
        self.dropout = nn.Dropout(dropout)

    def forward(self, value):
        hidden = self.conv1(F.silu(self.norm1(value)))
        hidden = self.dropout(hidden)
        hidden = self.conv2(F.silu(self.norm2(hidden)))
        return value + hidden


def normalize_state_rotations(state, epsilon=1e-8):
    if state.shape[-1] != STATE_WIDTH:
        raise ValueError("Expected 141 full-hierarchy state features")
    root = state[..., :3]
    rotation = state[..., 3:].reshape(*state.shape[:-1], JOINTS, 6)
    first, second = rotation[..., :3], rotation[..., 3:]
    x = F.normalize(first, dim=-1, eps=epsilon)
    y = second - x * torch.sum(x * second, dim=-1, keepdim=True)
    y = F.normalize(y, dim=-1, eps=epsilon)
    return torch.cat((root, torch.cat((x, y), dim=-1).reshape(*state.shape[:-1], 6 * JOINTS)), dim=-1)


class MaskedResidualTCN(nn.Module):
    def __init__(self, width=128, dilations=(1, 2, 4, 8, 16, 32), dropout=0.05):
        super().__init__()
        if width % 8 or width < 32 or not dilations:
            raise ValueError("TCN width must be a multiple of eight and dilations cannot be empty")
        self.width = int(width)
        self.dilations = tuple(int(value) for value in dilations)
        self.input_projection = nn.Conv1d(INPUT_WIDTH, width, 1)
        self.blocks = nn.ModuleList(
            ResidualTemporalBlock(width, dilation, dropout) for dilation in self.dilations
        )
        self.output_norm = nn.GroupNorm(8, width)
        self.output_projection = nn.Conv1d(width, STATE_WIDTH, 1)
        nn.init.zeros_(self.output_projection.weight)
        nn.init.zeros_(self.output_projection.bias)

    def forward(self, features, baseline, authored_mask):
        if features.ndim != 3 or features.shape[-1] != INPUT_WIDTH:
            raise ValueError("Features must have shape (batch, frames, 624)")
        if baseline.shape != (*features.shape[:-1], STATE_WIDTH):
            raise ValueError("Baseline must have shape (batch, frames, 141)")
        if authored_mask.shape != baseline.shape or authored_mask.dtype != torch.bool:
            raise ValueError("Authored mask must be boolean and match the baseline")
        hidden = self.input_projection(features.transpose(1, 2))
        for block in self.blocks:
            hidden = block(hidden)
        residual = self.output_projection(F.silu(self.output_norm(hidden))).transpose(1, 2)
        proposal = baseline + residual.masked_fill(authored_mask, 0.0)
        proposal = normalize_state_rotations(proposal)
        return torch.where(authored_mask, baseline, proposal)

    @property
    def parameter_count(self):
        return sum(parameter.numel() for parameter in self.parameters())
