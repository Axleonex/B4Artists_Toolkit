"""Constraint-conditioned temporal diffusion U-Net for hierarchy residuals.

Training dependency only. Runtime use requires a separately verified local
export, exact-control projection and deterministic refinement.
"""
import math

import torch
from torch import nn
from torch.nn import functional as F

from full_hierarchy_tcn_v1 import INPUT_WIDTH, STATE_WIDTH, normalize_state_rotations


DIFFUSION_STEPS = 100


def timestep_embedding(timestep, width):
    if timestep.ndim != 1 or width % 2:
        raise ValueError("Timestep must be a vector and embedding width must be even")
    half = width // 2
    scale = math.log(10000) / max(half - 1, 1)
    frequencies = torch.exp(torch.arange(half, device=timestep.device) * -scale)
    angles = timestep.float()[:, None] * frequencies[None]
    return torch.cat((torch.sin(angles), torch.cos(angles)), dim=-1)


class TimeResidualBlock(nn.Module):
    def __init__(self, width, time_width, dropout):
        super().__init__()
        self.norm1 = nn.GroupNorm(8, width)
        self.conv1 = nn.Conv1d(width, width, 3, padding=1)
        self.time = nn.Linear(time_width, width)
        self.norm2 = nn.GroupNorm(8, width)
        self.conv2 = nn.Conv1d(width, width, 3, padding=1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, value, time):
        hidden = self.conv1(F.silu(self.norm1(value)))
        hidden = hidden + self.time(F.silu(time))[:, :, None]
        hidden = self.conv2(self.dropout(F.silu(self.norm2(hidden))))
        return value + hidden


class ConditionalResidualDiffusionUNet(nn.Module):
    def __init__(self, channels=(128, 192, 256, 320), time_width=128, dropout=0.05):
        super().__init__()
        if len(channels) != 4 or any(value % 8 for value in channels) or time_width % 2:
            raise ValueError("Diffusion U-Net requires four group-normalized temporal scales")
        self.channels = tuple(int(value) for value in channels)
        self.time_width = int(time_width)
        self.time_mlp = nn.Sequential(
            nn.Linear(time_width, time_width * 2), nn.SiLU(), nn.Linear(time_width * 2, time_width)
        )
        self.input_projection = nn.Conv1d(INPUT_WIDTH + STATE_WIDTH, channels[0], 1)
        self.down_blocks = nn.ModuleList()
        self.downsamples = nn.ModuleList()
        for index, width in enumerate(channels):
            self.down_blocks.append(nn.ModuleList((
                TimeResidualBlock(width, time_width, dropout),
                TimeResidualBlock(width, time_width, dropout),
            )))
            if index < len(channels) - 1:
                self.downsamples.append(nn.Conv1d(width, channels[index + 1], 4, stride=2, padding=1))
        self.middle = nn.ModuleList((
            TimeResidualBlock(channels[-1], time_width, dropout),
            TimeResidualBlock(channels[-1], time_width, dropout),
        ))
        self.up_projections = nn.ModuleList()
        self.up_merges = nn.ModuleList()
        self.up_blocks = nn.ModuleList()
        for level in range(len(channels) - 2, -1, -1):
            width = channels[level]
            self.up_projections.append(nn.Conv1d(channels[level + 1], width, 1))
            self.up_merges.append(nn.Conv1d(width * 2, width, 1))
            self.up_blocks.append(nn.ModuleList((
                TimeResidualBlock(width, time_width, dropout),
                TimeResidualBlock(width, time_width, dropout),
            )))
        self.output_norm = nn.GroupNorm(8, channels[0])
        self.output_projection = nn.Conv1d(channels[0], STATE_WIDTH, 1)
        nn.init.zeros_(self.output_projection.weight)
        nn.init.zeros_(self.output_projection.bias)

    def predict_clean_residual(self, noisy_residual, features, authored_mask, timestep):
        if noisy_residual.ndim != 3 or noisy_residual.shape[-1] != STATE_WIDTH:
            raise ValueError("Noisy residual must have shape (batch, frames, 141)")
        if features.shape != (*noisy_residual.shape[:-1], INPUT_WIDTH):
            raise ValueError("Condition features must match residual frames and width")
        if authored_mask.shape != noisy_residual.shape or authored_mask.dtype != torch.bool:
            raise ValueError("Authored mask must be boolean and match the residual")
        if timestep.shape != (noisy_residual.shape[0],):
            raise ValueError("One diffusion timestep per batch item is required")
        time = self.time_mlp(timestep_embedding(timestep, self.time_width))
        hidden = self.input_projection(torch.cat((noisy_residual, features), dim=-1).transpose(1, 2))
        skips = []
        for level, blocks in enumerate(self.down_blocks):
            for block in blocks:
                hidden = block(hidden, time)
            skips.append(hidden)
            if level < len(self.downsamples):
                hidden = self.downsamples[level](hidden)
        for block in self.middle:
            hidden = block(hidden, time)
        for index, level in enumerate(range(len(self.channels) - 2, -1, -1)):
            skip = skips[level]
            hidden = F.interpolate(hidden, size=skip.shape[-1], mode="linear", align_corners=False)
            hidden = self.up_projections[index](hidden)
            hidden = self.up_merges[index](torch.cat((hidden, skip), dim=1))
            for block in self.up_blocks[index]:
                hidden = block(hidden, time)
        result = self.output_projection(F.silu(self.output_norm(hidden))).transpose(1, 2)
        return result.masked_fill(authored_mask, 0.0)

    def compose(self, clean_residual, baseline, authored_mask):
        if clean_residual.shape != baseline.shape or authored_mask.shape != baseline.shape:
            raise ValueError("Residual, baseline and mask shapes must match")
        proposal = normalize_state_rotations(baseline + clean_residual.masked_fill(authored_mask, 0.0))
        return torch.where(authored_mask, baseline, proposal)

    @property
    def parameter_count(self):
        return sum(parameter.numel() for parameter in self.parameters())


