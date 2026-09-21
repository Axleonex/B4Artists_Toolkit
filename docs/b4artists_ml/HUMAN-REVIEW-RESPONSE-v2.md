# Axlbot follow-up response: v18 candidate and second review

Date: 2026-09-19. Status: **deterministic candidate checks passed; human visual review required**.
The original goal, goalpost 79, its signed receipt, 168-hour successor, and prior
review evidence are unchanged by this work. This is not full-goal completion,
production acceptance, temporal training, model promotion, or a Cascadeur claim.

## Evidence and claim boundary

The completed Axlbot v1 follow-up remains the source of the six priorities:
jump height, bend direction, imported landing balance, reach stiffness,
landing float/absorption timing, and Rigify Basic jitter. Its export hash is
`bd0793d081e1775e21c7837dae94ffa6db9a1e1d7a149195457fdeb75a95a4a0`.

The previously started v18 generation finished all 16 cases. The new validator
rechecked their protocol, builder, runtime, scene and log bindings; source
restoration, save/reload, and unchanged pose anchors; numeric measurements;
and exact correspondence to the prior human review. The focused receipt is
`training/b4artists_ml/results/procedural-vertical-slice-v18-focused.json`,
SHA-256 `fcdac5b15aabe102287389554c570a55d7102ca8e72f9bb7a4f0117a036c1f68`.

These are **benchmark-specific procedural authoring changes**, including
declared pole hints, task targets, imported-root uprighting and timing. They
are not evidence of arbitrary production-rig generalization or a newly trained
motion model. The existing local limb-bend prior is distinct from temporal
learning. A larger elbow angle, for example, does not prove a natural reach.

| Focus | Measured result, not a visual verdict |
| --- | --- |
| Jump | Peak pelvis rise is 0.270–0.390 reference body heights across four rigs; frozen minimum 0.20. |
| Reach | Authored elbow flexion is 65.9–82.9 degrees across four rigs. |
| Landing | All four pre-impact vertical velocities are downward, with the required post-impact increase in knee absorption. |
| Imported landing | Priority-pose lateral torso tilt is approximately 0.0000395 degrees. |
| Rigify Basic jump | Rotation-velocity jump metric decreases from 0.470958 to 0.420848 rad/s. |
| Rigify Basic walk | The same metric decreases from 1.348528 to 1.294730 rad/s. |

The Bforartists Alpha process still reports `0xC0000005` during shutdown.
This is **not a clean process exit**. Qualification requires the exact complete
result marker before the access-violation marker and the known `ucrtbase.dll`
shutdown signature; other exits, missing markers and reversed ordering fail.
All 16 generation cases and 32 review extractions preserve that distinction.

## Separate human review packet

Open `training/b4artists_ml/results/review-directed-followup-reviewer-v2/reviewer.html`
through the existing localhost preview server on port 8767. It compares v18
against the previously reviewed v15 reach/land and v17 jump/walk/run outputs.
The old v1 page, export, manifest and browser-storage namespace are untouched.

- Sixteen comparisons; balanced eight/eight A/B assignment, revealed after lock.
- Each side uses its own source frames and fps. The shorter motion holds at its
  end; the loop reset is not part of the animation being rated.
- Shared camera framing and scale, with each variant's actual calibrated floor.
- Forty-nine evaluated joint samples per motion, interpolated for display.
  This skeleton preview cannot certify skin deformation, axial twist, mesh
  collisions, or every subframe motion artifact. Native scene tests remain separate.
- Axlbot / 10+ years are prefilled from the earlier export, not invented identity verification.
- Unlocked drafts autosave; amending one locked case retains its original blind
  rating and labels the amended rating as having seen the identities. Other cases
  are preserved. There is no erase-all control.
- Correction and interaction estimates are optional. Partial backups are allowed;
  completion requires every case to be valid and locked. Export JSON is visible
  on the page as well as offered as a download. Browser storage is not a substitute
  for saving a backup.

Packet data SHA-256: `af92c4c65adb761112ed10efe69e277f560742c48f966fdba0c97a3c552a3309`.
HTML SHA-256: `5120817580fda0b57365502d9a31b73742b60522be3e1aaeec1bff6fbf801efe`.
The manifest binds the extractor, builder, template, extraction processes and
focused v18 evidence. No human ratings were entered by the agent.

