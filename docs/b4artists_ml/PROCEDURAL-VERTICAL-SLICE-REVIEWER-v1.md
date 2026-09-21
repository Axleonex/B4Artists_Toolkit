# Procedural vertical-slice reviewer v1

The frozen 32-case procedural humanoid slice now has a dependency-free, blind human-review packet at `training/b4artists_ml/results/procedural-vertical-slice-reviewer-v1/reviewer.html`. It compares the saved pre-contact candidate with the saved corrected candidate for every combination of BoneForge, generated Rigify basic/default and imported Unity-style rigs with reach, crouch, walk, run, jump, land, turn and difficult-transition tasks.

This artifact makes the required animator assessment executable. It does not supply that assessment. `reviewed_cases` remains zero and no human quality, usability or Cascadeur claim has been credited.

## Frozen source and display

- All 32 `.blend` files and case reports match procedural vertical slice v12 by SHA-256.
- Each variant contains 49 evaluated samples from frames 1 through 25 at half-frame intervals.
- Each sample uses the certified 17-joint semantic adapter rather than name-only inference.
- The two variants retain every displayed priority pose exactly; maximum component difference is zero after seven-decimal display serialization.
- A/B placement is deterministically balanced: corrected output is A in 16 cases and B in 16.
- Both candidates use one camera, scale, timeline, floor and contact display per case. Front, side and oblique views, priority ghosts and pelvis trails are available.

Method identity and automated v12 measurements stay hidden until the reviewer locks a case. A locked rating cannot be edited within that review session. Moving to an unrated case hides the preceding reveal. This reduces order and metric bias while retaining traceable source actions after judgment.

## Required human fields

Every case requires 1-5 scores for naturalness, contact stability, transition continuity and intent preservation for both candidates. The reviewer must also record production acceptability, estimated corrections, estimated interactions, overall preference and any visible failure tags. Notes are optional. Export remains disabled until all 32 cases are locked and a reviewer ID plus animation-experience category are present.

The resulting `b4ml-procedural-vertical-slice-human-review-v1.json` is bound to the review-data, aggregate, protocol and source-scene hashes. `check_procedural_vertical_slice_human_review_v1.py` validates a completed export and creates a method-unblinded summary without treating the result as a Cascadeur comparison or full-goal completion.

## Validation evidence

`manifest.json` records 32 cases, 2 variants and 3,136 displayed skeleton frames. Its review-data SHA-256 is `7f5dbcaa0c8a1e0b7f7e862fb3bbbb590be5725a418c2b22d386f46f5d3bd709`; the standalone HTML SHA-256 is `a88b2a225b33e8594ae974904f27680dda64e2826b92fb696bb3409d31d5f57e`.

`validation.json` verifies exact scene/report hashes, protocol order, deterministic page composition, finite 49-by-17-by-3 samples, balanced blinding, priority equality, required rating/export controls, no external resources and valid embedded JavaScript.

`browser-interaction-validation-v2.json` exercises the local file in Edge 152.0.4191.66 through an isolated temporary profile. The page initialized all 32 cases and both canvases; playback advanced; the BoneForge filter returned eight tasks; incomplete export was blocked; a synthetic case locked before reveal; navigation hid identity on the next unrated case; state persisted across reload; and no uncaught browser exception occurred. The synthetic rating was destroyed with the temporary profile and is explicitly not human evidence. `browser-interaction-smoke-v2.png` records the rendered locked state.

The first extraction attempt for BoneForge run assumed the hidden source armature had to belong to a visible view layer. Native motion layers intentionally exclude that source. The failed report/log are retained, and the resumed extractor evaluates through the visible motion-layer owner. All host processes wrote complete case data before the already documented post-result `ucrtbase.dll` shutdown crash; none is described as a clean host exit.

## Remaining gate

An independent animator must open the reviewer, complete all 32 locked judgments and provide the exported JSON for validation. The skeleton display does not show mesh deformation, axial twist or collision surfaces. A separate hands-on timed Bforartists pass is still needed for measured correction effort and UI usability, and equivalent Cascadeur tasks remain unverified.
