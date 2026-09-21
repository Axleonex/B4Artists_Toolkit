"""Build a one-case native-display review for the v58 Rigify jitter repair."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(TRAIN))
import build_review_directed_followup_reviewer_v6 as prior


OUT = TRAIN / "results/review-directed-followup-reviewer-v11"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v58-rigify-run-final/summary.json"
REVIEW_EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v9-axlbot.json"
CASES = (("rigify_basic", "run"),)


def source_root(variant, task):
    if task != "run":
        raise ValueError("The v11 packet is restricted to run")
    if variant == "candidate":
        return TRAIN / "results/procedural-vertical-slice-v58-rigify-run-final"
    if variant == "baseline":
        return TRAIN / "results/procedural-vertical-slice-v54-run-final"
    raise ValueError("Unknown review variant")


qualification = SimpleNamespace(
    read=prior.qualification.read,
    number=prior.qualification.number,
    finite_tree=prior.qualification.finite_tree,
    REVIEW_EXPORT=REVIEW_EXPORT,
    validate=lambda: prior.qualification.read(FOCUSED),
)


def configure():
    prior.HERE = HERE
    prior.OUT = OUT
    prior.FOCUSED = FOCUSED
    prior.CASES = CASES
    prior.qualification = qualification
    prior.extractor.HERE = HERE
    prior.extractor.OUT = OUT
    prior.extractor.source_root = source_root
    prior.prior_builder.HERE = HERE
    prior.prior_builder.OUT = OUT
    prior.prior_builder.FOCUSED = FOCUSED
    prior.prior_builder.CASES = CASES
    prior.prior_builder.qualification = qualification
    prior.prior_builder.extractor = prior.extractor
    original = prior.assemble_case

    def assemble(profile, task, candidate_is_a):
        value = original(profile, task, candidate_is_a)
        value["prompt"] = (
            "Compare only Rigify natural flow and jitter. Does v58 reduce abrupt toe-off and "
            "lower-leg snapping versus v54 while retaining a clear running cadence?"
        )
        for reveal in value["reveal"].values():
            reveal["kind"] = (
                "v58 Rigify support-and-swing toe-off interpolation"
                if reveal["variant"] == "candidate"
                else "v54 Rigify run rejected for jitter"
            )
        return value

    prior.assemble_case = assemble


def finalize_identity():
    data_path = OUT / "review-data.json"
    html_path = OUT / "reviewer.html"
    manifest_path = OUT / "manifest.json"
    old_encoded = data_path.read_text(encoding="utf-8")
    old_hash = hashlib.sha256(old_encoded.encode()).hexdigest()
    data = json.loads(old_encoded)
    data.update(
        schema="b4ml-review-directed-followup-review-data-v11",
        title="Rigify jitter repair follow-up 11",
        source_candidate="procedural-vertical-slice-v58-rigify-run-final",
        source_baseline="procedural-vertical-slice-v54-run-final",
        training_authorized=False,
        model_promotion_authorized=False,
        full_goal_complete=False,
    )
    encoded = json.dumps(data, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    data_hash = hashlib.sha256(encoded.encode()).hexdigest()
    page = html_path.read_text(encoding="utf-8")
    old_embedded = old_encoded.replace("<", "\\u003c")
    new_embedded = encoded.replace("<", "\\u003c")
    if old_embedded not in page or old_hash not in page:
        raise ValueError("Completed v6 adapter page does not contain its exact data identity")
    page = page.replace(old_embedded, new_embedded).replace(old_hash, data_hash)
    page = page.replace("Native-display follow-up 6", "Rigify jitter repair follow-up 11")
    page = page.replace(
        "Compare v21 repair 2 with the v20 animation you already reviewed.",
        "Compare the Rigify-only v58 toe-off repair with the v54 run you rejected for jitter.",
    )
    page = page.replace("b4ml-review-directed-followup-v6-", "b4ml-review-directed-followup-v11-")
    page = page.replace(
        "b4ml-review-directed-followup-human-review-v6",
        "b4ml-review-directed-followup-human-review-v11",
    )
    data_path.write_text(encoded, encoding="utf-8", newline="\n")
    html_path.write_text(page, encoding="utf-8", newline="\n")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        schema="b4ml-review-directed-followup-reviewer-manifest-v11",
        data_sha256=data_hash,
        html_sha256=prior.sha(html_path),
        builder_sha256=prior.sha(HERE),
        focused_sha256=prior.sha(FOCUSED),
        source_candidate="procedural-vertical-slice-v58-rigify-run-final",
        source_baseline="procedural-vertical-slice-v54-run-final",
    )
    prior.write(manifest_path, manifest)
    print(json.dumps(manifest, indent=2))


def main():
    configure()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) != 3 or tuple(args[1:]) not in CASES:
            raise ValueError("Unexpected extraction request")
        prior.native_display_host(*args)
    else:
        prior.build()
        finalize_identity()


if __name__ == "__main__":
    main()