## Verification and falsification

Commands executed from the X: repository:

```powershell
python -m unittest discover -s tests -p test_b4artists_ml_review_directed_v18.py -v
python -m unittest discover -s tests -p test_b4artists_ml_followup_reviewer_v2.py -v
```

Both suites pass: **10 test methods**, with additional negative subcases.
The v18 checker also passes directly against all 16 frozen cases.

| Gate | Concrete failing input exercised | Result |
| --- | --- | --- |
| Evidence identity | Stale protocol/runtime/review hash, out-of-scope blend path | Rejected |
| Numeric quality | NaN, infinity, boolean measurement, excessive pin error, upward landing velocity, tilted imported landing, increased jitter | Rejected |
| Complete matrix | Empty/duplicate process entries or empty gate map | Rejected |
| Host qualification | Missing result marker, wrong exit, crash before result | Rejected |
| Extraction | Wrong sample/frame count, nonfinite joint, non-increasing frames, stale scene hash, zero/bool fps | Rejected |
| Timing | Different source durations sampled at the same elapsed time | Correct distinct poses and frame labels; shorter output holds |
| Ratings | Empty required score, negative estimate, edit of locked case | Rejected |
| Amendments | Reopen/relock one case with another case already locked | Original blind rating and other case preserved |
| Learning boundary | Completed synthetic review export | Training and promotion still false |

Browser smoke: the local v2 page loads, both skeleton canvases render,
play/pause advances elapsed time, jump selection shows its 1.20-second timeline,
empty ratings cannot lock, reviewer defaults are correct, zero cases are locked,
and no console warnings/errors were observed. Browser verification used no real
or synthetic ratings. The draft/amendment logic was tested with isolated Node
fixtures, not by changing the user's browser reviews.

## Execution governance

The six-file plan entered the canonical router. Recommended/actual governed
lane: `T3_PRIME_OMP`; policy fingerprint
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
OMP preflight reported `RUNTIME_UNAVAILABLE`, and the router returned
`NATIVE_CONTINUATION`, `outcome=fallback`, `native_fallback_authorized=true`.
There were no model execution attempts or escalations.
The real host-owned fallback receipt is
`C:/Users/Jonvilario/.hermes/state/prime/coding-execution-receipts/391ac7086a0b49ab865d1f74d3739d0c.json`.
It does **not** authorize integration or certify an independent code review.

Declared source/document scope:

1. `training/b4artists_ml/check_review_directed_vertical_slice_v18.py`
2. `tests/test_b4artists_ml_review_directed_v18.py`
3. `training/b4artists_ml/build_review_directed_followup_reviewer_v2.py`
4. `training/b4artists_ml/review_directed_followup_template_v2.html`
5. `tests/test_b4artists_ml_followup_reviewer_v2.py`
6. This document.

The checker changed from SHA-256
`b632a6b801e02cb40cbba6f588eb361c477797733daac88acd91632c548e139d`
to `7eee27b02afee57ca507fc542c34f5bb39f5ba431f913e1a592c725cd70ef482`.
The other five scoped files were added. Generated results are separate artifacts;
previous reviews and frozen scenes were not overwritten. No rollback was
performed or claimed to be tested. No commit, push, merge, install or promotion
was performed.

The adaptive review classification at checkpoint scope is **INCONCLUSIVE**:
tests/gates require S2, above that scope's S1 ceiling. No independent reviewer
was invoked and no PASS is claimed. `git diff --check` was also unavailable in
the observed checkout context; its error is not counted as validation.
These limitations prevent an independent-code-review or release-completion
claim, but do not change the separately measured deterministic results.

## Next boundary

Human judgment is now required for this candidate: do the new outputs actually
improve height, bend direction, balance, reach articulation, impact timing and
jitter without losing task intent? Rate both sides honestly, including neither
if appropriate. Do not infer a visual pass from the numeric results above.

Training, model promotion, Cascadeur entitlement/connector work, broad production
character acceptance, and the overall goal remain open and fail-closed.
