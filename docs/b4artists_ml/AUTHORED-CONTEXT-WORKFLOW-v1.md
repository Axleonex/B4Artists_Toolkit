# Authored context workflow experiment v1

Evaluation 52 preparation, 2026-09-09. Original full goal and 75 total evaluation ceiling remain. This is a procedural research workflow, not a trained temporal model, product promotion, or Cascadeur comparison.

## Result

The same controlled standing/crouch/recover fixture now passes authored interpolation, explicit foot contacts, editable preview, native save/reload, Discard, and Keep/Restore Source on BoneForge and basic/default generated Rigify humanoids. Source data and the authored priorities remain preserved. This does not qualify broader motion quality or the complete humanoid product milestone.

| Experiment | Pelvis vertical range | BoneForge contacts | Basic Rigify | Default Rigify |
|---|---:|---|---|---|
| Original source-neighbor Hermite | about 0.338 | Reject | Reject | Reject |
| Authored position tangents, original source rotation tangents | about 0.150 | Reject | Pass | Pass |
| Authored position tangents, authored endpoint SLERP | about 0.150 | Pass | Pass | Pass |

Intended authored range is about 0.150. Position tangents alone remove the observed overshoot. Changing the rotation comparator removes the remaining BoneForge failure in this scene. This is evidence of sensitivity to the mismatched source context, not proof that every limb branch failure shares one cause.

The unchanged contact gate is position drift <= 0.0002 of evaluated two-segment limb length and orientation error <= 0.001 radians. Adaptive refinement remains capped at four. Passing generation maxima: BoneForge 0.0001483464; basic/default Rigify 0.00005549225. No limits were relaxed and no failed result was published as a corrected candidate.

Fresh processes reopened all three successful saved scenes. All 21 integer-frame joint samples match the saved report exactly. A separate fixed 321-time grid checked 642 foot contacts per rig, with maximum drift 0.0001032554 on BoneForge and 0.00005549225 on each Rigify rig; measured foot orientation error was zero. This reload grid is coarser than the adaptive generation check, so its lower BoneForge maximum is not an improvement claim. Discard and Keep/Restore Source both preserve original action curves and input rig modes after reopening. The source blend files remain byte-identical.

## Implementation and validation

`training/b4artists_ml/authored_context_v1.py` uses all authored endpoint positions, nonuniform interval durations, harmonic interior slopes, and a fixed first-pose body basis. Extremum slopes are zero; repeated priorities remain fixed. Endpoint slopes use their interval secants. The position curve is procedural PCHIP-style interpolation with no trained parameters. SLERP rotations are explicitly procedural and may have velocity discontinuities at priorities; whole-body projection and contact fitting may also change motion derivatives.

`temporal_authored_cooperative_v1.py` is an isolated research variant of the preserved cooperative source. It gathers observations through the existing transaction sampler before invoking a preparation factory, then passes explicit interval indices to the returned provider. This avoids ambiguous pose matching or hidden call counters. Existing source/anchor/rig guards, cancellation, ownership cleanup, lifecycle hooks, and final candidate publication checks remain.

Eight numerical behavior tests pass both in local Python and native Bforartists: exact priorities, no crouch overshoot, nonuniform timing and repeated poses, source-neighbor isolation, common rigid-transform/uniform-scale equivariance, rejected invalid inputs, shared-anchor consistency, and unchanged source-rotation comparator. Eight native lifecycle tests pass: source-visible preparation and editable completion, close during sampling and after preparation, intervening anchor/source edits, host lifecycle cancellation, invalid preparation result, and injected preparation failure.

The first source-curve edit test compared against stale pose channels before dependency evaluation. Its failed report and original test source are preserved. The revised test first evaluates the edited source curve, then checks that rejection preserves that actual visible state. No runtime change was made to satisfy this test.

All native processes report the already separately reproduced ucrtbase shutdown access violation after recording their assertions. Assertion completion and process exit are recorded separately. No host crash mask or host replacement was used.

## Limits and next work

- One controlled crouch/recover fixture per rig; no bound production character meshes or independent animator rating.
- Authored SLERP does not establish rotational velocity continuity, learned motion, stylistic preservation, or quality on turns/walk/run/jump/landing.
- The research comparison still samples source neighbors even when SLERP discards them. An authored-only sampler and product-facing scheduling integration remain to be validated.
- Responsiveness is not qualified. Tick outliers exceeded one second in two runs, and default Rigify p95 exceeded 90 ms. Runs partly overlapped short regression tests; these are observations, not isolated speed comparisons.
- No new add-on controls, shipped temporal model, installed build, Git history change, or package promotion. The existing 0.17.5 ZIP remains unchanged and does not include the prior worktree contact-key fix.
- Formal goal assessment remains unknown because authenticated host assessment envelopes are unavailable. Previous quality floors, endpoint, history, deadline, and all deferred requirements remain intact.

Evidence: `training/b4artists_ml/results/authored-context-comparison-v1.json`, both `humanoid-workflow-review-v5-*` directories, `authored-review-reload-v1`, and `authored-context-v1*-regression.json`.

Successful native scene files are under `training/b4artists_ml/results/humanoid-workflow-review-v5-slerp/{boneforge,rigify_basic,rigify_default}/`. They contain editable animation and a READ ME text; no auto-executed scripts.
