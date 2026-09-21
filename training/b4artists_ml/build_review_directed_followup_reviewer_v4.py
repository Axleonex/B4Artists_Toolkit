"""Timing-faithful non-blind review of v19 repair-2 versus reviewed v18.

Reuses the frozen 17-joint scene extractor; never rewrites earlier ratings/scenes.
This is a procedural candidate review, not model training or product acceptance.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(TRAIN))
import build_review_directed_followup_reviewer_v1 as extractor
import check_review_directed_vertical_slice_v19_repair2 as qualification

OUT = TRAIN / "results/review-directed-followup-reviewer-v4"
TEMPLATE = TRAIN / "review_directed_followup_template_v2.html"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v19-repair2-focused.json"
CASES = (
    ("boneforge", "jump"),
    ("rigify_basic", "jump"),
    ("rigify_default", "land"),
    ("rigify_default", "jump"),
    ("imported_unity", "land"),
    ("imported_unity", "jump"),
    ("boneforge", "run"),
    ("rigify_basic", "run"),
)
sha, read, write = extractor.sha, qualification.read, extractor.write


def source_root(variant, task):
    if variant == "candidate":
        return TRAIN / "results/procedural-vertical-slice-v19-repair2"
    elif variant == "baseline":
        return TRAIN / "results/procedural-vertical-slice-v18"
    else:
        raise ValueError("Unknown variant")


extractor.HERE = HERE
extractor.OUT = OUT
extractor.source_root = source_root


def qualified_exit(code, log, result):
    if result.get("complete") is not True:
        return False
    marker = "B4ML_FOLLOWUP_REVIEW_EXTRACT=" + json.dumps({
        key: result.get(key) for key in ("variant", "profile", "task", "complete", "error", "seconds")
    }, allow_nan=False)
    index = log.find(marker)
    if index < 0:
        return False
    if code == 0:
        return "EXCEPTION_ACCESS_VIOLATION" not in log
    crash = log.find("EXCEPTION_ACCESS_VIOLATION")
    return (code & 0xffffffff == 0xc0000005 and crash > index
            and "ucrtbase.dll" in log[crash:])


def validate_extraction(value, variant, profile, task):
    if (value.get("complete") is not True or value.get("variant") != variant or
            value.get("profile") != profile or value.get("task") != task):
        raise ValueError("Extraction identity/incompletion")
    _, blend, report_path = extractor.case_paths(variant, profile, task)
    report = read(report_path)
    if (value.get("blend_sha256") != sha(blend) or
            report.get("blend_sha256") != sha(blend) or
            value.get("report_sha256") != sha(report_path)):
        raise ValueError("Stale extraction source")
    qualification.finite_tree(value)
    frames, samples = value["frames"], value["samples"]
    if len(frames) != 49 or len(samples) != 49:
        raise ValueError("Expected 49 samples independently for each method")
    if any(type(f) not in (int, float) for f in frames) or any(a >= b for a, b in zip(frames, frames[1:])):
        raise ValueError("Invalid frame sequence")
    if qualification.number(value["fps"]) <= 0:
        raise ValueError("Invalid source fps")
    for sample in samples:
        if len(sample) != 17 or any(len(point) != 3 for point in sample):
            raise ValueError("Invalid skeleton shape")
        for point in sample:
            for coordinate in point:
                qualification.number(coordinate)
    return value


def extract_all():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extracted").mkdir(exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    process_path = OUT / "processes.json"
    processes = read(process_path) if process_path.exists() else []
    for variant in ("baseline", "candidate"):
        for profile, task in CASES:
            _, blend, _ = extractor.case_paths(variant, profile, task)
            target = OUT / "extracted" / f"{variant}-{profile}-{task}.json"
            log_path = OUT / "logs" / f"{variant}-{profile}-{task}.log"
            prior = [r for r in processes if (r["variant"], r["profile"], r["task"]) == (variant, profile, task)]
            if target.exists():
                value = validate_extraction(read(target), variant, profile, task)
                if (len(prior) != 1 or prior[0]["extract_sha256"] != sha(target) or
                        prior[0]["log_sha256"] != sha(log_path) or
                        not qualified_exit(prior[0]["returncode"], log_path.read_text(encoding="utf-8", errors="replace"), value)):
                    raise ValueError("Existing extraction lacks matching process evidence; preserved")
                continue
            if log_path.exists() or prior:
                raise ValueError("Incomplete prior attempt retained; refusing overwrite")
            started = time.perf_counter()
            with log_path.open("x", encoding="utf-8") as stream:
                result = subprocess.run([
                    str(extractor.HOST), "--background", "--factory-startup", "--disable-autoexec",
                    str(blend), "--python", str(HERE), "--", variant, profile, task,
                ], stdout=stream, stderr=subprocess.STDOUT, timeout=180,
                    env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"))
            value = read(target) if target.exists() else {}
            qualified = qualified_exit(result.returncode, log_path.read_text(encoding="utf-8", errors="replace"), value)
            processes.append(dict(variant=variant, profile=profile, task=task,
                returncode=result.returncode, qualified=qualified,
                seconds=time.perf_counter() - started, log_sha256=sha(log_path),
                extract_sha256=sha(target) if target.exists() else None))
            write(process_path, processes)
            if not qualified:
                raise ValueError(f"Unqualified extraction {variant}/{profile}/{task}")
            validate_extraction(value, variant, profile, task)
            print(f"extracted {variant}/{profile}/{task}", flush=True)
    return processes


def assemble_case(profile, task, candidate_is_a):
    variants = {kind: validate_extraction(read(OUT / "extracted" / f"{kind}-{profile}-{task}.json"), kind, profile, task)
                for kind in ("baseline", "candidate")}
    mapping = {"A": "candidate", "B": "baseline"} if candidate_is_a else {"A": "baseline", "B": "candidate"}
    methods = {}
    for label, kind in mapping.items():
        value = variants[kind]
        methods[label] = {key: value[key] for key in ("samples", "frames", "fps", "floor_z", "priority_frames")}
        methods[label]["duration_seconds"] = (value["frames"][-1] - value["frames"][0]) / value["fps"]
    # Shared world-to-view framing: neither method is individually auto-zoomed.
    points = [point for value in variants.values() for sample in value["samples"] for point in sample]
    lows = [min(p[i] for p in points) for i in range(3)]
    highs = [max(p[i] for p in points) for i in range(3)]
    lows[2] = min(lows[2], *(v["floor_z"] for v in variants.values()))
    center = [(a + b) / 2 for a, b in zip(lows, highs)]
    radius = max(.2, max(math.dist(point, center) for point in points))
    instructions = {
        "jump": "Check jump height, knee direction, takeoff/landing contact and jitter.",
        "land": "Check descent before impact, knee absorption after impact, feet and torso balance.",
        "reach": "Check elbow direction and whether the reach feels naturally articulated rather than rigid.",
        "walk": "Check hip motion, limb direction, planted feet and popping.",
        "run": "Check whether foot contact, stride and body motion remain coherent.",
    }
    return dict(id=f"{profile}/{task}", profile=profile, task=task, prompt=instructions[task],
        semantic_profile=variants["candidate"]["semantic_profile"], methods=methods,
        center=center, radius=radius, duration_seconds=max(m["duration_seconds"] for m in methods.values()),
        reveal={label: dict(kind=("v19 repair-2 candidate" if kind == "candidate" else "previously reviewed v18"),
            variant=kind, blend_path=variants[kind]["blend_path"], blend_sha256=variants[kind]["blend_sha256"],
            report_sha256=variants[kind]["report_sha256"], **variants[kind]["provenance"]) for label, kind in mapping.items()})


def build():
    if (OUT / "manifest.json").exists():
        raise RuntimeError("Immutable completed v4 review already exists")
    checked = qualification.validate()
    if read(FOCUSED) != checked:
        raise ValueError("Focused receipt is stale")
    processes = extract_all()
    expected = {(v, p, t) for v in ("baseline", "candidate") for p, t in CASES}
    if len(processes) != len(expected) or {(r["variant"], r["profile"], r["task"]) for r in processes} != expected:
        raise ValueError("Incomplete extraction matrix")
    ids = [f"{p}/{t}" for p, t in CASES]
    seed = sha(FOCUSED)
    ranked = sorted(ids, key=lambda item: hashlib.sha256((seed + ":" + item).encode()).digest())
    as_a = set(ranked[:len(ranked) // 2])
    payload = dict(schema="b4ml-review-directed-followup-review-data-v4",
        title="Review-directed follow-up 4", parents=list(extractor.PARENTS), roles=list(extractor.ROLES),
        cases=[assemble_case(p, t, f"{p}/{t}" in as_a) for p, t in CASES],
        frame_sampling="49 evaluated samples per method, interpolated at each method's source fps; hold after shorter method ends",
        source_qualification_sha256=seed, human_review_status="pending non-blind visual review",
        prior_exposure=True,
        source_human_review_sha256=sha(qualification.REVIEW_EXPORT),
        default_reviewer=read(qualification.REVIEW_EXPORT)["reviewer"],
        training_authorized=False, model_promotion_authorized=False, full_goal_complete=False)
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    data_hash = hashlib.sha256(encoded.encode()).hexdigest()
    page = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "Follow-up review 2": "Review-directed follow-up 4",
        "Independent human assessment pending": "Non-blind visual re-review",
        "Compare the new v18 candidate with the previously reviewed v15/v17 candidate. A/B identities stay hidden until you lock each case. Your earlier ratings remain untouched.":
            "Compare the new full-body repair-2 candidate with the v18 animation you already reviewed. Judge only visible animation quality; all earlier ratings remain untouched. This review cannot authorize training or model promotion.",
        "Blind variant": "Previously viewed comparison",
        "a completed review requires all 16 cases locked": f'a completed review requires all {len(CASES)} cases locked',
        "b4ml-review-directed-followup-v2-": "b4ml-review-directed-followup-v4-",
        "b4ml-review-directed-followup-human-review-v2": "b4ml-review-directed-followup-human-review-v4",
        "blind_at_rating:!prior.reveal_seen": "blind_at_rating:false",
        "shown=Boolean(review?.reveal_seen)": "shown=true",
        "source_qualification_sha256:data.source_qualification_sha256,reviewer:":
            "source_qualification_sha256:data.source_qualification_sha256,source_human_review_sha256:data.source_human_review_sha256,prior_exposure:true,reviewer:",
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
    manifest = dict(schema="b4ml-review-directed-followup-reviewer-manifest-v4", complete=True,
        cases=len(CASES), variants=2, candidate_as_A=len(as_a), candidate_as_B=len(CASES)-len(as_a), data_sha256=data_hash,
        html_sha256=sha(OUT / "reviewer.html"), builder_sha256=sha(HERE),
        extractor_sha256=sha(Path(extractor.__file__)), template_sha256=sha(TEMPLATE),
        processes_sha256=sha(OUT / "processes.json"), focused_sha256=seed,
        source_human_review_sha256=sha(qualification.REVIEW_EXPORT), prior_exposure=True,
        external_dependencies=False, reviewed_cases=0, human_assessment="awaiting reviewer",
        known_host_shutdown_faults=sum(r["returncode"] != 0 for r in processes),
        training_authorized=False, model_promotion_authorized=False, full_goal_complete=False)
    write(OUT / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) != 3 or tuple(args[1:]) not in CASES:
            raise ValueError("Unexpected extraction request")
        extractor.host(*args)
    else:
        build()
