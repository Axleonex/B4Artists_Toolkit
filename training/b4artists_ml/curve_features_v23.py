"""Known-proposal geometry descriptors; no hidden motion or correctness oracle.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from kinematic_features_v20 import features as observed_features
from kinematic_trajectory_v20 import observation_scale
from context_data import PARENTS
GRID = np.linspace(0., 1., 9)


def features(observations, predictions):
    base = observed_features(observations.features(), 'motion')
    values = np.asarray(predictions, dtype=float)
    if values.shape != (4, 9, 153) or not np.isfinite(values).all():
        raise ValueError('Four finite nine-point expert trajectories required')
    points = values.reshape(4, 9, 17, 9)[..., :3]
    line = points[0]
    amplitude = observation_scale(observations).reshape(17,9)[:,0]
    rest = np.asarray(observations.rest, dtype=float)
    if rest.shape != (17,3) or not np.isfinite(rest).all(): raise ValueError('Finite semantic rest positions required')
    parents = np.asarray(PARENTS[1:])
    lengths = np.linalg.norm(rest[1:] - rest[parents], axis=-1)
    line_lengths = np.linalg.norm(line[:,1:] - line[:,parents], axis=-1)
    delta = observations.positions[1] - observations.positions[0]
    incoming = (observations.positions[0] - observations.positions[2]) * observations.duration / observations.dt if observations.context else delta
    outgoing = (observations.positions[3] - observations.positions[1]) * observations.duration / observations.dt if observations.context else delta
    def relative(vector):
        magnitude = np.linalg.norm(vector, axis=-1)
        return np.divide(magnitude, amplitude, out=np.zeros_like(magnitude), where=amplitude>0)
    descriptors = []
    for p in points:
        speed = np.diff(p, axis=0) * 8
        acceleration = np.diff(p, n=2, axis=0) * 64
        edge_delta = abs(np.linalg.norm(p[:,1:] - p[:,parents], axis=-1) - line_lengths)
        edge = np.divide(edge_delta, lengths, out=np.zeros_like(edge_delta), where=lengths>0)
        arrays = [relative(p-line), relative(speed), relative(acceleration), relative(speed[0]-incoming), relative(speed[-1]-outgoing), edge]
        for a in arrays: descriptors.extend([float(np.mean(a)),float(np.max(a))])
    descriptors = np.log1p(np.asarray(descriptors))
    result = np.r_[base,descriptors]
    if result.shape != (596,) or not np.isfinite(result).all() or np.any(descriptors<0):
        raise ValueError('Nonfinite curve descriptors')
    return result
