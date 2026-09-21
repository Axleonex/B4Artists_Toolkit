# Recorded jump reference v1

This milestone uses only CMU clip `141_04`, already exposed in the frozen validation split and described by the pinned catalog as “Jump Distances.” It does not open the six sealed confirmation clips, download data, alter a split, fit a model or modify the add-on. The source BVH remains excluded from installable packages under the existing data policy.

The analysis uses the BVH Y axis as vertical and normalizes distance by mean left/right hip-to-ankle chain length in the artificial calibration pose. Four observed sites—both ankles and toe bases—receive independent robust floor estimates from the second percentile of their height over the clip. A confirmed clear-flight span requires every site to exceed its floor by 0.05 leg lengths. Candidate spans are retained only when they last 0.12–0.25 seconds and pelvis height rises at least 0.15 leg lengths above the lower boundary. These are reproducible motion phases, not force-plate contacts.

For each clear-flight span, the preparation and landing observations are the local minima of four-site clearance during the preceding/following 15 frames. The pelvis apex is the highest pelvis frame between those observations. Record ankle/toe displacement and lower-limb rotations through the five phases; estimate the current add-on mass model’s center of mass from the mapped BVH joints. Preserve the exact source frames at 120 fps.

Generate a local Bforartists review scene through the host’s built-in BVH importer only after the analysis succeeds. Normalize imported scale by the same leg length, retain the editable action and all source frames, add phase markers and a provenance text block, and verify mapped joint positions against the independent parser at multiple frames under one fixed axis transform. This does not prove production-rig retargeting, twist fidelity, visual quality or Cascadeur parity.

Limits: source file below 8 MB, generated blend below 64 MB, one analysis pass and one serial host import, 1,000-second host timeout, original goal deadline `1789053845`. No automatic fit or data replacement follows. The full goal remains active at checkpoint 68/100 with unchanged requirements and release 0.19.2.

Routing evidence is in `recorded-jump-routing-v1.json`. The required router failed before application with the existing `uv` trampoline spawn error. The static native policy permits project-local continuation after that recoverable pre-apply failure; the explicit fallback receipt records eligibility, scope and required validation.

## Completed evidence

The independent parser identified three major distance jumps. Their phase rows are preparation / clear takeoff / apex / clear landing / landing at source frames `70/78/88/98/102`, `210/222/233/244/248`, and `376/391/401/412/419`. The estimated clear-flight vertical COM accelerations are `-53.0766`, `-53.1081`, and `-53.4270` leg lengths per second squared. Their range is `0.3504`, while the maximum constant-acceleration fit residual is `0.01191` leg lengths. These are kinematic estimates from the current artist-default COM model.

The generated Bforartists scene preserves all 548 source frames at 120 fps and exposes 15 timeline markers. The Blender 5.2 layered Action contains 127 F-curves and 548 unique keyed frames. Across 17 endpoint and phase frames, a single fixed rigid coordinate mapping agrees with the independent BVH parser within `6.65e-7` leg lengths; pairwise joint distances agree within `3.71e-7`. The saved `.blend` is 461,072 bytes and remains a local research artifact.

The first host attempt imported the motion but failed validation because the checker assumed the legacy `Action.fcurves` API. The corrective attempt used the host's layered Action/channel-bag API and completed before the known `ucrtbase.dll` shutdown crash. Both attempts preserved production add-on sources. This is recorded rather than hidden.

The recorded-motion comparison rejects a single global angular-acceleration ceiling. Foot channels in the source reach `48.99 rad/s` and `5951.27 rad/s^2`, while the recorded upper-body maxima across the three jump windows are `36.25 rad/s` and `1086.34 rad/s^2`. The retained artificial reconstruction's hand-control rates near takeoff reach roughly `98 rad/s`, and its quarter-frame hand acceleration estimate exceeds `6000 rad/s^2`. The next temporal solve should therefore compare phase-normalized distributions by joint group and penalize localized upper-body spikes; it must not classify all high-frequency foot motion by the same ceiling.

This milestone supplies a realistic calibration reference. It does not qualify interpolation, learned prediction, retargeting, contacts, force plausibility, animator usability, or comparison with Cascadeur. The sealed confirmation clips remain unopened, the experimental `0.19.2` package remains unchanged, and no solver result was installed or released.
