"""Build an offline blind follow-up review for the review-directed v15/v17 candidates.

The original 32-case v13 review remains immutable.  This packet compares the
original corrected v13 scenes to the later review-directed candidates, using a
smaller fixed matrix for the specific issues the reviewer identified.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
BASELINE = TRAIN / "results/procedural-vertical-slice-v13"
V15 = TRAIN / "results/procedural-vertical-slice-v15"
V17 = TRAIN / "results/procedural-vertical-slice-v17"
TEMPLATE = TRAIN / "procedural_vertical_slice_review_template_v2.html"
OUT = TRAIN / "results/review-directed-followup-reviewer-v1"
HOST = Path("X:/5.1.0/bforartists.exe")
NAMES = ("Hips", "Spine", "Spine1", "Neck1", "Head", "LeftArm", "LeftForeArm", "LeftHand",
         "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot",
         "RightUpLeg", "RightLeg", "RightFoot")
ROLES = ("pelvis", "spine", "chest", "neck", "head", "upper_arm_L", "elbow_L", "wrist_L",
         "upper_arm_R", "elbow_R", "wrist_R", "hip_L", "knee_L", "ankle_L",
         "hip_R", "knee_R", "ankle_R")
PARENTS = (-1, 0, 1, 2, 3, 2, 5, 6, 2, 8, 9, 0, 11, 12, 0, 14, 15)
PROFILES = ("boneforge", "rigify_basic", "rigify_default", "imported_unity")
CASES = tuple(
    (profile, task)
    for profile in PROFILES
    for task in ("reach", "land", "jump")
) + tuple(
    (profile, task)
    for profile in ("boneforge", "rigify_basic")
    for task in ("walk", "run")
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def source_root(variant, task):
    if variant == "baseline":
        return BASELINE
    if task in {"reach", "land"}:
        return V15
    if task in {"walk", "run", "jump"}:
        return V17
    raise ValueError("No review-directed candidate for task: " + task)


def case_paths(variant, profile, task):
    directory = source_root(variant, task) / profile / task
    return directory, directory / f"{profile}-{task}.blend", directory / "report.json"


def host(variant, profile, task):
    """Extract 17-joint evaluated samples from one saved case scene."""
    import bpy
    import numpy as np
    from mathutils import Vector

    sys.path[:0] = [str(ROOT), str(TRAIN)]
    import b4artists_ml
    from b4artists_ml import body_solver, motion_layer, posing

    destination = OUT / "extracted" / f"{variant}-{profile}-{task}.json"
    result = dict(
        schema="b4ml-review-directed-followup-extract-v1",
        variant=variant,
        profile=profile,
        task=task,
        complete=False,
        full_goal_complete=False,
    )
    started = time.perf_counter()
    try:
        b4artists_ml.register()
        _directory, blend, report_path = case_paths(variant, profile, task)
        report = read(report_path)
        if report.get("complete") is not True or report.get("failures"):
            raise ValueError("Source case is incomplete")
        if sha(blend) != report["blend_sha256"]:
            raise ValueError("Saved scene no longer matches its source report")
        armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and hasattr(obj, "b4ml")]
        # Rigify scenes retain a source metarig alongside the generated animated rig.
        # Select the sole B4ML armature that actually owns an animation, rather than
        # relying on an object-count assumption that is false for those frozen scenes.
        animated = [obj for obj in armatures if (
            (obj.animation_data and obj.animation_data.action is not None)
            or getattr(obj.b4ml, "candidate_action", None) is not None
        )]
        if len(animated) != 1:
            raise ValueError(f"Expected one animated review armature, found {len(animated)} of {len(armatures)}")
        obj = animated[0]
        scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
        bpy.context.window.scene = scene
        binding = body_solver.mapping(obj, writable=False)
        if len(binding["names"]) != 17:
            raise ValueError("Review adapter must expose exactly 17 semantic joints")
        action = obj.animation_data.action if obj.animation_data else None
        if action is None:
            action = getattr(obj.b4ml, "candidate_action", None)
        if action is None:
            raise ValueError("Saved review scene has no active candidate action")
        start = float(scene.frame_start)
        end = float(scene.frame_end)
        if not math.isfinite(start) or not math.isfinite(end) or end <= start:
            raise ValueError("Saved review scene has invalid frame bounds")
        frames = [start + (end - start) * index / 48.0 for index in range(49)]
        axes = [Vector(row) for row in report["task_basis_world"]]
        if any(abs(axis.length - 1.0) > 1e-5 for axis in axes):
            raise ValueError("Task display basis is not orthonormal")
        height = float(report["reference_height"])
        if not math.isfinite(height) or height <= 0:
            raise ValueError("Invalid reference height")

        def world_points(frame):
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            posing._update(obj)
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            return [evaluated.matrix_world @ evaluated.pose.bones[name].head for name in binding["names"]]

        origin = world_points(start)[0]
        rows = []
        for frame in frames:
            points = world_points(frame)
            rows.append([[float((point - origin).dot(axis) / height) for axis in axes] for point in points])
        values = np.asarray(rows, dtype=np.float64)
        if values.shape != (49, 17, 3) or not np.isfinite(values).all():
            raise ValueError("Nonfinite or malformed review skeleton")
        low, high = values.reshape(-1, 3).min(axis=0), values.reshape(-1, 3).max(axis=0)
        center = (low + high) * 0.5
        radius = float(np.max(np.linalg.norm(values.reshape(-1, 3) - center, axis=1)))
        floor_point = Vector((0.0, 0.0, float(report["rig_floor_calibration"]["floor_z"])))
        floor_z = float((floor_point - origin).dot(axes[2]) / height)
        result.update(
            complete=True,
            blend_path=report["blend_path"],
            blend_sha256=report["blend_sha256"],
            report_sha256=sha(report_path),
            report_schema=report["schema"],
            semantic_profile=binding["profile"],
            semantic_bones=list(binding["names"]),
            frames=frames,
            fps=float(scene.render.fps / scene.render.fps_base),
            priority_frames=[float(value) for value in report.get("priority_frames", [])],
            samples=np.round(values, 7).tolist(),
            provenance=dict(action=action.name, backend=action.get("b4ml_backend", "unknown")),
            center=np.round(center, 7).tolist(),
            radius=radius,
            floor_z=floor_z,
            seconds=time.perf_counter() - started,
        )
    except BaseException:
        result.update(error=traceback.format_exc(), seconds=time.perf_counter() - started)
    destination.parent.mkdir(parents=True, exist_ok=True)
    write(destination, result)
    print("B4ML_FOLLOWUP_REVIEW_EXTRACT=" + json.dumps({
        key: result.get(key) for key in ("variant", "profile", "task", "complete", "error", "seconds")
    }, allow_nan=False), flush=True)


def metrics(report):
    automated = report["automated_metrics"]
    contact = automated.get("contact_report") or {}
    flight = automated.get("flight_report") or {}
    return dict(
        priority_matrix_error=automated.get("priority_matrix_error"),
        max_pin_residual=automated.get("max_pin_residual"),
        max_sampled_limb_stretch=automated.get("max_sampled_limb_stretch"),
        max_penetration_body_fraction=automated.get("max_penetration_body_fraction"),
        contact_error_limb_fraction=contact.get("max_after"),
        flight_acceleration_error=flight.get("max_after"),
        scripted_interaction_count=report.get("interaction_count"),
        scripted_correction_count=report.get("scripted_correction_count"),
    )


def qualified_exit(returncode, log_text, extracted):
    if returncode == 0:
        return True, "clean"
    known = {1, 11, -1073741819, 3221225477}
    if returncode in known and extracted.get("complete") and "ucrtbase.dll" in log_text:
        return True, "known post-result ucrtbase.dll host crash"
    return False, "unqualified host exit"


def extract_all():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extracted").mkdir(exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    process_path = OUT / "processes.json"
    processes = read(process_path) if process_path.exists() else []
    for variant in ("baseline", "candidate"):
        for profile, task in CASES:
            _directory, blend, _report = case_paths(variant, profile, task)
            extract = OUT / "extracted" / f"{variant}-{profile}-{task}.json"
            existing = read(extract) if extract.exists() else None
            if existing and existing.get("complete") and existing.get("blend_sha256") == sha(blend):
                continue
            log = OUT / "logs" / f"{variant}-{profile}-{task}.log"
            started = time.perf_counter()
            with log.open("w", encoding="utf-8") as stream:
                process = subprocess.run(
                    [str(HOST), "--background", "--factory-startup", "--disable-autoexec", str(blend),
                     "--python", str(HERE), "--", variant, profile, task],
                    stdout=stream, stderr=subprocess.STDOUT, timeout=180,
                    env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
                )
            extracted = read(extract) if extract.exists() else {"complete": False}
            qualified, qualification = qualified_exit(
                process.returncode, log.read_text(encoding="utf-8", errors="replace"), extracted
            )
            row = dict(variant=variant, profile=profile, task=task, returncode=process.returncode,
                       result_written=bool(extracted.get("complete")), qualified=qualified,
                       qualification=qualification, seconds=time.perf_counter() - started,
                       log_sha256=sha(log), extract_sha256=sha(extract) if extract.exists() else None)
            processes.append(row)
            write(process_path, processes)
            if not qualified:
                raise RuntimeError(f"Follow-up extraction failed: {variant}/{profile}/{task}")


def build():
    if (OUT / "manifest.json").exists():
        raise RuntimeError("Completed follow-up review evidence already exists: " + str(OUT))
    extract_all()
    ids = [f"{profile}/{task}" for profile, task in CASES]
    assignment_seed = sha(TRAIN / "results/procedural-vertical-slice-v17-focused.json")
    ranked = sorted(ids, key=lambda value: hashlib.sha256((assignment_seed + ":" + value).encode()).digest())
    candidate_as_a = set(ranked[:len(ranked) // 2])
    cases = []
    for profile, task in CASES:
        case_id = f"{profile}/{task}"
        baseline = read(OUT / "extracted" / f"baseline-{profile}-{task}.json")
        candidate = read(OUT / "extracted" / f"candidate-{profile}-{task}.json")
        if not baseline.get("complete") or not candidate.get("complete"):
            raise ValueError("Missing complete extraction: " + case_id)
        if len(baseline["samples"]) != len(candidate["samples"]) != 49:
            raise ValueError("Sample count changed: " + case_id)
        baseline_report = read(case_paths("baseline", profile, task)[2])
        candidate_report = read(case_paths("candidate", profile, task)[2])
        candidate_is_a = case_id in candidate_as_a
        mapping = {"A": candidate, "B": baseline} if candidate_is_a else {"A": baseline, "B": candidate}
        mapping_kind = {"A": "review_directed_candidate", "B": "v13_corrected"} if candidate_is_a else {"A": "v13_corrected", "B": "review_directed_candidate"}
        contact_report = candidate_report if task in {"reach", "land", "jump", "walk", "run"} else baseline_report
        declared_contacts = [
            dict(limb=row[0], start=float(row[1]), end=float(row[2]))
            for row in read(TRAIN / f"procedural_vertical_slice_protocol_v{'15' if task in {'reach','land'} else '17'}.json")["tasks"][task]["contacts"]
        ]
        cases.append(dict(
            id=case_id, profile=profile, task=task,
            semantic_profile=candidate["semantic_profile"],
            frames=candidate["frames"], fps=candidate["fps"],
            priority_frames=candidate["priority_frames"],
            # Timing differs between baseline and candidate.  Candidate-only contact
            # dots would bias a blind A/B review, so they remain evidence only.
            contacts=[], declared_candidate_contacts=declared_contacts,
            methods={label: value["samples"] for label, value in mapping.items()},
            reveal={label: dict(kind=mapping_kind[label], **mapping[label]["provenance"])
                    for label in ("A", "B")},
            center=candidate["center"], radius=max(candidate["radius"], baseline["radius"]),
            floor_z=candidate["floor_z"], source_blend=candidate["blend_path"],
            source_blend_sha256=candidate["blend_sha256"],
            source_report_sha256=candidate["report_sha256"],
            baseline_blend=baseline["blend_path"], baseline_blend_sha256=baseline["blend_sha256"],
            baseline_report_sha256=baseline["report_sha256"],
            automated_metrics=dict(v13_corrected=metrics(baseline_report), review_directed_candidate=metrics(candidate_report)),
            candidate_version="v15" if task in {"reach", "land"} else "v17",
            complete=True,
        ))
    payload = dict(
        schema="b4ml-review-directed-followup-review-data-v1",
        title="B4Artists Machine Learning review-directed follow-up",
        names=list(NAMES), roles=list(ROLES), parents=list(PARENTS),
        frame_sampling="49 normalized-time samples per saved animation; displayed labels retain source frames",
        blind_assignment="balanced deterministic SHA-256 rank; identity hidden until each case is locked",
        baseline="frozen corrected v13 case scene",
        candidate="review-directed v15 reach/landing or v17 locomotion/jump scene",
        cases=cases, human_review_status="unreviewed", full_goal_complete=False,
    )
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    data_hash = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    (OUT / "review-data.json").write_text(encoded, encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    page = template.replace("__REVIEW_DATA__", encoded.replace("<", "\\u003c")).replace("__DATA_SHA256__", data_hash)
    page = page.replace("Compare two anonymized outputs from each frozen v13 Bforartists scene.",
                        "Compare the original reviewed v13 output with a later review-directed candidate."
    ).replace("all 32 cases", "all 16 cases"
    ).replace("Automated v13 case measurements", "Automated measurements (context only; not a quality verdict)"
    ).replace("b4ml-procedural-review-v1-", "b4ml-review-directed-followup-v1-"
    ).replace("b4ml-procedural-vertical-slice-human-review-v2", "b4ml-review-directed-followup-human-review-v1"
    ).replace("${c.frames[frame].toFixed(1)} / 25.0", "${c.frames[frame].toFixed(1)} / ${c.frames[c.frames.length-1].toFixed(1)}"
    ).replace("const pi=Math.round((pf-1)*2);skeleton(ctx,c,c.methods[label][pi],",
              "const pi=c.frames.reduce((best,value,index)=>Math.abs(value-pf)<Math.abs(c.frames[best]-pf)?index:best,0);skeleton(ctx,c,c.methods[label][pi],"
    ).replace("Source: ${c.source_blend}", "Candidate source: ${c.source_blend}\\nBaseline source: ${c.baseline_blend}"
    ).replace('v===null?"n/a":v', 'v===null?"n/a":(typeof v==="object"?JSON.stringify(v):v)')
    # Keep the exact export payload available in the local DOM as a recovery path.
    # Some embedded browsers acknowledge Blob downloads without exposing a file path.
    page = page.replace(
        'const a=document.createElement("a");',
        '$("exportPayload").value=JSON.stringify(output,null,2);const a=document.createElement("a");',
    ).replace(
        "</body>",
        '<textarea id="exportPayload" aria-label="Local export recovery payload" '
        'style="position:fixed;right:0;bottom:0;width:2px;height:2px"></textarea></body>',
    )
    page_path = OUT / "reviewer.html"
    page_path.write_text(page, encoding="utf-8")
    manifest = dict(
        schema="b4ml-review-directed-followup-reviewer-manifest-v1", complete=True,
        cases=len(cases), variants=2,
        candidate_as_A=len(candidate_as_a), candidate_as_B=len(ids) - len(candidate_as_a),
        data_sha256=data_hash, html_sha256=sha(page_path), builder_sha256=sha(HERE),
        template_sha256=sha(TEMPLATE), external_dependencies=False, reviewed_cases=0,
        human_assessment="awaiting reviewer", full_goal_complete=False,
    )
    write(OUT / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2, allow_nan=False))


if __name__ == "__main__":
    if "--" in sys.argv:
        index = sys.argv.index("--")
        host(sys.argv[index + 1], sys.argv[index + 2], sys.argv[index + 3])
    else:
        build()
