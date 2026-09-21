# Weak motion-label proposals v1

This train-only research layer turns motion geometry into review candidates for foot contact, static windows, takeoff and landing. It does not turn those candidates into ground truth. The frozen thresholds ran across 1,392 eligible clips, 530,072 frames and all 68 future-training subjects. Two one-frame clips were excluded because velocity is undefined. The 17 future-development subjects, sealed confirmation data and model outcomes were not read.

The scan produced 6,160 foot-contact intervals, 1,629 takeoff events, 1,828 landing events and 398 static windows. A deterministic queue selected 130 items: 30 per foot, 20 takeoffs, 20 landings and 30 static windows. It spans 39 subjects, 16 weak motion tags and short, medium and long durations. Every item remains `unreviewed`; `reviewed_label` is null.

## Method

The complete 23-joint hierarchy is reconstructed with fixed offsets and forward kinematics. Foot indices come from the 17-control semantic map, which maps the semantic foot slots to hierarchy joints 4 and 8. Positions are expressed in the clip's fixed rest-reference frame and normalized by stored body scale.

Contact probability combines low height above the clip's second-percentile foot floor with low foot speed. Hysteresis turns contact on at 0.65 and off at 0.35, then removes runs shorter than three frames. A double-airborne run must last four frames. A takeoff also requires preceding support and upward root speed; a landing requires following support and downward root speed. Static proposals use a prospective 32-frame window and fixed root-speed, root-displacement and semantic-joint angular-speed limits.

All confidence is at most 0.35 and provenance is `heuristic`. The thresholds were frozen before a successful corpus pass. The first attempted pass exposed two undersampled one-frame clips; the implementation was amended to report them as ineligible without changing thresholds.

## Evidence

- Synthetic contract: eight positive cases and three invalid cases pass, covering semantic foot mapping, hysteresis, event boundaries, confidence, translation/scale invariance and evidence boundaries.
- Corpus report: `training/b4artists_ml/results/motion-label-proposals-v1/report.json`.
- Compact proposals: `training/b4artists_ml/results/motion-label-proposals-v1/proposals.json`.
- Review queue: `training/b4artists_ml/results/motion-label-proposals-v1/review-queue.json`.
- Independent contract: `training/b4artists_ml/results/motion-label-proposals-contract-v1/report.json`. It reconstructs the 130-item queue exactly and verifies every queued interval against its compact source proposal.

## What remains unknown

Motion-only BVH data cannot establish force, support-surface geometry, contact normals, moving platforms, hand contact, penetration, animator intent or perceived naturalness. These signals may be used as low-confidence training conditions or review candidates. They may not be used as hard physical constraints or quality labels until reviewed or measured evidence replaces their provenance and confidence.

The next model comparison must use the full hierarchy, exact authored masks and explicit conditioning. It must treat these heuristics as an ablation: compare no contact input, weak contact input and reviewed/measured contact input when that evidence exists. A gain from weak labels does not validate the labels themselves.

No add-on runtime, package, learned weight, Ghost Tool or Anim Assist source changed in this milestone. Full learned motion and the overall goal remain incomplete.
