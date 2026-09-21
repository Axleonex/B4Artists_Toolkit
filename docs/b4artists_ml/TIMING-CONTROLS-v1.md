# Interpolation Timing Controls v1

Status: implemented and verified on development source; not packaged.

## Animator workflow

Under **Generate and Review**, choose **Pose Blending**, then select Uniform, Ease In / Out, Ease In, or Ease Out. **Breakdown Bias** shifts the apparent transition midpoint while every captured pose remains on its authored frame. Negative values arrive later; positive values arrive earlier. The setting applies independently inside every adjacent pair of captured poses, so a multi-pose sequence keeps each priority pose exact.

Generate the interpolation preview, scrub it, then Keep or Discard through the existing copied-action workflow. Deterministic candidates store the selected easing and bias as Action metadata so their timing provenance remains inspectable. Projected whole-body samples already own their timing; the publication API rejects a non-neutral bias and removes inherited deterministic timing metadata from projected candidates.

## Math and boundaries

The bias control is bounded from -1 to 1. A rational, monotonic remap moves the raw midpoint from 0.1 through 0.5 to 0.9 across that range while preserving exact 0 and 1 endpoints. Uniform uses the remapped value directly. Ease In / Out applies smoothstep; Ease In uses a quadratic start; Ease Out uses a quadratic arrival. Location, scale, and shortest-path rotation all use the same weight.

This is deterministic timing assistance. It does not learn timing, infer intent or style, change pose frames, edit a source Action, add per-transition settings, or satisfy the learned-inbetweening and Cascadeur-comparison requirements.

## Verification

- Focused Bforartists tests: 7/7. They cover all four timing shapes, endpoint and monotonic bounds, exact midpoint bias, multiple intervals, authored-pose preservation, bounded Action/AnimData structure recovery, invalid input, projected-sample separation, stale-metadata removal, Action provenance, UI operator execution, and save/reload. Report: `training/b4artists_ml/results/timing-controls-v1.json`, SHA-256 `8dd546a63d0891716aa04185ffd761cf8ee2a51d48c98056c6084ba1d5c8f426`.
- Affected regression: 143/143 across 19 suites and one frozen 44-file runtime set. Report: `training/b4artists_ml/results/timing-controls-affected-v1-regression.json`, SHA-256 `36e8fb11a50fa138ec04e6cafcd2dcef56815254475a05fa4f83765dd2955b28`.
- Foreground Bforartists journey: passed visible Ease Out / -0.50 preview, expected midpoint, Discard, source Action identity, and the bounded Action/AnimData structure digest. Report: `docs/b4artists_ml/timing-controls-ui-v1.json`; its final hash is bound by `timing-controls-v1-final.json`.
- Screenshot: `training/b4artists_ml/cache/timing-controls-ui-v1.png`, SHA-256 `f154b49d51a41e8f955247c761e61f79bc7f2fcbd97a8e40db0c0be202045158`.

Every host assertion and evidence write completed. The affected processes and foreground host then followed the known Bforartists Alpha `ucrtbase.dll` shutdown-fault path, so clean shutdown is not claimed.

## Routing and review

The required coding router was invoked for this assignment but its `uv` trampoline failed before emitting `actual_lane`. Live production-authority verification also remains unavailable because the configured verifier environment lacks `rfc8785`. Work therefore continued as `DEGRADED_NATIVE_CONTINUE` with one parent writer and one serial read-only reviewer. The reviewer found inherited stale timing metadata on projected candidates; the final source removes it and the new regression proves the original source metadata remains unchanged. Final review passed. No activation, provider, model, service, package, version, commit, merge, push, Ghost Tool, or Anim Assist state changed.
