"""Compare group-weighted constraint projection on the frozen BoneForge jump."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
BASE = ROOT / "training" / "b4artists_ml" / "results" / "group-weighted-trajectory-v3"
PROFILE = "boneforge"
DEADLINE = 1789053845
VARIANTS = {
    "uniform": {},
    "grouped16": {"core": 4.0, "upper": 16.0},
    "distal64": {"core": 4.0, "torso": 4.0, "arm": 8.0, "forearm": 16.0, "hand": 64.0},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def host_main():
    sys.path.insert(0, str(ROOT))
    import bpy
    import numpy as np
    import b4artists_ml
    from mathutils import Quaternion, Vector
    from b4artists_ml import body_solver as bs, contacts as c, flight as f, posing as p, support
    from b4artists_ml import workflow as w
    from b4artists_ml.support_math import center_of_mass

    started = time.perf_counter()
    report = {
        "schema": 1,
        "complete": False,
        "qualified": False,
        "profile": PROFILE,
        "method": "phase_ramped_group_weighted_constraint_projection",
        "learned": False,
        "script_sha256": sha256(HERE),
        "variants": [],
    }

    def persist():
        write_json(BASE / "report.json", report)

    def budget():
        if time.perf_counter() - started > 900 or time.time() > DEADLINE:
            raise TimeoutError("Frozen group-weighted trajectory budget exhausted")

    try:
        source_report_path = ROOT / "training" / "b4artists_ml" / "results" / "grounded-jump-diagnostic-v1" / PROFILE / "report.json"
        source_report = json.loads(source_report_path.read_text(encoding="utf-8"))
        blend = ROOT / source_report["blend"]
        assert sha256(blend) == source_report["blend_sha256"]
        original_path = ROOT / "training" / "b4artists_ml" / "results" / "coupled-trajectory-v1"
        original_report = json.loads((original_path / "report.json").read_text(encoding="utf-8"))
        assert original_report["complete"] and original_report["source_preserved"]
        envelope_path = ROOT / "training" / "b4artists_ml" / "results" / "jump-temporal-envelope-v1" / "report.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert envelope["complete"] and not envelope["qualified"] and not envelope["method_promoted"]
        report["input_blend_sha256"] = sha256(blend)
        report["input_trajectory_sha256"] = sha256(original_path / "latest-trajectory.npz")
        report["reference_envelope_sha256"] = sha256(envelope_path)

        b4artists_ml.register()
        bpy.ops.wm.open_mainfile(filepath=str(blend), use_scripts=False)
        rigs = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and obj.b4ml.candidate_action]
        assert len(rigs) == 1
        obj = rigs[0]
        scene = bpy.context.scene
        initial_frame = p._frame(scene)
        initial_pose = w.raw_pose(obj)
        source_token = f._curve_token(obj)
        original_actions = set(bpy.data.actions.keys())
        original_objects = set(bpy.data.objects.keys())
        binding = bs.mapping(obj)
        names = binding["names"]
        root = binding["root"]
        controls = list(dict.fromkeys(binding["rotations"] + binding["effectors"]))
        legs = [row for row in p.bindings(obj)[2] if row["id"] in ("leg-L", "leg-R")]
        masses = [item.weight for item in obj.b4ml.mass_segments]
        fractions = [item.fraction for item in obj.b4ml.mass_segments]

        def raw_equal(left, right):
            return left.keys() == right.keys() and all(
                all(left[name][key] == right[name][key]
                    for key in ("mode", "location", "scale", "raw_rotation", "channels"))
                for name in left)

        def geometry():
            p._update(obj)
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            world = w.display_world(obj)
            heads = np.asarray([world @ evaluated.pose.bones[name].head for name in names])
            tails = np.asarray([world @ evaluated.pose.bones[name].tail for name in names])
            starts = np.asarray([heads[i] for _, i, _, _ in support.SEGMENTS])
            ends = np.asarray([heads[j] if j is not None else tails[i] for _, i, j, _ in support.SEGMENTS])
            com = center_of_mass(starts, ends, masses, fractions)[0]
            trunk = float(sum(np.linalg.norm(ends[index] - starts[index]) for index in range(3)))
            return com, heads, trunk

        c._frame(scene, 1)
        _, _, trunk = geometry()
        root_origin = np.asarray(w.display_world(obj) @ obj.pose.bones[root].head)
        reference_quaternions = [bs._quat(obj.pose.bones[name]) for name in controls]
        feet = [{
            "point": np.asarray((w.display_world(obj) @ obj.pose.bones[row["joints"][2]].matrix).translation),
            "rotation": (w.display_world(obj) @ obj.pose.bones[row["joints"][2]].matrix).to_quaternion(),
        } for row in legs]
        leg_scale = source_report["leg_length_world"]
        frames = np.arange(1.0, 50.0)
        fixed = np.asarray([0, 8, 14, 32, 38, 48])
        pins = set(frames[fixed])
        dimension = 3 + 3 * len(controls)

        def rotation_vector(quaternion):
            if quaternion.w < 0:
                quaternion.negate()
            vector = np.asarray([quaternion.x, quaternion.y, quaternion.z])
            length = np.linalg.norm(vector)
            return vector * (2 * np.arctan2(length, quaternion.w) / length) if length > 1e-12 else vector * 2

        def sample_base(frame):
            c._frame(scene, float(frame))
            p._update(obj)
            raw = w.raw_pose(obj)
            com, points, _ = geometry()
            root_position = (np.asarray(w.display_world(obj) @ obj.pose.bones[root].head) - root_origin) / trunk
            value = np.r_[root_position, np.concatenate([
                rotation_vector(reference.rotation_difference(bs._quat(obj.pose.bones[name])))
                for name, reference in zip(controls, reference_quaternions)
            ])]
            return {"frame": float(frame), "raw": raw, "com": com, "root_position": root_position, "points": points}, value

        bases = []
        source_values = []
        for frame in frames:
            base, value = sample_base(frame)
            bases.append(base)
            source_values.append(value)
        source_values = np.asarray(source_values)
        with np.load(original_path / "latest-trajectory.npz", allow_pickle=False) as archive:
            trajectory = archive["values"].copy()
            np.testing.assert_allclose(archive["source_values"], source_values, rtol=0, atol=2e-6)
        assert np.array_equal(trajectory[fixed], source_values[fixed])

        def apply(base, value):
            w.restore_pose(obj, base["raw"])
            p._update(obj)
            translation = w.display_world(obj).inverted().to_3x3() @ Vector((value[:3] - base["root_position"]) * trunk)
            p._translate(obj, root, translation)
            for index, (name, reference) in enumerate(zip(controls, reference_quaternions)):
                vector = Vector(value[3 + 3 * index:6 + 3 * index])
                angle = vector.length
                delta = Quaternion(vector / angle, angle) if angle > 1e-12 else Quaternion()
                bs._set_quat(obj.pose.bones[name], reference @ delta)
            p._update(obj)

        def observe(base, value):
            apply(base, value)
            com, points, _ = geometry()
            residual = list((com - base["com"]) / trunk)
            contact = 0.0
            orientation = 0.0
            if base["frame"] <= 15 or base["frame"] >= 33:
                for leg, target in zip(legs, feet):
                    matrix = w.display_world(obj) @ obj.pose.bones[leg["joints"][2]].matrix
                    offset = (np.asarray(matrix.translation) - target["point"]) / leg_scale
                    difference = target["rotation"].rotation_difference(matrix.to_quaternion())
                    if difference.w < 0:
                        difference.negate()
                    angle = np.asarray([2 * difference.x, 2 * difference.y, 2 * difference.z])
                    residual.extend(offset)
                    residual.extend(angle)
                    contact = max(contact, float(np.linalg.norm(offset)))
                    orientation = max(orientation, float(np.linalg.norm(angle)))
            return np.asarray(residual), {
                "com": float(np.linalg.norm(residual[:3])),
                "contact": contact,
                "orientation": orientation,
            }, points

        def interpolate(times, values, frame):
            index = min(len(times) - 2, max(0, int(np.searchsorted(times, frame, side="right") - 1)))
            spans = np.diff(times)
            slopes = np.diff(values, axis=0) / spans[:, None]

            def tangent(point):
                if point == 0:
                    return slopes[0]
                if point == len(times) - 1:
                    return slopes[-1]
                return ((spans[point] * slopes[point - 1] + spans[point - 1] * slopes[point]) /
                        (spans[point - 1] + spans[point]))

            span = spans[index]
            u = (frame - times[index]) / span
            return ((2 * u ** 3 - 3 * u * u + 1) * values[index] +
                    (u ** 3 - 2 * u * u + u) * span * tangent(index) +
                    (-2 * u ** 3 + 3 * u * u) * values[index + 1] +
                    (u ** 3 - u * u) * span * tangent(index + 1))

        control_groups = {}
        for name in controls:
            if name == "hips":
                control_groups[name] = "core"
            elif name.startswith("hand"):
                control_groups[name] = "hand"
            elif name.startswith("forearm"):
                control_groups[name] = "forearm"
            elif name.startswith(("upperarm", "clavicle")):
                control_groups[name] = "arm"
            elif name.startswith(("thigh", "shin", "foot")):
                control_groups[name] = "lower"
            else:
                control_groups[name] = "torso"
        assert set(control_groups) == set(controls)

        def ground_strength(frame):
            left = np.clip((17.0 - frame) / 2.0, 0.0, 1.0)
            right = np.clip((frame - 31.0) / 2.0, 0.0, 1.0)
            return float(max(left, right))

        def coordinate_penalty(frame, variant):
            configuration = VARIANTS[variant]
            strength = ground_strength(frame)
            penalty = np.ones(dimension)
            for index, name in enumerate(controls):
                group = control_groups[name]
                base = configuration.get(group, configuration.get("upper", 1.0)
                                         if group in ("torso", "arm", "forearm", "hand") else 1.0)
                penalty[3 + 3 * index:6 + 3 * index] = 1.0 + (base - 1.0) * strength
            return penalty

        def quaternion_multiply(a, b):
            aw, ax, ay, az = np.moveaxis(a, -1, 0)
            bw, bx, by, bz = np.moveaxis(b, -1, 0)
            return np.stack((aw * bw - ax * bx - ay * by - az * bz,
                             aw * bx + ax * bw + ay * bz - az * by,
                             aw * by - ax * bz + ay * bw + az * bx,
                             aw * bz + ax * by - ay * bx + az * bw), axis=-1)

        def quaternion_velocity(sequence, dt):
            sequence = sequence / np.linalg.norm(sequence, axis=-1, keepdims=True)
            inverse = sequence[:-1].copy()
            inverse[..., 1:] *= -1
            relative = quaternion_multiply(inverse, sequence[1:])
            relative = np.where(relative[..., :1] < 0, -relative, relative)
            vector = relative[..., 1:]
            length = np.linalg.norm(vector, axis=-1)
            angle = 2 * np.arctan2(length, np.clip(relative[..., 0], 0, None))
            factor = np.divide(angle, length, out=np.full_like(length, 2.0), where=length > 1e-12)
            return vector * factor[..., None] / dt

        temporal_groups = {
            "upper_body": [name for name in controls if control_groups[name] in ("torso", "arm", "forearm", "hand")],
            "legs_and_feet": [name for name in controls if control_groups[name] == "lower"],
            "core": ["hips"],
        }
        phase_boundaries = {"compression": (9.0, 15.0), "clear_flight": (15.0, 33.0), "recovery": (33.0, 39.0)}

        def metric(values, labels):
            magnitude = np.linalg.norm(values, axis=-1)
            flat = magnitude.reshape(-1)
            index = int(np.argmax(magnitude))
            _, member = np.unravel_index(index, magnitude.shape)
            return {"p95": float(np.percentile(flat, 95)), "p99": float(np.percentile(flat, 99)),
                    "max": float(flat[index]), "rms": float(np.sqrt(np.mean(flat * flat))),
                    "max_member": labels[member]}

        def temporal_metrics(checks):
            quarter = sorted((row for row in checks if abs(row["frame"] * 4 - round(row["frame"] * 4)) < 1e-9),
                             key=lambda row: row["frame"])
            check_frames = np.asarray([row["frame"] for row in quarter])
            sequence = np.asarray([[row["control_quaternions"][name] for name in controls] for row in quarter])
            rows = {}
            for phase, (first, last) in phase_boundaries.items():
                mask = (check_frames >= first) & (check_frames <= last)
                phase_sequence = sequence[mask]
                velocity = quaternion_velocity(phase_sequence, 1 / 120)
                acceleration = np.diff(velocity, axis=0) * 120
                rows[phase] = {}
                for group, members in temporal_groups.items():
                    ids = [controls.index(name) for name in members]
                    rows[phase][group] = {
                        "angular_speed_rad_s": metric(velocity[:, ids], members),
                        "angular_acceleration_rad_s2": metric(acceleration[:, ids], members),
                    }
            return rows

        for variant in VARIANTS:
            budget()
            variant_started = time.perf_counter()
            projection_records = []

            def project(frame, seed):
                budget()
                base, _ = sample_base(frame)
                value = seed.copy()
                try:
                    for iteration in range(9):
                        residual, metrics, _ = observe(base, value)
                        if metrics["com"] <= 2e-5 and metrics["contact"] <= 2e-5 and metrics["orientation"] <= 1e-4:
                            break
                        if frame in pins:
                            raise ValueError("Never move an authored priority in reconstruction")
                        if iteration == 8:
                            raise ValueError("Projection iteration limit exceeded")
                        jacobian = np.empty((len(residual), dimension))
                        for coordinate in range(dimension):
                            shifted = value.copy()
                            shifted[coordinate] += 0.0005
                            jacobian[:, coordinate] = (observe(base, shifted)[0] - residual) / 0.0005
                        inverse_penalty = 1.0 / coordinate_penalty(frame, variant)
                        weighted_transpose = inverse_penalty[:, None] * jacobian.T
                        delta = -weighted_transpose @ np.linalg.solve(
                            jacobian @ weighted_transpose + 1e-8 * np.eye(len(residual)), residual)
                        factor = max(1.0, float(np.linalg.norm(delta[:3])) / 0.025,
                                     float(np.max(np.linalg.norm(delta[3:].reshape(-1, 3), axis=1))) / 0.1)
                        delta /= factor
                        accepted = False
                        for fraction in (1.0, 0.5, 0.25, 0.125):
                            trial = value + fraction * delta
                            trial_residual = observe(base, trial)[0]
                            if trial_residual @ trial_residual < residual @ residual:
                                value = trial
                                accepted = True
                                break
                        if not accepted:
                            raise ValueError("Weighted reconstruction projection stalled")
                    projection_records.append({
                        "frame": frame, "iterations": iteration, "final": metrics,
                        "max_coordinate_change": float(np.max(np.abs(value - seed))),
                    })
                    return value
                finally:
                    w.restore_pose(obj, base["raw"])
                    p._update(obj)
                    assert raw_equal(w.raw_pose(obj), base["raw"])

            values = {float(frame): project(float(frame), interpolate(frames, trajectory, float(frame)))
                      for frame in np.arange(1.0, 49.001, 0.25)}
            passes = []
            last_checks = []
            for refinement in range(4):
                times = np.asarray(sorted(values))
                matrix = np.asarray([values[frame] for frame in times])
                np.savez(BASE / f"{variant}.npz", frames=times, values=matrix)
                queries = set(times)
                for left, right in zip(times, times[1:]):
                    queries.update(left + (right - left) * fraction for fraction in (0.25, 0.5, 0.75))
                queries.update(15 - 2 ** (-index) for index in range(1, 8))
                queries.update(33 + 2 ** (-index) for index in range(1, 8))
                failures = []
                checks = []
                for frame in sorted(queries):
                    budget()
                    base, _ = sample_base(frame)
                    seed = interpolate(times, matrix, frame)
                    try:
                        _, metrics, _ = observe(base, seed)
                        checks.append({
                            "frame": frame, **metrics,
                            "control_quaternions": {name: list(obj.pose.bones[name].matrix.to_quaternion())
                                                    for name in controls},
                        })
                        if metrics["com"] > 2e-4 or metrics["contact"] > 2e-4 or metrics["orientation"] > 0.001:
                            failures.append(frame)
                    finally:
                        w.restore_pose(obj, base["raw"])
                        p._update(obj)
                        assert raw_equal(w.raw_pose(obj), base["raw"])
                last_checks = checks
                pass_row = {
                    "refinement": refinement,
                    "knots": len(times),
                    "samples": len(checks),
                    "failed_samples": len(failures),
                    "max_errors": {key: max(row[key] for row in checks)
                                   for key in ("com", "contact", "orientation")},
                }
                passes.append(pass_row)
                if not failures:
                    break
                additions = set(failures) - set(values)
                if refinement == 3 or len(values) + len(additions) > 512:
                    break
                if not additions:
                    raise ValueError("Existing weighted projected knot fails validation")
                for frame in sorted(additions):
                    values[frame] = project(frame, interpolate(times, matrix, frame))
            for index in fixed:
                np.testing.assert_array_equal(values[float(frames[index])], source_values[index])
            temporal = temporal_metrics(last_checks)
            ratios = {}
            for phase in phase_boundaries:
                ratios[phase] = {}
                for group in temporal_groups:
                    ratios[phase][group] = {}
                    for quantity in ("angular_speed_rad_s", "angular_acceleration_rad_s2"):
                        ratios[phase][group][quantity] = {
                            statistic: temporal[phase][group][quantity][statistic] /
                            envelope["recorded_envelopes"][phase][group][quantity][statistic]
                            for statistic in ("p95", "p99", "max", "rms")
                        }
            row = {
                "name": variant,
                "configuration": VARIANTS[variant],
                "phase_ramp": {"left": [15.0, 17.0], "right": [31.0, 33.0]},
                "passes": passes,
                "sampled_constraints_passed": passes[-1]["failed_samples"] == 0,
                "spatial_max": passes[-1]["max_errors"],
                "projection_records": len(projection_records),
                "max_projection_coordinate_change": max(item["max_coordinate_change"] for item in projection_records),
                "temporal": temporal,
                "recorded_envelope_ratios": ratios,
                "trajectory_sha256": sha256(BASE / f"{variant}.npz"),
                "seconds": time.perf_counter() - variant_started,
            }
            report["variants"].append(row)
            persist()
            print(json.dumps({
                "variant": variant,
                "spatial_pass": row["sampled_constraints_passed"],
                "knots": passes[-1]["knots"],
                "samples": passes[-1]["samples"],
                "recovery_upper_speed_p99_ratio": ratios["recovery"]["upper_body"]["angular_speed_rad_s"]["p99"],
                "recovery_upper_acceleration_p99_ratio": ratios["recovery"]["upper_body"]["angular_acceleration_rad_s2"]["p99"],
                "seconds": row["seconds"],
            }), flush=True)

        passing = [row for row in report["variants"] if row["sampled_constraints_passed"]]
        assert passing
        for row in passing:
            row["selection_score"] = max(
                row["recorded_envelope_ratios"][phase]["upper_body"][quantity][statistic]
                for phase in ("compression", "recovery")
                for quantity in ("angular_speed_rad_s", "angular_acceleration_rad_s2")
                for statistic in ("p99", "max")
            )
        selected = min(passing, key=lambda row: row["selection_score"])
        baseline = next(row for row in report["variants"] if row["name"] == "uniform")
        report.update(
            complete=True,
            selected=selected["name"],
            selected_score=selected["selection_score"],
            baseline_score=baseline["selection_score"],
            score_improvement_ratio=selected["selection_score"] / baseline["selection_score"],
            method_promoted=False,
            source_preserved=True,
            priorities_unchanged=True,
            production_changed=False,
            confirmation_read=False,
            control_groups=control_groups,
            runtime_sha256={path.relative_to(ROOT).as_posix(): sha256(path)
                            for path in (ROOT / "b4artists_ml").glob("*.py")},
            decision="Retain only as bounded research. A selected variant must still receive visual review, broader motions and independent usability evidence before production integration.",
            limits="One artificial BoneForge jump and one recorded actor clip; no force, collision, learned, human or Cascadeur qualification.",
        )
        c._frame(scene, initial_frame)
        w.restore_pose(obj, initial_pose)
        p._update(obj)
        assert raw_equal(w.raw_pose(obj), initial_pose)
        assert f._curve_token(obj) == source_token
        assert original_actions == set(bpy.data.actions.keys()) and original_objects == set(bpy.data.objects.keys())
        assert sha256(blend) == source_report["blend_sha256"]
    except BaseException:
        report["error"] = traceback.format_exc()
    report["seconds"] = time.perf_counter() - started
    persist()
    print(json.dumps({key: report.get(key) for key in (
        "complete", "selected", "selected_score", "baseline_score", "score_improvement_ratio", "seconds", "error"
    )}), flush=True)


def wrapper_main():
    BASE.mkdir(exist_ok=False)
    log = BASE / "host.log"
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            ["X:/5.1.0/bforartists.exe", "--background", "--factory-startup", "--disable-autoexec",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=1000,
            env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
        )
    report = json.loads((BASE / "report.json").read_text(encoding="utf-8")) if (BASE / "report.json").exists() else {}
    result = {
        "exit_code": process.returncode,
        "complete": report.get("complete", False),
        "selected": report.get("selected"),
        "error": report.get("error"),
        "seconds": time.perf_counter() - started,
        "log_sha256": sha256(log),
    }
    write_json(BASE / "process.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        host_main()
    else:
        wrapper_main()
