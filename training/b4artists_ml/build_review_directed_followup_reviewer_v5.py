"""Build the native-display v20 versus v19 non-blind follow-up review.

The v4 page omitted each scene's native motion-instance transform.  This
builder reuses its immutable review UI while replacing extraction with the
actual depsgraph display instance and proving parity with the saved motion
layer before any review sample can qualify.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import time
import traceback


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(TRAIN))
import build_review_directed_followup_reviewer_v1 as extractor
import build_review_directed_followup_reviewer_v4 as prior_builder
import check_review_directed_vertical_slice_v20 as qualification


OUT = TRAIN / "results/review-directed-followup-reviewer-v5"
TEMPLATE = TRAIN / "review_directed_followup_template_v2.html"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v20-focused.json"
CASES = prior_builder.CASES
sha, read, write = extractor.sha, qualification.read, extractor.write


def source_root(variant, task):
    if variant == "candidate":
        return TRAIN / "results/procedural-vertical-slice-v20-final"
    if variant == "baseline":
        return TRAIN / "results/procedural-vertical-slice-v19-repair2"
    raise ValueError("Unknown review variant")


extractor.HERE = HERE
extractor.OUT = OUT
extractor.source_root = source_root
prior_builder.HERE = HERE
prior_builder.OUT = OUT
prior_builder.FOCUSED = FOCUSED
prior_builder.CASES = CASES
prior_builder.qualification = qualification
prior_builder.extractor = extractor


def native_display_host(variant, profile, task):
    """Run the legacy extractor, then fail closed unless native display replaces it."""
    import bpy
    import numpy as np
    from mathutils import Vector

    sys.path[:0] = [str(ROOT), str(TRAIN)]
    from b4artists_ml import body_solver, motion_layer, posing

    destination = OUT / "extracted" / f"{variant}-{profile}-{task}.json"
    extractor.host(variant, profile, task)
    result = read(destination)
    result["complete"] = False
    write(destination, result)
    started = time.perf_counter()
    try:
        _directory, blend, report_path = extractor.case_paths(variant, profile, task)
        report = read(report_path)
        armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and hasattr(obj, "b4ml")]
        animated = [obj for obj in armatures if (
            (obj.animation_data and obj.animation_data.action is not None)
            or getattr(obj.b4ml, "candidate_action", None) is not None
        )]
        if len(animated) != 1:
            raise ValueError(f"Expected one animated review armature, found {len(animated)}")
        obj = animated[0]
        scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
        bpy.context.window.scene = scene
        binding = body_solver.mapping(obj, writable=False)
        axes = [Vector(row) for row in report["task_basis_world"]]
        height = float(report["reference_height"])
        frames = result["frames"]
        rows = []
        origin = None
        native_parity_error = 0.0
        has_layer = motion_layer.find(obj) is not None
        if has_layer:
            motion_layer.validate(obj)
        for frame in frames:
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            posing._update(obj)
            graph = bpy.context.evaluated_depsgraph_get()
            evaluated = obj.evaluated_get(graph)
            instances = [
                instance.matrix_world.copy()
                for instance in graph.object_instances
                if instance.object.original == obj and bool(instance.is_instance) == has_layer
            ]
            if len(instances) != 1:
                raise ValueError(f"Expected one displayed armature instance, found {len(instances)}")
            native = [instances[0] @ evaluated.pose.bones[name].head for name in binding["names"]]
            raw = [evaluated.matrix_world @ evaluated.pose.bones[name].head for name in binding["names"]]
            layer = motion_layer.transform(obj)
            corrected = [layer @ point for point in raw]
            native_parity_error = max(
                native_parity_error,
                max((a - b).length / height for a, b in zip(native, corrected)),
            )
            if origin is None:
                origin = native[0].copy()
            rows.append([[float((point - origin).dot(axis) / height) for axis in axes] for point in native])
        values = np.asarray(rows, dtype=np.float64)
        if values.shape != (49, 17, 3) or not np.isfinite(values).all():
            raise ValueError("Nonfinite or malformed native-display skeleton")
        if native_parity_error > 2e-6:
            raise ValueError(f"Native display parity failed: {native_parity_error}")
        low, high = values.reshape(-1, 3).min(axis=0), values.reshape(-1, 3).max(axis=0)
        center = (low + high) * 0.5
        radius = float(np.max(np.linalg.norm(values.reshape(-1, 3) - center, axis=1)))
        floor_point = Vector((0.0, 0.0, float(report["rig_floor_calibration"]["floor_z"])))
        result.update(
            schema="b4ml-review-directed-followup-native-display-extract-v1",
            complete=True,
            samples=np.round(values, 7).tolist(),
            center=np.round(center, 7).tolist(),
            radius=radius,
            floor_z=float((floor_point - origin).dot(axes[2]) / height),
            display_representation="native depsgraph armature instance",
            has_native_motion_layer=has_layer,
            maximum_native_instance_error=native_parity_error,
            native_display_validated=True,
            training_authorized=False,
            model_promotion_authorized=False,
            seconds=time.perf_counter() - started,
        )
    except BaseException:
        result.update(error=traceback.format_exc(), seconds=time.perf_counter() - started)
    write(destination, result)
    print("B4ML_FOLLOWUP_REVIEW_EXTRACT=" + json.dumps({
        key: result.get(key)
        for key in ("variant", "profile", "task", "complete", "error", "seconds")
    }, allow_nan=False), flush=True)


def assemble_case(profile, task, candidate_is_a):
    variants = {
        kind: prior_builder.validate_extraction(
            read(OUT / "extracted" / f"{kind}-{profile}-{task}.json"), kind, profile, task
        )
        for kind in ("baseline", "candidate")
    }
    for value in variants.values():
        if value.get("native_display_validated") is not True:
            raise ValueError("Review extraction lacks native-display validation")
        if qualification.number(value.get("maximum_native_instance_error")) > 2e-6:
            raise ValueError("Review extraction exceeds native-display parity tolerance")
    mapping = {"A": "candidate", "B": "baseline"} if candidate_is_a else {
        "A": "baseline", "B": "candidate"
    }
    methods = {}
    for label, kind in mapping.items():
        value = variants[kind]
        methods[label] = {
            key: value[key] for key in ("samples", "frames", "fps", "floor_z", "priority_frames")
        }
        methods[label]["duration_seconds"] = (
            value["frames"][-1] - value["frames"][0]
        ) / value["fps"]
    points = [point for value in variants.values() for sample in value["samples"] for point in sample]
    lows = [min(point[index] for point in points) for index in range(3)]
    highs = [max(point[index] for point in points) for index in range(3)]
    lows[2] = min(lows[2], *(value["floor_z"] for value in variants.values()))
    center = [(low + high) / 2 for low, high in zip(lows, highs)]
    radius = max(0.2, max(math.dist(point, center) for point in points))
    instructions = {
        "jump": "Check visible jump height, knee direction, takeoff/landing contact, arm control and jitter.",
        "land": "Check descent before impact, knee absorption after impact, feet, torso balance and impact jitter.",
        "run": "Check whether foot contact, stride, arm swing and body timing remain coherent.",
    }
    return {
        "id": f"{profile}/{task}", "profile": profile, "task": task,
        "prompt": instructions[task], "semantic_profile": variants["candidate"]["semantic_profile"],
        "methods": methods, "center": center, "radius": radius,
        "duration_seconds": max(method["duration_seconds"] for method in methods.values()),
        "display_representation": "native depsgraph armature instance",
        "reveal": {
            label: {
                "kind": "v20 native-display candidate" if kind == "candidate" else "reviewed v19 candidate",
                "variant": kind, "blend_path": variants[kind]["blend_path"],
                "blend_sha256": variants[kind]["blend_sha256"],
                "report_sha256": variants[kind]["report_sha256"], **variants[kind]["provenance"],
            }
            for label, kind in mapping.items()
        },
    }


def build():
    if (OUT / "manifest.json").exists():
        raise RuntimeError("Immutable completed v5 review already exists")
    checked = qualification.validate()
    if read(FOCUSED) != checked:
        raise ValueError("Focused v20 receipt is stale")
    processes = prior_builder.extract_all()
    expected = {(variant, profile, task) for variant in ("baseline", "candidate") for profile, task in CASES}
    if len(processes) != len(expected) or {
            (row["variant"], row["profile"], row["task"]) for row in processes
    } != expected:
        raise ValueError("Incomplete native-display extraction matrix")
    ids = [f"{profile}/{task}" for profile, task in CASES]
    seed = sha(FOCUSED)
    ranked = sorted(ids, key=lambda item: hashlib.sha256((seed + ":" + item).encode()).digest())
    as_a = set(ranked[:len(ranked) // 2])
    payload = {
        "schema": "b4ml-review-directed-followup-review-data-v5",
        "title": "Review-directed native-display follow-up 5",
        "parents": list(extractor.PARENTS), "roles": list(extractor.ROLES),
        "cases": [assemble_case(profile, task, f"{profile}/{task}" in as_a) for profile, task in CASES],
        "frame_sampling": "49 native-display samples per method at source fps; hold after shorter method ends",
        "source_qualification_sha256": seed,
        "human_review_status": "pending non-blind visual review",
        "prior_exposure": True,
        "source_human_review_sha256": sha(qualification.REVIEW_EXPORT),
        "default_reviewer": read(qualification.REVIEW_EXPORT)["reviewer"],
        "native_display_validated": True,
        "training_authorized": False, "model_promotion_authorized": False,
        "full_goal_complete": False,
    }
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    data_hash = hashlib.sha256(encoded.encode()).hexdigest()
    page = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "Follow-up review 2": "Native-display follow-up 5",
        "Independent human assessment pending": "Non-blind native-display visual re-review",
        "Compare the new v18 candidate with the previously reviewed v15/v17 candidate. A/B identities stay hidden until you lock each case. Your earlier ratings remain untouched.":
            "Compare v20 with the v19 animation you already reviewed. This page now includes each scene's native motion layer, so judge the visible jump, landing and run as displayed. Earlier ratings remain untouched; this review cannot authorize training or model promotion.",
        "Blind variant": "Previously viewed comparison",
        "a completed review requires all 16 cases locked": f"a completed review requires all {len(CASES)} cases locked",
        "b4ml-review-directed-followup-v2-": "b4ml-review-directed-followup-v5-",
        "b4ml-review-directed-followup-human-review-v2": "b4ml-review-directed-followup-human-review-v5",
        "blind_at_rating:!prior.reveal_seen": "blind_at_rating:false",
        "shown=Boolean(review?.reveal_seen)": "shown=true",
        "source_qualification_sha256:data.source_qualification_sha256,reviewer:":
            "source_qualification_sha256:data.source_qualification_sha256,source_human_review_sha256:data.source_human_review_sha256,native_display_validated:true,prior_exposure:true,reviewer:",
        "reveal_seen?c.reveal:null": "locked?c.reveal:null",
    }
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("Template anchor changed: " + before)
        page = page.replace(before, after)
    page = page.replace("__REVIEW_DATA__", encoded.replace("<", "\\u003c")).replace("__DATA_SHA256__", data_hash)
    for name, content in (("review-data.json", encoded), ("reviewer.html", page)):
        with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    manifest = {
        "schema": "b4ml-review-directed-followup-reviewer-manifest-v5",
        "complete": True, "cases": len(CASES), "variants": 2,
        "candidate_as_A": len(as_a), "candidate_as_B": len(CASES) - len(as_a),
        "data_sha256": data_hash, "html_sha256": sha(OUT / "reviewer.html"),
        "builder_sha256": sha(HERE), "extractor_sha256": sha(Path(extractor.__file__)),
        "template_sha256": sha(TEMPLATE), "processes_sha256": sha(OUT / "processes.json"),
        "focused_sha256": seed, "source_human_review_sha256": sha(qualification.REVIEW_EXPORT),
        "prior_exposure": True, "native_display_validated": True,
        "maximum_native_instance_error": max(
            read(path)["maximum_native_instance_error"] for path in (OUT / "extracted").glob("*.json")
        ),
        "external_dependencies": False, "reviewed_cases": 0,
        "human_assessment": "awaiting reviewer", "known_host_shutdown_faults": sum(
            row["returncode"] != 0 for row in processes
        ),
        "training_authorized": False, "model_promotion_authorized": False,
        "full_goal_complete": False,
    }
    write(OUT / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) != 3 or tuple(args[1:]) not in CASES:
            raise ValueError("Unexpected extraction request")
        native_display_host(*args)
    else:
        build()
