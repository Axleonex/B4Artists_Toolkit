# Priority continuity: shape-curve research

The existing 0.18.0 runtime and archive remain unchanged. This experiment addresses observed root and rotation velocity jumps after integer-frame baking. It is procedural, not learned motion, and does not qualify the complete animation workflow or Cascadeur parity.

## Result on the same three humanoid crouch scenes

Changing only final corrected curves breaks the original contact gate on every rig: maximum drift is 0.000835 limb units on BoneForge and 0.000717 on Rigify, above 0.0002. This rejected order is retained.

Smoothing the body curves, correcting contacts, then smoothing the corrected curves passes 2,562 contact checks per rig at 1,281 sample times. Every authored priority matrix matches exactly. At the same 0.015625-frame derivative probe around the middle pose:

| Rig | Original angular-velocity jump, rad/s | Refined jump, rad/s | Refined contact drift, limb units |
|---|---:|---:|---:|
| BoneForge | 0.4140473 | 0.0135619 | 0.000115787 |
| Basic Rigify | 0.3719997 | 0.0121081 | 0.000038006 |
| Default Rigify | 0.3719997 | 0.0121081 | 0.000038006 |

This is about 96.7% lower local angular-velocity change. Pelvis velocity change drops from about 0.17356 to 0.004175 world units/second, about 97.6%. The finite differences shrink with probe size, consistent with the intended continuous tangents. These numbers are local diagnostics; they do not prove full-sequence continuity or visual quality.

A separate run with the bounded implementation reproduces contact, priority, pelvis-range, and derivative results exactly on all three rigs. Original actions, anchors, and saved source scenes remain unchanged. Accepted research candidates are saved under `training/b4artists_ml/results/shape-curve-workflow-v2/`; rejected candidates were not saved as accepted results.

## Implementation and preservation

Scalar harmonic tangents leave every key coordinate fixed, avoid scalar overshoot, and use a common incoming/outgoing derivative at each interior key. Adjacent quaternion samples must have positive dot products; this provides a same-sign nonzero component over each scalar-monotone interval and avoids a zero quaternion when normalized. Opposite signs/turn ambiguity and axis-angle channels are rejected for now, not silently rewritten.

Eight numerical checks pass: fixed samples, monotone bounds, shared derivatives, flat intervals, two-key linearity, time transformations, invalid inputs, and quaternion nonzero behavior. Seven native checks pass for exact keys, untouched source action and unowned channels, Free/Auto-Clamped handles outside the selected span, guarded rejection, and saved/reloaded boundary behavior.

The first bounded implementation incorrectly checked unused outside handles even where no neighboring span existed. Correcting that scope exposed a real automatic-handle issue: calling `handles_recalc()` moved an unowned boundary handle. The final research version writes only the owned Free handles and does not recalculate unrelated Auto handles; key coordinates/order are unchanged. Native outside-span samples and save/reload remain exact. Failed v2/v3 tests and their original sources are retained.

## Limits and next work

- One controlled crouch/recover motion per rig; reach/hold, root-turn transitions, different timings and real character motions need broader coverage.
- Isolated numerical checks do not establish joint-limit safety, collision avoidance, automatic contacts, style, or learned motion.
- No runtime promotion, new package, installation, Git history change, or human visual rating in this milestone.
- Any integration must apply smoothing before contact correction and validate the final smoothed result. Smoothing an already corrected candidate alone is rejected by the observed drift results.
- Preserve the source, adjacent animation, authored keys, original contact tolerances, and normal cancellation/lifecycle behavior. Additional continuous-time guarantees remain open.
- Native assertions completed before the known host shutdown access violation; clean host termination is not qualified.

Evidence: `shape-curve-comparison-v1.json`, both `shape-curve-workflow-v*` directories, `shape-curve-v2/v3/v4-*-regression` reports, and their source/test files. The full goal remains active with the same 75 total evaluations and existing deadline.
