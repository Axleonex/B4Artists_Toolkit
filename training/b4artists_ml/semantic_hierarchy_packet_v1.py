"""Versioned fixed-offset local hierarchy packet for real humanoid rigs.

The product-facing graph contains the 17 animator-semantic body joints. Richer
source skeletons remain adapter detail. This module performs no model inference.
"""
from dataclasses import dataclass

import numpy as np

from context_data import NAMES, PARENTS
from rig_observations import SCHEMA as OBSERVATION_SCHEMA, _project_rotations
from temporal_data import rotation6


SCHEMA = "b4ml-semantic-hierarchy-packet-v1"
JOINTS = len(NAMES)
STATE_WIDTH = 3 + JOINTS * 6


@dataclass(frozen=True)
class SemanticHierarchyPacket:
    root_positions: np.ndarray
    local_rotations: np.ndarray
    offsets: np.ndarray
    dt: float
    duration: float
    context: bool
    reconstruction_error: float
    names: tuple = NAMES
    parents: tuple = PARENTS
    schema: str = SCHEMA

    def world(self):
        frames = len(self.root_positions)
        positions = np.empty((frames, JOINTS, 3), dtype=np.float64)
        rotations = np.empty((frames, JOINTS, 3, 3), dtype=np.float64)
        positions[:, 0] = self.root_positions
        rotations[:, 0] = self.local_rotations[:, 0]
        for child, parent in enumerate(self.parents[1:], 1):
            rotations[:, child] = rotations[:, parent] @ self.local_rotations[:, child]
            positions[:, child] = positions[:, parent] + np.einsum(
                "fij,j->fi", rotations[:, parent], self.offsets[child]
            )
        return positions, rotations

    def state(self):
        return np.concatenate(
            (self.root_positions, rotation6(self.local_rotations).reshape(len(self.root_positions), -1)),
            axis=-1,
        ).astype(np.float32)


def packet(observations, *, position_tolerance=2e-4):
    if getattr(observations, "schema", None) != OBSERVATION_SCHEMA:
        raise ValueError("Unsupported real-rig observation schema")
    if not np.isfinite(position_tolerance) or position_tolerance <= 0:
        raise ValueError("Positive hierarchy reconstruction tolerance required")
    positions = np.asarray(observations.positions, dtype=np.float64)
    world_rotations = np.asarray(observations.rotations, dtype=np.float64)
    if positions.shape != (4, JOINTS, 3) or world_rotations.shape != (4, JOINTS, 3, 3):
        raise ValueError("Expected four known poses for 17 semantic joints")
    local = np.empty_like(world_rotations)
    local[:, 0] = world_rotations[:, 0]
    offsets = np.zeros((JOINTS, 3), dtype=np.float64)
    for child, parent in enumerate(PARENTS[1:], 1):
        local[:, child] = np.swapaxes(world_rotations[:, parent], -1, -2) @ world_rotations[:, child]
        offsets[child] = world_rotations[0, parent].T @ (positions[0, child] - positions[0, parent])
    local = _project_rotations(local, "semantic local rotations")
    result = SemanticHierarchyPacket(
        positions[:, 0].copy(), local, offsets, float(observations.dt),
        float(observations.duration), bool(observations.context), 0.0,
    )
    reconstructed_positions, reconstructed_rotations = result.world()
    position_error = float(np.max(np.linalg.norm(reconstructed_positions - positions, axis=-1)))
    rotation_error = float(np.max(np.abs(reconstructed_rotations - world_rotations)))
    if position_error > position_tolerance:
        raise ValueError(
            f"Semantic rig is not a fixed-offset hierarchy: {position_error:.9g} body scales"
        )
    if rotation_error > 2e-10:
        raise ValueError("Semantic local rotations failed world reconstruction")
    if result.state().shape != (4, STATE_WIDTH):
        raise ValueError("Unexpected semantic hierarchy state width")
    object.__setattr__(result, "reconstruction_error", position_error)
    return result