def alpha_bars(device, dtype=torch.float32):
    betas = torch.linspace(1e-4, 0.02, DIFFUSION_STEPS, device=device, dtype=dtype)
    return torch.cumprod(1 - betas, dim=0)


def q_sample(clean_residual, authored_mask, timestep, noise=None):
    if noise is None:
        noise = torch.randn_like(clean_residual)
    if noise.shape != clean_residual.shape or authored_mask.shape != clean_residual.shape:
        raise ValueError("Diffusion sample tensors must have matching shapes")
    bars = alpha_bars(clean_residual.device, clean_residual.dtype)[timestep]
    view = bars.reshape(len(bars), 1, 1)
    value = torch.sqrt(view) * clean_residual + torch.sqrt(1 - view) * noise
    return value.masked_fill(authored_mask, 0.0), noise.masked_fill(authored_mask, 0.0)


def ddim_sample(model, features, baseline, authored_mask, steps, seed):
    if steps not in (4, 8, 12):
        raise ValueError("Qualified DDIM step counts are 4, 8 or 12")
    generator = torch.Generator(device=baseline.device)
    generator.manual_seed(int(seed))
    residual = torch.randn(baseline.shape, generator=generator, device=baseline.device, dtype=baseline.dtype)
    residual = residual.masked_fill(authored_mask, 0.0)
    schedule = torch.linspace(DIFFUSION_STEPS - 1, 0, steps, device=baseline.device).round().long()
    bars = alpha_bars(baseline.device, baseline.dtype)
    clean = torch.zeros_like(residual)
    for index, timestep in enumerate(schedule):
        batch_time = timestep.expand(baseline.shape[0])
        clean = model.predict_clean_residual(residual, features, authored_mask, batch_time)
        if index == len(schedule) - 1:
            residual = clean
            break
        current = bars[timestep]
        following = bars[schedule[index + 1]]
        epsilon = (residual - torch.sqrt(current) * clean) / torch.sqrt(1 - current)
        residual = torch.sqrt(following) * clean + torch.sqrt(1 - following) * epsilon
        residual = residual.masked_fill(authored_mask, 0.0)
    return model.compose(residual, baseline, authored_mask)
