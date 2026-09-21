# Axlbot follow-up v2 capture and corrected native-display review

Date: 2026-09-19. Overall goal remains incomplete. Same inherited goal and
168-hour successor; no contract, history, floors, or goalpost changes.

## Preserved human evidence

All 16 locked ratings were exported through the existing reviewer UI. Reviewer
metadata remains Axlbot / 10+ years. No ratings, notes, failure tags, estimates,
timestamps, or identities were supplied or amended by the agent.

The saved JSON differs only in serialization from the browser export. Sorted-key
compact UTF-8 SHA-256 was independently computed for both and matched:
`0819d253b73347be9fa23fc647c8cfe10c3f2889712dcd5c1a45ab620063ddf5`.
The saved file SHA-256 is
`4df237fe927dfc7b05a1038831fc4f225e7d13c9c61395c9defc9222b881b9ea`.

- Capture: `training/b4artists_ml/results/human-review-exports/b4ml-review-directed-followup-human-review-v2-axlbot.json`
- Strict import: `training/b4artists_ml/import_followup_review_v2.py`
- Summary: `training/b4artists_ml/results/review-directed-followup-reviewer-v2/human-review-summary-v2.json`

For the representation actually shown, candidate acceptability is 7/16 versus
5/16 baseline. Preferences: candidate 4, baseline 0, tie 6, neither 6. No jump
is accepted. Rigify Basic walk is a regression: baseline accepted, candidate
rejected. Its baseline remains available and unchanged. Optional blank effort
estimates remain blank, not zero. Reviewer metadata is not an identity receipt.

## Root cause: preview dropped the native motion-instance transform

The systematic-debugging skill required reproducing the mismatch before tuning
the solver. The old extractor at
`build_review_directed_followup_reviewer_v1.py::host::world_points` used
`evaluated.matrix_world @ evaluated.pose.bones[name].head` without the separate
native collection-instance motion layer. The v2 builder reuses that extractor.
The old files and reviewed page remain frozen as historical evidence.

The displayed position must include the rigid motion-instance transform before
projecting into the fixed task basis. Tests first reproduced the lost translation
and rotation, then passed with that transform restored. All 32 saved comparison
clips were re-opened without saving or changing the .blend files. At all 49 source
sample times per clip, the corrected calculation was independently compared with
the native depsgraph displayed-instance matrix. Maximum error across the matrix:
`1.1324545691974622e-07` body lengths (limit `2e-6`). The old samples were also
reproduced to distinguish a display fix from an animation change.

Candidate maximum two-foot clearance in body-height units is now faithfully
displayed: BoneForge 0.398849, Rigify Basic 0.347208, Rigify Default 0.347208,
imported Unity 0.278911. The old preview showed approximately zero. These are
sampled geometric measurements, NOT human usability or motion-quality passes.

Evidence: `training/b4artists_ml/results/review-display-recovery-v3/` contains
32 exclusive-created extraction records, process records and logs. Every host
process returned the known Bforartists alpha `C0000005` shutdown fault after its
exact successful result marker, with `ucrtbase.dll` in the subsequent traceback.
This is qualified result evidence, never a clean process-exit claim.

## New human boundary: only the affected display comparisons

The corrected page is:
`http://127.0.0.1:8767/training/b4artists_ml/results/review-directed-followup-reviewer-v3/reviewer.html`

It contains ten comparisons: four jumps, four landings, and BoneForge/Rigify
Basic runs. Six reach/walk comparisons were unchanged; their ratings are retained
and they are not requested again. All original ratings, including the ten affected
ones, remain historical evidence for the original representation.

This is explicitly a non-blind re-review because the user has already seen the
identities. New exports always record `blind_at_rating=false` and prior exposure.
The page has its own data-hash-scoped browser storage; no previous ratings are
cleared, overwritten, or pre-marked accepted. Identity defaults remain Axlbot /
10+ years. Actual source frame rates, immutable scene hashes and fixed ground
planes are retained. No animation was retuned to conceal the exporter bug.

Verify jump height and arm/knee motion, landing descent/contact/absorption,
and running balance with the full-body trajectory visible. The agent inspected
the corrected Rigify Basic jump at 0.56 seconds in side view, verified zero browser
console errors, and left every rating field untouched (0/10 locked).

## Implementation, checks, and governance decision

Declared source scope is the importer, `diagnose_review_directed_v19.py`,
`build_review_directed_v19.py`, two associated test files, this document, and the
captured review JSON. The v19 script names identify this investigation; they do
NOT mean a v19 animation candidate was built. Generated evidence lives in the
separate recovery and reviewer-v3 result directories.

The code router selected recommended/actual `T3_PRIME_OMP`; the OMP preflight
returned `RUNTIME_UNAVAILABLE`, before host application. It explicitly authorized
project-local native continuation with outcome `fallback` and no escalation.
Authorization risk tier: `workflow_scaffolding`.
Router policy fingerprint:
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
Real receipt:
`C:\Users\Jonvilario\.hermes\state\prime\coding-execution-receipts\3cebe061bc684fc588c2f1810a6bc8c7.json`.
Its `integration_authorized=false` remains unchanged; no integration or promotion
is claimed. Changes are isolated additions; no source/review rollback was needed.

Validation commands, all passing:

```powershell
# [PowerShell] From X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github
python -m unittest discover -s tests -p test_b4artists_ml_review_directed_v18.py -v
python -m unittest discover -s tests -p test_b4artists_ml_followup_reviewer_v2.py -v
python -m unittest discover -s tests -p test_b4artists_ml_followup_review_import_v2.py -v
python -m unittest discover -s tests -p test_b4artists_ml_review_directed_v19.py -v
```

22 test methods total (5+5+3+9), including negative evidence and stale-hash cases;
32 native extraction comparisons; generated manifest/data/HTML hashes verified.
The original v1 human export is unchanged at
`bd0793d081e1775e21c7837dae94ffa6db9a1e1d7a149195457fdeb75a95a4a0`.
The v18 and v2 frozen-evidence tests still pass.

Code Evaluator plan-scope classification selected runnable S2, fingerprint
`95e923fbec07b91a6667e116f90d86466b6f41252b0d2a111a268010a45bd808`.
Its PASS applies only to classification: `classification_only=true`,
`reviewer_invoked=false`, `review_completed=false`. Independent code review is
NOT passed by that result. No package, release, or completion claim is made.

## Pending work, not erased by this correction

BoneForge reach still lacks torso participation; imported reach still has the
wrong elbow-leading relationship; Rigify Basic walk still has the human-reported
regression. BoneForge arm flail and Rigify shoulder jitter remain open negative
signals. Corrected-display human review is needed before retuning airborne
height, landing timing or running balance against misleading previews.

Production-character generalization and temporal evaluation remain incomplete.
Training, model promotion and Cascadeur stay fail-closed under their existing
human, identity, qualified-disjoint-corpus and entitlement prerequisites. No
training, commit, push, merge, signing, new goal, or new authority action occurred.
Stop here at the fresh human visual-review boundary; preserve the existing goal.
