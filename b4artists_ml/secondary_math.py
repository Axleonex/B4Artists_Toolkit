"""Host-independent deterministic secondary-motion dynamics.

SPDX-License-Identifier: GPL-2.0-or-later

This module contains no learned parameters.  It uses an unconditionally stable
implicit spring step so the same request remains finite at ordinary animation
frame rates and at the deliberately hostile rates covered by the tests.
"""
import math
import numpy as np


CONTROL_FORCE_LIMIT = 1_000_000.0
CONTROL_MASS_MIN = 0.001
CONTROL_MASS_MAX = 10_000.0
CONTROL_ACCELERATION_LIMIT = 100.0
CONTROL_OFFSET_LIMIT = 1_000.0
CONTROL_INERTIA_MIN = 0.001
CONTROL_INERTIA_MAX = 1_000_000.0
CONTROL_ANGULAR_ACCELERATION_LIMIT = 100.0


def validate_control_acceleration(value):
    """Return one finite, bounded per-control world acceleration."""
    try:
        components = tuple(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Control acceleration must contain three numeric values") from exc
    if (len(components) != 3
            or any(isinstance(item, (bool, np.bool_))
                   or not isinstance(item, (int, float, np.integer, np.floating))
                   for item in components)):
        raise ValueError("Control acceleration must contain three numeric values")
    acceleration = np.asarray(components, dtype=float)
    if (not np.isfinite(acceleration).all()
            or np.any(np.abs(acceleration) > CONTROL_ACCELERATION_LIMIT)):
        raise ValueError("Control acceleration exceeds the acceleration limit")
    return acceleration


def control_load_acceleration(force, mass):
    """Validate one authored control load and return its world acceleration.

    Force is expressed in kg * scene-units / second squared and mass in kg.
    Keeping this conversion host independent makes the stored request and its
    numerical effect directly reproducible outside Blender.
    """
    try:
        components = tuple(force)
    except (TypeError, ValueError) as exc:
        raise ValueError("Control force must contain three numeric values") from exc
    if (len(components) != 3
            or any(isinstance(value, (bool, np.bool_))
                   or not isinstance(value, (int, float, np.integer, np.floating))
                   for value in components)):
        raise ValueError("Control force must contain three numeric values")
    vector = np.asarray(components, dtype=float)
    if (not np.isfinite(vector).all()
            or np.any(np.abs(vector) > CONTROL_FORCE_LIMIT)):
        raise ValueError("Control force must contain three finite values within the force limit")
    if (isinstance(mass, (bool, np.bool_)) or not isinstance(mass, (int, float, np.integer, np.floating))
            or not math.isfinite(float(mass))
            or not CONTROL_MASS_MIN <= float(mass) <= CONTROL_MASS_MAX):
        raise ValueError("Control mass must be finite and within the mass limits")
    try:
        return validate_control_acceleration(vector / float(mass))
    except ValueError as exc:
        raise ValueError("Control force divided by mass exceeds the acceleration limit") from exc


def validate_control_torque_settings(force, offset, rotational_inertia):
    """Validate bounded force-at-offset inputs independently of pose samples."""
    # Validate force independently from linear acceleration so a large force
    # can remain valid when paired with proportionally large mass and inertia.
    try:
        force_components = tuple(force)
        offset_components = tuple(offset)
    except (TypeError, ValueError) as exc:
        raise ValueError("Control force and offset must contain three numeric values") from exc
    numeric = (int, float, np.integer, np.floating)
    if (len(force_components) != 3 or len(offset_components) != 3
            or any(isinstance(value, (bool, np.bool_)) or not isinstance(value, numeric)
                   for value in force_components + offset_components)):
        raise ValueError("Control force and offset must contain three numeric values")
    force_vector = np.asarray(force_components, dtype=float)
    local_offset = np.asarray(offset_components, dtype=float)
    if (not np.isfinite(force_vector).all()
            or np.any(np.abs(force_vector) > CONTROL_FORCE_LIMIT)):
        raise ValueError("Control force must contain three finite values within the force limit")
    if (not np.isfinite(local_offset).all()
            or np.any(np.abs(local_offset) > CONTROL_OFFSET_LIMIT)):
        raise ValueError("Control offset must contain three finite values within the offset limit")
    if (isinstance(rotational_inertia, (bool, np.bool_))
            or not isinstance(rotational_inertia, numeric)
            or not math.isfinite(float(rotational_inertia))
            or not CONTROL_INERTIA_MIN <= float(rotational_inertia) <= CONTROL_INERTIA_MAX):
        raise ValueError("Control rotational inertia must be finite and within the inertia limits")
    maximum = (float(np.linalg.norm(force_vector))
               * float(np.linalg.norm(local_offset)) / float(rotational_inertia))
    if not math.isfinite(maximum) or maximum > CONTROL_ANGULAR_ACCELERATION_LIMIT:
        raise ValueError("Control force and offset divided by inertia exceed the angular acceleration limit")
    return force_vector, local_offset, float(rotational_inertia)


def control_load_angular_acceleration(force, offset, rotational_inertia, orientations):
    """Return world torque and angular acceleration for a local force offset.

    ``force`` is constant in world space. ``offset`` is authored in the
    control's local space and rotated by each target WXYZ orientation. The
    scalar rotational inertia is expressed in kg * scene-units squared.
    """
    force_vector, local_offset, inertia = validate_control_torque_settings(
        force, offset, rotational_inertia)
    rotations = normalize_quaternions(orientations)
    vector = np.broadcast_to(local_offset, (len(rotations), 3))
    xyz = rotations[:, 1:]
    doubled_cross = 2.0 * np.cross(xyz, vector)
    world_offsets = vector + rotations[:, :1] * doubled_cross + np.cross(xyz, doubled_cross)
    torques = np.cross(world_offsets, force_vector)
    angular = torques / inertia
    if (not np.isfinite(torques).all() or not np.isfinite(angular).all()
            or np.any(np.linalg.norm(angular, axis=1) > CONTROL_ANGULAR_ACCELERATION_LIMIT)):
        raise ValueError("Control torque divided by inertia exceeds the angular acceleration limit")
    return torques, angular


def validate_settings(*, frequency, damping, air_friction, strength, blend_frames, dt):
    values = np.asarray((frequency, damping, air_friction, strength, blend_frames, dt), dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Secondary-motion settings must be finite")
    if not 0.05 <= frequency <= 30.0:
        raise ValueError("Secondary frequency must be between 0.05 and 30 Hz")
    if not 0.0 <= damping <= 4.0:
        raise ValueError("Secondary damping must be between 0 and 4")
    if not 0.0 <= air_friction <= 20.0:
        raise ValueError("Secondary air friction must be between 0 and 20")
    if not 0.0 <= strength <= 1.0:
        raise ValueError("Secondary strength must be between 0 and 1")
    if not 0.0 <= blend_frames <= 240.0:
        raise ValueError("Secondary boundary blend must be between 0 and 240 frames")
    if dt <= 0.0:
        raise ValueError("Secondary-motion sample time must be positive")


def boundary_envelope(frames, blend_frames):
    """Smooth zero-to-one-to-zero weights with exact endpoint preservation."""
    t = np.asarray(frames, dtype=float)
    if t.ndim != 1 or len(t) < 2 or not np.isfinite(t).all() or np.any(np.diff(t) <= 0):
        raise ValueError("Increasing finite secondary-motion frames required")
    if not math.isfinite(blend_frames) or blend_frames < 0:
        raise ValueError("Boundary blend must be finite and nonnegative")
    if blend_frames == 0:
        result = np.ones(len(t), dtype=float)
        result[[0, -1]] = 0.0
        return result
    ramp = np.minimum((t - t[0]) / blend_frames, (t[-1] - t) / blend_frames)
    ramp = np.clip(ramp, 0.0, 1.0)
    return ramp * ramp * (3.0 - 2.0 * ramp)


def priority_envelope(frames, priority_frames, blend_frames):
    """Smooth correction weights that are exactly zero at every priority pose."""
    t = np.asarray(frames, dtype=float)
    priorities = np.asarray(priority_frames, dtype=float)
    if (t.ndim != 1 or priorities.ndim != 1 or len(t) < 2 or len(priorities) < 2 or
            not np.isfinite(t).all() or not np.isfinite(priorities).all() or
            np.any(np.diff(t) <= 0) or np.any(np.diff(priorities) <= 0) or
            priorities[0] < t[0] or priorities[-1] > t[-1]):
        raise ValueError("Increasing finite frames and priorities required")
    if not math.isfinite(blend_frames) or blend_frames < 0:
        raise ValueError("Priority blend must be finite and nonnegative")
    distance = np.min(np.abs(t[:, None] - priorities[None, :]), axis=1)
    if blend_frames == 0:
        return (distance > 1e-10).astype(float)
    ramp = np.clip(distance / blend_frames, 0.0, 1.0)
    return ramp * ramp * (3.0 - 2.0 * ramp)


def follow_vectors(values, frame_steps, *, dt, frequency, damping, air_friction):
    """Follow vector targets with a stable implicit mass-spring update.

    ``frame_steps`` contains the positive frame distance from each preceding
    sample. ``dt`` is seconds per frame. The first result equals the first
    target, making initialization deterministic and source preserving.
    """
    target = np.asarray(values, dtype=float)
    steps = np.asarray(frame_steps, dtype=float)
    if target.ndim < 2 or len(target) < 2 or steps.shape != (len(target) - 1,):
        raise ValueError("Secondary targets and frame steps disagree")
    if not np.isfinite(target).all() or not np.isfinite(steps).all() or np.any(steps <= 0):
        raise ValueError("Secondary samples must be finite and increasing")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=0.0, blend_frames=0.0, dt=dt)
    omega = 2.0 * math.pi * frequency
    stiffness = omega * omega
    drag = 2.0 * damping * omega + air_friction
    result = np.empty_like(target)
    result[0] = target[0]
    velocity = np.zeros(target.shape[1:], dtype=float)
    current = target[0].copy()
    for index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
        velocity = (velocity + seconds * stiffness * (target[index] - current)) / denominator
        current = current + seconds * velocity
        result[index] = current
    if not np.isfinite(result).all():
        raise ValueError("Secondary-motion dynamics produced nonfinite output")
    return result


def normalize_quaternions(values):
    q = np.asarray(values, dtype=float).copy()
    if q.ndim != 2 or q.shape[1] != 4 or not np.isfinite(q).all():
        raise ValueError("Finite WXYZ quaternions required")
    lengths = np.linalg.norm(q, axis=1)
    if np.any(lengths < 1e-10):
        raise ValueError("Zero-length quaternion")
    q /= lengths[:, None]
    for index in range(1, len(q)):
        if np.dot(q[index - 1], q[index]) < 0:
            q[index] *= -1
    return q


def _mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array((aw*bw-ax*bx-ay*by-az*bz,
                     aw*bx+ax*bw+ay*bz-az*by,
                     aw*by-ax*bz+ay*bw+az*bx,
                     aw*bz+ax*by-ay*bx+az*bw), dtype=float)


def _rotvec(q):
    value = np.asarray(q, dtype=float)
    if value[0] < 0:
        value = -value
    length = float(np.linalg.norm(value[1:]))
    if length < 1e-12:
        return 2.0 * value[1:]
    return value[1:] * (2.0 * math.atan2(length, float(value[0])) / length)


def _from_rotvec(value):
    vector = np.asarray(value, dtype=float)
    angle = float(np.linalg.norm(vector))
    if angle < 1e-12:
        q = np.r_[1.0, vector * 0.5]
        return q / np.linalg.norm(q)
    half = angle * 0.5
    return np.r_[math.cos(half), vector * (math.sin(half) / angle)]


def _slerp(a, b, amount):
    dot = float(np.dot(a, b))
    if dot < 0:
        b = -b
        dot = -dot
    dot = min(1.0, max(-1.0, dot))
    if dot > 0.9995:
        q = a + amount * (b - a)
        return q / np.linalg.norm(q)
    angle = math.acos(dot)
    scale = math.sin(angle)
    return (math.sin((1.0-amount)*angle)/scale)*a + (math.sin(amount*angle)/scale)*b


def follow_quaternions(values, frame_steps, *, dt, frequency, damping, air_friction,
                       strength, envelope):
    """Stable rotational follower, blended back to authored target rotations."""
    target = normalize_quaternions(values)
    steps = np.asarray(frame_steps, dtype=float)
    weights = np.asarray(envelope, dtype=float)
    if steps.shape != (len(target)-1,) or weights.shape != (len(target),):
        raise ValueError("Quaternion secondary-motion samples disagree")
    if (not np.isfinite(steps).all() or np.any(steps<=0)
            or not np.isfinite(weights).all()
            or np.any((weights < 0) | (weights > 1))):
        raise ValueError("Secondary-motion envelope must be within zero and one")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=0.0, dt=dt)
    omega = 2.0 * math.pi * frequency
    stiffness = omega * omega
    drag = 2.0 * damping * omega + air_friction
    current = target[0].copy()
    velocity = np.zeros(3, dtype=float)
    result = np.empty_like(target)
    result[0] = target[0]
    for index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        error = _rotvec(_mul(target[index], np.array((current[0], -current[1], -current[2], -current[3]))))
        denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
        velocity = (velocity + seconds * stiffness * error) / denominator
        current = _mul(_from_rotvec(seconds * velocity), current)
        current /= np.linalg.norm(current)
        result[index] = _slerp(target[index], current, strength * weights[index])
    result[0] = target[0]
    result[-1] = target[-1]
    return normalize_quaternions(result)


def follow_forced_quaternions(values, frame_steps, *, dt, frequency, damping,
                              air_friction, strength, envelope,
                              angular_accelerations):
    """Stable rotational follower with bounded world angular acceleration."""
    source = np.asarray(values, dtype=float)
    if source.ndim != 2 or source.shape[1] != 4:
        raise ValueError("Finite WXYZ quaternions required")
    raw_forcing = np.asarray(angular_accelerations, dtype=object)
    if any(isinstance(value, (bool, np.bool_)) for value in raw_forcing.flat):
        raise ValueError("Angular acceleration must contain numeric values, not booleans")
    forcing = np.asarray(angular_accelerations, dtype=float)
    if forcing.shape != (len(source), 3) or not np.isfinite(forcing).all():
        raise ValueError("Angular acceleration must match finite quaternion samples")
    if np.any(np.linalg.norm(forcing, axis=1) > CONTROL_ANGULAR_ACCELERATION_LIMIT):
        raise ValueError("Control angular acceleration exceeds the angular acceleration limit")
    if not np.any(forcing != 0.0):
        return follow_quaternions(
            values, frame_steps, dt=dt, frequency=frequency, damping=damping,
            air_friction=air_friction, strength=strength, envelope=envelope)
    target = normalize_quaternions(source)
    steps = np.asarray(frame_steps, dtype=float)
    weights = np.asarray(envelope, dtype=float)
    if steps.shape != (len(target)-1,) or weights.shape != (len(target),):
        raise ValueError("Forced quaternion secondary-motion samples disagree")
    if (not np.isfinite(steps).all() or np.any(steps<=0)
            or not np.isfinite(weights).all()
            or np.any((weights < 0) | (weights > 1))):
        raise ValueError("Secondary-motion envelope must be within zero and one")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=0.0, dt=dt)
    omega = 2.0 * math.pi * frequency
    stiffness = omega * omega
    drag = 2.0 * damping * omega + air_friction
    current = target[0].copy()
    velocity = np.zeros(3, dtype=float)
    result = np.empty_like(target)
    result[0] = target[0]
    for index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        inverse = np.array((current[0], -current[1], -current[2], -current[3]))
        error = _rotvec(_mul(target[index], inverse))
        denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
        velocity = (velocity + seconds * stiffness * error
                    + seconds * forcing[index]) / denominator
        current = _mul(_from_rotvec(seconds * velocity), current)
        current /= np.linalg.norm(current)
        result[index] = _slerp(target[index], current, strength * weights[index])
    result[0] = target[0]
    result[-1] = target[-1]
    return normalize_quaternions(result)


def follow_quaternion_chain(values, frame_steps, *, dt, frequency, damping,
                            air_friction, strength, envelope, propagation):
    """Follow an ordered local-rotation chain with parent-lag propagation.

    The input shape is ``(samples, controls, 4)`` in WXYZ order.  A zero
    propagation value is exactly the independent quaternion follower.  At
    larger values, each child follows a fraction of its parent's simulated
    lag and responds more softly with depth.  This is a bounded rotational
    control-chain model; the host rig hierarchy preserves physical bone
    lengths when the resulting local rotations are evaluated.
    """
    source = np.asarray(values, dtype=float)
    steps = np.asarray(frame_steps, dtype=float)
    weights = np.asarray(envelope, dtype=float)
    if source.ndim != 3 or source.shape[2] != 4 or source.shape[1] < 2:
        raise ValueError("Secondary rotation chain requires at least two quaternion controls")
    if steps.shape != (len(source)-1,) or weights.shape != (len(source),):
        raise ValueError("Secondary rotation-chain samples disagree")
    if (not np.isfinite(source).all() or not np.isfinite(steps).all()
            or np.any(steps <= 0) or not np.isfinite(weights).all()
            or np.any((weights < 0) | (weights > 1))):
        raise ValueError("Secondary rotation-chain samples must be finite and increasing")
    if not math.isfinite(propagation) or not 0.0 <= propagation <= 1.0:
        raise ValueError("Secondary chain propagation must be between 0 and 1")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=0.0, dt=dt)
    target = np.stack(
        [normalize_quaternions(source[:, index, :]) for index in range(source.shape[1])],
        axis=1,
    )
    if propagation == 0.0:
        return np.stack([
            follow_quaternions(target[:, index, :], steps, dt=dt,
                frequency=frequency, damping=damping, air_friction=air_friction,
                strength=strength, envelope=weights)
            for index in range(target.shape[1])
        ], axis=1)
    current = target[0].copy()
    velocity = np.zeros((target.shape[1], 3), dtype=float)
    simulated = np.empty_like(target)
    simulated[0] = target[0]
    identity = np.array((1.0, 0.0, 0.0, 0.0), dtype=float)
    for sample_index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        for control_index in range(target.shape[1]):
            effective_target = target[sample_index, control_index]
            if control_index:
                parent_target = target[sample_index, control_index-1]
                parent_inverse = np.array((parent_target[0], -parent_target[1],
                                           -parent_target[2], -parent_target[3]))
                parent_lag = _mul(current[control_index-1], parent_inverse)
                propagated_lag = _slerp(identity, parent_lag, propagation)
                effective_target = _mul(effective_target, propagated_lag)
                effective_target /= np.linalg.norm(effective_target)
            current_inverse = np.array((current[control_index, 0],
                                        -current[control_index, 1],
                                        -current[control_index, 2],
                                        -current[control_index, 3]))
            error = _rotvec(_mul(effective_target, current_inverse))
            depth_scale = 1.0 + 0.35 * propagation * control_index
            omega = 2.0 * math.pi * frequency / depth_scale
            stiffness = omega * omega
            drag = 2.0 * damping * omega + air_friction
            denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
            velocity[control_index] = (
                velocity[control_index] + seconds * stiffness * error
            ) / denominator
            current[control_index] = _mul(
                _from_rotvec(seconds * velocity[control_index]),
                current[control_index],
            )
            current[control_index] /= np.linalg.norm(current[control_index])
        simulated[sample_index] = current
    result = np.empty_like(target)
    for sample_index in range(len(target)):
        amount = strength * weights[sample_index]
        for control_index in range(target.shape[1]):
            result[sample_index, control_index] = _slerp(
                target[sample_index, control_index],
                simulated[sample_index, control_index],
                amount,
            )
    result[0] = target[0]
    result[-1] = target[-1]
    return np.stack(
        [normalize_quaternions(result[:, index, :]) for index in range(result.shape[1])],
        axis=1,
    )


def follow_forced_quaternion_chain(values, frame_steps, *, dt, frequency,
                                   damping, air_friction, strength, envelope,
                                   propagation, inertias,
                                   angular_accelerations, coupling_passes=1,
                                   return_report=False):
    """Follow a local rotation chain with bounded torque and angular coupling.

    ``values`` and ``angular_accelerations`` are per-sample, per-control local
    values.  The angular follower applies the authored acceleration first, then
    exchanges equal-and-opposite weighted angular impulses over adjacent
    controls.  This preserves the chain's weighted control angular momentum,
    but is deliberately not a general rigid-body or joint-inertia solver.
    ``return_report`` exposes the deterministic conservation receipt used by
    the host-bound workflow.
    """
    source = np.asarray(values, dtype=float)
    steps = np.asarray(frame_steps, dtype=float)
    weights = np.asarray(envelope, dtype=float)
    try:
        inertia_components = tuple(inertias)
    except (TypeError, ValueError) as exc:
        raise ValueError("Control rotational inertias must contain numeric values") from exc
    if any(isinstance(value, (bool, np.bool_)) for value in inertia_components):
        raise ValueError("Control rotational inertias must contain numeric values, not booleans")
    if source.ndim != 3 or source.shape[2] != 4 or source.shape[1] < 2:
        raise ValueError("Secondary forced rotation chain requires at least two quaternion controls")
    if steps.shape != (len(source)-1,) or weights.shape != (len(source),):
        raise ValueError("Forced secondary rotation-chain samples disagree")
    raw_forcing = np.asarray(angular_accelerations, dtype=object)
    if any(isinstance(value, (bool, np.bool_)) for value in raw_forcing.flat):
        raise ValueError("Angular acceleration must contain numeric values, not booleans")
    forcing = np.asarray(angular_accelerations, dtype=float)
    if forcing.shape != (len(source), source.shape[1], 3):
        raise ValueError("Angular acceleration must match the forced quaternion chain samples")
    inertia_values = np.asarray(inertias, dtype=float)
    if (inertia_values.shape != (source.shape[1],)
            or not np.isfinite(inertia_values).all()
            or np.any(inertia_values < CONTROL_INERTIA_MIN)
            or np.any(inertia_values > CONTROL_INERTIA_MAX)):
        raise ValueError("Control rotational inertias are outside the inertia limits")
    if (not np.isfinite(source).all() or not np.isfinite(steps).all()
            or np.any(steps <= 0) or not np.isfinite(weights).all()
            or np.any((weights < 0) | (weights > 1))
            or not np.isfinite(forcing).all()
            or np.any(np.linalg.norm(forcing, axis=2) > CONTROL_ANGULAR_ACCELERATION_LIMIT)):
        raise ValueError("Forced secondary rotation-chain samples must be finite and bounded")
    if (isinstance(coupling_passes, (bool, np.bool_))
            or type(coupling_passes) is not int
            or not 1 <= coupling_passes <= 4):
        raise ValueError("Angular momentum coupling passes must be an integer between 1 and 4")
    if not math.isfinite(propagation) or not 0.0 <= propagation <= 1.0:
        raise ValueError("Secondary chain propagation must be between 0 and 1")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=0.0, dt=dt)
    target = np.stack(
        [normalize_quaternions(source[:, index, :]) for index in range(source.shape[1])],
        axis=1,
    )
    if not np.any(forcing != 0.0):
        result = follow_quaternion_chain(
            target, steps, dt=dt, frequency=frequency, damping=damping,
            air_friction=air_friction, strength=strength, envelope=weights,
            propagation=propagation)
        report = dict(angular_momentum_residual=0.0,
                      maximum_internal_angular_impulse=0.0,
                      coupling_passes=0, coupling_edges=0, coupled_samples=0)
        return (result, report) if return_report else result
    if propagation == 0.0:
        result = np.stack([
            follow_forced_quaternions(
                target[:, index, :], steps, dt=dt, frequency=frequency,
                damping=damping, air_friction=air_friction, strength=strength,
                envelope=weights, angular_accelerations=forcing[:, index, :])
            for index in range(target.shape[1])
        ], axis=1)
        report = dict(angular_momentum_residual=0.0,
                      maximum_internal_angular_impulse=0.0,
                      coupling_passes=0, coupling_edges=0, coupled_samples=0)
        return (result, report) if return_report else result
    current = target[0].copy()
    velocity = np.zeros((target.shape[1], 3), dtype=float)
    simulated = np.empty_like(target)
    simulated[0] = target[0]
    identity = np.array((1.0, 0.0, 0.0, 0.0), dtype=float)
    maximum_residual = 0.0
    maximum_impulse = 0.0
    for sample_index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        sample_start = current.copy()
        force_velocity = np.zeros_like(velocity)
        for control_index in range(target.shape[1]):
            effective_target = target[sample_index, control_index]
            if control_index:
                parent_target = target[sample_index, control_index-1]
                parent_inverse = np.array((parent_target[0], -parent_target[1],
                                           -parent_target[2], -parent_target[3]))
                parent_lag = _mul(current[control_index-1], parent_inverse)
                propagated_lag = _slerp(identity, parent_lag, propagation)
                effective_target = _mul(effective_target, propagated_lag)
                effective_target /= np.linalg.norm(effective_target)
            current_inverse = np.array((current[control_index, 0],
                                        -current[control_index, 1],
                                        -current[control_index, 2],
                                        -current[control_index, 3]))
            error = _rotvec(_mul(effective_target, current_inverse))
            depth_scale = 1.0 + 0.35 * propagation * control_index
            omega = 2.0 * math.pi * frequency / depth_scale
            stiffness = omega * omega
            drag = 2.0 * damping * omega + air_friction
            denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
            spring_velocity = (
                velocity[control_index] + seconds * stiffness * error
            ) / denominator
            force_velocity[control_index] = (
                seconds * forcing[sample_index, control_index] / denominator
            )
            velocity[control_index] = spring_velocity + force_velocity[control_index]
            # The next child observes its parent's update at this sample, just
            # as it does in the unforced chain.
            current[control_index] = _mul(
                _from_rotvec(seconds * velocity[control_index]),
                current[control_index],
            )
            current[control_index] /= np.linalg.norm(current[control_index])
        coupled_force_velocity, transfer_report = transfer_chain_angular_momentum(
            force_velocity, inertia_values, propagation, passes=coupling_passes)
        velocity += coupled_force_velocity - force_velocity
        maximum_residual = max(maximum_residual,
                               transfer_report['angular_momentum_residual'])
        maximum_impulse = max(maximum_impulse,
                              transfer_report['maximum_internal_angular_impulse'])
        # Reapply the coupled force increment from the same sample start. With
        # zero forcing this is exactly the ordinary parent-first update.
        for control_index in range(target.shape[1]):
            current[control_index] = _mul(
                _from_rotvec(seconds * velocity[control_index]),
                sample_start[control_index],
            )
            current[control_index] /= np.linalg.norm(current[control_index])
        simulated[sample_index] = current
    result = np.empty_like(target)
    for sample_index in range(len(target)):
        amount = strength * weights[sample_index]
        for control_index in range(target.shape[1]):
            result[sample_index, control_index] = _slerp(
                target[sample_index, control_index],
                simulated[sample_index, control_index],
                amount,
            )
    result[0] = target[0]
    result[-1] = target[-1]
    result = np.stack(
        [normalize_quaternions(result[:, index, :]) for index in range(result.shape[1])],
        axis=1,
    )
    report = dict(angular_momentum_residual=maximum_residual,
                  maximum_internal_angular_impulse=maximum_impulse,
                  coupling_passes=coupling_passes,
                  coupling_edges=(target.shape[1]-1) * coupling_passes,
                  coupled_samples=len(steps))
    return (result, report) if return_report else result


