"""Test world-orientation-aware hard projection at two contact-boundary samples."""
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
BASE = ROOT / "training" / "b4artists_ml" / "results" / "world-metric-boundary-v1"
DEADLINE = 1789053845
LAMBDAS = (1.0, 10.0, 100.0, 1000.0)


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
              "method": "world_orientation_metric_boundary_feasibility", "learned": False,
              "script_sha256": sha256(HERE), "cases": []}

    def persist():
        write_json(BASE / "report.json", report)

    def budget():
        if time.perf_counter() - started > 900 or time.time() > DEADLINE:
            raise TimeoutError("World-metric boundary probe budget exhausted")

    try:
        source_report_path = ROOT / "training/b4artists_ml/results/grounded-jump-diagnostic-v1/boneforge/report.json"
        source_report = json.loads(source_report_path.read_text(encoding="utf-8"))
        blend = ROOT / source_report["blend"]
        assert sha256(blend) == source_report["blend_sha256"]
        original_path = ROOT / "training/b4artists_ml/results/coupled-trajectory-v1"
        weighted_path = ROOT / "training/b4artists_ml/results/group-weighted-trajectory-v3"
        weighted_report = json.loads((weighted_path / "report.json").read_text(encoding="utf-8"))
        assert weighted_report["complete"] and weighted_report["selected"] == "grouped16"
        assert weighted_report["variants"][1]["sampled_constraints_passed"]
        assert weighted_report["variants"][1]["trajectory_sha256"] == sha256(weighted_path / "grouped16.npz")
        envelope_path = ROOT / "training/b4artists_ml/results/jump-temporal-envelope-v1/report.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert envelope["complete"] and not envelope["qualified"]
        report["input_blend_sha256"] = sha256(blend)
        report["input_trajectory_sha256"] = sha256(original_path / "latest-trajectory.npz")
        report["weighted_trajectory_sha256"] = sha256(weighted_path / "grouped16.npz")
        report["recorded_envelope_sha256"] = sha256(envelope_path)

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
        assert len(upper) == 13
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
        frames = np.arange(1.0, 50.0)
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
        with np.load(weighted_path / "grouped16.npz", allow_pickle=False) as archive:
            weighted_times = archive["frames"]
            weighted_values = archive["values"]

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
            apply(base, value)
            com, _, _ = geometry()
            residual = list((com - base["com"]) / trunk)
            contact = 0.0
            orientation = 0.0
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
                difference = target[name].rotation_difference(obj.pose.bones[name].matrix.to_quaternion())
                rows.extend(rotation_vector(difference))
            return np.asarray(rows)

        def relative_speed(left, right):
            values = []
            for name in upper:
                values.append(float(np.linalg.norm(rotation_vector(left[name].rotation_difference(right[name]))) * 120))
            index = int(np.argmax(values))
            return {"max_rad_s": values[index], "max_member": upper[index], "all_rad_s": dict(zip(upper, values))}

        boundary_cases = (("compression", 14.75, 15.0), ("recovery", 33.25, 33.0))
        for phase, frame, pin_frame in boundary_cases:
            budget()
            base, _ = sample_base(frame)
            source_seed = interpolate(frames, trajectory, frame)
            weighted_seed = interpolate(weighted_times, weighted_values, frame)
            apply(base, source_seed)
            target_world = world_upper()
            source_hard, source_metrics = observe(base, source_seed)
            apply(base, weighted_seed)
            weighted_world = world_upper()
            weighted_hard, weighted_metrics = observe(base, weighted_seed)
            pin_base, pin_value = sample_base(pin_frame)
            apply(pin_base, pin_value)
            pin_world = world_upper()
            baseline_speed = relative_speed(weighted_world, pin_world) if phase == "compression" else relative_speed(pin_world, weighted_world)
            source_speed = relative_speed(target_world, pin_world) if phase == "compression" else relative_speed(pin_world, target_world)
            case = {
                "phase": phase,
                "frame": frame,
                "pin_frame": pin_frame,
                "source_seed_hard": source_metrics,
                "weighted_seed_hard": weighted_metrics,
                "source_seed_boundary_speed": source_speed,
                "weighted_seed_boundary_speed": baseline_speed,
                "recorded_upper_speed_max_envelope": envelope["recorded_envelopes"][phase]["upper_body"]["angular_speed_rad_s"]["max"],
                "lambdas": [],
            }
            for strength in LAMBDAS:
                value = weighted_seed.copy()
                trace = []
                for iteration in range(8):
                    budget()
                    hard, hard_metrics = observe(base, value)
                    soft = orientation_residual(target_world)
                    fidelity = value - source_seed
                    merit = 1e8 * float(hard @ hard) + strength * float(soft @ soft) + 0.01 * float(fidelity @ fidelity)
                    trace.append({"iteration": iteration, "hard": hard_metrics,
                                  "soft_norm": float(np.linalg.norm(soft)), "merit": merit})
                    jacobian = np.empty((len(hard), dimension))
                    world_jacobian = np.empty((len(soft), dimension))
                    for coordinate in range(dimension):
                        shifted = value.copy()
                        shifted[coordinate] += 0.0005
                        shifted_hard, _ = observe(base, shifted)
                        shifted_soft = orientation_residual(target_world)
                        jacobian[:, coordinate] = (shifted_hard - hard) / 0.0005
                        world_jacobian[:, coordinate] = (shifted_soft - soft) / 0.0005
                    hessian = 0.01 * np.eye(dimension) + strength * (world_jacobian.T @ world_jacobian)
                    gradient = 0.01 * fidelity + strength * (world_jacobian.T @ soft)
                    unconstrained = -np.linalg.solve(hessian, gradient)
                    inverse_jt = np.linalg.solve(hessian, jacobian.T)
                    delta = unconstrained - inverse_jt @ np.linalg.solve(
                        jacobian @ inverse_jt + 1e-8 * np.eye(len(hard)), hard + jacobian @ unconstrained)
                    factor = max(1.0, float(np.linalg.norm(delta[:3])) / 0.025,
                                 float(np.max(np.linalg.norm(delta[3:].reshape(-1, 3), axis=1))) / 0.1)
                    delta /= factor
                    accepted = False
                    for fraction in (1.0, 0.5, 0.25, 0.125, 0.0625):
                        trial = value + fraction * delta
                        trial_hard, _ = observe(base, trial)
                        trial_soft = orientation_residual(target_world)
                        trial_fidelity = trial - source_seed
                        trial_merit = (1e8 * float(trial_hard @ trial_hard) +
                                       strength * float(trial_soft @ trial_soft) +
                                       0.01 * float(trial_fidelity @ trial_fidelity))
                        if trial_merit < merit:
                            value = trial
                            accepted = True
                            break
                    if not accepted:
                        break
                hard, hard_metrics = observe(base, value)
                soft = orientation_residual(target_world)
                candidate_world = world_upper()
                speed = relative_speed(candidate_world, pin_world) if phase == "compression" else relative_speed(pin_world, candidate_world)
                case["lambdas"].append({
                    "strength": strength,
                    "hard": hard_metrics,
                    "soft_norm": float(np.linalg.norm(soft)),
                    "boundary_speed": speed,
                    "boundary_speed_recorded_max_ratio": speed["max_rad_s"] / case["recorded_upper_speed_max_envelope"],
                    "coordinate_change_from_weighted_seed": float(np.linalg.norm(value - weighted_seed)),
                    "trace": trace,
                    "hard_pass": hard_metrics["com"] <= 2e-5 and hard_metrics["contact"] <= 2e-5 and hard_metrics["orientation"] <= 1e-4,
                })
            report["cases"].append(case)
            persist()

        feasible = [row for case in report["cases"] for row in case["lambdas"] if row["hard_pass"]]
        assert feasible
        report.update(
            complete=True,
            feasibility_demonstrated=any(
                min(row["boundary_speed"]["max_rad_s"] for row in case["lambdas"] if row["hard_pass"])
                < case["weighted_seed_boundary_speed"]["max_rad_s"] * 0.75
                for case in report["cases"]),
            source_preserved=True,
            priorities_unchanged=True,
            production_changed=False,
            confirmation_read=False,
            runtime_sha256={path.relative_to(ROOT).as_posix(): sha256(path)
                            for path in (ROOT / "b4artists_ml").glob("*.py")},
            decision="If boundary world-orientation preservation reduces speed while hard constraints pass, integrate the metric into full reconstruction with bounded variants. Otherwise reject this direction.",
            limits="Two boundary samples on one artificial BoneForge jump; no continuous, learned, force, visual, human or Cascadeur qualification.",
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
    print(json.dumps({"complete": report.get("complete"),
                      "feasibility_demonstrated": report.get("feasibility_demonstrated"),
                      "cases": [{"phase": case["phase"], "baseline_speed": case["weighted_seed_boundary_speed"]["max_rad_s"],
                                 "candidates": [{"strength": row["strength"], "hard_pass": row["hard_pass"],
                                                 "speed": row["boundary_speed"]["max_rad_s"],
                                                 "ratio": row["boundary_speed_recorded_max_ratio"]}
                                                for row in case["lambdas"]]}
                                for case in report.get("cases", [])],
                      "seconds": report.get("seconds"), "error": report.get("error")}, indent=2), flush=True)


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
                      "feasibility_demonstrated": report.get("feasibility_demonstrated"), "error": report.get("error"),
                      "seconds": time.perf_counter() - started, "log_sha256": sha256(log)}
    write_json(BASE / "process.json", process_report)
    print(json.dumps(process_report, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        host_main()
    else:
        wrapper_main()
