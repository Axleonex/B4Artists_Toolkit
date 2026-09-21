"""Source-relative boundary-window SQP research on the frozen BoneForge jump."""
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
BASE = ROOT / "training/b4artists_ml/results/boundary-window-sqp-v3"
DEADLINE = 1789053845
FINAL_LIMITS = {"com": 2e-4, "contact": 2e-4, "orientation": 0.001}
WINDOWS = {"compression": (13.5, 15.5, 15.0), "recovery": (32.5, 34.5, 33.0)}


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
    report = {"schema": 1, "complete": False, "qualified": False,
              "method": "source_relative_world_orientation_boundary_window_projected_descent",
              "learned": False, "script_sha256": sha256(HERE), "windows": []}

    def persist():
        write_json(BASE / "report.json", report)

    def budget():
        if time.perf_counter() - started > 900 or time.time() > DEADLINE:
            raise TimeoutError("Boundary-window SQP budget exhausted")

    try:
        source_report_path = ROOT / "training/b4artists_ml/results/grounded-jump-diagnostic-v1/boneforge/report.json"
        source_report = json.loads(source_report_path.read_text(encoding="utf-8"))
        blend = ROOT / source_report["blend"]
        assert sha256(blend) == source_report["blend_sha256"]
        original_path = ROOT / "training/b4artists_ml/results/coupled-trajectory-v1"
        weighted_path = ROOT / "training/b4artists_ml/results/group-weighted-trajectory-v3"
        weighted_report = json.loads((weighted_path / "report.json").read_text(encoding="utf-8"))
        assert weighted_report["complete"] and weighted_report["selected"] == "grouped16"
        selected_row = next(row for row in weighted_report["variants"] if row["name"] == "grouped16")
        assert selected_row["sampled_constraints_passed"]
        assert selected_row["trajectory_sha256"] == sha256(weighted_path / "grouped16.npz")
        envelope_path = ROOT / "training/b4artists_ml/results/jump-temporal-envelope-v1/report.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert envelope["complete"] and not envelope["qualified"]
        report.update(input_blend_sha256=sha256(blend),
                      input_trajectory_sha256=sha256(original_path / "latest-trajectory.npz"),
                      weighted_trajectory_sha256=sha256(weighted_path / "grouped16.npz"),
                      recorded_envelope_sha256=sha256(envelope_path),
                      baseline_selection_score=selected_row["selection_score"])

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
        upper = [name for name in controls if name not in {
            "hips", "thigh.fk-L", "thigh.fk-R", "shin.fk-L", "shin.fk-R", "foot.fk-L", "foot.fk-R"
        }]
        assert len(controls) == 20 and len(upper) == 13
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
            return center_of_mass(starts, ends, masses, fractions)[0], heads, float(
                sum(np.linalg.norm(ends[index] - starts[index]) for index in range(3)))

        c._frame(scene, 1)
        _, _, trunk = geometry()
        root_origin = np.asarray(w.display_world(obj) @ obj.pose.bones[root].head)
        reference_quaternions = [bs._quat(obj.pose.bones[name]) for name in controls]
        feet = [{
            "point": np.asarray((w.display_world(obj) @ obj.pose.bones[row["joints"][2]].matrix).translation),
            "rotation": (w.display_world(obj) @ obj.pose.bones[row["joints"][2]].matrix).to_quaternion(),
        } for row in legs]
        leg_scale = source_report["leg_length_world"]
        source_frames = np.arange(1.0, 50.0)
        source_fixed = np.asarray([0, 8, 14, 32, 38, 48])
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
            return {"frame": float(frame), "raw": raw, "com": com,
                    "root_position": root_position, "points": points}, value

        source_values = []
        for frame in source_frames:
            _, value = sample_base(frame)
            source_values.append(value)
        source_values = np.asarray(source_values)
        with np.load(original_path / "latest-trajectory.npz", allow_pickle=False) as archive:
            trajectory = archive["values"].copy()
            np.testing.assert_allclose(archive["source_values"], source_values, rtol=0, atol=2e-6)
        assert np.array_equal(trajectory[source_fixed], source_values[source_fixed])
        with np.load(weighted_path / "grouped16.npz", allow_pickle=False) as archive:
            master_times = archive["frames"].copy()
            master_values = archive["values"].copy()

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

        def apply(base, value):
            w.restore_pose(obj, base["raw"])
            p._update(obj)
            p._translate(obj, root, w.display_world(obj).inverted().to_3x3() @ Vector(
                (value[:3] - base["root_position"]) * trunk))
            for index, (name, reference) in enumerate(zip(controls, reference_quaternions)):
                vector = Vector(value[3 + 3 * index:6 + 3 * index])
                angle = vector.length
                delta = Quaternion(vector / angle, angle) if angle > 1e-12 else Quaternion()
                bs._set_quat(obj.pose.bones[name], reference @ delta)
            p._update(obj)

        def observe(base, value):
            c._frame(scene, base["frame"])
            apply(base, value)
            com, _, _ = geometry()
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
            return np.asarray(residual), {"com": float(np.linalg.norm(residual[:3])),
                                          "contact": contact, "orientation": orientation}

        def world_upper():
            return {name: obj.pose.bones[name].matrix.to_quaternion().copy() for name in upper}

        def orientation_residual(target):
            rows = []
            for name in upper:
                rows.extend(rotation_vector(target[name].rotation_difference(
                    obj.pose.bones[name].matrix.to_quaternion())))
            return np.asarray(rows)

        def temporal_operator(times):
            seconds = times / 30.0
            spans = np.diff(seconds)
            d1 = np.zeros((len(times) - 1, len(times)))
            for index, span in enumerate(spans):
                d1[index, index:index + 2] = (-1 / span, 1 / span)
                d1[index] *= np.sqrt(span)
            d2 = np.zeros((len(times) - 2, len(times)))
            for index in range(len(times) - 2):
                average = (spans[index] + spans[index + 1]) * 0.5
                d2[index, index:index + 3] = (
                    1 / (spans[index] * average),
                    -(1 / spans[index] + 1 / spans[index + 1]) / average,
                    1 / (spans[index + 1] * average),
                )
                d2[index] *= np.sqrt(average)
            return 100.0 * np.eye(len(times)) + 0.01 * (d1.T @ d1) + 1e-6 * (d2.T @ d2)

        def evaluate_window(times, values, bases, targets, source_seeds, operator):
            soft = []
            hard_rows = []
            metrics = []
            for base, value, target in zip(bases, values, targets):
                hard, row = observe(base, value)
                soft.append(orientation_residual(target))
                hard_rows.append(hard)
                metrics.append(row)
            soft = np.asarray(soft)
            objective = float(sum(soft[:, component] @ operator @ soft[:, component]
                                  for component in range(soft.shape[1])) +
                              0.01 * np.sum((values - source_seeds) ** 2))
            return soft, hard_rows, metrics, objective

        for phase, (lower, upper_bound, pin) in WINDOWS.items():
            budget()
            mask = (master_times >= lower) & (master_times <= upper_bound)
            times = master_times[mask]
            values = master_values[mask].copy()
            original_values = values.copy()
            assert len(times) == 22 and pin in set(times)
            fixed = {0, len(times) - 1, int(np.where(times == pin)[0][0])}
            bases = []
            targets = []
            source_seeds = []
            for frame in times:
                base, _ = sample_base(frame)
                source_seed = interpolate(source_frames, trajectory, frame)
                apply(base, source_seed)
                bases.append(base)
                targets.append(world_upper())
                source_seeds.append(source_seed)
                w.restore_pose(obj, base["raw"])
                p._update(obj)
                assert raw_equal(w.raw_pose(obj), base["raw"])
            source_seeds = np.asarray(source_seeds)
            operator = temporal_operator(times)
            soft, hard, metrics, objective = evaluate_window(
                times, values, bases, targets, source_seeds, operator)
            initial_objective = objective
            iterations = []
            for iteration in range(6):
                budget()
                qsoft = operator @ soft
                directions = np.zeros_like(values)
                for frame_index in range(len(times)):
                    if frame_index in fixed:
                        continue
                    base = bases[frame_index]
                    value = values[frame_index]
                    target = targets[frame_index]
                    current_hard = hard[frame_index]
                    current_soft = soft[frame_index]
                    jacobian = np.empty((len(current_hard), dimension))
                    world_jacobian = np.empty((len(current_soft), dimension))
                    for coordinate in range(dimension):
                        shifted = value.copy()
                        shifted[coordinate] += 0.0005
                        shifted_hard, _ = observe(base, shifted)
                        shifted_soft = orientation_residual(target)
                        jacobian[:, coordinate] = (shifted_hard - current_hard) / 0.0005
                        world_jacobian[:, coordinate] = (shifted_soft - current_soft) / 0.0005
                    gradient = (2 * world_jacobian.T @ qsoft[frame_index] +
                                0.02 * (value - source_seeds[frame_index]))
                    projected = gradient - jacobian.T @ np.linalg.solve(
                        jacobian @ jacobian.T + 1e-8 * np.eye(len(current_hard)), jacobian @ gradient)
                    directions[frame_index] = -projected
                largest = max(1.0, float(np.max(np.linalg.norm(directions[:, :3], axis=1))) / 0.0025,
                              float(np.max(np.linalg.norm(directions[:, 3:].reshape(-1, 3), axis=1))) / 0.01)
                directions /= largest
                accepted = False
                chosen = None
                for fraction in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
                    trial = values + fraction * directions
                    trial[list(fixed)] = original_values[list(fixed)]
                    trial_soft, trial_hard, trial_metrics, trial_objective = evaluate_window(
                        times, trial, bases, targets, source_seeds, operator)
                    spatial_pass = all(all(row[name] <= limit for name, limit in FINAL_LIMITS.items())
                                       for row in trial_metrics)
                    if spatial_pass and trial_objective < objective:
                        values = trial
                        soft, hard, metrics, objective = trial_soft, trial_hard, trial_metrics, trial_objective
                        chosen = fraction
                        accepted = True
                        break
                iterations.append({
                    "iteration": iteration,
                    "accepted": accepted,
                    "fraction": chosen,
                    "objective": objective,
                    "max_errors": {name: max(row[name] for row in metrics) for name in FINAL_LIMITS},
                    "max_soft_norm": float(max(np.linalg.norm(row) for row in soft)),
                })
                persist()
                if not accepted:
                    break
            np.testing.assert_array_equal(values[list(fixed)], original_values[list(fixed)])
            master_values[mask] = values
            window_row = {
                "phase": phase,
                "times": times.tolist(),
                "knots": len(times),
                "fixed_times": [float(times[index]) for index in sorted(fixed)],
                "initial_objective": initial_objective,
                "final_objective": objective,
                "objective_ratio": objective / initial_objective,
                "iterations": iterations,
                "accepted_iterations": sum(row["accepted"] for row in iterations),
                "final_spatial_max": {name: max(row[name] for row in metrics) for name in FINAL_LIMITS},
                "max_coordinate_change": float(np.max(np.abs(values - original_values))),
            }
            report["windows"].append(window_row)
            persist()
            print(json.dumps(window_row), flush=True)

        np.savez(BASE / "optimized.npz", frames=master_times, values=master_values)
        queries = set(master_times)
        for left, right in zip(master_times, master_times[1:]):
            queries.update(left + (right - left) * fraction for fraction in (0.25, 0.5, 0.75))
        queries.update(15 - 2 ** (-index) for index in range(1, 8))
        queries.update(33 + 2 ** (-index) for index in range(1, 8))
        checks = []
        for frame in sorted(queries):
            budget()
            base, _ = sample_base(frame)
            value = interpolate(master_times, master_values, frame)
            try:
                _, metrics = observe(base, value)
                checks.append({
                    "frame": frame, **metrics,
                    "control_quaternions": {name: list(obj.pose.bones[name].matrix.to_quaternion())
                                            for name in controls},
                })
            finally:
                w.restore_pose(obj, base["raw"])
                p._update(obj)
                assert raw_equal(w.raw_pose(obj), base["raw"])
        spatial_max = {name: max(row[name] for row in checks) for name in FINAL_LIMITS}
        sampled_constraints_passed = all(spatial_max[name] <= limit for name, limit in FINAL_LIMITS.items())

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
            "upper_body": upper,
            "legs_and_feet": [name for name in controls if name.startswith(("thigh", "shin", "foot"))],
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

        quarter = sorted((row for row in checks if abs(row["frame"] * 4 - round(row["frame"] * 4)) < 1e-9),
                         key=lambda row: row["frame"])
        quarter_frames = np.asarray([row["frame"] for row in quarter])
        sequence = np.asarray([[row["control_quaternions"][name] for name in controls] for row in quarter])
        temporal = {}
        ratios = {}
        for phase, (first, last) in phase_boundaries.items():
            mask = (quarter_frames >= first) & (quarter_frames <= last)
            velocity = quaternion_velocity(sequence[mask], 1 / 120)
            acceleration = np.diff(velocity, axis=0) * 120
            temporal[phase] = {}
            ratios[phase] = {}
            for group, members in temporal_groups.items():
                ids = [controls.index(name) for name in members]
                temporal[phase][group] = {
                    "angular_speed_rad_s": metric(velocity[:, ids], members),
                    "angular_acceleration_rad_s2": metric(acceleration[:, ids], members),
                }
                ratios[phase][group] = {}
                for quantity in ("angular_speed_rad_s", "angular_acceleration_rad_s2"):
                    ratios[phase][group][quantity] = {
                        statistic: temporal[phase][group][quantity][statistic] /
                        envelope["recorded_envelopes"][phase][group][quantity][statistic]
                        for statistic in ("p95", "p99", "max", "rms")
                    }
        selection_score = max(
            ratios[phase]["upper_body"][quantity][statistic]
            for phase in ("compression", "recovery")
            for quantity in ("angular_speed_rad_s", "angular_acceleration_rad_s2")
            for statistic in ("p99", "max"))
        report.update(
            complete=True,
            optimized_trajectory_sha256=sha256(BASE / "optimized.npz"),
            sampled_constraints_passed=sampled_constraints_passed,
            validation_samples=len(checks),
            spatial_max=spatial_max,
            temporal=temporal,
            recorded_envelope_ratios=ratios,
            selection_score=selection_score,
            score_to_grouped_baseline=selection_score / selected_row["selection_score"],
            method_promoted=False,
            source_preserved=True,
            priorities_unchanged=True,
            production_changed=False,
            confirmation_read=False,
            runtime_sha256={path.relative_to(ROOT).as_posix(): sha256(path)
                            for path in (ROOT / "b4artists_ml").glob("*.py")},
            decision="Promote only if all dense spatial checks pass and full transition metrics improve without shifting the spike. Human and broader-motion review remain mandatory.",
            limits="Two contact-boundary windows on one artificial BoneForge jump; no force, collision, learned, visual, human or Cascadeur qualification.",
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
        "complete", "sampled_constraints_passed", "validation_samples", "spatial_max",
        "selection_score", "score_to_grouped_baseline", "seconds", "error")
    }, indent=2), flush=True)


def wrapper_main():
    BASE.mkdir(exist_ok=False)
    log = BASE / "host.log"
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            ["X:/5.1.0/bforartists.exe", "--background", "--factory-startup", "--disable-autoexec",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=1000,
            env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"))
    report = json.loads((BASE / "report.json").read_text(encoding="utf-8")) if (BASE / "report.json").exists() else {}
    process_report = {"exit_code": process.returncode, "complete": report.get("complete", False),
                      "sampled_constraints_passed": report.get("sampled_constraints_passed"),
                      "selection_score": report.get("selection_score"), "error": report.get("error"),
                      "seconds": time.perf_counter() - started, "log_sha256": sha256(log)}
    write_json(BASE / "process.json", process_report)
    print(json.dumps(process_report, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        host_main()
    else:
        wrapper_main()