def transfer_chain_momentum(velocities, masses, propagation, passes=1):
    """Apply bounded internal momentum transfer over an ordered chain.

    ``velocities`` is ordered from parent to child. Each adjacent pair gets an
    equal-and-opposite impulse, so total linear momentum is unchanged to
    floating-point tolerance. Additional passes alternate direction, reducing
    directional bias when a longer chain has several coupled links. This is
    an authored procedural coupling; it is not a learned or inferred physical
    model.
    """
    values = np.asarray(velocities, dtype=float).copy()
    weights = np.asarray(masses, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3 or values.shape[0] < 2:
        raise ValueError("Momentum transfer requires at least two 3D velocities")
    if weights.shape != (values.shape[0],) or not np.isfinite(values).all():
        raise ValueError("Momentum transfer inputs must be finite and shape-matched")
    if (not np.isfinite(weights).all()
            or np.any(weights < CONTROL_MASS_MIN)
            or np.any(weights > CONTROL_MASS_MAX)):
        raise ValueError("Momentum transfer masses are outside the control mass limits")
    if (isinstance(propagation, (bool, np.bool_))
            or not isinstance(propagation, (int, float, np.integer, np.floating))
            or not math.isfinite(float(propagation))
            or not 0.0 <= float(propagation) <= 1.0):
        raise ValueError("Momentum transfer propagation must be between 0 and 1")
    if type(passes) is not int or not 1 <= passes <= 4:
        raise ValueError("Momentum transfer passes must be an integer between 1 and 4")
    before = np.sum(weights[:, None] * values, axis=0)
    maximum_impulse = 0.0
    amount = float(propagation)
    for pass_index in range(passes):
        order = (range(len(values) - 1) if pass_index % 2 == 0
                 else range(len(values) - 2, -1, -1))
        for index in order:
            reduced_mass = (weights[index] * weights[index + 1]
                            / (weights[index] + weights[index + 1]))
            impulse = reduced_mass * (values[index + 1] - values[index]) * amount
            values[index] += impulse / weights[index]
            values[index + 1] -= impulse / weights[index + 1]
            maximum_impulse = max(maximum_impulse, float(np.linalg.norm(impulse)))
    residual = float(np.linalg.norm(np.sum(weights[:, None] * values, axis=0) - before))
    tolerance = 1e-10 * max(1.0, float(np.linalg.norm(before)))
    if residual > tolerance or not np.isfinite(values).all():
        raise ValueError("Momentum transfer failed its conservation check")
    return values, dict(momentum_residual=residual,
                        maximum_internal_impulse=maximum_impulse,
                        coupling_passes=passes,
                        coupling_edges=(len(values) - 1) * passes)


def transfer_chain_angular_momentum(angular_velocities, inertias, propagation,
                                    passes=1):
    """Exchange bounded equal-and-opposite angular impulses over a chain.

    The values are angular velocities expressed in each control's local frame;
    the conserved quantity is therefore weighted control angular momentum, not
    world-space rigid-body angular momentum.
    """
    values = np.asarray(angular_velocities, dtype=float).copy()
    weights = np.asarray(inertias, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3 or values.shape[0] < 2:
        raise ValueError("Angular momentum transfer requires at least two 3D velocities")
    if weights.shape != (values.shape[0],) or not np.isfinite(values).all():
        raise ValueError("Angular momentum transfer inputs must be finite and shape-matched")
    if (not np.isfinite(weights).all()
            or np.any(weights < CONTROL_INERTIA_MIN)
            or np.any(weights > CONTROL_INERTIA_MAX)):
        raise ValueError("Angular momentum transfer inertias are outside the inertia limits")
    if (isinstance(propagation, (bool, np.bool_))
            or not isinstance(propagation, (int, float, np.integer, np.floating))
            or not math.isfinite(float(propagation))
            or not 0.0 <= float(propagation) <= 1.0):
        raise ValueError("Angular momentum transfer propagation must be between 0 and 1")
    if type(passes) is not int or not 1 <= passes <= 4:
        raise ValueError("Angular momentum transfer passes must be an integer between 1 and 4")
    before = np.sum(weights[:, None] * values, axis=0)
    maximum_impulse = 0.0
    amount = float(propagation)
    for pass_index in range(passes):
        order = (range(len(values) - 1) if pass_index % 2 == 0
                 else range(len(values) - 2, -1, -1))
        for index in order:
            reduced_inertia = (weights[index] * weights[index + 1]
                               / (weights[index] + weights[index + 1]))
            impulse = reduced_inertia * (values[index + 1] - values[index]) * amount
            values[index] += impulse / weights[index]
            values[index + 1] -= impulse / weights[index + 1]
            maximum_impulse = max(maximum_impulse, float(np.linalg.norm(impulse)))
    residual = float(np.linalg.norm(np.sum(weights[:, None] * values, axis=0) - before))
    tolerance = 1e-10 * max(1.0, float(np.linalg.norm(before)))
    if residual > tolerance or not np.isfinite(values).all():
        raise ValueError("Angular momentum transfer failed its conservation check")
    return values, dict(angular_momentum_residual=residual,
                        maximum_internal_angular_impulse=maximum_impulse,
                        coupling_passes=passes,
                        coupling_edges=(len(values) - 1) * passes)


def transfer_pairwise_momentum(velocities, masses, propagation):
    """Backward-compatible one-pass parent-child momentum transfer."""
    result, report = transfer_chain_momentum(velocities, masses, propagation, passes=1)
    return result, {key: report[key]
                    for key in ("momentum_residual", "maximum_internal_impulse")}


def follow_world_vector_chain(values, frame_steps, *, dt, frequency, damping,
                              air_friction, strength, envelope, propagation,
                              masses, accelerations, collision_point=None,
                              collision_normal=None, clearance=0.0,
                              restitution=0.0, surface_friction=0.0,
                              collision_triangles=None,
                              collision_sphere_center=None,
                              collision_sphere_radius=None,
                              collision_spheres=None,
                              collision_sphere_trajectories=None,
                              collision_sphere_continuous=False,
                              collision_capsule_start=None,
                              collision_capsule_end=None,
                              collision_capsule_radius=None,
                              collision_capsule_trajectories=None,
                              collision_mesh_triangles=None,
                              collision_mesh_trajectories=None,
                              collision_mesh_closed=False,
                              collision_mesh_volume_radius=0.0,
                              collision_mesh_continuous=False,
                              collision_capsule_continuous=False,
                              coupling_passes=1, compound_plane_spheres=False,
                              compound_static_capsule=False,
                              compound_moving_capsule=False,
                              compound_static_mesh=False):
    """Follow world-space location targets with bounded chain coupling.

    The input shape is ``(samples, controls, 3)`` in direct parent-to-child
    order.  ``accelerations`` contains one authored world acceleration per
    control (gravity and scene-wide acceleration may already be included by
    the caller).  The implicit follower supplies target tracking; adjacent
    controls then exchange equal-and-opposite momentum. ``coupling_passes``
    bounds alternating adjacent-link passes for longer chains. An optional static
    planar or surface-mesh collider, one sampled moving/deforming surface mesh,
    or one static/directly animated spherical or capsule collider, applies an external
    response after internal transfer; priority endpoints and the supplied
    envelope remain exact. A continuous sweep is available for one static
    closed surface mesh, including the exact finite-volume variant when a
    positive volume radius is supplied. Sampled moving/deforming meshes use a
    bounded interpolation sweep, with the same finite-volume helper for a
    positive volume radius. Static sphere sets and sampled moving or uniformly
    scaling sphere sets are resolved in a deterministic canonical order, with
    repeated bounded projection for overlaps. Capsule endpoint rotation is
    deliberately approximated by midpoint translation. Continuous sphere sweeps
    select the earliest hit from the bounded sphere set; capsule sweeps remain
    bounded to one collider. An opt-in compound mode
    may combine the authored planar support surface with a static sphere set;
    the plane is resolved first and the sphere set is then projected in
    deterministic order. An explicitly enabled static compound may add one
    static capsule and one closed static triangle mesh to the support-plus-
    sphere set. A separate bounded mode permits one directly sampled moving
    capsule alongside the support and static sphere set. A second bounded
    compound form permits at most two directly sampled moving spheres alongside
    the support plane, with an optional static sphere set but without capsules
    or meshes. Moving meshes and general multi-collider rigid-body response
    remain outside this path.
    """
    target = np.asarray(values, dtype=float)
    steps = np.asarray(frame_steps, dtype=float)
    weights = np.asarray(envelope, dtype=float)
    masses_array = np.asarray(masses, dtype=float)
    forcing = np.asarray(accelerations, dtype=float)
    if (target.ndim != 3 or target.shape[1] < 2 or target.shape[2] != 3
            or steps.shape != (len(target) - 1,)
            or weights.shape != (len(target),)
            or masses_array.shape != (target.shape[1],)
            or forcing.shape != (target.shape[1], 3)):
        raise ValueError("World secondary chain samples disagree")
    if (not np.isfinite(target).all() or not np.isfinite(steps).all()
            or np.any(steps <= 0) or not np.isfinite(weights).all()
            or np.any((weights < 0) | (weights > 1))):
        raise ValueError("World secondary chain samples must be finite and increasing")
    if (not np.isfinite(masses_array).all()
            or np.any(masses_array < CONTROL_MASS_MIN)
            or np.any(masses_array > CONTROL_MASS_MAX)):
        raise ValueError("World secondary chain masses are outside the control mass limits")
    if (not np.isfinite(forcing).all()
            or np.any(np.abs(forcing) > 1000.0)):
        raise ValueError("World secondary chain acceleration is outside the bounded limit")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=0.0, dt=dt)
    _, plane_point, plane_normal = validate_world_settings(
        gravity=(0.0, 0.0, 0.0), gravity_scale=0.0,
        collision_point=collision_point, collision_normal=collision_normal,
        clearance=clearance, restitution=restitution,
        surface_friction=surface_friction)
    triangles = (validate_mesh_triangles(collision_triangles)
                 if collision_triangles is not None else None)
    if type(compound_plane_spheres) is not bool:
        raise ValueError("World secondary chain compound collider flag must be boolean")
    if type(compound_static_capsule) is not bool:
        raise ValueError("World secondary chain compound capsule flag must be boolean")
    if type(compound_moving_capsule) is not bool:
        raise ValueError("World secondary chain moving compound capsule flag must be boolean")
    if type(compound_static_mesh) is not bool:
        raise ValueError("World secondary chain compound mesh flag must be boolean")
    sphere_center = sphere_radius = None
    static_spheres = ()
    if collision_spheres is not None:
        if collision_sphere_center is not None or collision_sphere_radius is not None:
            raise ValueError("World secondary chain accepts one static sphere input form")
        if plane_point is not None and not compound_plane_spheres:
            raise ValueError("World secondary chain accepts one planar or spherical collider")
        static_spheres = validate_sphere_colliders(collision_spheres)
    elif collision_sphere_center is not None or collision_sphere_radius is not None:
        if plane_point is not None and not compound_plane_spheres:
            raise ValueError("World secondary chain accepts one planar or spherical collider")
        if collision_sphere_center is None or collision_sphere_radius is None:
            raise ValueError("World secondary chain sphere center and radius must be provided together")
        sphere_center, sphere_radius = validate_sphere_collider(
            collision_sphere_center, collision_sphere_radius)
        static_spheres = ((sphere_center, sphere_radius),)
        if triangles is not None:
            raise ValueError("World secondary chain sphere collision cannot use planar triangles")
    moving_spheres = (validate_sphere_trajectories(
        collision_sphere_trajectories, len(target))
        if collision_sphere_trajectories is not None else ())
    if static_spheres and moving_spheres and not compound_plane_spheres:
        raise ValueError(
            "World secondary chain accepts one static or moving sphere input form")
    sphere_continuous = bool(collision_sphere_continuous)
    moving_sphere_compound = bool(
        moving_spheres and plane_point is not None and compound_plane_spheres)
    if moving_sphere_compound and not 1 <= len(moving_spheres) <= 3:
        raise ValueError(
            "World secondary chain moving-sphere compound supports one to three moving spheres")
    if len(static_spheres)+len(moving_spheres)>MAX_SPHERE_COLLIDERS:
        raise ValueError(f"World secondary chain is limited to {MAX_SPHERE_COLLIDERS} sphere colliders")
    if moving_spheres and plane_point is not None and not compound_plane_spheres:
        raise ValueError(
            "World secondary chain accepts spherical collision or an enabled compound support plane")
    if compound_static_capsule and (plane_point is None or not static_spheres
                                    or moving_spheres):
        raise ValueError(
            "World secondary chain compound capsule requires a static support plane and static spheres")
    capsule = None
    capsule_trajectory = (validate_capsule_trajectories(
        collision_capsule_trajectories, len(target))
        if collision_capsule_trajectories is not None else None)
    capsule_continuous = bool(collision_capsule_continuous)
    moving_capsule_compound = bool(
        compound_moving_capsule and capsule_trajectory is not None
        and plane_point is not None and compound_plane_spheres
        and static_spheres and not moving_spheres)
    if compound_moving_capsule and not moving_capsule_compound:
        raise ValueError(
            "World secondary chain moving compound capsule requires a moving capsule, support plane, and static spheres")
    if moving_capsule_compound and compound_static_mesh:
        raise ValueError(
            "World secondary chain moving compound capsule does not combine with a compound mesh")
    if (collision_capsule_start is not None or collision_capsule_end is not None
            or collision_capsule_radius is not None):
        if capsule_trajectory is not None:
            raise ValueError(
                "World secondary chain accepts one static or moving capsule input form")
        if ((plane_point is not None or static_spheres or moving_spheres)
                and not compound_static_capsule):
            raise ValueError("World secondary chain accepts one planar, spherical, or capsule collider")
        if (collision_capsule_start is None or collision_capsule_end is None
                or collision_capsule_radius is None):
            raise ValueError("World secondary chain capsule endpoints and radius must be provided together")
        capsule = validate_capsule_collider(
            collision_capsule_start, collision_capsule_end, collision_capsule_radius)
        if triangles is not None:
            raise ValueError("World secondary chain capsule collision cannot use planar triangles")
    if capsule_trajectory is not None:
        if ((plane_point is not None or static_spheres or moving_spheres
             or triangles is not None) and not moving_capsule_compound):
            raise ValueError(
                "World secondary chain accepts one planar, spherical, or capsule collider")
    if capsule_continuous and capsule is None and capsule_trajectory is None:
        raise ValueError(
            "World secondary chain continuous capsule collision requires a capsule")
    if sphere_continuous and not (static_spheres or moving_spheres):
        raise ValueError(
            "World secondary chain continuous sphere collision requires a sphere")
    mesh = (validate_mesh_triangles(collision_mesh_triangles)
            if collision_mesh_triangles is not None else None)
    mesh_trajectory = (validate_mesh_trajectories(
        collision_mesh_trajectories, len(target))
        if collision_mesh_trajectories is not None else None)
    if mesh is not None and mesh_trajectory is not None:
        raise ValueError("World secondary chain accepts one static or sampled mesh input form")
    if compound_static_mesh and (
            plane_point is None or not static_spheres or mesh is None
            or mesh_trajectory is not None or not bool(collision_mesh_closed)
            or bool(collision_mesh_continuous)):
        raise ValueError(
            "World secondary chain compound mesh requires a static closed mesh, support plane, and static spheres")
    if mesh is not None or mesh_trajectory is not None:
        if ((not compound_static_mesh and (
                plane_point is not None or static_spheres
                or moving_spheres or capsule is not None
                or capsule_trajectory is not None))
                or (compound_static_mesh and (
                    moving_spheres or capsule_trajectory is not None))):
            raise ValueError(
                "World secondary chain accepts one planar, spherical, capsule, or mesh collider")
    if compound_static_capsule and capsule is None:
        raise ValueError(
            "World secondary chain compound capsule requires static capsule endpoints")
    if compound_static_capsule and capsule_continuous:
        raise ValueError(
            "World secondary chain compound capsule supports only a static capsule")
    if triangles is not None and mesh is not None:
        raise ValueError("World secondary chain mesh collision cannot use planar triangles")
    if (isinstance(collision_mesh_volume_radius, (bool, np.bool_))
            or not math.isfinite(float(collision_mesh_volume_radius))
            or float(collision_mesh_volume_radius) < 0.0):
        raise ValueError("World secondary chain mesh volume radius must be finite and nonnegative")
    if float(collision_mesh_volume_radius) > 0.0:
        if compound_static_mesh:
            raise ValueError(
                "World secondary chain compound mesh does not support finite-volume mode")
        if (mesh is None and mesh_trajectory is None) or not bool(collision_mesh_closed):
            raise ValueError(
                "World secondary chain finite-volume collision requires a closed mesh")
        if not bool(collision_mesh_continuous):
            raise ValueError(
                "World secondary chain finite-volume collision requires continuous sweep")
    if (bool(collision_mesh_continuous)
            and mesh is None and mesh_trajectory is None):
        raise ValueError("World secondary chain continuous collision requires a mesh")
    if bool(collision_mesh_continuous) and not bool(collision_mesh_closed):
        raise ValueError("World secondary chain continuous mesh collision requires a closed mesh")
    if (isinstance(propagation, (bool, np.bool_))
            or not isinstance(propagation, (int, float, np.integer, np.floating))
            or not math.isfinite(float(propagation))
            or not 0.0 <= float(propagation) <= 1.0):
        raise ValueError("World secondary chain propagation must be between 0 and 1")
    if type(coupling_passes) is not int or not 1 <= coupling_passes <= 4:
        raise ValueError("World secondary chain coupling passes must be an integer between 1 and 4")
    if float(strength) == 0.0:
        retained_penetration=0.0
        for sample_index,sample in enumerate(target):
            final_spheres=list(static_spheres)+[
                (centers[sample_index],_trajectory_radius(radii,sample_index))
                for centers,radii in moving_spheres]
            for point in sample:
                residuals=[]
                if plane_point is not None:
                    projected=point-plane_normal*float(np.dot(point-plane_point,plane_normal))
                    if triangles is None or _inside_triangles(projected,triangles):
                        residuals.append(float(clearance)-float(np.dot(point-plane_point,plane_normal)))
                residuals.extend(radius+float(clearance)-float(np.linalg.norm(point-center))
                                 for center,radius in final_spheres)
                if capsule is not None or capsule_trajectory is not None:
                    if capsule_trajectory is not None:
                        start=capsule_trajectory[0][sample_index];end=capsule_trajectory[1][sample_index]
                        radius=capsule_trajectory[2][sample_index]
                    else:start,end,radius=capsule
                    residuals.append(float(radius)+float(clearance)-float(np.linalg.norm(
                        point-_capsule_closest(point,start,end))))
                if mesh is not None or mesh_trajectory is not None:
                    active_mesh=(mesh_trajectory[sample_index]
                                 if mesh_trajectory is not None else mesh)
                    residuals.append(float(_mesh_collision_state(
                        point,active_mesh,float(clearance),bool(collision_mesh_closed),(),
                        float(collision_mesh_volume_radius))[3]))
                retained_penetration=max(retained_penetration,
                    max((max(0.0,value) for value in residuals),default=0.0))
        return target.copy(), dict(
            momentum_conservation_error=0.0,
            maximum_internal_impulse=0.0,
            coupled_samples=0,
            collision_samples=0,
            continuous_collision_samples=0,
            coupling_passes=coupling_passes,
            coupling_edges=(target.shape[1]-1)*coupling_passes,
            collision_collider_count=(len(static_spheres) + len(moving_spheres)
                                       + int(plane_point is not None)
                                       + int(compound_static_capsule and capsule is not None)
                                       + int(moving_capsule_compound and capsule_trajectory is not None)
                                       + int(compound_static_mesh and mesh is not None)
                                       + int((capsule is not None or capsule_trajectory is not None)
                                             and not (compound_static_capsule or moving_capsule_compound))
                                       + int((mesh is not None or mesh_trajectory is not None)
                                             and not compound_static_mesh)),
            collision_plane=plane_point is not None,
            collision_compound=bool(compound_plane_spheres and plane_point is not None
                                    and (static_spheres or moving_spheres)),
            collision_compound_capsule=bool(
                (compound_static_capsule and capsule is not None)
                or (moving_capsule_compound and capsule_trajectory is not None)),
            collision_compound_mesh=bool(compound_static_mesh and mesh is not None),
            max_raw_penetration=retained_penetration,
            max_penetration_after=retained_penetration)
    omega = 2.0 * math.pi * frequency
    stiffness = omega * omega
    drag = 2.0 * damping * omega + air_friction
    current = target[0].copy()
    velocity = np.zeros_like(current)
    simulated = np.empty_like(target)
    simulated[0] = current
    maximum_residual = 0.0
    maximum_impulse = 0.0
    collision_samples = 0
    continuous_collision_samples = 0
    maximum_penetration = 0.0
    maximum_penetration_after = 0.0
    for index, frame_step in enumerate(steps, 1):
        seconds = float(frame_step) * dt
        previous = current.copy()
        denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
        velocity = (velocity + seconds * stiffness * (target[index] - current)
                    + seconds * forcing) / denominator
        velocity, transfer_report = transfer_chain_momentum(
            velocity, masses_array, propagation, passes=coupling_passes)
        current = current + seconds * velocity
        if plane_point is not None:
            for control_index, point in enumerate(current):
                projected = point-plane_normal * float(
                    np.dot(point-plane_point, plane_normal))
                if triangles is not None and not _inside_triangles(projected, triangles):
                    continue
                separation = float(np.dot(point-plane_point, plane_normal) - clearance)
                if separation >= -1e-10:
                    continue
                maximum_penetration = max(maximum_penetration, -separation)
                current[control_index] = point-plane_normal * separation
                normal_speed = float(np.dot(velocity[control_index], plane_normal))
                tangent = velocity[control_index]-normal_speed*plane_normal
                if normal_speed < 0.0:
                    normal_speed = -normal_speed * float(restitution)
                velocity[control_index] = (normal_speed * plane_normal
                                           + tangent * (1.0-float(surface_friction)))
                collision_samples += 1
                if not moving_capsule_compound:
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, float(clearance)
                            - float(np.dot(current[control_index]-plane_point, plane_normal))))
        if static_spheres or moving_spheres:
            active_spheres = tuple(
                (center, float(radius), center, float(radius))
                for center, radius in static_spheres)
            active_spheres += tuple(
                (centers[index], _trajectory_radius(radii, index),
                 centers[index-1], _trajectory_radius(radii, index-1))
                for centers, radii in moving_spheres)
            active_sphere_moving = ((False,) * len(static_spheres)
                                    + (True,) * len(moving_spheres))
            for control_index, point in enumerate(current):
                if sphere_continuous:
                    swept_hit = _first_sphere_sweep_hit(
                        previous[control_index], point, active_spheres, clearance,
                        (target[index, control_index]-point, -velocity[control_index]))
                    if swept_hit is not None:
                        sphere_index, swept = swept_hit
                        projected, normal, penetration, hit = swept
                        maximum_penetration = max(maximum_penetration, penetration)
                        current[control_index] = projected
                        active_center, active_radius, previous_center, previous_radius = active_spheres[sphere_index]
                        center_velocity = (active_center-previous_center)/seconds
                        radius_velocity = (active_radius-previous_radius)/seconds
                        surface_velocity = center_velocity + normal*radius_velocity
                        relative_velocity = velocity[control_index]-surface_velocity
                        normal_speed = float(np.dot(relative_velocity, normal))
                        tangent = relative_velocity-normal_speed*normal
                        if normal_speed < 0.0:
                            normal_speed = -normal_speed*float(restitution)
                        velocity[control_index] = (
                            normal_speed*normal + tangent*(1.0-float(surface_friction))
                            + surface_velocity)
                        current[control_index] = (
                            projected + velocity[control_index]*seconds*(1.0-hit)
                            if active_sphere_moving[sphere_index] else projected)
                        extra_hits = 0
                        if active_sphere_moving[sphere_index] and hit < 1.0:
                            remaining_spheres = tuple(
                                (center, radius,
                                 np.asarray(previous_center, dtype=float)
                                 +(np.asarray(center, dtype=float)
                                   -np.asarray(previous_center, dtype=float))*hit,
                                 float(previous_radius)
                                 +(float(radius)-float(previous_radius))*hit)
                                for center, radius, previous_center, previous_radius
                                in active_spheres)
                            (current[control_index], displacement, extra_hits,
                             extra_penetration) = _resolve_moving_sphere_sweep_path(
                                projected, current[control_index], remaining_spheres,
                                clearance, restitution, surface_friction,
                                (target[index, control_index]-point,
                                 -velocity[control_index]))
                            velocity[control_index] = displacement/(
                                seconds*(1.0-hit))
                            maximum_penetration = max(
                                maximum_penetration, extra_penetration)
                        collision_samples += 1
                        collision_samples += extra_hits
                        continuous_collision_samples += 1+extra_hits
                        point = current[control_index]
                # Resolve the best bounded exterior candidate first. Evaluating
                # every active sphere and its deterministic outward alternatives
                # avoids alternating forever on overlapping sphere boundaries.
                for _ in range(8*len(active_spheres)+8):
                    candidates = []
                    for sphere_index, (active_center, active_radius, _, _) in enumerate(active_spheres):
                        separation = (float(np.linalg.norm(point-active_center))
                                      - active_radius-float(clearance))
                        if separation >= -1e-10:
                            continue
                        maximum_penetration = max(maximum_penetration, -separation)
                        others = [item[0] for other_index, item in enumerate(active_spheres)
                                  if other_index != sphere_index]
                        away = (active_center-np.mean(others, axis=0)
                                if others else np.zeros(3, dtype=float))
                        fallback = _sphere_normal(
                            point, active_center,
                            (target[index, control_index]-active_center,
                             -velocity[control_index]))
                        directions = ((fallback,) if len(active_spheres) == 1 else
                                      (point-active_center, away,
                                       target[index, control_index]-active_center,
                                       -velocity[control_index], fallback))
                        for direction_index, direction in enumerate(directions):
                            length = float(np.linalg.norm(direction))
                            if length < 1e-10:
                                continue
                            normal = direction/length
                            projected = active_center + normal * (
                                active_radius+float(clearance))
                            worst = max(
                                active_radius_other+float(clearance)
                                - float(np.linalg.norm(projected-other_center))
                                for other_center, active_radius_other, _, _
                                in active_spheres)
                            candidates.append((worst, sphere_index, direction_index,
                                               active_center, active_radius, normal,
                                               projected))
                    if not candidates:
                        break
                    (_, sphere_index, _, active_center, active_radius,
                     normal, projected) = min(candidates, key=lambda item: item[:3])
                    current[control_index] = projected
                    if active_sphere_moving[sphere_index]:
                        _, _, previous_center, previous_radius = active_spheres[sphere_index]
                        center_velocity = (active_center-previous_center) / seconds
                        radius_velocity = (active_radius-previous_radius) / seconds
                        collider_velocity = center_velocity + normal*radius_velocity
                    else:
                        collider_velocity = np.zeros(3, dtype=float)
                    relative_velocity = velocity[control_index]-collider_velocity
                    normal_speed = float(np.dot(relative_velocity, normal))
                    tangent = relative_velocity-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*float(restitution)
                    velocity[control_index] = (
                        normal_speed*normal + tangent*(1.0-float(surface_friction))
                        + collider_velocity)
                    point = current[control_index]
                    collision_samples += 1
                for active_center, active_radius, _, _ in active_spheres:
                    remaining = (active_radius+float(clearance)
                                 - float(np.linalg.norm(
                                     current[control_index]-active_center)))
                    if not moving_capsule_compound:
                        maximum_penetration_after = max(
                            maximum_penetration_after, max(0.0, remaining))
                    if remaining > 1e-8:
                        raise ValueError(
                            "World secondary chain sphere set did not converge to an exterior point")
            if compound_static_capsule:
                start, end, radius = capsule
                for control_index, point in enumerate(current):
                    closest = _capsule_closest(point, start, end)
                    distance = float(np.linalg.norm(point-closest))
                    separation = distance-radius-float(clearance)
                    if separation >= -1e-10:
                        continue
                    normal = _capsule_normal(
                        point, start, end,
                        (target[index, control_index]-closest,
                         -velocity[control_index]))
                    maximum_penetration = max(maximum_penetration, -separation)
                    current[control_index] = closest + normal * (radius+float(clearance))
                    normal_speed = float(np.dot(velocity[control_index], normal))
                    tangent = velocity[control_index]-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*float(restitution)
                    velocity[control_index] = (
                        normal_speed*normal + tangent*(1.0-float(surface_friction)))
                    collision_samples += 1
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, radius+float(clearance)
                            - float(np.linalg.norm(
                                current[control_index]-_capsule_closest(
                                    current[control_index], start, end)))))
            if moving_capsule_compound:
                previous_start = capsule_trajectory[0][index-1]
                previous_end = capsule_trajectory[1][index-1]
                previous_radius = capsule_trajectory[2][index-1]
                start = capsule_trajectory[0][index]
                end = capsule_trajectory[1][index]
                radius = capsule_trajectory[2][index]
                projection_threshold = (float(radius)+float(clearance)+1e-7)
                previous_midpoint = previous_start + 0.5 * (previous_end-previous_start)
                midpoint = start + 0.5 * (end-start)
                midpoint_velocity = (midpoint-previous_midpoint)/seconds
                radius_velocity = (radius-previous_radius)/seconds
                if (not np.isfinite(midpoint_velocity).all()
                        or not math.isfinite(float(radius_velocity))):
                    raise ValueError(
                        "World secondary chain compound capsule surface velocity was nonfinite")
                for control_index, point in enumerate(current):
                    swept = (_capsule_trajectory_sweep_hit(
                        previous[control_index], point,
                        previous_start, previous_end, previous_radius,
                        start, end, radius, clearance,
                        (target[index, control_index]-point,
                         -velocity[control_index]))
                              if capsule_continuous else None)
                    if swept is not None:
                        projected, normal, penetration, hit = swept
                        maximum_penetration = max(maximum_penetration, penetration)
                        current[control_index] = projected
                    else:
                        closest = _capsule_closest(point, start, end)
                        distance = float(np.linalg.norm(point-closest))
                        separation = distance-float(radius)-float(clearance)
                        if separation >= -1e-10:
                            continue
                        normal = _capsule_normal(
                            point, start, end,
                            (target[index, control_index]-closest,
                             -velocity[control_index]))
                        maximum_penetration = max(maximum_penetration, -separation)
                        current[control_index] = closest + normal * (
                            projection_threshold)
                    surface_velocity = midpoint_velocity + normal*radius_velocity
                    relative_velocity = velocity[control_index]-surface_velocity
                    normal_speed = float(np.dot(relative_velocity, normal))
                    tangent = relative_velocity-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*float(restitution)
                    velocity[control_index] = (
                        normal_speed*normal + tangent*(1.0-float(surface_friction))
                        + surface_velocity)
                    if swept is not None:
                        current[control_index] = (
                            projected+velocity[control_index]*seconds*(1.0-hit))
                    collision_samples += 1
                    if swept is not None:
                        continuous_collision_samples += 1
                    # The moving capsule can displace a point back into the
                    # support or sphere set. Re-project the bounded compound
                    # in a deterministic order until all three surfaces agree.
                    for _ in range(8):
                        changed = False
                        support_projection=(current[control_index]
                            -plane_normal*float(np.dot(
                                current[control_index]-plane_point,plane_normal)))
                        active_compound_plane=(triangles is None
                            or _inside_triangles(support_projection,triangles))
                        plane_penetration = (max(
                            0.0, float(clearance)
                            - float(np.dot(
                                current[control_index]-plane_point,
                                plane_normal))) if active_compound_plane else 0.0)
                        if plane_penetration > 1e-10:
                            current[control_index] += plane_normal*plane_penetration
                            collision_samples += 1
                            changed = True
                        sphere_penetration = max(
                            active_radius+float(clearance)
                            - float(np.linalg.norm(
                                current[control_index]-active_center))
                            for active_center, active_radius, _, _ in active_spheres)
                        if sphere_penetration > 1e-10:
                            current[control_index], _ = _project_sphere_set_point(
                                current[control_index], target[index, control_index],
                                active_spheres, float(clearance))
                            collision_samples += 1
                            changed = True
                        closest = _capsule_closest(
                            current[control_index], start, end)
                        remaining = (float(radius)+float(clearance)
                                     - float(np.linalg.norm(
                                         current[control_index]-closest)))
                        if remaining > 1e-10:
                            normal = _capsule_normal(
                                current[control_index], start, end,
                                (target[index, control_index]-closest,
                                 -velocity[control_index]))
                            current[control_index] = closest + normal * (
                                projection_threshold)
                            collision_samples += 1
                            changed = True
                        if not changed:
                            break
                    closest = _capsule_closest(
                        current[control_index], start, end)
                    final_capsule_penetration = (float(radius)+float(clearance)
                        - float(np.linalg.norm(
                            current[control_index]-closest)))
                    final_sphere_penetration = max(
                        active_radius+float(clearance)
                        - float(np.linalg.norm(
                            current[control_index]-active_center))
                        for active_center, active_radius, _, _ in active_spheres)
                    final_support_projection=(current[control_index]
                        -plane_normal*float(np.dot(
                            current[control_index]-plane_point,plane_normal)))
                    final_compound_plane=(triangles is None
                        or _inside_triangles(final_support_projection,triangles))
                    final_plane_penetration = (max(
                        0.0, float(clearance)
                        - float(np.dot(
                            current[control_index]-plane_point, plane_normal)))
                        if final_compound_plane else 0.0)
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, final_capsule_penetration),
                        max(0.0, final_sphere_penetration),
                        final_plane_penetration)
                    if max(final_capsule_penetration, final_sphere_penetration,
                           final_plane_penetration) > 1e-8:
                        raise ValueError(
                            "World secondary chain moving compound capsule did not converge")
            if compound_static_mesh:
                for control_index, point in enumerate(current):
                    mesh_state = _mesh_collision_state(
                        point, mesh, float(clearance), True,
                        (target[index, control_index]-point,
                         -velocity[control_index]), 0.0)
                    if not mesh_state[0]:
                        continue
                    _, projected, normal, penetration, _, _, _ = mesh_state
                    maximum_penetration = max(maximum_penetration,
                                              float(penetration))
                    current[control_index] = projected
                    normal_speed = float(np.dot(velocity[control_index], normal))
                    tangent = velocity[control_index]-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*float(restitution)
                    velocity[control_index] = (
                        normal_speed*normal + tangent*(1.0-float(surface_friction)))
                    collision_samples += 1
                    resolved = _mesh_collision_state(
                        current[control_index], mesh, float(clearance), True,
                        (-velocity[control_index],), 0.0)
                    maximum_penetration_after = max(
                        maximum_penetration_after, max(0.0, float(resolved[3])))
        elif capsule is not None or capsule_trajectory is not None:
            if capsule_trajectory is not None:
                previous_start = capsule_trajectory[0][index-1]
                previous_end = capsule_trajectory[1][index-1]
                previous_radius = capsule_trajectory[2][index-1]
                start = capsule_trajectory[0][index]
                end = capsule_trajectory[1][index]
                radius = capsule_trajectory[2][index]
                midpoint = start + 0.5 * (end-start)
                previous_midpoint = previous_start + 0.5 * (previous_end-previous_start)
                midpoint_delta = midpoint-previous_midpoint
                if not np.isfinite(midpoint_delta).all():
                    raise ValueError(
                        "World secondary chain capsule midpoint velocity was nonfinite")
                midpoint_velocity = midpoint_delta/seconds
                radius_velocity = (radius-previous_radius)/seconds
                if (not np.isfinite(midpoint_velocity).all()
                        or not math.isfinite(float(radius_velocity))):
                    raise ValueError(
                        "World secondary chain capsule surface velocity was nonfinite")
            else:
                start, end, radius = capsule
                midpoint_velocity = np.zeros(3, dtype=float)
                radius_velocity = 0.0
            for control_index, point in enumerate(current):
                swept = None
                if capsule_continuous:
                    fallbacks = (target[index, control_index]-point,
                                 -velocity[control_index])
                    swept = (_capsule_trajectory_sweep_hit(
                        previous[control_index], point,
                        previous_start, previous_end, previous_radius,
                        start, end, radius, clearance, fallbacks)
                             if capsule_trajectory is not None else
                             _capsule_sweep_hit(
                                 previous[control_index], point, start, end,
                                 radius, clearance, fallbacks))
                if swept is not None:
                    projected, normal, penetration, hit = swept
                    maximum_penetration = max(maximum_penetration, penetration)
                    current[control_index] = projected
                    surface_velocity = midpoint_velocity+normal*radius_velocity
                    relative_velocity = velocity[control_index]-surface_velocity
                    normal_speed = float(np.dot(relative_velocity, normal))
                    tangent = relative_velocity-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*float(restitution)
                    velocity[control_index] = (
                        normal_speed*normal + tangent*(1.0-float(surface_friction))
                        + surface_velocity)
                    if capsule_trajectory is not None:
                        current[control_index] = (
                            projected+velocity[control_index]*seconds*(1.0-hit))
                    collision_samples += 1
                    continuous_collision_samples += 1
                    point=current[control_index]
                closest = _capsule_closest(point, start, end)
                distance = float(np.linalg.norm(point-closest))
                separation = distance-float(radius)-float(clearance)
                if separation >= -1e-10:
                    continue
                normal = _capsule_normal(
                    point, start, end,
                    (target[index, control_index]-closest, -velocity[control_index]))
                maximum_penetration = max(maximum_penetration, -separation)
                current[control_index] = closest + normal * (
                    float(radius)+float(clearance))
                surface_velocity = midpoint_velocity+normal*radius_velocity
                relative_velocity = velocity[control_index]-surface_velocity
                normal_speed = float(np.dot(relative_velocity, normal))
                tangent = relative_velocity-normal_speed*normal
                if normal_speed < 0.0:
                    normal_speed = -normal_speed*float(restitution)
                velocity[control_index] = (
                    normal_speed*normal + tangent*(1.0-float(surface_friction))
                    + surface_velocity)
                collision_samples += 1
                maximum_penetration_after = max(
                    maximum_penetration_after,
                    max(0.0, float(radius)+float(clearance)
                        - float(np.linalg.norm(current[control_index]-closest))))
        elif mesh is not None or mesh_trajectory is not None:
            active_mesh = (mesh_trajectory[index]
                           if mesh_trajectory is not None else mesh)
            for control_index, point in enumerate(current):
                state = _mesh_collision_state(
                    point, active_mesh, float(clearance), bool(collision_mesh_closed),
                    (target[index, control_index]-point, -velocity[control_index]),
                    float(collision_mesh_volume_radius))
                fallbacks = (target[index, control_index]-point,
                             -velocity[control_index])
                if mesh_trajectory is not None and collision_mesh_continuous:
                    sweep = (_mesh_deforming_volume_sweep_hit
                              if (float(clearance)
                                  + float(collision_mesh_volume_radius)) > 0.0
                              else _mesh_deforming_sweep_hit)
                    swept = sweep(
                        previous[control_index], point,
                        mesh_trajectory[index-1], active_mesh,
                        float(clearance), bool(collision_mesh_closed),
                        fallbacks, float(collision_mesh_volume_radius))
                elif (collision_mesh_continuous
                      and float(clearance)+float(collision_mesh_volume_radius)>0.0):
                    swept = _mesh_exact_swept_volume_hit(
                        previous[control_index], point, active_mesh, float(clearance),
                        bool(collision_mesh_closed),
                        fallbacks, float(collision_mesh_volume_radius))
                else:
                    swept = (_mesh_segment_hit(
                        previous[control_index], point, active_mesh,
                        bool(collision_mesh_closed))
                             if collision_mesh_continuous else None)
                if not state[0] and swept is None:
                    continue
                if swept is not None:
                    continuous_collision_samples += 1
                if swept is not None:
                    if mesh_trajectory is not None:
                        projected, normal, penetration, triangle_index = swept
                    elif (float(clearance)
                          +float(collision_mesh_volume_radius)>0.0):
                        projected, normal, penetration, triangle_index = swept
                    else:
                        _, hit_point, normal, triangle_index = swept
                        projected = hit_point + normal * float(clearance)
                        penetration = 0.0
                else:
                    _, projected, normal, penetration, _, _, triangle_index = state
                maximum_penetration = max(maximum_penetration, float(penetration))
                current[control_index] = projected
                endpoint_state = _mesh_collision_state(
                    current[control_index], active_mesh, float(clearance),
                    bool(collision_mesh_closed), fallbacks,
                    float(collision_mesh_volume_radius))
                if endpoint_state[0]:
                    current[control_index]=endpoint_state[1]
                    normal=endpoint_state[2]
                    triangle_index=endpoint_state[6]
                    maximum_penetration=max(
                        maximum_penetration,float(endpoint_state[3]))
                surface_velocity = (_mesh_surface_velocity(
                    current[control_index], triangle_index,
                    mesh_trajectory[index-1], active_mesh, seconds)
                    if mesh_trajectory is not None else np.zeros(3, dtype=float))
                relative_velocity = velocity[control_index]-surface_velocity
                normal_speed = float(np.dot(relative_velocity, normal))
                tangent = relative_velocity-normal_speed*normal
                if normal_speed < 0.0:
                    normal_speed = -normal_speed * float(restitution)
                velocity[control_index] = (
                    normal_speed*normal + tangent*(1.0-float(surface_friction))
                    + surface_velocity)
                collision_samples += 1
                resolved = _mesh_collision_state(
                    current[control_index], active_mesh, float(clearance),
                    bool(collision_mesh_closed), (-velocity[control_index],),
                    float(collision_mesh_volume_radius))
                maximum_penetration_after = max(
                    maximum_penetration_after, max(0.0, float(resolved[3])))
        simulated[index] = current
        maximum_residual = max(maximum_residual,
                               transfer_report['momentum_residual'])
        maximum_impulse = max(maximum_impulse,
                              transfer_report['maximum_internal_impulse'])
    weight = weights[:, None, None] * float(strength)
    result = target + (simulated - target) * weight
    result[0] = target[0]
    result[-1] = target[-1]
    if static_spheres or moving_spheres:
        maximum_penetration_after = 0.0
        strength_enabled = float(strength) > 0.0
        for sample_index in range(len(result)):
            active_spheres = tuple(
                (center, float(radius), center, float(radius))
                for center, radius in static_spheres)
            active_spheres += tuple(
                (centers[sample_index], _trajectory_radius(radii, sample_index),
                 centers[sample_index-1] if sample_index else centers[sample_index],
                 _trajectory_radius(radii, sample_index-1)
                 if sample_index else _trajectory_radius(radii, sample_index))
                for centers, radii in moving_spheres)
            for control_index, point in enumerate(result[sample_index]):
                projected_plane=(point-plane_normal*float(np.dot(
                    point-plane_point,plane_normal)) if plane_point is not None else None)
                compound_plane_here=(compound_plane_spheres and plane_point is not None
                    and (triangles is None or _inside_triangles(projected_plane,triangles)))
                penetration = max(
                    radius+float(clearance)-float(np.linalg.norm(point-center))
                    for center, radius, _, _ in active_spheres)
                maximum_penetration = max(maximum_penetration, penetration)
                plane_penetration = (
                    max(0.0, float(clearance)
                        - float(np.dot(point-plane_point, plane_normal)))
                    if compound_plane_here else 0.0)
                swept_hit = None
                if sphere_continuous and sample_index > 0:
                    swept_hit = _first_sphere_sweep_hit(
                        result[sample_index-1, control_index], point,
                        active_spheres, clearance,
                        (target[sample_index, control_index]-point,
                         result[sample_index-1, control_index]-point))
                if ((penetration > 1e-10 or plane_penetration > 1e-10
                     or swept_hit is not None)
                        and 0 < sample_index < len(result)-1
                        and strength_enabled and weights[sample_index] > 0.0):
                    if swept_hit is not None and penetration <= 1e-10:
                        sphere_index, swept = swept_hit
                        if any(not np.array_equal(center, previous_center)
                               or float(radius) != float(previous_radius)
                               for center, radius, previous_center, previous_radius
                               in active_spheres):
                            corrected, _, _, _ = _resolve_moving_sphere_sweep_path(
                                result[sample_index-1, control_index], point,
                                active_spheres, clearance, restitution,
                                surface_friction,
                                (target[sample_index, control_index]-point,
                                 result[sample_index-1, control_index]-point))
                        else:
                            corrected = _sphere_sweep_endpoint(
                                result[sample_index-1, control_index], point,
                                active_spheres[sphere_index], swept, restitution,
                                surface_friction)
                        if compound_plane_here:
                            corrected, _ = _project_compound_plane_spheres_point(
                                corrected, target[sample_index, control_index],
                                active_spheres, plane_point, plane_normal,
                                float(clearance))
                        else:
                            corrected, _ = _project_sphere_set_point(
                                corrected, target[sample_index, control_index],
                                active_spheres, float(clearance))
                    elif compound_plane_here:
                        corrected, _ = _project_compound_plane_spheres_point(
                            point, target[sample_index, control_index],
                            active_spheres, plane_point, plane_normal,
                            float(clearance))
                    else:
                        corrected, _ = _project_sphere_set_point(
                            point, target[sample_index, control_index],
                            active_spheres, float(clearance))
                    result[sample_index, control_index] = corrected
                    collision_samples += 1
                    if swept_hit is not None:
                        continuous_collision_samples += 1
                maximum_penetration_after = max(
                    maximum_penetration_after,
                    max(0.0, max(
                        radius+float(clearance)-float(np.linalg.norm(
                            result[sample_index, control_index]-center))
                        for center, radius, _, _ in active_spheres)))
                if compound_plane_here:
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, float(clearance)
                            - float(np.dot(
                                result[sample_index, control_index]-plane_point,
                                plane_normal))))
                if compound_static_capsule:
                    start, end, radius = capsule
                    target_point = target[sample_index, control_index]
                    for _ in range(8):
                        changed = False
                        plane_penetration = (
                            max(0.0, float(clearance)
                                - float(np.dot(
                                    result[sample_index, control_index]-plane_point,
                                    plane_normal)))
                            if compound_plane_here
                            else 0.0)
                        if (plane_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            result[sample_index, control_index] = (
                                result[sample_index, control_index]
                                + plane_normal*plane_penetration)
                            collision_samples += 1
                            changed = True
                        sphere_penetration = max(
                            active_radius+float(clearance)
                            - float(np.linalg.norm(
                                result[sample_index, control_index]-active_center))
                            for active_center, active_radius, _, _ in active_spheres)
                        if (sphere_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            result[sample_index, control_index], _ = _project_sphere_set_point(
                                result[sample_index, control_index], target_point,
                                active_spheres, float(clearance))
                            collision_samples += 1
                            changed = True
                        closest = _capsule_closest(
                            result[sample_index, control_index], start, end)
                        capsule_penetration = radius+float(clearance)-float(np.linalg.norm(
                            result[sample_index, control_index]-closest))
                        maximum_penetration = max(
                            maximum_penetration, capsule_penetration)
                        if (capsule_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            normal = _capsule_normal(
                                result[sample_index, control_index], start, end,
                                (target_point-closest,
                                 result[sample_index-1, control_index]
                                 - result[sample_index, control_index]
                                 if sample_index else target_point-closest))
                            result[sample_index, control_index] = closest + normal * (
                                radius+float(clearance))
                            collision_samples += 1
                            changed = True
                        if not changed:
                            break
                    final_capsule_closest = _capsule_closest(
                        result[sample_index, control_index], start, end)
                    final_capsule_penetration = radius+float(clearance)-float(np.linalg.norm(
                        result[sample_index, control_index]-final_capsule_closest))
                    maximum_penetration_after = max(
                        maximum_penetration_after, max(0.0, final_capsule_penetration))
                    editable = (0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0)
                    if editable and final_capsule_penetration > 1e-8:
                        raise ValueError(
                            "World secondary chain compound collider did not converge")
                if moving_capsule_compound:
                    start = capsule_trajectory[0][sample_index]
                    end = capsule_trajectory[1][sample_index]
                    radius = capsule_trajectory[2][sample_index]
                    target_point = target[sample_index, control_index]
                    editable=(0 < sample_index < len(result)-1
                              and strength_enabled and weights[sample_index]>0.0)
                    if collision_capsule_continuous and sample_index>0 and editable:
                        swept=_capsule_trajectory_sweep_hit(
                            result[sample_index-1,control_index],
                            result[sample_index,control_index],
                            capsule_trajectory[0][sample_index-1],
                            capsule_trajectory[1][sample_index-1],
                            capsule_trajectory[2][sample_index-1],start,end,radius,
                            float(clearance),(target_point-result[sample_index,control_index],))
                        if swept is not None:
                            result[sample_index,control_index]=_capsule_sweep_endpoint(
                                result[sample_index-1,control_index],
                                result[sample_index,control_index],
                                capsule_trajectory[0][sample_index-1],
                                capsule_trajectory[1][sample_index-1],
                                capsule_trajectory[2][sample_index-1],
                                start,end,radius,swept,restitution,surface_friction)
                            continuous_collision_samples+=1;collision_samples+=1
                    closest = _capsule_closest(
                        result[sample_index, control_index], start, end)
                    capsule_penetration = radius+float(clearance)-float(
                        np.linalg.norm(result[sample_index, control_index]-closest))
                    maximum_penetration = max(maximum_penetration, capsule_penetration)
                    if (capsule_penetration > 1e-10
                            and 0 < sample_index < len(result)-1
                            and strength_enabled and weights[sample_index] > 0.0):
                        normal = _capsule_normal(
                            result[sample_index, control_index], start, end,
                            (target_point-closest,
                             result[sample_index-1, control_index]
                             - result[sample_index, control_index]))
                        result[sample_index, control_index] = closest + normal * (
                            radius+float(clearance))
                        collision_samples += 1
                    # The capsule correction can move a point back into the
                    # support or sphere set.  Re-project the bounded compound
                    # in a deterministic order until all three surfaces agree
                    # (or fail closed at the same strict tolerance used by the
                    # static compound path).
                    for _ in range(8):
                        changed = False
                        support_projection=(result[sample_index,control_index]
                            -plane_normal*float(np.dot(
                                result[sample_index,control_index]-plane_point,
                                plane_normal)))
                        active_compound_plane=(triangles is None
                            or _inside_triangles(support_projection,triangles))
                        plane_penetration = (max(
                            0.0, float(clearance)
                            - float(np.dot(
                                result[sample_index, control_index]-plane_point,
                                plane_normal))) if active_compound_plane else 0.0)
                        if (plane_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            result[sample_index, control_index] += (
                                plane_normal*plane_penetration)
                            collision_samples += 1
                            changed = True
                        sphere_penetration = max(
                            active_radius+float(clearance)
                            - float(np.linalg.norm(
                                result[sample_index, control_index]-active_center))
                            for active_center, active_radius, _, _ in active_spheres)
                        if (sphere_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            result[sample_index, control_index], _ = _project_sphere_set_point(
                                result[sample_index, control_index], target_point,
                                active_spheres, float(clearance))
                            collision_samples += 1
                            changed = True
                        closest = _capsule_closest(
                            result[sample_index, control_index], start, end)
                        capsule_penetration = radius+float(clearance)-float(
                            np.linalg.norm(result[sample_index, control_index]
                                           - closest))
                        if (capsule_penetration > 1e-10
                                and 0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0):
                            normal = _capsule_normal(
                                result[sample_index, control_index], start, end,
                                (target_point-closest,
                                 result[sample_index-1, control_index]
                                 - result[sample_index, control_index]))
                            result[sample_index, control_index] = closest + normal * (
                                radius+float(clearance))
                            collision_samples += 1
                            changed = True
                        if not changed:
                            break
                    final_capsule_closest = _capsule_closest(
                        result[sample_index, control_index], start, end)
                    final_capsule_penetration = radius+float(clearance)-float(
                        np.linalg.norm(result[sample_index, control_index]
                                       - final_capsule_closest))
                    final_sphere_penetration = max(
                        active_radius+float(clearance)
                        - float(np.linalg.norm(
                            result[sample_index, control_index]-active_center))
                        for active_center, active_radius, _, _ in active_spheres)
                    final_support_projection=(result[sample_index,control_index]
                        -plane_normal*float(np.dot(
                            result[sample_index,control_index]-plane_point,
                            plane_normal)))
                    final_compound_plane=(triangles is None
                        or _inside_triangles(final_support_projection,triangles))
                    final_plane_penetration = (max(
                        0.0, float(clearance)
                        - float(np.dot(
                            result[sample_index, control_index]-plane_point,
                            plane_normal))) if final_compound_plane else 0.0)
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, final_capsule_penetration),
                        max(0.0, final_sphere_penetration),
                        final_plane_penetration)
                    editable = (0 < sample_index < len(result)-1
                                and strength_enabled and weights[sample_index] > 0.0)
                    if (editable and max(final_capsule_penetration,
                                         final_sphere_penetration,
                                         final_plane_penetration) > 1e-8):
                        raise ValueError(
                            "World secondary chain moving compound capsule did not converge")
                if compound_static_mesh:
                    mesh_state = _mesh_collision_state(
                        result[sample_index, control_index], mesh,
                        float(clearance), True,
                        (target[sample_index, control_index]
                         - result[sample_index, control_index],), 0.0)
                    mesh_penetration = max(0.0, float(mesh_state[3]))
                    maximum_penetration = max(maximum_penetration,
                                              mesh_penetration)
                    editable=(0 < sample_index < len(result)-1
                              and strength_enabled and weights[sample_index]>0.0)
                    plane_penetration=(max(0.0,float(clearance)-float(np.dot(
                        result[sample_index,control_index]-plane_point,plane_normal)))
                        if compound_plane_here else 0.0)
                    supported_point=(result[sample_index,control_index]
                                     +plane_normal*plane_penetration)
                    supported_mesh_state=(_mesh_collision_state(
                        supported_point,mesh,float(clearance),True,(plane_normal,),0.0)
                        if compound_plane_here else None)
                    supported_mesh_collision=bool(
                        supported_mesh_state is not None and supported_mesh_state[0])
                    joint_resolved=False
                    if (editable and compound_plane_here
                            and supported_mesh_collision):
                        nearest_supported=np.asarray(supported_mesh_state[1],dtype=float)
                        nearest_plane_distance=float(np.dot(
                            nearest_supported-plane_point,plane_normal))
                        if nearest_plane_distance >= float(clearance)-1e-10:
                            result[sample_index,control_index]=nearest_supported
                            collision_samples += 1
                            supported_mesh_collision=False
                            joint_resolved=True
                    if (editable and compound_plane_here
                            and supported_mesh_collision):
                        vertices=np.asarray(mesh,dtype=float).reshape((-1,3))
                        travel=(float(np.linalg.norm(np.ptp(vertices,axis=0)))
                                +float(np.linalg.norm(result[sample_index,control_index]
                                                      -np.mean(vertices,axis=0)))
                                +float(clearance)+1.0)
                        exit_hit=_mesh_segment_hit(
                            result[sample_index,control_index],
                            result[sample_index,control_index]+plane_normal*travel,
                            mesh)
                        if exit_hit is None:
                            raise ValueError(
                                "World secondary chain compound mesh has no support-side exit")
                        result[sample_index,control_index]=(exit_hit[1]+plane_normal*(
                            float(clearance)+1e-9))
                        collision_samples += 1
                    elif mesh_penetration > 1e-10 and editable and not joint_resolved:
                        result[sample_index, control_index] = mesh_state[1]
                        collision_samples += 1
                    final_mesh_state = _mesh_collision_state(
                        result[sample_index, control_index], mesh,
                        float(clearance), True,
                        (-result[sample_index, control_index],), 0.0)
                    maximum_penetration_after = max(
                        maximum_penetration_after,
                        max(0.0, float(final_mesh_state[3])))
                    if editable and final_mesh_state[0]:
                        raise ValueError(
                            "World secondary chain compound collider did not converge")
    elif capsule is not None or capsule_trajectory is not None:
        maximum_penetration_after = 0.0
        strength_enabled = float(strength) > 0.0
        for sample_index in range(len(result)):
            if capsule_trajectory is not None:
                start = capsule_trajectory[0][sample_index]
                end = capsule_trajectory[1][sample_index]
                radius = capsule_trajectory[2][sample_index]
            else:
                start, end, radius = capsule
            for control_index, point in enumerate(result[sample_index]):
                swept = None
                if capsule_continuous and sample_index > 0:
                    previous_start = (capsule_trajectory[0][sample_index-1]
                                      if capsule_trajectory is not None else start)
                    previous_end = (capsule_trajectory[1][sample_index-1]
                                    if capsule_trajectory is not None else end)
                    previous_radius = (capsule_trajectory[2][sample_index-1]
                                       if capsule_trajectory is not None else radius)
                    swept = (_capsule_trajectory_sweep_hit(
                        result[sample_index-1, control_index], point,
                        previous_start, previous_end, previous_radius,
                        start, end, radius, clearance,
                        (target[sample_index, control_index]-point,
                         result[sample_index-1, control_index]-point))
                             if capsule_trajectory is not None else
                             _capsule_sweep_hit(
                                 result[sample_index-1, control_index], point,
                                 start, end, radius, clearance,
                                 (target[sample_index, control_index]-point,
                                  result[sample_index-1, control_index]-point)))
                closest = _capsule_closest(point, start, end)
                distance = float(np.linalg.norm(point-closest))
                penetration = float(radius)+float(clearance)-distance
                maximum_penetration = max(maximum_penetration, penetration)
                if ((penetration > 1e-10 or swept is not None)
                        and 0 < sample_index < len(result)-1
                        and strength_enabled and weights[sample_index] > 0.0):
                    if swept is not None and penetration <= 1e-10:
                        result[sample_index, control_index] = (
                            _capsule_sweep_endpoint(
                                result[sample_index-1, control_index], point,
                                previous_start, previous_end, previous_radius,
                                start, end, radius, swept, restitution,
                                surface_friction)
                            if capsule_trajectory is not None else swept[0])
                    closest = _capsule_closest(
                        result[sample_index, control_index], start, end)
                    penetration = (float(radius)+float(clearance)
                                   -float(np.linalg.norm(
                                       result[sample_index, control_index]-closest)))
                    if penetration > 1e-10:
                        normal = _capsule_normal(
                            result[sample_index, control_index], start, end,
                            (target[sample_index, control_index]-closest,
                             simulated[sample_index, control_index]-closest))
                        result[sample_index, control_index] = (
                            closest+normal*(float(radius)+float(clearance)))
                    collision_samples += 1
                    if swept is not None:
                        continuous_collision_samples += 1
                    closest = _capsule_closest(
                        result[sample_index, control_index], start, end)
                    penetration = max(
                        0.0, float(radius)+float(clearance)
                        - float(np.linalg.norm(
                            result[sample_index, control_index]-closest)))
                maximum_penetration_after = max(
                    maximum_penetration_after, max(0.0, penetration))
    elif mesh is not None or mesh_trajectory is not None:
        maximum_penetration_after = 0.0
        strength_enabled = float(strength) > 0.0
        for sample_index in range(len(result)):
            active_mesh = (mesh_trajectory[sample_index]
                           if mesh_trajectory is not None else mesh)
            for control_index, point in enumerate(result[sample_index]):
                if (collision_mesh_continuous and sample_index > 0
                        and 0 < sample_index < len(result)-1
                        and strength_enabled and weights[sample_index] > 0.0):
                    fallbacks=(target[sample_index,control_index]-point,
                               simulated[sample_index,control_index]-point)
                    if mesh_trajectory is not None:
                        sweep=(_mesh_deforming_volume_sweep_hit
                               if (float(clearance)
                                   + float(collision_mesh_volume_radius))>0.0
                               else _mesh_deforming_sweep_hit)
                        swept=sweep(result[sample_index-1,control_index],point,
                                    mesh_trajectory[sample_index-1],active_mesh,
                                    float(clearance),bool(collision_mesh_closed),
                                    fallbacks,float(collision_mesh_volume_radius))
                    else:
                        swept=_mesh_exact_swept_volume_hit(
                            result[sample_index-1,control_index],point,active_mesh,
                            float(clearance),bool(collision_mesh_closed),fallbacks,
                            float(collision_mesh_volume_radius))
                    if swept is not None:
                        result[sample_index,control_index]=swept[0]
                        point=result[sample_index,control_index]
                        collision_samples+=1
                        continuous_collision_samples+=1
                state = _mesh_collision_state(
                    point, active_mesh, float(clearance),
                    bool(collision_mesh_closed),
                    (target[sample_index, control_index]-point,
                     simulated[sample_index, control_index]-point),
                    float(collision_mesh_volume_radius))
                penetration = max(0.0, float(state[3]))
                maximum_penetration = max(maximum_penetration, penetration)
                if (state[0] and 0 < sample_index < len(result)-1
                        and strength_enabled and weights[sample_index] > 0.0):
                    result[sample_index, control_index] = state[1]
                    collision_samples += 1
                    state = _mesh_collision_state(
                        result[sample_index, control_index], active_mesh,
                        float(clearance), bool(collision_mesh_closed),
                        (-simulated[sample_index, control_index],),
                        float(collision_mesh_volume_radius))
                maximum_penetration_after = max(
                    maximum_penetration_after, max(0.0, float(state[3])))
                if (state[0] and 0 < sample_index < len(result)-1
                        and strength_enabled and weights[sample_index]>0.0):
                    raise ValueError(
                        "World secondary chain mesh collider did not converge to a clear point")
    if not np.isfinite(result).all():
        raise ValueError("World secondary chain dynamics produced nonfinite output")
    if plane_point is not None:
        for sample_index, sample in enumerate(result):
            if (not 0 < sample_index < len(result)-1
                    or float(strength) <= 0.0 or weights[sample_index] <= 0.0):
                continue
            for point in sample:
                projected = point-plane_normal*float(np.dot(point-plane_point, plane_normal))
                if triangles is not None and not _inside_triangles(projected, triangles):
                    continue
                penetration = max(
                    0.0, float(clearance)
                    - float(np.dot(point-plane_point, plane_normal)))
                if penetration > 1e-10:
                    point += plane_normal*penetration
                    collision_samples += 1
                maximum_penetration_after = max(
                    maximum_penetration_after,
                    max(0.0, float(clearance)
                        - float(np.dot(point-plane_point, plane_normal))))
    # Recompute the residual from the actual published result after every
    # compound projection. Endpoints and zero-weight priorities remain exact,
    # but their retained penetration is still reported honestly.
    maximum_penetration_after = 0.0
    for sample_index, sample in enumerate(result):
        final_spheres=list(static_spheres)+[
            (centers[sample_index],_trajectory_radius(radii,sample_index))
            for centers,radii in moving_spheres]
        for point in sample:
            residuals=[]
            if plane_point is not None:
                projected=point-plane_normal*float(np.dot(
                    point-plane_point,plane_normal))
                if triangles is None or _inside_triangles(projected,triangles):
                    residuals.append(float(clearance)-float(np.dot(
                        point-plane_point,plane_normal)))
            residuals.extend(radius+float(clearance)-float(np.linalg.norm(point-center))
                             for center,radius in final_spheres)
            if capsule is not None or capsule_trajectory is not None:
                if capsule_trajectory is not None:
                    start=capsule_trajectory[0][sample_index]
                    end=capsule_trajectory[1][sample_index]
                    radius=capsule_trajectory[2][sample_index]
                else:
                    start,end,radius=capsule
                closest=_capsule_closest(point,start,end)
                residuals.append(float(radius)+float(clearance)
                                 -float(np.linalg.norm(point-closest)))
            if mesh is not None or mesh_trajectory is not None:
                active_mesh=(mesh_trajectory[sample_index]
                             if mesh_trajectory is not None else mesh)
                residuals.append(float(_mesh_collision_state(
                    point,active_mesh,float(clearance),bool(collision_mesh_closed),
                    (),float(collision_mesh_volume_radius))[3]))
            published=max((max(0.0,value) for value in residuals),default=0.0)
            maximum_penetration_after=max(maximum_penetration_after,published)
            editable=(0 < sample_index < len(result)-1 and float(strength)>0.0
                      and weights[sample_index]>0.0)
            if editable and published>1e-8:
                raise ValueError('World secondary chain compound collider did not converge')
    return result, dict(momentum_conservation_error=maximum_residual,
                        maximum_internal_impulse=maximum_impulse,
                        coupling_passes=coupling_passes,
                        coupling_edges=(target.shape[1]-1)*coupling_passes,
                        coupled_samples=len(steps),
                         collision_samples=collision_samples,
                         continuous_collision_samples=continuous_collision_samples,
                        collision_collider_count=(len(static_spheres) + len(moving_spheres)
                                                   + int(plane_point is not None)
                                                   + int(compound_static_capsule and capsule is not None)
                                                   + int(moving_capsule_compound and capsule_trajectory is not None)
                                                   + int(compound_static_mesh and mesh is not None)
                                                   + int((capsule is not None or capsule_trajectory is not None)
                                                         and not (compound_static_capsule or moving_capsule_compound))
                                                   + int((mesh is not None or mesh_trajectory is not None)
                                                         and not compound_static_mesh)),
                        collision_plane=plane_point is not None,
                        collision_compound=bool(compound_plane_spheres and plane_point is not None
                                               and (static_spheres or moving_spheres)),
                         collision_compound_capsule=bool(
                             (compound_static_capsule and capsule is not None)
                             or (moving_capsule_compound and capsule_trajectory is not None)),
                        collision_compound_mesh=bool(compound_static_mesh and mesh is not None),
                        max_raw_penetration=maximum_penetration,
                        max_penetration_after=maximum_penetration_after)


def apply_vector_follow(values, frames, *, dt, frequency, damping, air_friction,
                        strength, blend_frames, envelope=None):
    target = np.asarray(values, dtype=float)
    times = np.asarray(frames, dtype=float)
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=blend_frames, dt=dt)
    follower = follow_vectors(target, np.diff(times), dt=dt, frequency=frequency,
                              damping=damping, air_friction=air_friction)
    base_weight=(boundary_envelope(times,blend_frames) if envelope is None
                 else np.asarray(envelope,dtype=float))
    if (base_weight.shape!=(len(times),) or not np.isfinite(base_weight).all()
            or np.any((base_weight<0)|(base_weight>1))):
        raise ValueError("Secondary-motion envelope must be within zero and one")
    weight=base_weight*strength
    shape = (len(weight),) + (1,) * (target.ndim - 1)
    result = target + (follower - target) * weight.reshape(shape)
    result[0] = target[0]
    result[-1] = target[-1]
    return result


def validate_world_settings(*, gravity, gravity_scale,
                            external_acceleration=(0.0, 0.0, 0.0),
                            wind_velocity=(0.0, 0.0, 0.0),
                            velocity_impulse=(0.0, 0.0, 0.0), collision_point=None,
                            collision_normal=None, clearance=0.0,
                            restitution=0.0, surface_friction=0.0):
    gravity = np.asarray(gravity, dtype=float)
    external = np.asarray(external_acceleration, dtype=float)
    wind = np.asarray(wind_velocity, dtype=float)
    impulse = np.asarray(velocity_impulse, dtype=float)
    scalars = np.asarray((gravity_scale, clearance, restitution, surface_friction), dtype=float)
    if (gravity.shape != (3,) or external.shape != (3,) or wind.shape != (3,)
            or impulse.shape != (3,)
            or not np.isfinite(gravity).all() or not np.isfinite(external).all()
            or not np.isfinite(wind).all() or not np.isfinite(impulse).all()
            or not np.isfinite(scalars).all()):
        raise ValueError("World secondary-motion settings must be finite")
    if np.any(np.abs(external) > 100.0):
        raise ValueError("Secondary external acceleration must be between -100 and 100 per axis")
    if np.any(np.abs(wind) > 100.0):
        raise ValueError("Secondary wind velocity must be between -100 and 100 per axis")
    if np.any(np.abs(impulse) > 100.0):
        raise ValueError("Secondary velocity impulse must be between -100 and 100 per axis")
    if not 0.0 <= gravity_scale <= 4.0:
        raise ValueError("Secondary gravity influence must be between 0 and 4")
    if clearance < 0.0:
        raise ValueError("Secondary collision clearance must be nonnegative")
    if not 0.0 <= restitution <= 1.0 or not 0.0 <= surface_friction <= 1.0:
        raise ValueError("Secondary restitution and surface friction must be between 0 and 1")
    if (collision_point is None) != (collision_normal is None):
        raise ValueError("Secondary collision point and normal must be provided together")
    if collision_point is not None:
        point = np.asarray(collision_point, dtype=float)
        normal = np.asarray(collision_normal, dtype=float)
        if point.shape != (3,) or normal.shape != (3,) or not np.isfinite(point).all() or not np.isfinite(normal).all():
            raise ValueError("Secondary collision plane must contain finite 3D vectors")
        length = float(np.linalg.norm(normal))
        if length < 1e-8:
            raise ValueError("Secondary collision normal must be nonzero")
        return gravity, point, normal / length
    return gravity, None, None


def validate_sphere_collider(center, radius):
    if isinstance(radius, (bool, np.bool_)):
        raise ValueError("Secondary sphere radius must be numeric")
    center = np.asarray(center)
    if center.dtype.kind == "b":
        raise ValueError("Secondary sphere center must be numeric")
    try:
        center = center.astype(float)
        radius = float(radius)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary sphere collider must contain numeric values") from exc
    if center.shape != (3,) or not np.isfinite(center).all() or not math.isfinite(radius):
        raise ValueError("Secondary sphere collider must contain a finite 3D center and radius")
    if not 1e-6 <= radius <= 1000.0:
        raise ValueError("Secondary sphere radius must be between 0.000001 and 1000 world units")
    return center, radius


MAX_SPHERE_COLLIDERS = 8


def validate_sphere_colliders(colliders):
    if not isinstance(colliders, (list, tuple)) or not 1 <= len(colliders) <= MAX_SPHERE_COLLIDERS:
        raise ValueError(f"Secondary sphere set must contain 1 to {MAX_SPHERE_COLLIDERS} colliders")
    result = []
    for item in colliders:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("Each secondary sphere collider must contain center and radius")
        center, radius = validate_sphere_collider(item[0], item[1])
        result.append((center, radius))
    return tuple(sorted(result, key=lambda item: (*item[0], item[1])))


def validate_sphere_trajectories(trajectories, sample_count):
    """Validate per-sample sphere centers and optional sampled radii.

    A scalar radius retains the moving-rigid-sphere contract. A one-dimensional
    radius array enables a bounded expanding/contracting primitive without
    weakening validation for existing callers.
    """
    if (type(sample_count) is not int or sample_count < 2
            or not isinstance(trajectories, (list, tuple))
            or not 1 <= len(trajectories) <= MAX_SPHERE_COLLIDERS):
        raise ValueError(
            f"Secondary moving sphere set must contain 1 to {MAX_SPHERE_COLLIDERS} colliders")
    result = []
    for item in trajectories:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("Each moving sphere collider must contain sampled centers and radius")
        centers = np.asarray(item[0])
        if centers.dtype.kind == "b":
            raise ValueError("Secondary moving sphere centers must be numeric")
        try:
            centers = centers.astype(float)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Secondary moving sphere centers must be numeric") from exc
        if centers.shape != (sample_count, 3) or not np.isfinite(centers).all():
            raise ValueError("Secondary moving sphere centers must match the finite 3D samples")
        raw_radius = np.asarray(item[1])
        if raw_radius.ndim == 0:
            _, radius = validate_sphere_collider(centers[0], item[1])
        else:
            if raw_radius.dtype.kind == "b":
                raise ValueError("Secondary moving sphere radii must be numeric")
            try:
                radius = raw_radius.astype(float)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("Secondary moving sphere radii must be numeric") from exc
            if (radius.shape != (sample_count,) or not np.isfinite(radius).all()
                    or np.any(radius < 1e-6) or np.any(radius > 1000.0)):
                raise ValueError(
                    "Secondary moving sphere radii must match the finite samples and radius limits")
        result.append((centers, radius))
    # Full-trajectory ordering makes overlapping-collider resolution independent
    # of collection order while retaining every sampled center.
    return tuple(sorted(result, key=lambda item: (
        np.asarray(item[1], dtype=float).tobytes(), item[0].tobytes())))


def _trajectory_radius(radius, index):
    return float(radius if np.ndim(radius) == 0 else radius[index])


def _sphere_specs(center, radius, colliders):
    single_active = center is not None or radius is not None
    set_active = colliders is not None
    if single_active and set_active:
        raise ValueError("Secondary collision accepts one sphere input form")
    if single_active:
        if center is None or radius is None:
            raise ValueError("Secondary sphere center and radius must be provided together")
        center, radius = validate_sphere_collider(center, radius)
        return ((center, radius),)
    return validate_sphere_colliders(colliders) if set_active else ()


def _sphere_normal(point, center, fallbacks):
    delta = point-center
    length = float(np.linalg.norm(delta))
    if length >= 1e-10:
        return delta/length
    for fallback in fallbacks:
        fallback = np.asarray(fallback, dtype=float)
        length = float(np.linalg.norm(fallback))
        if length >= 1e-10:
            return fallback/length
    return np.array((0.0, 0.0, 1.0))


def _sphere_sweep_hit(previous, current, previous_center, previous_radius,
                      center, radius, clearance, fallbacks=()):
    """Return the first bounded contact while a point and sphere interpolate."""
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    previous_center = np.asarray(previous_center, dtype=float)
    center = np.asarray(center, dtype=float)
    previous_radius = float(previous_radius)
    radius = float(radius)
    clearance = float(clearance)
    relative = previous-previous_center
    relative_rate = (current-previous)-(center-previous_center)
    threshold = previous_radius+clearance
    threshold_rate = radius-previous_radius
    if (not np.isfinite(previous).all() or not np.isfinite(current).all()
            or not np.isfinite(previous_center).all() or not np.isfinite(center).all()
            or not math.isfinite(previous_radius) or not math.isfinite(radius)
            or not math.isfinite(clearance) or not np.isfinite(relative).all()
            or not np.isfinite(relative_rate).all()):
        raise ValueError("Secondary sphere sweep geometry was nonfinite")
    hit = _quadratic_first_hit(
        float(np.dot(relative_rate, relative_rate)-threshold_rate*threshold_rate),
        2.0 * float(np.dot(relative, relative_rate)-threshold*threshold_rate),
        float(np.dot(relative, relative)-threshold*threshold),
        0.0, 1.0)
    if hit is None:
        return None
    contact = previous + (current-previous)*hit
    active_center = previous_center + (center-previous_center)*hit
    active_radius = previous_radius + (radius-previous_radius)*hit
    distance = float(np.linalg.norm(contact-active_center))
    normal = _sphere_normal(contact, active_center,
                            tuple(fallbacks) + (current-previous,))
    projected = active_center + normal*(active_radius+clearance)
    return projected, normal, max(0.0, active_radius+clearance-distance), hit


def _first_sphere_sweep_hit(previous, current, active_spheres, clearance,
                            fallbacks=()):
    """Return the deterministic earliest hit from a bounded sphere set."""
    hits = []
    for sphere_index, (center, radius, previous_center, previous_radius) in enumerate(
            active_spheres):
        swept = _sphere_sweep_hit(
            previous, current, previous_center, previous_radius,
            center, radius, clearance, fallbacks)
        if swept is not None:
            hits.append((float(swept[3]), sphere_index, swept))
    if not hits:
        return None
    _, sphere_index, swept = min(hits, key=lambda item: (item[0], item[1]))
    return sphere_index, swept


def _sphere_sweep_endpoint(previous, current, sphere, swept, restitution,
                           surface_friction):
    """Advance a swept sphere contact through the unconsumed sample time."""
    center, radius, previous_center, previous_radius = sphere
    projected, normal, _, hit = swept
    if (np.array_equal(np.asarray(center), np.asarray(previous_center))
            and float(radius) == float(previous_radius)):
        return np.asarray(projected, dtype=float)
    surface_displacement = (
        np.asarray(center, dtype=float)-np.asarray(previous_center, dtype=float)
        + np.asarray(normal, dtype=float)*(float(radius)-float(previous_radius)))
    relative_displacement = (
        np.asarray(current, dtype=float)-np.asarray(previous, dtype=float)
        - surface_displacement)
    normal_speed = float(np.dot(relative_displacement, normal))
    tangent = relative_displacement-normal_speed*normal
    if normal_speed < 0.0:
        normal_speed = -normal_speed*float(restitution)
    resolved_displacement = (
        normal_speed*normal+tangent*(1.0-float(surface_friction))
        +surface_displacement)
    return np.asarray(projected, dtype=float)+resolved_displacement*(1.0-float(hit))


def _resolve_moving_sphere_sweep_path(previous, current, active_spheres,
                                      clearance, restitution, surface_friction,
                                      fallbacks=()):
    """Resolve a bounded sequence of impacts over one sampled sphere interval."""
    point_start = np.asarray(previous, dtype=float)
    point_end = np.asarray(current, dtype=float)
    start_alpha = 0.0
    velocity_displacement = point_end-point_start
    hit_count = 0
    maximum_penetration = 0.0
    for _ in range(2*len(active_spheres)+2):
        local_spheres = tuple(
            (np.asarray(center, dtype=float), float(radius),
             np.asarray(previous_center, dtype=float)
             +(np.asarray(center, dtype=float)-np.asarray(previous_center, dtype=float))*start_alpha,
             float(previous_radius)+(float(radius)-float(previous_radius))*start_alpha)
            for center, radius, previous_center, previous_radius in active_spheres)
        swept_hit = _first_sphere_sweep_hit(
            point_start, point_end, local_spheres, clearance, fallbacks)
        if swept_hit is None:
            return point_end, velocity_displacement, hit_count, maximum_penetration
        sphere_index, swept = swept_hit
        projected, normal, penetration, local_hit = swept
        maximum_penetration = max(maximum_penetration, float(penetration))
        remaining_fraction = 1.0-start_alpha
        sphere = local_spheres[sphere_index]
        resolved_end = _sphere_sweep_endpoint(
            point_start, point_end, sphere, swept, restitution, surface_friction)
        local_velocity = (resolved_end-projected)/max(
            (1.0-float(local_hit))*remaining_fraction,
            np.finfo(float).tiny)
        velocity_displacement = local_velocity
        hit_count += 1
        moved = (not np.array_equal(sphere[0], sphere[2])
                 or sphere[1] != sphere[3])
        if not moved:
            return np.asarray(projected, dtype=float), velocity_displacement, hit_count, maximum_penetration
        start_alpha += remaining_fraction*float(local_hit)
        if start_alpha >= 1.0-1e-12:
            return np.asarray(projected, dtype=float), velocity_displacement, hit_count, maximum_penetration
        point_start = np.asarray(projected, dtype=float)
        point_end = np.asarray(resolved_end, dtype=float)
    raise ValueError("Secondary moving sphere sweep exceeded its bounded impact limit")


def _project_sphere_set_point(point, target, active_spheres, clearance):
    """Project one published point outside a bounded static/moving sphere set."""
    current = np.asarray(point, dtype=float).copy()
    target = np.asarray(target, dtype=float)
    for _ in range(8*len(active_spheres)+8):
        candidates = []
        for sphere_index, (center, radius, _, _) in enumerate(active_spheres):
            separation = float(np.linalg.norm(current-center))-radius-clearance
            if separation >= -1e-10:
                continue
            others = [item[0] for other_index, item in enumerate(active_spheres)
                      if other_index != sphere_index]
            away = (center-np.mean(others, axis=0)
                    if others else np.zeros(3, dtype=float))
            fallback = _sphere_normal(current, center, (target-center,))
            directions = ((fallback,) if len(active_spheres) == 1 else
                          (current-center, away, target-center, fallback))
            for direction_index, direction in enumerate(directions):
                length = float(np.linalg.norm(direction))
                if length < 1e-10:
                    continue
                normal = direction/length
                projected = center+normal*(radius+clearance)
                worst = max(
                    other_radius+clearance
                    - float(np.linalg.norm(projected-other_center))
                    for other_center, other_radius, _, _ in active_spheres)
                candidates.append((worst, sphere_index, direction_index, projected))
        if not candidates:
            break
        current = min(candidates, key=lambda item: item[:3])[3]
    remaining = max(
        radius+clearance-float(np.linalg.norm(current-center))
        for center, radius, _, _ in active_spheres)
    if remaining > 1e-8:
        raise ValueError("World secondary chain sphere set did not converge to an exterior point")
    return current, max(0.0, remaining)


def _project_compound_plane_spheres_point(point, target, active_spheres,
                                          plane_point, plane_normal, clearance):
    """Project one point outside a planar support and a static sphere set.

    Alternating a sphere projection with a plane projection can oscillate when
    a sphere intersects the support plane.  Include the deterministic circle of
    intersection as a candidate so the bounded projection remains outside both
    surfaces instead of allowing the final blend to reintroduce plane contact.
    """
    current = np.asarray(point, dtype=float).copy()
    target = np.asarray(target, dtype=float)
    plane_point = np.asarray(plane_point, dtype=float)
    plane_normal = np.asarray(plane_normal, dtype=float)
    effective_clearance = float(clearance)

    def project_plane(value):
        separation = float(np.dot(value-plane_point, plane_normal)
                           - effective_clearance)
        return (value-plane_normal*separation
                if separation < -1e-10 else value)

    def score(value):
        return max(
            float(radius)+effective_clearance-float(np.linalg.norm(value-center))
            for center, radius, _, _ in active_spheres)

    for _ in range(16*len(active_spheres)+16):
        current = project_plane(current)
        if score(current) <= 1e-10:
            break
        candidates = []
        projected_target = project_plane(target)
        for sphere_index, (center, radius, _, _) in enumerate(active_spheres):
            effective_radius = float(radius)+effective_clearance
            separation = float(np.linalg.norm(current-center)-effective_radius)
            if separation >= -1e-10:
                continue
            others = [item[0] for other_index, item in enumerate(active_spheres)
                      if other_index != sphere_index]
            away = (center-np.mean(others, axis=0)
                    if others else np.zeros(3, dtype=float))
            fallback=_sphere_normal(current,center,
                                    (projected_target-center,plane_normal))
            directions = (current-center, away, projected_target-center, fallback)
            for direction_index, direction in enumerate(directions):
                length = float(np.linalg.norm(direction))
                if length < 1e-10:
                    continue
                normal = direction/length
                projected = project_plane(center+normal*effective_radius)
                candidates.append((score(projected), sphere_index,
                                   direction_index, projected))

            # A sphere that reaches the plane has a circle of valid boundary
            # points.  Choose the point on that circle nearest the target's
            # tangential direction, with a fixed perpendicular fallback.
            signed_height = float(np.dot(center-plane_point, plane_normal)
                                  - effective_clearance)
            if abs(signed_height) < effective_radius:
                circle_radius = math.sqrt(max(
                    0.0, effective_radius*effective_radius
                    - signed_height*signed_height))
                center_on_plane = center-plane_normal*signed_height
                tangent = projected_target-center_on_plane
                tangent -= plane_normal*float(np.dot(tangent, plane_normal))
                tangent_length = float(np.linalg.norm(tangent))
                if tangent_length < 1e-10:
                    axis = (np.array((1.0, 0.0, 0.0))
                            if abs(float(plane_normal[0])) < .9
                            else np.array((0.0, 1.0, 0.0)))
                    tangent = np.cross(plane_normal, axis)
                    tangent_length = float(np.linalg.norm(tangent))
                if tangent_length >= 1e-10:
                    circle_point = center_on_plane + tangent/tangent_length*circle_radius
                    candidates.append((score(circle_point), sphere_index,
                                       len(directions), circle_point))
        if not candidates:
            break
        current = min(candidates, key=lambda item: item[:3])[3]

    current = project_plane(current)
    remaining = max(
        max(0.0, float(radius)+effective_clearance
            - float(np.linalg.norm(current-center)))
        for center, radius, _, _ in active_spheres)
    remaining = max(remaining, max(0.0, effective_clearance
                                   - float(np.dot(current-plane_point,
                                                  plane_normal))))
    if remaining > 1e-8:
        raise ValueError(
            "World secondary chain compound collider did not converge to a clear point")
    return current, remaining


def validate_capsule_collider(start, end, radius):
    """Validate a static world-space capsule represented by two endpoints."""
    if isinstance(radius, (bool, np.bool_)):
        raise ValueError("Secondary capsule radius must be numeric")
    start = np.asarray(start)
    end = np.asarray(end)
    if start.dtype.kind == "b" or end.dtype.kind == "b":
        raise ValueError("Secondary capsule endpoints must be numeric")
    try:
        start = start.astype(float)
        end = end.astype(float)
        radius = float(radius)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary capsule collider must contain numeric values") from exc
    if (start.shape != (3,) or end.shape != (3,)
            or not np.isfinite(start).all() or not np.isfinite(end).all()
            or not math.isfinite(radius)):
        raise ValueError("Secondary capsule collider must contain finite 3D endpoints and radius")
    if not 1e-6 <= radius <= 1000.0:
        raise ValueError("Secondary capsule radius must be between 0.000001 and 1000 world units")
    with np.errstate(over="ignore", invalid="ignore"):
        segment = end-start
        segment_sq = float(np.dot(segment, segment))
        midpoint = start + 0.5*segment
    if (not np.isfinite(segment).all() or not math.isfinite(segment_sq)
            or not np.isfinite(midpoint).all()):
        raise ValueError("Secondary capsule geometry exceeds the finite coordinate limits")
    if segment_sq < 1e-16:
        raise ValueError("Secondary capsule endpoints must be distinct")
    return start, end, radius


def validate_capsule_trajectories(trajectories, sample_count):
    """Validate sampled endpoint trajectories for a bounded moving capsule.

    The endpoint paths and radius are sampled by the host.  This kernel only
    accepts finite, stable samples; it deliberately does not claim an exact
    continuous moving-surface distance between those samples.
    """
    if type(sample_count) is not int or sample_count < 2:
        raise ValueError("Secondary capsule trajectories need at least two samples")
    if not isinstance(trajectories, (list, tuple)) or len(trajectories) != 3:
        raise ValueError("Secondary capsule trajectories must contain starts, ends, and radii")
    starts = np.asarray(trajectories[0])
    ends = np.asarray(trajectories[1])
    if starts.dtype.kind == "b" or ends.dtype.kind == "b":
        raise ValueError("Secondary capsule trajectories must be numeric")
    try:
        starts = starts.astype(float)
        ends = ends.astype(float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary capsule trajectories must be numeric") from exc
    if (starts.shape != (sample_count, 3) or ends.shape != (sample_count, 3)
            or not np.isfinite(starts).all() or not np.isfinite(ends).all()):
        raise ValueError("Secondary capsule endpoint trajectories must match finite 3D samples")
    raw_radii = np.asarray(trajectories[2])
    if raw_radii.dtype.kind == "b":
        raise ValueError("Secondary capsule radii must be numeric")
    try:
        if raw_radii.ndim == 0:
            radius = np.full(sample_count, float(raw_radii), dtype=float)
        else:
            radius = raw_radii.astype(float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary capsule radii must be numeric") from exc
    if (radius.shape != (sample_count,) or not np.isfinite(radius).all()
            or np.any(radius < 1e-6) or np.any(radius > 1000.0)):
        raise ValueError("Secondary capsule radii must match finite samples and radius limits")
    for start, end, value in zip(starts, ends, radius):
        validate_capsule_collider(start, end, value)
    return starts, ends, radius


def _capsule_closest(point, start, end):
    """Return the closest point on the finite capsule center segment."""
    point = np.asarray(point, dtype=float)
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        segment = end-start
        relative = point-start
        denominator = float(np.dot(segment, segment))
        numerator = float(np.dot(relative, segment))
    if (not np.isfinite(point).all() or not np.isfinite(start).all()
            or not np.isfinite(end).all() or not np.isfinite(segment).all()
            or not np.isfinite(relative).all() or not math.isfinite(denominator)
            or denominator < 1e-16 or not math.isfinite(numerator)):
        raise ValueError("Secondary capsule closest-point geometry was nonfinite or degenerate")
    fraction = numerator/denominator
    fraction = min(1.0, max(0.0, fraction))
    return start + fraction * segment


def _capsule_normal(point, start, end, fallbacks):
    """Return a deterministic outward normal, including centerline degeneracy."""
    closest = _capsule_closest(point, start, end)
    delta = np.asarray(point, dtype=float) - closest
    length = float(np.linalg.norm(delta))
    if length >= 1e-10:
        return delta / length
    axis = end - start
    axis_length = float(np.linalg.norm(axis))
    axis = axis / axis_length
    for fallback in fallbacks:
        fallback = np.asarray(fallback, dtype=float)
        projected = fallback - axis * float(np.dot(fallback, axis))
        length = float(np.linalg.norm(projected))
        if length >= 1e-10:
            return projected / length
    # Pick the world axis least parallel to the capsule, then project it.
    axis_index = int(np.argmin(np.abs(axis)))
    basis = np.zeros(3, dtype=float)
    basis[axis_index] = 1.0
    projected = basis - axis * float(np.dot(basis, axis))
    length = float(np.linalg.norm(projected))
    return projected / length


def _capsule_specs(start, end, radius):
    active = start is not None or end is not None or radius is not None
    if not active:
        return None
    if start is None or end is None or radius is None:
        raise ValueError("Secondary capsule endpoints and radius must be provided together")
    return validate_capsule_collider(start, end, radius)


def _quadratic_first_hit(a, b, c, lower, upper):
    """Return the first parameter in an interval where a quadratic is nonpositive."""
    lower = float(lower)
    upper = float(upper)
    if upper < lower - 1e-12:
        return None
    coefficient_scale=max(abs(a),abs(b),abs(c))
    if coefficient_scale==0.0:
        return None
    a/=coefficient_scale;b/=coefficient_scale;c/=coefficient_scale
    epsilon = 1e-12
    value_at_lower = a*lower*lower + b*lower + c
    derivative_at_lower = 2.0*a*lower+b
    if value_at_lower < -epsilon:
        return lower
    if abs(value_at_lower) <= epsilon and (
            derivative_at_lower < -epsilon
            or (abs(derivative_at_lower) <= epsilon and a < -epsilon)):
        return lower
    if abs(a) <= epsilon:
        if abs(b) <= epsilon:
            return None
        root = -c / b
        if b < 0.0 and root > lower + epsilon and root <= upper + epsilon:
            return root
        return None
    discriminant = b*b - 4.0*a*c
    discriminant_epsilon=(np.finfo(float).eps*16.0
                          * max(b*b,abs(4.0*a*c),np.finfo(float).tiny))
    if discriminant < -discriminant_epsilon:
        return None
    discriminant = max(0.0, discriminant)
    root = math.sqrt(discriminant)
    first = (-b-root) / (2.0*a)
    second = (-b+root) / (2.0*a)
    left, right = sorted((first, second))
    if a > 0.0:
        return (left if left > lower + epsilon
                and left <= min(upper, right) + epsilon else None)
    # A concave quadratic is nonpositive outside its roots. Since the
    # lower endpoint was positive, the first contact is the right root.
    return right if right > lower + epsilon and right <= upper + epsilon else None


def _capsule_sweep_hit(previous, current, start, end, radius, clearance,
                       fallbacks=()):
    """Return the first bounded static point/capsule contact on a linear step.

    Distance to a finite capsule is the minimum of the distances to its two
    endpoint spheres and its projected interior line.  Each feature is a
    quadratic in the moving point's parameter, so the earliest threshold
    crossing can be solved without time sampling.
    """
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    start, end, radius = _capsule_specs(start, end, radius)
    threshold = float(radius) + float(clearance)
    direction = current - previous
    axis = end - start
    axis_squared = float(np.dot(axis, axis))
    candidates = []

    def endpoint_candidate(endpoint):
        offset = previous - endpoint
        return _quadratic_first_hit(
            float(np.dot(direction, direction)),
            2.0 * float(np.dot(offset, direction)),
            float(np.dot(offset, offset)) - threshold*threshold,
            0.0, 1.0)

    for endpoint in (start, end):
        hit = endpoint_candidate(endpoint)
        if hit is not None:
            candidates.append(hit)

    offset = previous - start
    projection_start = float(np.dot(offset, axis) / axis_squared)
    projection_rate = float(np.dot(direction, axis) / axis_squared)
    lower = 0.0
    upper = 1.0
    if abs(projection_rate) <= 1e-14:
        if projection_start < -1e-12 or projection_start > 1.0+1e-12:
            lower = 1.0
            upper = 0.0
    elif projection_rate > 0.0:
        lower = max(lower, -projection_start / projection_rate)
        upper = min(upper, (1.0-projection_start) / projection_rate)
    else:
        lower = max(lower, (1.0-projection_start) / projection_rate)
        upper = min(upper, -projection_start / projection_rate)
    if upper >= lower - 1e-12:
        perpendicular = offset - axis * projection_start
        perpendicular_rate = direction - axis * projection_rate
        hit = _quadratic_first_hit(
            float(np.dot(perpendicular_rate, perpendicular_rate)),
            2.0 * float(np.dot(perpendicular, perpendicular_rate)),
            float(np.dot(perpendicular, perpendicular)) - threshold*threshold,
            max(0.0, lower), min(1.0, upper))
        if hit is not None:
            candidates.append(hit)

    if not candidates:
        return None
    contact_alpha = min(candidates)
    contact = previous + direction * contact_alpha
    closest = _capsule_closest(contact, start, end)
    delta = contact - closest
    distance = float(np.linalg.norm(delta))
    normal = _capsule_normal(contact, start, end, tuple(fallbacks) + (direction,))
    projected = closest + normal * threshold
    return projected, normal, max(0.0, threshold-distance), contact_alpha


def _capsule_trajectory_sweep_hit(previous, current, previous_start,
                                  previous_end, previous_radius, start, end,
                                  radius, clearance, fallbacks=()):
    """Find a bounded contact while both point and capsule interpolate.

    Each substep uses the static analytic capsule sweep at the substep's
    interpolated capsule state.  This catches bounded point-path crossings
    without presenting the result as a globally exact moving/deforming
    capsule solver.
    """
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    previous_start, previous_end, previous_radius = validate_capsule_collider(
        previous_start, previous_end, previous_radius)
    start, end, radius = validate_capsule_collider(start, end, radius)

    def capsule_at(alpha):
        previous_midpoint = (previous_start + previous_end) * 0.5
        current_midpoint = (start + end) * 0.5
        previous_vector = (previous_end - previous_start) * 0.5
        current_vector = (end - start) * 0.5
        previous_length = float(np.linalg.norm(previous_vector))
        current_length = float(np.linalg.norm(current_vector))
        first_direction = previous_vector / previous_length
        second_direction = current_vector / current_length
        cosine = max(-1.0, min(1.0, float(np.dot(
            first_direction, second_direction))))
        if cosine > 1.0 - 1e-10:
            direction = ((1.0-alpha)*first_direction
                         +alpha*second_direction)
            direction /= float(np.linalg.norm(direction))
        elif cosine < -1.0 + 1e-10:
            basis = np.zeros(3, dtype=float)
            basis[int(np.argmin(np.abs(first_direction)))] = 1.0
            perpendicular = np.cross(first_direction, basis)
            perpendicular /= float(np.linalg.norm(perpendicular))
            direction = (math.cos(math.pi*alpha)*first_direction
                         +math.sin(math.pi*alpha)*perpendicular)
        else:
            angle = math.acos(cosine)
            sine = math.sin(angle)
            direction = (math.sin((1.0-alpha)*angle)/sine*first_direction
                         +math.sin(alpha*angle)/sine*second_direction)
        midpoint = previous_midpoint + (current_midpoint-previous_midpoint)*alpha
        half_length = previous_length + (current_length-previous_length)*alpha
        vector = direction*half_length
        return midpoint-vector, midpoint+vector

    best = None
    for step in range(1, MAX_CAPSULE_SWEEP_SUBSTEPS + 1):
        start_alpha = (step - 1) / MAX_CAPSULE_SWEEP_SUBSTEPS
        end_alpha = step / MAX_CAPSULE_SWEEP_SUBSTEPS
        point_a = previous + (current - previous) * start_alpha
        point_b = previous + (current - previous) * end_alpha
        capsule_start_a, capsule_end_a = capsule_at(start_alpha)
        capsule_start, capsule_end = capsule_at(end_alpha)
        radius_a = previous_radius + (radius - previous_radius) * start_alpha
        capsule_radius = previous_radius + (radius - previous_radius) * end_alpha
        candidates = []

        start_motion = capsule_start-capsule_start_a
        end_motion = capsule_end-capsule_end_a
        translation_only = (np.allclose(start_motion, end_motion, rtol=0.0, atol=1e-10)
                            and abs(capsule_radius-radius_a) <= 1e-10)
        if not translation_only:
            swept = _capsule_sweep_hit(
                point_a, point_b, capsule_start, capsule_end, capsule_radius,
                clearance, fallbacks)
            if swept is not None:
                projected, normal, penetration, alpha = swept
                candidates.append((alpha, projected, normal, penetration))

        # A translating capsule can cross a stationary point while both
        # sampled world-space endpoints remain clear.  Solve that bounded
        # relative translation against the substep's starting capsule.  For
        # rotation/deformation this is intentionally an approximation, while
        # the interpolated endpoint-state checks above remain authoritative.
        midpoint_a = (capsule_start_a + capsule_end_a) * 0.5
        midpoint_b = (capsule_start + capsule_end) * 0.5
        local_start = capsule_start_a - midpoint_a
        local_end = capsule_end_a - midpoint_a
        relative_swept = _capsule_sweep_hit(
            point_a - midpoint_a, point_b - midpoint_b,
            local_start, local_end, radius_a, clearance, fallbacks)
        if relative_swept is not None:
            projected, normal, penetration, alpha = relative_swept
            midpoint = midpoint_a + (midpoint_b - midpoint_a) * alpha
            candidates.append((alpha, projected + midpoint, normal, penetration))

        closest = _capsule_closest(point_b, capsule_start, capsule_end)
        distance = float(np.linalg.norm(point_b - closest))
        threshold = capsule_radius + float(clearance)
        if distance < threshold - 1e-10:
            normal = _capsule_normal(
                point_b, capsule_start, capsule_end,
                tuple(fallbacks) + (current - previous,))
            candidates.append((1.0, closest + normal * threshold, normal,
                               threshold - distance))
        if candidates:
            alpha, projected, normal, penetration = min(candidates, key=lambda row: row[0])
            return projected, normal, penetration, (
                start_alpha + (end_alpha - start_alpha) * alpha)
    return best


def _capsule_sweep_endpoint(previous, current, previous_start, previous_end,
                            previous_radius, start, end, radius, swept,
                            restitution, surface_friction):
    """Advance a moving-capsule contact through the unconsumed sample time."""
    projected, normal, _, hit = swept
    axis = np.asarray(end, dtype=float)-np.asarray(start, dtype=float)
    axis_length_squared = float(np.dot(axis, axis))
    contact = np.asarray(projected, dtype=float)-np.asarray(normal, dtype=float)*float(radius)
    amount = max(0.0, min(1.0, float(np.dot(
        contact-np.asarray(start, dtype=float), axis))/axis_length_squared))
    current_surface = np.asarray(start, dtype=float)+axis*amount
    previous_surface = (np.asarray(previous_start, dtype=float)
                        +(np.asarray(previous_end, dtype=float)
                          -np.asarray(previous_start, dtype=float))*amount)
    surface_displacement = (current_surface-previous_surface
                            +np.asarray(normal, dtype=float)
                            *(float(radius)-float(previous_radius)))
    relative_displacement = (np.asarray(current, dtype=float)
                             -np.asarray(previous, dtype=float)
                             -surface_displacement)
    normal_speed = float(np.dot(relative_displacement, normal))
    tangent = relative_displacement-normal_speed*normal
    if normal_speed < 0.0:
        normal_speed = -normal_speed*float(restitution)
    resolved_displacement = (
        normal_speed*normal+tangent*(1.0-float(surface_friction))
        +surface_displacement)
    return np.asarray(projected, dtype=float)+resolved_displacement*(1.0-float(hit))


MAX_MESH_COLLISION_TRIANGLES = 4096
MAX_MESH_SWEEP_SUBSTEPS = 8
MAX_CAPSULE_SWEEP_SUBSTEPS = 8
MAX_SELF_COLLISION_ITERATIONS = 32


def validate_mesh_triangles(triangles):
    """Validate one finite static triangle-mesh collision surface.

    The mesh is deliberately supplied as world-space triangles.  This keeps
    the numerical solver independent from Blender's evaluated-mesh API and
    makes the static-surface contract explicit: no deformation, modifiers, or
    frame-dependent geometry may be hidden inside a solve.
    """
    values = np.asarray(triangles)
    if values.dtype.kind == "b":
        raise ValueError("Secondary mesh collision triangles must be numeric")
    try:
        values = values.astype(float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary mesh collision triangles must be numeric") from exc
    if (values.ndim != 3 or values.shape[1:] != (3, 3)
            or not 1 <= len(values) <= MAX_MESH_COLLISION_TRIANGLES
            or not np.isfinite(values).all()):
        raise ValueError(
            f"Secondary mesh collision needs 1 to {MAX_MESH_COLLISION_TRIANGLES} finite 3D triangles")
    edges = values[:, [1, 2, 0]] - values[:, [0, 0, 0]]
    cross = np.cross(edges[:, 0], edges[:, 1])
    if np.any(np.linalg.norm(cross, axis=1) < 1e-12):
        raise ValueError("Secondary mesh collision cannot contain degenerate triangles")
    return np.array(values, dtype=float, copy=True)


def validate_mesh_trajectories(trajectories, sample_count):
    """Validate one topology-stable sequence of world-space mesh samples."""
    if type(sample_count) is not int or sample_count < 2:
        raise ValueError("Secondary mesh trajectory needs at least two samples")
    values = np.asarray(trajectories)
    if values.dtype.kind == "b":
        raise ValueError("Secondary mesh trajectory triangles must be numeric")
    try:
        values = values.astype(float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Secondary mesh trajectory triangles must be numeric") from exc
    if (values.ndim != 4 or values.shape[0] != sample_count
            or values.shape[2:] != (3, 3)
            or not 1 <= values.shape[1] <= MAX_MESH_COLLISION_TRIANGLES
            or not np.isfinite(values).all()):
        raise ValueError(
            "Secondary mesh trajectory must contain a finite, topology-stable 3D triangle sample per frame")
    edges = values[:, :, [1, 2, 0]] - values[:, :, [0, 0, 0]]
    cross = np.cross(edges[:, :, 0], edges[:, :, 1])
    if np.any(np.linalg.norm(cross, axis=2) < 1e-12):
        raise ValueError("Secondary mesh trajectory cannot contain degenerate triangles")
    return np.array(values, dtype=float, copy=True)


def _closest_point_triangle(point, triangle):
    """Return the closest point on a nondegenerate triangle."""
    a, b, c = triangle
    point = np.asarray(point, dtype=float)
    ab = b - a
    ac = c - a
    ap = point - a
    d1 = float(np.dot(ab, ap))
    d2 = float(np.dot(ac, ap))
    if d1 <= 0.0 and d2 <= 0.0:
        return a.copy()
    bp = point - b
    d3 = float(np.dot(ab, bp))
    d4 = float(np.dot(ac, bp))
    if d3 >= 0.0 and d4 <= d3:
        return b.copy()
    vc = d1*d4 - d3*d2
    if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
        return a + (d1 / (d1-d3)) * ab
    cp = point - c
    d5 = float(np.dot(ab, cp))
    d6 = float(np.dot(ac, cp))
    if d6 >= 0.0 and d5 <= d6:
        return c.copy()
    vb = d5*d2 - d1*d6
    if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
        return a + (d2 / (d2-d6)) * ac
    va = d3*d6 - d5*d4
    if va <= 0.0 and (d4-d3) >= 0.0 and (d5-d6) >= 0.0:
        return b + ((d4-d3) / ((d4-d3)+(d5-d6))) * (c-b)
    denominator = va + vb + vc
    return a + (vb*ab + vc*ac) / denominator


def _mesh_closest(point, triangles, fallbacks):
    point = np.asarray(point, dtype=float)
    best_distance = math.inf
    best_point = None
    best_normal = None
    best_index = -1
    for index, triangle in enumerate(triangles):
        closest = _closest_point_triangle(point, triangle)
        delta = point - closest
        distance = float(np.linalg.norm(delta))
        if distance < best_distance:
            face = np.cross(triangle[1]-triangle[0], triangle[2]-triangle[0])
            face_length = float(np.linalg.norm(face))
            best_distance = distance
            best_point = closest
            best_index = index
            best_normal = face / face_length
            if distance >= 1e-10:
                best_normal = delta / distance
    if best_point is None:
        raise ValueError("Secondary mesh collision has no usable triangle")
    if best_distance < 1e-10:
        for fallback in fallbacks:
            fallback = np.asarray(fallback, dtype=float)
            normal_speed = float(np.dot(fallback, best_normal))
            if abs(normal_speed) >= 1e-10:
                if normal_speed > 0.0:
                    best_normal = -best_normal
                break
    return best_point, best_normal, best_distance, best_index


def _mesh_surface_velocity(point, triangle_index, previous_mesh, current_mesh,
                           seconds):
    """Return the material velocity of a deforming triangle at a contact."""
    previous_triangle = np.asarray(previous_mesh[triangle_index], dtype=float)
    current_triangle = np.asarray(current_mesh[triangle_index], dtype=float)
    contact = _closest_point_triangle(
        np.asarray(point, dtype=float), current_triangle)
    first = current_triangle[1] - current_triangle[0]
    second = current_triangle[2] - current_triangle[0]
    offset = contact - current_triangle[0]
    d00 = float(np.dot(first, first))
    d01 = float(np.dot(first, second))
    d11 = float(np.dot(second, second))
    d20 = float(np.dot(offset, first))
    d21 = float(np.dot(offset, second))
    denominator = d00 * d11 - d01 * d01
    threshold = (np.finfo(float).eps * 32.0
                 * max(d00 * d11, np.finfo(float).tiny))
    if abs(denominator) <= threshold:
        raise ValueError("Secondary mesh contact triangle is degenerate")
    second_weight = (d11 * d20 - d01 * d21) / denominator
    third_weight = (d00 * d21 - d01 * d20) / denominator
    first_weight = 1.0 - second_weight - third_weight
    weights = np.asarray((first_weight, second_weight, third_weight), dtype=float)
    previous_contact = weights @ previous_triangle
    return (contact - previous_contact) / float(seconds)


def _mesh_inside(point, triangles):
    """Use deterministic ray parity for a validated closed triangle mesh."""
    point = np.asarray(point, dtype=float)
    triangles = np.asarray(triangles, dtype=float)
    coordinate_scale = max(
        1.0, float(np.max(np.abs(point))),
        float(np.max(np.abs(triangles))))
    distance_epsilon = np.finfo(float).eps * 32.0 * coordinate_scale
    barycentric_epsilon = np.finfo(float).eps * 32.0
    directions = (
        (1.0, 0.3713906763541037, 0.2176242636071215),
        (0.1732050807568877, 1.0, 0.4142135623730951),
        (0.6180339887498948, 0.2718281828459045, 1.0))
    votes = 0
    for raw_direction in directions:
        direction = np.asarray(raw_direction, dtype=float)
        direction /= float(np.linalg.norm(direction))
        hit_distances = []
        for triangle in triangles:
            a, b, c = triangle
            edge1 = b-a
            edge2 = c-a
            cross = np.cross(direction, edge2)
            determinant = float(np.dot(edge1, cross))
            determinant_epsilon=(np.finfo(float).eps*32.0
                                 * max(float(np.linalg.norm(edge1))
                                       *float(np.linalg.norm(edge2)),
                                       np.finfo(float).tiny))
            if abs(determinant) < determinant_epsilon:
                continue
            inverse = 1.0 / determinant
            offset = point-a
            u = inverse * float(np.dot(offset, cross))
            if u < -barycentric_epsilon or u > 1.0+barycentric_epsilon:
                continue
            q = np.cross(offset, edge1)
            v = inverse * float(np.dot(direction, q))
            if v < -barycentric_epsilon or u+v > 1.0+barycentric_epsilon:
                continue
            distance = inverse * float(np.dot(edge2, q))
            if distance > distance_epsilon:
                hit_distances.append(distance)
        hit_distances.sort()
        unique_hits = []
        for distance in hit_distances:
            if (not unique_hits
                    or abs(distance-unique_hits[-1]) > distance_epsilon):
                unique_hits.append(distance)
        votes += len(unique_hits) % 2
    return votes >= 2


def _mesh_segment_hit(start, end, triangles, closed=False):
    """Return the earliest segment/triangle hit for a validated mesh."""
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    direction = end-start
    if float(np.linalg.norm(direction)) < 1e-12:
        return None
    best = None
    epsilon = 1e-10
    for index, triangle in enumerate(triangles):
        a, b, c = triangle
        edge1 = b-a
        edge2 = c-a
        cross = np.cross(direction, edge2)
        determinant = float(np.dot(edge1, cross))
        determinant_epsilon=(np.finfo(float).eps*32.0
                             * max(float(np.linalg.norm(direction))
                                   *float(np.linalg.norm(edge1))
                                   *float(np.linalg.norm(edge2)),
                                   np.finfo(float).tiny))
        if abs(determinant) < determinant_epsilon:
            continue
        inverse = 1.0/determinant
        offset = start-a
        u = inverse*float(np.dot(offset, cross))
        if u < -epsilon or u > 1.0+epsilon:
            continue
        q = np.cross(offset, edge1)
        v = inverse*float(np.dot(direction, q))
        if v < -epsilon or u+v > 1.0+epsilon:
            continue
        fraction = inverse*float(np.dot(edge2, q))
        if fraction < -epsilon or fraction > 1.0+epsilon:
            continue
        if closed and fraction <= epsilon:
            coordinate_scale=max(1.0,float(np.linalg.norm(start)),
                                 float(np.linalg.norm(end)))
            probe_fraction=min(1e-6,
                np.finfo(float).eps*256.0*coordinate_scale
                /max(float(np.linalg.norm(direction)),np.finfo(float).tiny))
            if not _mesh_inside(start+direction*probe_fraction,triangles):
                continue
        normal = np.cross(edge1, edge2)
        length = float(np.linalg.norm(normal))
        if length < 1e-12:
            continue
        normal = normal/length
        if float(np.dot(normal, direction)) > 0.0:
            normal = -normal
        candidate = (max(0.0, min(1.0, fraction)),
                     start+direction*fraction, normal, index)
        if best is None or candidate[0] < best[0]:
            best = candidate
    return best


def _segment_segment_closest(first_start, first_end, second_start, second_end):
    """Return the closest points and parameters for two finite segments."""
    first_start = np.asarray(first_start, dtype=float)
    first_end = np.asarray(first_end, dtype=float)
    second_start = np.asarray(second_start, dtype=float)
    second_end = np.asarray(second_end, dtype=float)
    first_direction = first_end - first_start
    second_direction = second_end - second_start
    offset = first_start - second_start
    a = float(np.dot(first_direction, first_direction))
    b = float(np.dot(first_direction, second_direction))
    c = float(np.dot(second_direction, second_direction))
    d = float(np.dot(first_direction, offset))
    e = float(np.dot(second_direction, offset))
    denominator = a * c - b * b
    zero = np.finfo(float).tiny
    if a <= zero and c <= zero:
        return first_start.copy(), second_start.copy(), 0.0, 0.0
    if a <= zero:
        second_fraction = max(0.0, min(1.0, e / c))
        return (first_start.copy(),
                second_start + second_direction * second_fraction,
                0.0, second_fraction)
    if c <= zero:
        first_fraction = max(0.0, min(1.0, -d / a))
        return (first_start + first_direction * first_fraction,
                second_start.copy(), first_fraction, 0.0)
    parallel_epsilon=(np.finfo(float).eps*32.0
                      *max(a*c,np.finfo(float).tiny))
    first_fraction = (0.0 if denominator <= parallel_epsilon else
                      max(0.0, min(1.0, (b*e-c*d)/denominator)))
    second_fraction = (b*first_fraction+e)/c
    if second_fraction < 0.0:
        second_fraction = 0.0
        first_fraction = max(0.0, min(1.0, -d/a))
    elif second_fraction > 1.0:
        second_fraction = 1.0
        first_fraction = max(0.0, min(1.0, (b-d)/a))
    return (first_start + first_direction * first_fraction,
            second_start + second_direction * second_fraction,
            first_fraction, second_fraction)


def _mesh_segment_triangle_closest(start, end, triangle):
    """Return exact closest distance between a segment and one filled triangle."""
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    triangle = np.asarray(triangle, dtype=float)
    hit = _mesh_segment_hit(start, end, triangle[None, ...])
    if hit is not None:
        return 0.0, float(hit[0]), np.asarray(hit[1], dtype=float), np.asarray(hit[1], dtype=float)
    best = None

    def consider(distance, segment_fraction, segment_point, triangle_point):
        nonlocal best
        candidate = (float(distance), float(segment_fraction),
                     np.asarray(segment_point, dtype=float),
                     np.asarray(triangle_point, dtype=float))
        if best is None or candidate[0] < best[0]:
            best = candidate

    for segment_fraction, point in ((0.0, start), (1.0, end)):
        triangle_point = _closest_point_triangle(point, triangle)
        consider(np.linalg.norm(point - triangle_point), segment_fraction,
                 point, triangle_point)
    for edge_start, edge_end in ((triangle[0], triangle[1]),
                                 (triangle[1], triangle[2]),
                                 (triangle[2], triangle[0])):
        segment_point, edge_point, segment_fraction, _ = _segment_segment_closest(
            start, end, edge_start, edge_end)
        consider(np.linalg.norm(segment_point - edge_point), segment_fraction,
                 segment_point, edge_point)
    # A segment parallel to the triangle plane can be closest to the triangle
    # interior even when neither endpoint is above the filled triangle and no
    # 3D edge pair is closest.  Add the exact projected overlap candidates.
    face = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    face_length = float(np.linalg.norm(face))
    if face_length >= 1e-12:
        plane_normal = face / face_length
        direction = end - start
        signed_start = float(np.dot(start - triangle[0], plane_normal))
        signed_end = float(np.dot(end - triangle[0], plane_normal))
        if abs(signed_end - signed_start) <= 1e-10:
            projected_start = start - plane_normal * signed_start
            projected_end = end - plane_normal * signed_end
            for segment_fraction, point in ((0.0, projected_start),
                                            (1.0, projected_end)):
                if (np.linalg.norm(point - _closest_point_triangle(point, triangle))
                        <= 1e-10):
                    original = start + direction * segment_fraction
                    consider(abs(signed_start), segment_fraction, original, point)
            for edge_start, edge_end in ((triangle[0], triangle[1]),
                                         (triangle[1], triangle[2]),
                                         (triangle[2], triangle[0])):
                projected_point, edge_point, segment_fraction, _ = _segment_segment_closest(
                    projected_start, projected_end, edge_start, edge_end)
                if np.linalg.norm(projected_point - edge_point) <= 1e-10:
                    original = start + direction * segment_fraction
                    consider(abs(signed_start), segment_fraction, original, edge_point)
    if best is None:
        raise ValueError("Secondary mesh sweep has no usable triangle")
    return best


def _mesh_exact_swept_volume_hit(previous, current, triangles, clearance,
                                 closed, fallbacks=(), volume_radius=0.0):
    """Find the earliest exact static swept-sphere/triangle contact.

    The center follows a line segment and the selected control volume is a
    sphere.  A filled triangle is convex, so its distance along the center
    segment is convex; after finding the segment/triangle minimum, bisection
    gives the first crossing of the exact radius boundary.  This path is
    intentionally static-only; moving and deforming surfaces retain their
    separately bounded interpolation contract.
    """
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    triangles = np.asarray(triangles, dtype=float)
    effective_radius = float(clearance) + float(volume_radius)
    sampled = _mesh_collision_state(
        current, triangles, clearance, closed, fallbacks, volume_radius)
    best = None
    tolerance = 1e-10
    for triangle_index, triangle in enumerate(triangles):
        minimum = _mesh_segment_triangle_closest(previous, current, triangle)
        minimum_distance, minimum_alpha, _, _ = minimum
        if minimum_distance > effective_radius + tolerance:
            continue

        def at(alpha):
            point = previous + (current - previous) * float(alpha)
            closest = _closest_point_triangle(point, triangle)
            return float(np.linalg.norm(point - closest)), closest, point

        start_distance, start_closest, start_point = at(0.0)
        if start_distance <= effective_radius + tolerance:
            if start_distance < effective_radius - tolerance:
                contact_alpha = 0.0
            elif closed and effective_radius <= tolerance:
                coordinate_scale = max(
                    1.0, float(np.linalg.norm(previous)),
                    float(np.linalg.norm(current)))
                probe_alpha = min(
                    1e-5,
                    np.finfo(float).eps * 256.0 * coordinate_scale
                    / max(float(np.linalg.norm(current - previous)),
                          np.finfo(float).tiny))
                _, _, probe_point = at(probe_alpha)
                if not _mesh_inside(probe_point, triangles):
                    continue
                contact_alpha = 0.0
            elif effective_radius <= tolerance:
                continue
            else:
                radial = start_point - start_closest
                radial_length = float(np.linalg.norm(radial))
                velocity = current - previous
                if (radial_length <= np.finfo(float).tiny
                        or float(np.dot(radial, velocity)) / radial_length
                        >= 0.0):
                    continue
                contact_alpha = 0.0
        elif minimum_alpha <= tolerance:
            continue
        else:
            lower = 0.0
            upper = float(minimum_alpha)
            for _ in range(48):
                middle = (lower + upper) * 0.5
                if at(middle)[0] <= effective_radius:
                    upper = middle
                else:
                    lower = middle
            contact_alpha = upper
        distance, closest, point = at(contact_alpha)
        delta = point - closest
        length = float(np.linalg.norm(delta))
        if length >= 1e-10:
            normal = delta / length
        else:
            face = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            face_length = float(np.linalg.norm(face))
            if face_length < 1e-12:
                continue
            normal = face / face_length
            direction = current - previous
            if float(np.dot(normal, direction)) > 0.0:
                normal = -normal
            for fallback in fallbacks:
                fallback = np.asarray(fallback, dtype=float)
                projected = fallback - normal * float(np.dot(fallback, normal))
                projected_length = float(np.linalg.norm(projected))
                if projected_length >= 1e-10:
                    normal = projected / projected_length
                    break
        projected = closest + normal * effective_radius
        candidate = (float(contact_alpha), projected, normal,
                     max(0.0, effective_radius - distance), triangle_index)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        if sampled[0]:
            _, projected, normal, penetration, _, _, triangle_index = sampled
            return projected, normal, penetration, triangle_index
        return None
    _, projected, normal, penetration, triangle_index = best
    return projected, normal, penetration, triangle_index


def _mesh_collision_state(point, triangles, clearance, closed, fallbacks=(), volume_radius=0.0):
    effective_clearance = clearance + volume_radius
    closest, face_normal, distance, triangle_index = _mesh_closest(
        point, triangles, fallbacks)
    coordinate_scale = max(
        1.0, float(np.max(np.abs(point))),
        float(np.max(np.abs(triangles))))
    inside = bool(
        closed
        and distance > np.finfo(float).eps * 32.0 * coordinate_scale
        and _mesh_inside(point, triangles))
    if inside:
        normal = np.asarray(closest-point, dtype=float)
        length = float(np.linalg.norm(normal))
        normal = normal/length if length >= 1e-10 else face_normal
        penetration = distance + effective_clearance
        colliding = True
    else:
        normal = np.asarray(point-closest, dtype=float)
        length = float(np.linalg.norm(normal))
        normal = normal/length if length >= 1e-10 else face_normal
        penetration = effective_clearance-distance
        colliding = penetration > 1e-10
    projected = (closest + normal*effective_clearance) if colliding else np.asarray(point, dtype=float).copy()
    return colliding, projected, normal, penetration, distance, inside, triangle_index


def _mesh_deforming_sweep_hit(previous, current, previous_mesh, current_mesh,
                              clearance, closed, fallbacks=(), volume_radius=0.0):
    """Find a bounded hit while both the point and mesh move between samples."""
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    previous_mesh = np.asarray(previous_mesh, dtype=float)
    current_mesh = np.asarray(current_mesh, dtype=float)
    if previous_mesh.shape != current_mesh.shape:
        raise ValueError("Secondary mesh sweep requires stable triangle topology")
    best = None
    for step in range(1, MAX_MESH_SWEEP_SUBSTEPS + 1):
        start_alpha = (step - 1) / MAX_MESH_SWEEP_SUBSTEPS
        end_alpha = step / MAX_MESH_SWEEP_SUBSTEPS
        start = previous + (current - previous) * start_alpha
        end = previous + (current - previous) * end_alpha
        mesh = previous_mesh + (current_mesh - previous_mesh) * end_alpha
        sampled = _mesh_collision_state(
            end, mesh, clearance, closed, fallbacks, volume_radius)
        swept = _mesh_segment_hit(start, end, mesh, closed)
        if swept is None and not sampled[0]:
            continue
        if swept is not None:
            _, hit_point, normal, triangle_index = swept
            projected = hit_point + normal * (clearance + volume_radius)
            candidate = (projected, normal, 0.0, triangle_index)
        else:
            _, projected, normal, penetration, _, _, triangle_index = sampled
            candidate = (projected, normal, penetration, triangle_index)
        best = candidate
        break
    return best


def _mesh_deforming_volume_sweep_hit(previous, current, previous_mesh, current_mesh,
                                     clearance, closed, fallbacks=(), volume_radius=0.0):
    """Find a bounded moving/deforming finite-volume hit.

    Each bounded interpolation interval evaluates the exact static swept-sphere
    distance against that interval's end mesh.  This closes the finite-volume
    moving/deforming path without claiming a globally exact moving-surface
    distance; the static exact helper remains the authority for static meshes.
    """
    previous = np.asarray(previous, dtype=float)
    current = np.asarray(current, dtype=float)
    previous_mesh = np.asarray(previous_mesh, dtype=float)
    current_mesh = np.asarray(current_mesh, dtype=float)
    if previous_mesh.shape != current_mesh.shape:
        raise ValueError("Secondary mesh volume sweep requires stable triangle topology")
    best = None
    for step in range(1, MAX_MESH_SWEEP_SUBSTEPS + 1):
        start_alpha = (step - 1) / MAX_MESH_SWEEP_SUBSTEPS
        end_alpha = step / MAX_MESH_SWEEP_SUBSTEPS
        start = previous + (current - previous) * start_alpha
        end = previous + (current - previous) * end_alpha
        mesh = previous_mesh + (current_mesh - previous_mesh) * end_alpha
        swept = _mesh_exact_swept_volume_hit(
            start, end, mesh, clearance, closed, fallbacks, volume_radius)
        if swept is not None:
            best = swept
            break
    return best


def resolve_self_collision_positions(points, radius, clearance=0.0):
    """Project selected-control points apart as equal finite self volumes."""
    values = np.asarray(points, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3 or len(values) < 2:
        raise ValueError("Secondary self-collision needs at least two 3D control points")
    if not np.isfinite(values).all():
        raise ValueError("Secondary self-collision points must be finite")
    if (isinstance(radius, (bool, np.bool_)) or not math.isfinite(float(radius))
            or float(radius) <= 0.0):
        raise ValueError("Secondary self-collision radius must be finite and positive")
    if (isinstance(clearance, (bool, np.bool_)) or not math.isfinite(float(clearance))
            or float(clearance) < 0.0):
        raise ValueError("Secondary self-collision clearance must be finite and nonnegative")
    result = np.array(values, dtype=float, copy=True)
    minimum = 2.0 * float(radius) + float(clearance)
    maximum_penetration = 0.0
    collision_pairs = 0
    for _ in range(MAX_SELF_COLLISION_ITERATIONS):
        changed = False
        for first in range(len(result)-1):
            for second in range(first+1, len(result)):
                delta = result[second]-result[first]
                distance = float(np.linalg.norm(delta))
                penetration = minimum-distance
                if penetration <= 1e-10:
                    continue
                if distance >= 1e-10:
                    normal = delta/distance
                else:
                    axis = (first+second) % 3
                    normal = np.zeros(3, dtype=float)
                    normal[axis] = 1.0
                correction = normal * (penetration * .5)
                result[first] -= correction
                result[second] += correction
                maximum_penetration = max(maximum_penetration, penetration)
                collision_pairs += 1
                changed = True
        if not changed:
            break
    residual = 0.0
    for first in range(len(result)-1):
        for second in range(first+1, len(result)):
            residual = max(residual, minimum-
                           float(np.linalg.norm(result[second]-result[first])))
    if residual > 1e-8:
        raise ValueError("Secondary self-collision projection did not converge")
    return result, dict(collision_pairs=collision_pairs,
                        max_raw_penetration=maximum_penetration,
                        max_penetration_after=max(0.0, residual))


def mesh_collision_state(point, triangles, clearance=0.0, closed=False, fallbacks=(), volume_radius=0.0):
    """Return the sampled exclusion state for one point and static mesh."""
    if isinstance(clearance, (bool, np.bool_)) or not math.isfinite(float(clearance)) or float(clearance) < 0.0:
        raise ValueError("Secondary mesh collision clearance must be finite and nonnegative")
    if (isinstance(volume_radius, (bool, np.bool_))
            or not math.isfinite(float(volume_radius)) or float(volume_radius) < 0.0):
        raise ValueError("Secondary mesh collision volume radius must be finite and nonnegative")
    values = validate_mesh_triangles(triangles)
    return _mesh_collision_state(
        point, values, float(clearance), bool(closed), fallbacks, float(volume_radius))


def _inside_triangles(point, triangles, tolerance=1e-8):
    if triangles is None:
        return True
    values = np.asarray(triangles, dtype=float)
    if values.ndim != 3 or values.shape[1:] != (3, 3) or len(values) < 1 or not np.isfinite(values).all():
        raise ValueError("Secondary collision triangles must be finite 3D triangles")
    point = np.asarray(point, dtype=float)
    for a, b, c in values:
        v0 = b-a
        v1 = c-a
        v2 = point-a
        d00 = float(np.dot(v0, v0))
        d01 = float(np.dot(v0, v1))
        d11 = float(np.dot(v1, v1))
        d20 = float(np.dot(v2, v0))
        d21 = float(np.dot(v2, v1))
        denominator = d00*d11-d01*d01
        denominator_epsilon=(np.finfo(float).eps*32.0
                             *max(d00*d11,np.finfo(float).tiny))
        if abs(denominator) < denominator_epsilon:
            continue
        u = (d11*d20-d01*d21)/denominator
        v = (d00*d21-d01*d20)/denominator
        if u >= -tolerance and v >= -tolerance and u+v <= 1.0+tolerance:
            return True
    return False


def follow_world_vectors(values, frame_steps, *, dt, frequency, damping,
                         air_friction, gravity=(0.0, 0.0, 0.0),
                         gravity_scale=0.0, external_acceleration=(0.0, 0.0, 0.0),
                         control_acceleration=(0.0, 0.0, 0.0),
                         wind_velocity=(0.0, 0.0, 0.0),
                         velocity_impulse=(0.0, 0.0, 0.0), impulse_index=None,
                         collision_point=None,
                         collision_normal=None, clearance=0.0,
                         restitution=0.0, surface_friction=0.0,
                         collision_mask=None, collision_triangles=None,
                         collision_sphere_center=None,
                         collision_sphere_radius=None, collision_spheres=None,
                         collision_sphere_trajectories=None,
                         collision_sphere_continuous=False,
                         collision_capsule_start=None, collision_capsule_end=None,
                         collision_capsule_radius=None,
                         collision_capsule_trajectories=None,
                         collision_mesh_triangles=None,
                         collision_mesh_trajectories=None,
                         collision_mesh_closed=False,
                         collision_mesh_volume_radius=0.0,
                         collision_mesh_continuous=False,
                         collision_capsule_continuous=False):
    """Follow world positions under a stable spring and bounded collision.

    The collision represents a selected control as a point with ``clearance``.
    A planar mask can exclude samples outside a bounded planar surface. A
    spherical collider keeps the point outside an explicit static or sampled
    directly animated volume.
    Returned raw dynamics are not influence-blended; callers can preserve
    authored poses.
    """
    target = np.asarray(values, dtype=float)
    steps = np.asarray(frame_steps, dtype=float)
    if target.ndim != 2 or target.shape[1] != 3 or len(target) < 2 or steps.shape != (len(target)-1,):
        raise ValueError("World secondary targets and frame steps disagree")
    if not np.isfinite(target).all() or not np.isfinite(steps).all() or np.any(steps <= 0):
        raise ValueError("World secondary samples must be finite and increasing")
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=0.0, blend_frames=0.0, dt=dt)
    gravity, point, normal = validate_world_settings(
        gravity=gravity, gravity_scale=gravity_scale,
        external_acceleration=external_acceleration,
        wind_velocity=wind_velocity,
        velocity_impulse=velocity_impulse,
        collision_point=collision_point, collision_normal=collision_normal,
        clearance=clearance, restitution=restitution,
        surface_friction=surface_friction)
    control_acceleration = validate_control_acceleration(control_acceleration)
    spheres = _sphere_specs(collision_sphere_center, collision_sphere_radius,
                            collision_spheres)
    moving_spheres = (validate_sphere_trajectories(
        collision_sphere_trajectories, len(target))
        if collision_sphere_trajectories is not None else ())
    sphere_continuous = bool(collision_sphere_continuous)
    capsule = _capsule_specs(collision_capsule_start, collision_capsule_end,
                             collision_capsule_radius)
    capsule_trajectory = (validate_capsule_trajectories(
        collision_capsule_trajectories, len(target))
        if collision_capsule_trajectories is not None else None)
    capsule_continuous = bool(collision_capsule_continuous)
    mesh = (validate_mesh_triangles(collision_mesh_triangles)
            if collision_mesh_triangles is not None else None)
    mesh_trajectory = (validate_mesh_trajectories(
        collision_mesh_trajectories, len(target))
        if collision_mesh_trajectories is not None else None)
    mesh_closed = bool(collision_mesh_closed)
    if (isinstance(collision_mesh_volume_radius, (bool, np.bool_))
            or not math.isfinite(float(collision_mesh_volume_radius))
            or float(collision_mesh_volume_radius) < 0.0):
        raise ValueError("Secondary collision mesh volume radius must be finite and nonnegative")
    mesh_volume_radius = float(collision_mesh_volume_radius)
    mesh_continuous = bool(collision_mesh_continuous)
    if mesh_continuous and not mesh_closed:
        raise ValueError("Continuous mesh collision requires a closed mesh")
    if sum((bool(spheres), bool(moving_spheres), capsule is not None,
            capsule_trajectory is not None,
            mesh is not None, mesh_trajectory is not None)) > 1:
        if spheres and moving_spheres:
            raise ValueError(
                "Secondary collision accepts one sphere input form; static and trajectory "
                "sphere forms cannot be combined")
        if (mesh is not None or mesh_trajectory is not None) and (spheres or moving_spheres):
            raise ValueError(
                "Secondary collision accepts one sphere input form or one mesh input form; "
                "collision inputs are mutually exclusive")
        raise ValueError(
            "Secondary collision inputs are mutually exclusive; spherical or capsule, mesh, "
            "and planar forms cannot be combined")
    sphere_active = bool(spheres or moving_spheres)
    if sphere_continuous and not sphere_active:
        raise ValueError("Secondary continuous sphere collision requires a sphere")
    capsule_active = capsule is not None or capsule_trajectory is not None
    mesh_active = mesh is not None or mesh_trajectory is not None
    if capsule_continuous and not capsule_active:
        raise ValueError("Secondary continuous capsule collision requires a capsule")
    if mesh_continuous and not mesh_active:
        raise ValueError("Secondary continuous mesh collision requires a mesh")
    if sphere_active or capsule_active or mesh_active:
        if point is not None:
            if sphere_active:
                raise ValueError(
                    "Secondary collision accepts one planar or spherical collider, or one sphere "
                    "input form; use one collision input form")
            if capsule_active:
                raise ValueError(
                    "Secondary collision accepts one planar, spherical, or capsule form; use one "
                    "collision input form")
            raise ValueError(
                "Secondary collision accepts one planar, spherical, capsule, or mesh form; use one "
                "collision input form")
        if collision_triangles is not None:
            raise ValueError("Secondary collision triangles require a planar collider")
    if collision_mask is None:
        mask = np.ones(len(target), dtype=bool)
    else:
        mask = np.asarray(collision_mask, dtype=bool)
        if mask.shape != (len(target),):
            raise ValueError("Secondary collision mask must match the samples")
    if collision_triangles is not None:
        if point is None:
            raise ValueError("Secondary collision triangles require a collision plane")
        _inside_triangles(point, collision_triangles)
    omega = 2.0 * math.pi * frequency
    stiffness = omega * omega
    drag = 2.0 * damping * omega + air_friction
    acceleration = (gravity * gravity_scale
                    + np.asarray(external_acceleration, dtype=float)
                    + control_acceleration)
    wind = np.asarray(wind_velocity, dtype=float)
    impulse = np.asarray(velocity_impulse, dtype=float)
    impulse_active = bool(np.any(impulse != 0.0))
    if impulse_active:
        if type(impulse_index) is not int or not 0 <= impulse_index < len(target)-1:
            raise ValueError("Secondary velocity impulse index must precede a following sample")
    elif impulse_index is not None:
        raise ValueError("A zero secondary velocity impulse must not have an impulse index")
    result = np.empty_like(target)
    result[0] = target[0]
    velocity = np.zeros(3, dtype=float)
    current = target[0].copy()
    collisions = 0
    continuous_collisions = 0
    maximum_penetration = 0.0
    for index, frame_step in enumerate(steps, 1):
        if impulse_active and index-1 == impulse_index:
            velocity = velocity + impulse
        previous = current.copy()
        seconds = float(frame_step) * dt
        denominator = 1.0 + seconds * drag + seconds * seconds * stiffness
        velocity = (velocity + seconds * stiffness * (target[index] - current)
                    + seconds * acceleration + seconds * air_friction * wind) / denominator
        current = current + seconds * velocity
        participates = (point is not None or sphere_active or capsule_active or mesh_active) and mask[index]
        response_normal = normal
        if participates and point is not None and collision_triangles is not None:
            projected = current-normal*float(np.dot(current-point, normal))
            participates = _inside_triangles(projected, collision_triangles)
        if participates:
            if not sphere_active and not capsule_active and not mesh_active:
                separation = float(np.dot(current - point, normal) - clearance)
            if sphere_active:
                active_spheres = list(spheres)+[
                    (centers[index], _trajectory_radius(radius, index))
                    for centers, radius in moving_spheres]
                active_sphere_moving = [None]*len(spheres)+list(range(len(moving_spheres)))
                if sphere_continuous:
                    sweep_active_spheres = tuple(
                        (center, radius,
                         (moving_spheres[moving_index][0][index-1]
                          if moving_index is not None else center),
                         (_trajectory_radius(moving_spheres[moving_index][1], index-1)
                          if moving_index is not None else radius))
                        for (center, radius), moving_index in
                        zip(active_spheres, active_sphere_moving))
                    swept_hit = _first_sphere_sweep_hit(
                        previous, current, sweep_active_spheres, clearance,
                        (target[index]-current, -velocity))
                    if swept_hit is not None:
                        sphere_index, swept = swept_hit
                        projected, response_normal, penetration, hit = swept
                        maximum_penetration = max(maximum_penetration, penetration)
                        active_center, active_radius, previous_center, previous_radius = sweep_active_spheres[sphere_index]
                        center_velocity = (active_center-previous_center)/seconds
                        radius_velocity = (active_radius-previous_radius)/seconds
                        surface_velocity = center_velocity + response_normal*radius_velocity
                        relative_velocity = velocity-surface_velocity
                        normal_speed = float(np.dot(relative_velocity, response_normal))
                        tangent = relative_velocity-normal_speed*response_normal
                        if normal_speed < 0.0:
                            normal_speed = -normal_speed*restitution
                        velocity = (normal_speed*response_normal
                                    + tangent*(1.0-surface_friction)
                                    + surface_velocity)
                        current = (projected + velocity*seconds*(1.0-hit)
                                   if active_sphere_moving[sphere_index] is not None
                                   else projected)
                        extra_hits = 0
                        if (active_sphere_moving[sphere_index] is not None
                                and hit < 1.0):
                            remaining_spheres = tuple(
                                (center, radius,
                                 np.asarray(previous_center, dtype=float)
                                 +(np.asarray(center, dtype=float)
                                   -np.asarray(previous_center, dtype=float))*hit,
                                 float(previous_radius)
                                 +(float(radius)-float(previous_radius))*hit)
                                for center, radius, previous_center, previous_radius
                                in sweep_active_spheres)
                            (current, displacement, extra_hits,
                             extra_penetration) = _resolve_moving_sphere_sweep_path(
                                projected, current, remaining_spheres, clearance,
                                restitution, surface_friction,
                                (target[index]-current, -velocity))
                            velocity = displacement/(seconds*(1.0-hit))
                            maximum_penetration = max(
                                maximum_penetration, extra_penetration)
                        collisions += 1+extra_hits
                        continuous_collisions += 1+extra_hits
                rows = [(radius+clearance-float(np.linalg.norm(current-center)),
                         center, radius, sphere_index)
                        for sphere_index, (center, radius) in enumerate(active_spheres)]
                penetration, _, _, sphere_index = max(rows, key=lambda row: row[0])
                if penetration > 1e-10:
                    maximum_penetration = max(maximum_penetration, penetration)
                    before_projection = current.copy()
                    projection_spheres = tuple((center, radius, center, radius)
                                               for center, radius in active_spheres)
                    current, _ = _project_sphere_set_point(
                        current, target[index], projection_spheres, clearance)
                    response_normal = _sphere_normal(
                        current, before_projection,
                        (target[index]-before_projection, -velocity))
                    moving_index=active_sphere_moving[sphere_index]
                    if moving_index is not None:
                        centers, radii = moving_spheres[moving_index]
                        collider_velocity = ((centers[index]-centers[index-1]) / seconds)
                        radius_velocity = ((_trajectory_radius(radii, index)
                                            - _trajectory_radius(radii, index-1)) / seconds)
                        collider_velocity = collider_velocity + response_normal*radius_velocity
                        relative_velocity = velocity-collider_velocity
                    else:
                        collider_velocity = None
                        relative_velocity = velocity
                    normal_speed = float(np.dot(relative_velocity, response_normal))
                    tangent = relative_velocity-normal_speed*response_normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*restitution
                    velocity = normal_speed*response_normal + tangent*(1.0-surface_friction)
                    if collider_velocity is not None:
                        velocity = velocity+collider_velocity
                    collisions += 1
            elif capsule_active:
                if capsule_trajectory is not None:
                    previous_start = capsule_trajectory[0][index-1]
                    previous_end = capsule_trajectory[1][index-1]
                    previous_radius = capsule_trajectory[2][index-1]
                    start = capsule_trajectory[0][index]
                    end = capsule_trajectory[1][index]
                    radius = capsule_trajectory[2][index]
                    midpoint_velocity = (
                        ((start + end) - (previous_start + previous_end))
                        * 0.5 / seconds)
                    radius_velocity = (radius - previous_radius) / seconds
                else:
                    previous_start = previous_end = None
                    previous_radius = None
                    start, end, radius = capsule
                    midpoint_velocity = np.zeros(3, dtype=float)
                    radius_velocity = 0.0

                def respond_capsule(normal):
                    nonlocal velocity, collisions
                    surface_velocity = (midpoint_velocity
                                        + np.asarray(normal, dtype=float)
                                        * radius_velocity)
                    relative_velocity = velocity - surface_velocity
                    normal_speed = float(np.dot(relative_velocity, normal))
                    tangent = relative_velocity-normal_speed*normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed * restitution
                    velocity = (normal_speed*normal
                                + tangent*(1.0-surface_friction)
                                + surface_velocity)
                    collisions += 1

                fallbacks = (target[index] - current, -velocity)
                swept = (_capsule_trajectory_sweep_hit(
                    previous, current, previous_start, previous_end,
                    previous_radius, start, end, radius, clearance, fallbacks)
                         if capsule_trajectory is not None and capsule_continuous
                         else _capsule_sweep_hit(
                             previous, current, start, end, radius, clearance,
                             fallbacks)
                         if capsule_continuous else None)
                if swept is not None:
                    projected, response_normal, penetration, hit = swept
                    maximum_penetration = max(maximum_penetration, penetration)
                    current = projected
                    respond_capsule(response_normal)
                    if capsule_trajectory is not None:
                        current = projected+velocity*seconds*(1.0-hit)
                    continuous_collisions += 1
                else:
                    for _ in range(16):
                        closest = _capsule_closest(current, start, end)
                        distance = float(np.linalg.norm(current - closest))
                        penetration = radius + clearance - distance
                        if penetration <= 1e-10:
                            break
                        response_normal = _capsule_normal(
                            current, start, end, (target[index] - closest, -velocity))
                        maximum_penetration = max(maximum_penetration, penetration)
                        current = closest + response_normal * (radius + clearance)
                        respond_capsule(response_normal)
                    closest = _capsule_closest(current, start, end)
                    if radius + clearance - float(np.linalg.norm(current - closest)) > 1e-8:
                        raise ValueError("Secondary capsule collider did not converge to an exterior point")
                closest = _capsule_closest(current, start, end)
                distance = float(np.linalg.norm(current - closest))
                penetration = radius + clearance - distance
                if penetration > 1e-10:
                    response_normal = _capsule_normal(
                        current, start, end, (target[index] - closest, -velocity))
                    maximum_penetration = max(maximum_penetration, penetration)
                    current = closest + response_normal * (radius + clearance)
                    respond_capsule(response_normal)
            elif mesh_active:
                swept = None
                active_mesh = (mesh_trajectory[index]
                               if mesh_trajectory is not None else mesh)
                fallbacks = (target[index]-current, -velocity)
                if mesh_continuous and mesh_trajectory is not None:
                    sweep = (_mesh_deforming_volume_sweep_hit
                              if clearance + mesh_volume_radius > 0.0
                              else _mesh_deforming_sweep_hit)
                    swept = sweep(
                        previous, current, mesh_trajectory[index-1], active_mesh,
                        clearance, mesh_closed, fallbacks, mesh_volume_radius)
                    if swept is None:
                        colliding = False
                        projected = current
                        response_normal = normal
                        penetration = 0.0
                    else:
                        projected, response_normal, penetration, triangle_index = swept
                        colliding = True
                else:
                    (colliding, projected, response_normal, penetration,
                     _, _, triangle_index) = _mesh_collision_state(
                        current, active_mesh, clearance, mesh_closed,
                        fallbacks, mesh_volume_radius)
                    if (mesh_continuous and clearance+mesh_volume_radius > 0.0
                            and mesh_trajectory is None):
                        swept = _mesh_exact_swept_volume_hit(
                            previous, current, active_mesh, clearance,
                            mesh_closed, fallbacks, mesh_volume_radius)
                        if swept is not None:
                            projected, response_normal, penetration, triangle_index = swept
                            colliding = True
                    else:
                        swept = (_mesh_segment_hit(previous, current, active_mesh,
                                                   mesh_closed)
                                 if mesh_continuous else None)
                        if swept is not None:
                            _, hit_point, response_normal, triangle_index = swept
                            projected = (hit_point + response_normal
                                         * (clearance + mesh_volume_radius))
                            colliding = True
                            penetration = 0.0
                if swept is not None:
                    continuous_collisions += 1
                if colliding:
                    maximum_penetration = max(maximum_penetration, penetration)
                    current = projected
                    endpoint_state = _mesh_collision_state(
                        current, active_mesh, clearance, mesh_closed,
                        fallbacks, mesh_volume_radius)
                    if endpoint_state[0]:
                        current=endpoint_state[1]
                        response_normal=endpoint_state[2]
                        triangle_index=endpoint_state[6]
                        maximum_penetration=max(
                            maximum_penetration,float(endpoint_state[3]))
                    surface_velocity = (_mesh_surface_velocity(
                        current, triangle_index, mesh_trajectory[index-1],
                        active_mesh, seconds)
                        if mesh_trajectory is not None else np.zeros(3, dtype=float))
                    relative_velocity = velocity-surface_velocity
                    normal_speed = float(np.dot(relative_velocity, response_normal))
                    tangent = relative_velocity-normal_speed*response_normal
                    if normal_speed < 0.0:
                        normal_speed = -normal_speed*restitution
                    velocity = (normal_speed*response_normal
                                + tangent*(1.0-surface_friction)
                                + surface_velocity)
                    collisions += 1
            elif separation < 0.0:
                maximum_penetration = max(maximum_penetration, -separation)
                current = current - separation * response_normal
                normal_speed = float(np.dot(velocity, response_normal))
                tangent = velocity - normal_speed * response_normal
                if normal_speed < 0.0:
                    normal_speed = -normal_speed * restitution
                velocity = normal_speed * response_normal + tangent * (1.0 - surface_friction)
                collisions += 1
        result[index] = current
    if not np.isfinite(result).all():
        raise ValueError("World secondary dynamics produced nonfinite output")
    return result, dict(collision_samples=collisions,
                        continuous_collision_samples=continuous_collisions,
                        max_raw_penetration=maximum_penetration)


def apply_world_vector_follow(values, frames, *, dt, frequency, damping,
                              air_friction, strength, blend_frames,
                              gravity=(0.0, 0.0, 0.0), gravity_scale=0.0,
                              external_acceleration=(0.0, 0.0, 0.0),
                              control_acceleration=(0.0, 0.0, 0.0),
                              wind_velocity=(0.0, 0.0, 0.0),
                              velocity_impulse=(0.0, 0.0, 0.0), impulse_index=None,
                              collision_point=None, collision_normal=None,
                              clearance=0.0, restitution=0.0,
                              surface_friction=0.0, collision_mask=None,
                              collision_triangles=None,
                              collision_sphere_center=None,
                              collision_sphere_radius=None, collision_spheres=None,
                              collision_sphere_trajectories=None,
                              collision_sphere_continuous=False,
                              collision_capsule_start=None, collision_capsule_end=None,
                              collision_capsule_radius=None,
                              collision_capsule_trajectories=None,
                              collision_mesh_triangles=None,
                              collision_mesh_trajectories=None,
                              collision_mesh_closed=False,
                              collision_mesh_volume_radius=0.0,
                              collision_mesh_continuous=False,
                              collision_capsule_continuous=False,
                              envelope=None):
    target = np.asarray(values, dtype=float)
    times = np.asarray(frames, dtype=float)
    validate_settings(frequency=frequency, damping=damping, air_friction=air_friction,
                      strength=strength, blend_frames=blend_frames, dt=dt)
    follower, metrics = follow_world_vectors(
        target, np.diff(times), dt=dt, frequency=frequency, damping=damping,
        air_friction=air_friction, gravity=gravity, gravity_scale=gravity_scale,
        external_acceleration=external_acceleration,
        control_acceleration=control_acceleration,
        wind_velocity=wind_velocity,
        velocity_impulse=velocity_impulse, impulse_index=impulse_index,
        collision_point=collision_point, collision_normal=collision_normal,
        clearance=clearance, restitution=restitution,
        surface_friction=surface_friction, collision_mask=collision_mask,
        collision_triangles=collision_triangles,
        collision_sphere_center=collision_sphere_center,
        collision_sphere_radius=collision_sphere_radius,
        collision_spheres=collision_spheres,
        collision_sphere_trajectories=collision_sphere_trajectories,
        collision_sphere_continuous=collision_sphere_continuous,
                              collision_capsule_start=collision_capsule_start,
                              collision_capsule_end=collision_capsule_end,
        collision_capsule_radius=collision_capsule_radius,
        collision_capsule_trajectories=collision_capsule_trajectories,
                              collision_mesh_triangles=collision_mesh_triangles,
                              collision_mesh_trajectories=collision_mesh_trajectories,
                              collision_mesh_closed=collision_mesh_closed,
                              collision_mesh_volume_radius=collision_mesh_volume_radius,
                              collision_mesh_continuous=collision_mesh_continuous,
                              collision_capsule_continuous=collision_capsule_continuous)
    base_weight=(boundary_envelope(times,blend_frames) if envelope is None
                 else np.asarray(envelope,dtype=float))
    if (base_weight.shape!=(len(times),) or not np.isfinite(base_weight).all()
            or np.any((base_weight<0)|(base_weight>1))):
        raise ValueError("Secondary-motion envelope must be within zero and one")
    weight=base_weight*strength
    result = target + (follower - target) * weight[:, None]
    result[0] = target[0]
    result[-1] = target[-1]
    editable_mask=weight>0.0
    editable_mask[0]=False;editable_mask[-1]=False
    if collision_point is not None:
        _, point, normal = validate_world_settings(
            gravity=gravity, gravity_scale=gravity_scale,
            external_acceleration=external_acceleration,
            wind_velocity=wind_velocity,
            velocity_impulse=velocity_impulse,
            collision_point=collision_point, collision_normal=collision_normal,
            clearance=clearance, restitution=restitution,
            surface_friction=surface_friction)
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool).copy())
        before_mask = base_mask.copy()
        after_mask = base_mask.copy()
        if collision_triangles is not None:
            for index, value in enumerate(target):
                projected = value-normal*float(np.dot(value-point, normal))
                before_mask[index] = before_mask[index] and _inside_triangles(projected, collision_triangles)
            for index, value in enumerate(result):
                projected = value-normal*float(np.dot(value-point, normal))
                after_mask[index] = after_mask[index] and _inside_triangles(projected, collision_triangles)
        before = np.dot(target-point, normal)-clearance
        for index in np.flatnonzero(base_mask & editable_mask):
            projected = result[index]-normal*float(np.dot(result[index]-point, normal))
            if (collision_triangles is not None
                    and not _inside_triangles(projected, collision_triangles)):
                continue
            separation = float(np.dot(result[index]-point, normal)-clearance)
            if separation < 0.0:
                result[index] = result[index]-normal*separation
        if collision_triangles is not None:
            for index, value in enumerate(result):
                projected = value-normal*float(np.dot(value-point, normal))
                after_mask[index] = base_mask[index] and _inside_triangles(
                    projected, collision_triangles)
        after = np.dot(result-point, normal)-clearance
        finite_before = before[before_mask]
        finite_after = after[after_mask]
        metrics["max_penetration_before"] = float(max(0.0, -np.min(finite_before))) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(max(0.0, -np.min(finite_after))) if finite_after.size else 0.0
    elif (collision_sphere_center is not None
          or collision_sphere_radius is not None
          or collision_spheres is not None):
        spheres = _sphere_specs(collision_sphere_center, collision_sphere_radius,
                                collision_spheres)
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool))
        before = np.asarray([[float(np.linalg.norm(value-center))-(radius+clearance)
                              for value in target] for center, radius in spheres])
        for index in np.flatnonzero(base_mask & editable_mask):
            active_spheres = tuple((center, radius, center, radius)
                                   for center, radius in spheres)
            if collision_sphere_continuous and index > 0 and base_mask[index-1]:
                swept_hit = _first_sphere_sweep_hit(
                    result[index-1], result[index], active_spheres, clearance,
                    (follower[index]-result[index], target[index]-result[index]))
                if swept_hit is not None:
                    result[index], _, _, _ = _resolve_moving_sphere_sweep_path(
                        result[index-1], result[index], active_spheres,
                        clearance, restitution, surface_friction,
                        (follower[index]-result[index],
                         target[index]-result[index]))
            result[index], _ = _project_sphere_set_point(
                result[index], target[index], active_spheres, clearance)
        after = np.asarray([[float(np.linalg.norm(value-center))-(radius+clearance)
                             for value in result] for center, radius in spheres])
        finite_before = before[:, base_mask]
        finite_after = after[:, base_mask]
        metrics["max_penetration_before"] = float(max(0.0, -np.min(finite_before))) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(max(0.0, -np.min(finite_after))) if finite_after.size else 0.0
    elif collision_capsule_trajectories is not None:
        starts, ends, radii = validate_capsule_trajectories(
            collision_capsule_trajectories, len(target))
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool))
        if base_mask.shape != (len(target),):
            raise ValueError("Secondary collision mask must match the samples")
        before = np.asarray([
            float(np.linalg.norm(value - _capsule_closest(value, starts[index], ends[index])))
            - (radii[index] + clearance)
            for index, value in enumerate(target)])
        for index in np.flatnonzero(base_mask & editable_mask):
            if collision_capsule_continuous and index > 0 and base_mask[index-1]:
                swept = _capsule_trajectory_sweep_hit(
                    result[index-1], result[index], starts[index-1], ends[index-1],
                    radii[index-1], starts[index], ends[index], radii[index],
                    clearance, (follower[index]-result[index],
                                target[index]-result[index]))
                if swept is not None:
                    result[index] = _capsule_sweep_endpoint(
                        result[index-1], result[index], starts[index-1],
                        ends[index-1], radii[index-1], starts[index],
                        ends[index], radii[index], swept, restitution,
                        surface_friction)
            for _ in range(16):
                closest = _capsule_closest(result[index], starts[index], ends[index])
                distance = float(np.linalg.norm(result[index] - closest))
                penetration = radii[index] + clearance - distance
                if penetration <= 1e-10:
                    break
                direction = _capsule_normal(
                    result[index], starts[index], ends[index],
                    (follower[index] - closest, target[index] - closest))
                result[index] = closest + direction * (radii[index] + clearance)
            closest = _capsule_closest(result[index], starts[index], ends[index])
            if radii[index] + clearance - float(np.linalg.norm(result[index] - closest)) > 1e-8:
                raise ValueError("Secondary moving capsule did not converge to an exterior point")
        after = np.asarray([
            float(np.linalg.norm(value - _capsule_closest(value, starts[index], ends[index])))
            - (radii[index] + clearance)
            for index, value in enumerate(result)])
        finite_before = before[base_mask]
        finite_after = after[base_mask]
        metrics["max_penetration_before"] = float(max(0.0, -np.min(finite_before))) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(max(0.0, -np.min(finite_after))) if finite_after.size else 0.0
    elif (collision_capsule_start is not None or collision_capsule_end is not None
          or collision_capsule_radius is not None):
        start, end, radius = _capsule_specs(
            collision_capsule_start, collision_capsule_end, collision_capsule_radius)
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool))
        before = np.asarray([
            float(np.linalg.norm(value - _capsule_closest(value, start, end)))
            - (radius + clearance) for value in target])
        for index in np.flatnonzero(base_mask & editable_mask):
            if collision_capsule_continuous and index > 0 and base_mask[index-1]:
                swept = _capsule_sweep_hit(
                    result[index-1], result[index], start, end, radius, clearance,
                    (follower[index]-result[index], target[index]-result[index]))
                if swept is not None:
                    result[index] = swept[0]
            for _ in range(16):
                closest = _capsule_closest(result[index], start, end)
                distance = float(np.linalg.norm(result[index] - closest))
                penetration = radius + clearance - distance
                if penetration <= 1e-10:
                    break
                direction = _capsule_normal(
                    result[index], start, end,
                    (follower[index] - closest, target[index] - closest))
                result[index] = closest + direction * (radius + clearance)
            closest = _capsule_closest(result[index], start, end)
            if radius + clearance - float(np.linalg.norm(result[index] - closest)) > 1e-8:
                raise ValueError("Secondary capsule collider did not converge to an exterior point")
        after = np.asarray([
            float(np.linalg.norm(value - _capsule_closest(value, start, end)))
            - (radius + clearance) for value in result])
        finite_before = before[base_mask]
        finite_after = after[base_mask]
        metrics["max_penetration_before"] = float(max(0.0, -np.min(finite_before))) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(max(0.0, -np.min(finite_after))) if finite_after.size else 0.0
    elif (collision_mesh_triangles is not None
          or collision_mesh_trajectories is not None):
        mesh = (validate_mesh_triangles(collision_mesh_triangles)
                if collision_mesh_triangles is not None else None)
        mesh_trajectory = (validate_mesh_trajectories(
            collision_mesh_trajectories, len(target))
            if collision_mesh_trajectories is not None else None)
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool))
        if base_mask.shape != (len(target),):
            raise ValueError("Secondary collision mask must match the samples")
        before = np.asarray([
            _mesh_collision_state(value,
                                  mesh_trajectory[index] if mesh_trajectory is not None else mesh,
                                  clearance, bool(collision_mesh_closed),
                                  (follower[index]-value,), collision_mesh_volume_radius) [3]
            for index, value in enumerate(target)])
        before = np.maximum(before, 0.0)
        for index in np.flatnonzero(base_mask & editable_mask):
            if collision_mesh_continuous and index > 0 and base_mask[index-1]:
                if mesh_trajectory is not None:
                    sweep = (_mesh_deforming_volume_sweep_hit
                             if clearance + collision_mesh_volume_radius > 0.0
                             else _mesh_deforming_sweep_hit)
                    swept = sweep(
                        result[index-1], result[index], mesh_trajectory[index-1],
                        mesh_trajectory[index], clearance,
                        bool(collision_mesh_closed),
                        (follower[index]-result[index], target[index]-result[index]),
                        collision_mesh_volume_radius)
                else:
                    swept = _mesh_exact_swept_volume_hit(
                        result[index-1], result[index], mesh, clearance,
                        bool(collision_mesh_closed),
                        (follower[index]-result[index], target[index]-result[index]),
                        collision_mesh_volume_radius)
                if swept is not None:
                    result[index] = swept[0]
            for _ in range(4):
                state = _mesh_collision_state(
                    result[index],
                    mesh_trajectory[index] if mesh_trajectory is not None else mesh,
                    clearance, bool(collision_mesh_closed),
                    (follower[index]-result[index], target[index]-result[index]),
                    collision_mesh_volume_radius)
                if not state[0]:
                    break
                result[index] = state[1]
            state = _mesh_collision_state(
                result[index],
                mesh_trajectory[index] if mesh_trajectory is not None else mesh,
                clearance, bool(collision_mesh_closed),
                (follower[index]-result[index], target[index]-result[index]),
                collision_mesh_volume_radius)
            if state[0]:
                raise ValueError("Secondary mesh collider did not converge to a clear point")
        after = np.asarray([
            max(0.0, _mesh_collision_state(
                value,
                mesh_trajectory[index] if mesh_trajectory is not None else mesh,
                clearance, bool(collision_mesh_closed), (follower[index]-value,),
                collision_mesh_volume_radius)[3])
            for index, value in enumerate(result)])
        finite_before = before[base_mask]
        finite_after = after[base_mask]
        metrics["max_penetration_before"] = float(np.max(finite_before)) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(np.max(finite_after)) if finite_after.size else 0.0
    elif collision_sphere_trajectories is not None:
        spheres = validate_sphere_trajectories(
            collision_sphere_trajectories, len(target))
        base_mask = (np.ones(len(target), dtype=bool) if collision_mask is None
                     else np.asarray(collision_mask, dtype=bool))
        before = np.asarray([
            [float(np.linalg.norm(target[index]-centers[index]))
             -(_trajectory_radius(radius, index)+clearance)
             for index in range(len(target))]
            for centers, radius in spheres])
        for index in np.flatnonzero(base_mask & editable_mask):
            active_spheres = tuple(
                (centers[index], _trajectory_radius(radius, index),
                 centers[index-1] if index > 0 else centers[index],
                 _trajectory_radius(radius, index-1) if index > 0
                 else _trajectory_radius(radius, index))
                for centers, radius in spheres)
            if collision_sphere_continuous and index > 0 and base_mask[index-1]:
                swept_hit = _first_sphere_sweep_hit(
                    result[index-1], result[index], active_spheres, clearance,
                    (follower[index]-result[index], target[index]-result[index]))
                if swept_hit is not None:
                    result[index], _, _, _ = _resolve_moving_sphere_sweep_path(
                        result[index-1], result[index], active_spheres,
                        clearance, restitution, surface_friction,
                        (follower[index]-result[index],
                         target[index]-result[index]))
            result[index], _ = _project_sphere_set_point(
                result[index], target[index], active_spheres, clearance)
        after = np.asarray([
            [float(np.linalg.norm(result[index]-centers[index]))
             -(_trajectory_radius(radius, index)+clearance)
             for index in range(len(target))]
            for centers, radius in spheres])
        finite_before = before[:, base_mask]
        finite_after = after[:, base_mask]
        metrics["max_penetration_before"] = float(max(0.0, -np.min(finite_before))) if finite_before.size else 0.0
        metrics["max_penetration_after"] = float(max(0.0, -np.min(finite_after))) if finite_after.size else 0.0
    else:
        metrics["max_penetration_before"] = 0.0
        metrics["max_penetration_after"] = 0.0
    metrics["max_world_correction"] = float(np.max(np.linalg.norm(result-target, axis=1)))
    result[0] = target[0]
    result[-1] = target[-1]
    return result, metrics
