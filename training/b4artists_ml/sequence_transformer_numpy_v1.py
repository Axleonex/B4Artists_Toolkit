"""Pure NumPy inference for the compact sequence Transformer.

SPDX-License-Identifier: GPL-2.0-or-later
Research only; weights are not bundled in the addon.
"""
import math

import numpy as np


WIDTH = 128
HEADS = 4
HEAD_WIDTH = WIDTH // HEADS
LAYERS = 4


def linear(values, weights, prefix):
    return values @ weights[prefix + ".weight"].T + weights[prefix + ".bias"]


def norm(values, weights, prefix):
    mean = values.mean(axis=-1, keepdims=True)
    variance = ((values - mean) ** 2).mean(axis=-1, keepdims=True)
    return (values - mean) / np.sqrt(variance + np.float32(1e-5)) * weights[
        prefix + ".weight"
    ] + weights[prefix + ".bias"]


def gelu(values):
    coefficient = np.float32(math.sqrt(2 / math.pi))
    return np.float32(0.5) * values * (
        np.float32(1.0)
        + np.tanh(coefficient * (values + np.float32(0.044715) * values**3))
    )


def softmax(values):
    shifted = values - values.max(axis=-1, keepdims=True)
    exponential = np.exp(shifted)
    return exponential / exponential.sum(axis=-1, keepdims=True)


def forward(weights, condition):
    condition = np.asarray(condition, dtype=np.float32)
    if condition.ndim != 3 or condition.shape[-1] != 547 or not np.isfinite(condition).all():
        raise ValueError("Invalid Transformer condition")
    values = linear(condition, weights, "input")
    batch, time, _ = values.shape
    for index in range(LAYERS):
        prefix = "blocks." + str(index)
        query, key, value = np.split(linear(norm(values, weights, prefix + ".norm1"), weights, prefix + ".qkv"), 3, axis=-1)
        query = query.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        key = key.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        value = value.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        attention = softmax(query @ key.transpose(0, 1, 3, 2) / np.float32(math.sqrt(HEAD_WIDTH)))
        attended = (attention @ value).transpose(0, 2, 1, 3).reshape(batch, time, WIDTH)
        values = values + linear(attended, weights, prefix + ".attention_output")
        hidden = gelu(linear(norm(values, weights, prefix + ".norm2"), weights, prefix + ".ff1"))
        values = values + linear(hidden, weights, prefix + ".ff2")
    result = linear(norm(values, weights, "norm"), weights, "output")
    if result.shape != (*condition.shape[:2], 154) or not np.isfinite(result).all():
        raise ValueError("Invalid Transformer output")
    return result


def residual(raw, envelope):
    raw = np.asarray(raw, dtype=np.float32)
    envelope = np.asarray(envelope, dtype=np.float32)
    if raw.ndim != 3 or raw.shape[-1] != 154 or envelope.shape != (*raw.shape[:2], 153):
        raise ValueError("Invalid residual inputs")
    gate = np.float32(1.0) / (np.float32(1.0) + np.exp(-np.clip(raw[..., -1:], -80, 80)))
    result = raw[..., :153] * gate * envelope
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite residual")
    return result
