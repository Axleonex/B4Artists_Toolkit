# Experimental temporal contact correction

The full product goal remains active and incomplete. This milestone adds explicit world-space hand/foot contact intervals to editable animation candidates. It is a geometric correction baseline for future learned motion, contacts and balance integration. Neural weights and training data are unchanged.

## Behavioral target and boundaries

Cascadeur documents fulcrums as contact points used by several animation/physics workflows, and describes contact recognition using proximity and motion. Its [Fulcrum Points](https://cascadeur.com/help/tools/physics_tools/fulcrum_points) and [Fulcrum Motion Cleaning](https://cascadeur.com/help/category/206) are behavioral references, not a source of proprietary implementation. No equivalent direct comparison has been run.

The current implementation uses animator-authored static world contacts. It does not detect the ground, collide with meshes, follow moving surfaces, solve COM/balance, adjust the root to make unreachable contacts feasible, or implement learned motion. Capturing a joint origin does not automatically identify a sole or palm; a local contact offset identifies a chosen point on the evaluated joint.

## Workflow and data preservation

Capture compatible humanoid pose anchors and generate an interpolation candidate. At a desired contact pose, choose the foot/hand and Capture Contact Here. Set Hold From/To, transition Blend Frames, Strength and Hold Rotation. Contact Point Settings exposes the local capture offset and the selected contact's world point/local offset. Add separate intervals for additional limbs or later contacts.

Preview Contact Correction creates an independent action copy. Existing priority poses are preserved; a contact inconsistent with an anchor fails instead of changing that anchor. All three affected animator controls must be present in every anchor. Generated rigs must use the existing verified normalized FK candidate. Read-only deform/mechanism bones provide evaluated positions and orientations; only mapped animator rotations receive correction keys.

Corrections are limited to each contact's hold and blend intervals. Unrelated channels are copied intact. The unmodified input candidate is retained as an editable alternative. Repeated previews regenerate from that retained input, so changing strength does not stack corrections. The input/output references and contact settings survive save/reload. Restore Before Contacts returns directly to the input interpolation candidate. Keep, Discard and Restore Source retain the original animation workflow.

The UI operator is cooperative and cancellable. During fitting, each checkpoint restores the preceding preview and original playhead; the copied result is evaluated before being offered for Keep. Escape, a failed fit, changed requests or input-action changes restore the previous candidate. Saving, loading, undo/redo and unregister cancel unfinished work. No original source action curves are rewritten.

## Timing and geometry

A contact holds its captured world point over its interval, with smoothstep influence ramps immediately outside the interval. Strength blends the input point/orientation toward the captured contact. Overlapping hold/ramp regions on the same limb are rejected to avoid contradictory requests. Different limbs may overlap. Blend intervals are clipped to the candidate's anchor span.

The FK projection uses the evaluated two-segment limb lengths and the input limb-plane normal. A straight limb uses a fallback transported with its input upper control; this avoids a target crossing the original pole and flipping the bend. The projection compensates the contact-point offset, and preserves or blends the evaluated end orientation. Unreachable targets fail rather than silently stretching limbs or shifting the body. Successful projection must preserve segment lengths within .002 relative error, positions within 2e-4 limb units and orientations within .001 radians.

The base output cadence is eight samples per frame, plus exact anchor/contact/blend boundaries. Every midpoint between sample keys is evaluated on the original rig after the candidate curves are written. Failed midpoint checks cause local key insertion and a new validation pass, with at most four adaptive refinements. Failure at an authored sample or after that budget rejects the result. This is finite sampling, not a proof of continuous-time contact accuracy at every possible subframe.

Candidate span remains at most 240 frames, with 32 contact intervals and the existing 200,000-key cap for the active action slot. The final key budget includes retained keys in the active action slot. Only rotation keys inside affected hold/blend regions are replaced. Blender can recalculate unused handle coordinates of LINEAR neighboring keys; tests measure actual outside-interval motion and key values/interpolation separately. General preservation of user-edited Bezier tangents at new interval boundaries still needs dedicated coverage.

## Metrics

Contact drift before/after measures distance from the captured world point during the hold interval, normalized by the evaluated two-segment limb length in world units. Weighted target fitting error is reported separately: a half-strength correction can have near-zero fitting error while intentionally retaining half the original contact drift. Orientation fitting error is in radians. Reports include key/validation frame counts, refinement history and elapsed time including refinement passes.

## Retained development evidence

The following reports remain under training/b4artists_ml/results, with logs in the cache directory:

- contacts-v1: six tests passed at quarter-frame sample keys; intermediate motion acceptance was not yet covered.
- contacts-v2: ten tests, one failure from comparing unused automatic handles on LINEAR keys. contacts-v3 added evaluated outside-interval motion checks and passed all ten tests without discarding key-value/interpolation preservation checks.
- contacts-v4: twelve tests, one between-key failure (0.00022984 limb units versus the 0.0002 gate). Eighth-frame sampling and explicit midpoint validation were added; gates were not relaxed.
- contacts-v5: thirteen tests with recovery errors caused by a variable collision between the previous action and previous quaternion map. The variables were separated.
- contacts-v6/v7 and contacts-hand-v8: intermediate hand motion still failed, including after added keys. A target crossing the original pole could flip the selected bend direction.
- contacts-hand-v9 passed its two hand fixtures using a transported initial direction, but contacts-v10 then exposed a knee discontinuity approaching an authored anchor. A hand-only pass was insufficient.
- contacts-v11: all fourteen tests passed after using the input segment-plane normal, with a transported fallback only for nearly straight input limbs. No accuracy threshold or priority-pose requirement was loosened.

The exact package passes all fourteen contact tests and all 138 established regressions: **152 tests**, zero skips. There are 142 package-entry tests and ten source-adapter tests against runtime bytes identical to the ZIP. Twelve unchanged contextual training/data tests were not rerun. All twelve background processes passed assertions and then exited with the known shutdown violation; these are not clean host exits.

Package: releases/b4artists_ml_v0.10.0.zip, 26 files, 211,066 bytes. SHA-256: bd489b6bcf7354cb679f2dd5f78318e76b2694bff55c3345c1758ecd19376a98. ZIP integrity, Python syntax and source-byte equality pass. The 0.9 release and both bundled models are unchanged. Per-suite hashes, actual-rig measurements, retained development outcomes and UI evidence are recorded in checkpoint-contacts-v1.json.

Across the packaged crouch fixtures, actual held-contact drift and runtime are recorded below. These are single transformed-rig fixtures, not population-level quality or performance claims.

| Rig | Before drift | After drift | Solve seconds |
|---|---:|---:|---:|
| boneforge | 0.04323267 | 0.0001525495 | 1.91 |
| rigify_basic | 0.02696173 | 1.495795e-05 | 4.76 |
| rigify_default | 0.02696173 | 1.495795e-05 | 13.57 |
| metarig_basic | 0.0269618 | 1.472221e-05 | 0.89 |
| metarig_default | 0.0269618 | 1.472221e-05 | 2.18 |

Drift units are fractions of each evaluated two-segment limb length. Hand/orientation fixtures require extra local key refinement and can take substantially longer; see the report rather than extrapolating crouch timings to all clips. The partial-strength/offset fixture verifies retained half-strength drift separately from near-zero target fitting error.

The required router stopped before host application because the remote /mnt/x workspace was unavailable. No lane, policy fingerprint or patch was emitted. Native continuation followed the canonical recoverable-infrastructure policy within the declared project scope. No commit, push, installed-addon update, preference change, Ghost Tool edit or Anim Assist edit occurred. Tracked and staged Git diffs remain empty.


## Actual-window workflow

The exact 0.10.0 ZIP passed contact capture, modal correction, Escape restoring the preceding candidate, undo, redo, Keep and Restore Source through the real window event loop. The native screenshot was inspected: the selected contact, interval/strength/orientation controls, Preview Contact Correction and Restore Before Contacts are visible. Some labels are truncated at the narrow sidebar width, and lower non-contact actions require scrolling. This is fixture/UI evidence, not animator visual-quality acceptance.

On the default generated Rigify crouch, the solve took 17.78 seconds. The result used 81 sample frames and 161 validation frames across a ten-frame span, with two contacts and two preserved priority poses. Held-contact drift fell from 0.02696169 to 0.00001463 limb-length units. The 323 cooperative steps had p95 91.04 ms and maximum 106.22 ms. The event-loop scenario took 18.93 seconds; the complete host process took 25.18 seconds. These are single-scenario measurements, not cold/warm distributions or a general performance comparison.

The UI passed its assertions and then exited with the known ucrtbase.dll shutdown access violation (unsigned 3221225477 / signed -1073741819). Background assertions must likewise be distinguished from clean process exits. The installed host's shutdown problem remains unresolved.

## Remaining product scope

This advances contact correction for captured humanoid motion, but does not complete phase 3 or the full goal. Learned temporal motion/style, contacts conditioned into learned models, automatic support/COM/balance, gravity and momentum, secondary motion, moving-surface/collision handling, anatomical limits through time, production rig/mesh/proportion coverage, quadrupeds, the separate optional connector and equivalent Cascadeur/animator comparison remain required.
