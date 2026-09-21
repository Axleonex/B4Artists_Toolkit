# Boundary-window trajectory experiments v1

## Purpose

The grouped upper-body metric reduced the artificial BoneForge jump's worst recorded-envelope ratio, but sharp corrections remained next to the contact pins. This milestone tested source-relative world-orientation objectives around those boundaries while preserving the six authored trajectory pins and the published COM, contact, and orientation gates.

The corrected two-sample probe is `world-metric-boundary-v2`. It supersedes the state-frame-invalid v1 probe. With world-orientation strength `1000`, compression speed returns from `62.2516` to `31.6248 rad/s`, and recovery returns from `62.3671` to `31.7388 rad/s`. Both candidates pass the published final gates. They miss the stricter internal knot target, and the probe does not establish full-trajectory feasibility.

## Full-window results

| Experiment | Dense spatial gate | Quarter-rate score | Finding |
|---|---:|---:|---|
| SQP v3 | Pass | 11.1940 | Correct implementation, but only `0.09%` better than grouped16. |
| SQP v5 | Fail | 11.0414 | Per-knot restoration improves timing but breaks interpolated spatial constraints. |
| SQP v6 | Fail | 9.0832 | Reaches a `19%` score improvement but leaves 24 dense spatial failures. |
| Adaptive Hermite v7 | Fail | 9.0832 | Added knots move and multiply the failures rather than converging. |
| Linear v8 | Fail | 9.0832 | Reduces failures to 18, proving Hermite overshoot is only part of the defect. |
| Linear convergence v9 | Fail | 9.0832 | Six refinements plateau at 18 failures concentrated around four pre-existing knots. |
| Linear continuation v10 | Pass | 9.0832 | Strong local branch continuity clears 1,385 spatial checks, but piecewise linear output is not an animation-quality curve. |
| Limited C1 continuation v11 | Pass | 9.0832 | Clears 1,461 spatial checks after four refinements and preserves every authored pin exactly. A stricter temporal audit rejects it. |
| Fixed lattice v12 | Fail | 9.0832 | Keeps 221 output knots and adds none, but its first distributed correction cannot improve the strict gate. |
| Fixed lattice merit v13 | Fail | 7.6873 | Aggregate violation falls over six passes, while failures spread from 24 to 61 and remain up to about `4.9x` gate. |
| Fixed lattice continuation v14 | Fail | 7.6871 | Reduces failures from 61 to 57 once, then line search plateaus with COM `0.000596` and contact `0.000983`. |

The v11 spatial maxima are `0.0001766` COM, `0.00019947` contact, and `0.0004922` orientation, inside unchanged limits of `0.0002`, `0.0002`, and `0.001`. The host completed its assertions before the independently reproduced Windows shutdown crash (`3221225477`). Production sources, release files, source animation, priorities, and sealed confirmation data were unchanged.

## Hidden temporal regression

The original temporal report samples quarter frames, equivalent to `120 Hz`, but v11 serializes adaptive keys between those samples. The independent interval audit found a minimum key spacing of `0.001953125` frame. Across one such interval, `shin.fk-R` reaches `502.0180 rad/s`, `7.0617x` the grouped16 global maximum. Its worst derived acceleration is `3,755,469.94 rad/s^2`, `70.1936x` the grouped16 maximum.

This invalidates the apparent `19%` improvement. A C1 curve can still contain severe acceleration when it follows densely packed corrections. Passing at knots or at a fixed sample rate is insufficient when the solver is free to insert output keys between those samples.

## Decision

No boundary-window method is promoted. Grouped16 remains the retained research baseline because it passes its sampled spatial checks without the newly demonstrated subinterval regression.

The fixed-lattice representation is still required: adaptive interval samples may identify constraint violations, but they must remain constraints and must not become output keys. Versions 12 through 14 show that local least-squares correction distribution is insufficient. Further boundary tuning is deferred until the solver can use cached spatial Jacobians with a true nonlinear active-set or augmented-Lagrangian formulation. Frames `1`, `9`, `15`, `33`, `39`, and `49` must remain exact, and acceptance still requires unchanged spatial gates plus quaternion speed and acceleration checks across every output interval. More local penalty and line-search variants are not justified by the plateau.

Machine-readable evidence is in `training/b4artists_ml/results/boundary-window-trajectory-summary-v1.json` and `training/b4artists_ml/results/boundary-window-c1-audit-v1/report.json`. Routing evidence is in `boundary-window-fixed-lattice-routing-v1.json`; the required local Prime router returned no lane because the available WSL runtimes lacked either Python or `jsonschema`, so reversible project-local research continued under the recorded fallback scope.

This milestone covers one artificial BoneForge jump and three recorded jumps from one actor. It does not qualify learned behavior, physical forces, visual quality, animator usability, other motions, Rigify, quadrupeds, or Cascadeur parity.
