"""Pure NumPy inference and composition for the reference-mixture Transformer.

SPDX-License-Identifier: GPL-2.0-or-later
Research only; weights are not bundled in the addon.
"""
import math

import numpy as np

from sequence_transformer_numpy_v1 import gelu, linear, norm, softmax


WIDTH = 128
HEADS = 4
HEAD_WIDTH = 32
LAYERS = 4


def forward(weights, condition):
    condition = np.asarray(condition, dtype=np.float32)
    if condition.ndim != 3 or condition.shape[-1] != 853 or not np.isfinite(condition).all():
        raise ValueError("Invalid mixture-Transformer condition")
    values = linear(condition, weights, "input")
    batch, time, _ = values.shape
    for index in range(LAYERS):
        prefix = "blocks." + str(index)
        query, key, value = np.split(
            linear(norm(values, weights, prefix + ".norm1"), weights, prefix + ".qkv"),
            3,
            axis=-1,
        )
        query = query.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        key = key.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        value = value.reshape(batch, time, HEADS, HEAD_WIDTH).transpose(0, 2, 1, 3)
        attention = softmax(
            query @ key.transpose(0, 1, 3, 2) / np.float32(math.sqrt(HEAD_WIDTH))
        )
        attended = (attention @ value).transpose(0, 2, 1, 3).reshape(batch, time, WIDTH)
        values = values + linear(attended, weights, prefix + ".attention_output")
        hidden = gelu(
            linear(norm(values, weights, prefix + ".norm2"), weights, prefix + ".ff1")
        )
        values = values + linear(hidden, weights, prefix + ".ff2")
    result = linear(norm(values, weights, "norm"), weights, "output")
    if result.shape != (*condition.shape[:2], 157) or not np.isfinite(result).all():
        raise ValueError("Invalid mixture-Transformer output")
    return result


def compose(raw, references, envelope, mask=None, observed=None):
    raw = np.asarray(raw, dtype=np.float32)
    references = np.asarray(references, dtype=np.float32)
    envelope = np.asarray(envelope, dtype=np.float32)
    if raw.ndim != 3 or raw.shape[-1] != 157:
        raise ValueError("Invalid mixture output")
    if references.shape != (*raw.shape[:2], 3, 153) or envelope.shape != (*raw.shape[:2], 153):
        raise ValueError("Invalid mixture references")
    logits = raw[..., 154:157].mean(axis=1)
    weights = softmax(logits)[:, None, :, None]
    reference = np.sum(references * weights, axis=2)
    gate = np.float32(1.0) / (
        np.float32(1.0) + np.exp(-np.clip(raw[..., 153:154], -80, 80))
    )
    correction = raw[..., :153] * gate * envelope
    result = reference + correction
    if (mask is None) != (observed is None):
        raise ValueError("Mask and observed motion must be supplied together")
    if mask is not None:
        mask = np.asarray(mask, dtype=bool)
        observed = np.asarray(observed, dtype=np.float32)
        if mask.shape != result.shape or observed.shape != result.shape:
            raise ValueError("Invalid authored-motion restoration")
        result[mask] = observed[mask]
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite composed motion")
    return result, weights[:, 0, :, 0], correction
