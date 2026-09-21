# Procedural Quadruped Gait-Phase Review v1

Development 0.35 adds a read-only support-phase review to **Four-Paw Contacts** for generated Rigify cat, horse, and wolf rigs. It derives exact support intervals from animator-accepted paw contacts and labels only the support set that those contacts prove. It does not infer or generate motion.

## Workflow

1. Generate or select a compatible Pose Blending candidate on a generated Rigify cat, horse, or wolf.
2. Capture, accept, or edit the four-paw contact intervals until they describe the intended contact schedule.
3. Open **Four-Paw Contacts** and click **Analyze Gait Phases**.
4. Review the current interval, support label, and supporting paws. Use **Previous Phase** and **Next Phase** to move through the report.
5. Click **Clear Phase Report** when the contact schedule should be revised.

Navigation moves the playhead to the midpoint of each open phase interval. That avoids ambiguous closed contact endpoints and makes the evaluated contact weights agree with the displayed support set. Navigation revalidates the candidate action and accepted contacts before moving the playhead.

## Labels and claim boundary

The report uses `FLIGHT`, `SINGLE_SUPPORT`, `DIAGONAL_SUPPORT`, `LATERAL_SUPPORT`, `FORE_SUPPORT`, `HIND_SUPPORT`, `TRIPLE_SUPPORT`, and `FULL_SUPPORT`. These are conservative support-set descriptions. The tool does not label walk, trot, pace, canter, gallop, lead, cadence, intent, naturalness, or quality because accepted contact intervals alone do not establish them.

This feature is procedural contact-schedule review. It does not contain a learned model, infer contacts, edit curves, change the pose, generate a gait, apply dynamics, or establish Cascadeur parity. Imported and custom quadruped adapters remain outside this qualification.

## Safety and persistence

Analysis reads the animator-accepted contacts, priority-pose range, current candidate action, and generated-Rigify quadruped adapter state. It stores only a compact JSON report and current phase index on the armature. The strict path rederives the phase table and rejects stale or malformed state, changed contacts or anchors, changed/replaced actions, active playback, and active solve/preview jobs before navigation.

The action binding includes same-session identity plus a complete bounded digest of action, curve, key, sample, modifier, Envelope, ActionGroup, slot, layer, strip, and channel-bag state. Save/reload is supported through the content digest; same-name action replacement in the same session is rejected. Limits are 32 accepted contacts, 128 phases, the existing action-point budget, 1,024 modifiers, and 4,096 Envelope control points.

## Performance and evidence

The explicit **Analyze Gait Phases** action took 110.29–112.35 ms on the recorded cat, horse, and wolf fixtures. Lightweight display validation used by panel redraw stayed below 5.03 ms. Previous/Next uses the strict validation path because it changes the playhead.

- Focused Bforartists tests: 5/5. Report: `training/b4artists_ml/results/quadruped-gait-phase-v1.json`, SHA-256 `df0aff05b2041a09b73bd2dc4a90ca5622637491048e5aaf580bf6fe8ca0bd7c`.
- Affected regression: 98/98 across 13 suites and one 44-file runtime set. Report: `training/b4artists_ml/results/quadruped-gait-affected-v1-regression.json`, SHA-256 `9f0613359aec59316998d4ccf57c148c63ea1a9e2b98b6f0e404d73902548eec`.
- Foreground Bforartists journey: passed Analyze and fractional midpoint navigation with unchanged source action and contacts. Report: `docs/b4artists_ml/quadruped-gait-phase-ui-v1.json`, SHA-256 `5912aaf89b87bcccbeaca97d48dfd8040c7d47251e1bf21688d7f57641caa489`.
- Screenshot: `training/b4artists_ml/cache/quadruped-gait-phase-ui-v1.png`, SHA-256 `8495fa99f7abe0ecf87bfd0236bd22866ec3fc14afbcb79112846ead06705ea3`.
- Final evidence manifest: `training/b4artists_ml/results/quadruped-gait-v1-final.json`, SHA-256 `48fd1380949b368e1897664b3bc78a60ad088c18ab0651df5eb22db9a89f2c8a`.
- Final serial read-only reviewer: PASS with no actionable findings.

The Bforartists 5.2 Alpha process completed all assertions and evidence writes, then hit the known `ucrtbase.dll` `EXCEPTION_ACCESS_VIOLATION` during shutdown (`3221225477`). This evidence does not claim a clean host exit.

The coding router failed before emitting a T0–T4 lane because its `uv` trampoline could not spawn the Python child. The owner verifier also lacked `rfc8785`. Work therefore followed the recorded `DEGRADED_NATIVE_CONTINUE` path with one writer and serial read-only review; no activation, authorization, commit, merge, push, package, or production state changed. See `quadruped-gait-phase-routing-v1.json`.
