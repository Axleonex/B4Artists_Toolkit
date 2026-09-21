# Jump temporal envelope comparison v1

## Purpose

The retained artificial BoneForge reconstruction passes sampled COM, contact and orientation constraints but contains localized hand-control speed and acceleration spikes. The recorded CMU `141_04` reference shows that foot channels can legitimately contain much higher acceleration than the upper body. This comparison determines where and when the artificial trajectory differs from the recorded reference before another solver is attempted.

## Frozen inputs

- Artificial result: `coupled-trajectory-reconstruction-v2/report.json`, including its unchanged pins at frames 1, 9, 15, 33, 39 and 49.
- Recorded result: exposed validation clip `141_04` and `recorded-jump-reference-v1/analysis.json`.
- Effective derivative spacing: artificial quarter frames at 30 fps and recorded whole frames at 120 fps both equal `1/120` second.
- Artificial phases: compression 9–15, clear flight 15–33, recovery 33–39.
- Recorded phases: preparation–clear takeoff, clear takeoff–clear landing, and clear landing–landing for each of the three detected jumps.
- Joint groups: upper body, legs and feet, and core. Exact source/control members are recorded in the result.

Quaternion differences use shortest-arc relative rotations. Angular acceleration is the finite difference of rotation-vector velocities at the common sample interval. Each phase and body group reports p95, p99, maximum, RMS, and the control/joint producing the maximum. Ratios compare the artificial values with the largest corresponding statistic among the three recorded jumps; they are diagnostics rather than acceptance thresholds.

## Decision rule

Proceed to a group-aware trajectory solver only if the comparison localizes an artificial excess by phase and group. Use reference percentiles to choose regularization priorities and line-search objectives, while keeping hard COM/contact/orientation constraints and every authored pin unchanged. If the artificial result does not materially exceed the recorded envelopes, stop treating rate magnitude as the principal failure and inspect discontinuity, timing, or visual semantics instead.

The recorded clip is one actor performing one motion family. It cannot establish population bounds, anatomical limits, force plausibility, visual quality, animator usability, or Cascadeur parity. No production code, model, release, source animation, or sealed confirmation data changes in this milestone.

Routing evidence is in `temporal-envelope-routing-v1.json`. The required router again failed before applying work with the known `uv` trampoline child-spawn error, so the static native fallback is recorded with project-local scope and deterministic validation requirements.

## Completed comparison

The equal-rate comparison found five material exceedances. The artificial upper body is the clear outlier: recovery reaches `8.93x` the recorded p99 speed and `11.39x` the recorded p99 acceleration, while compression reaches `1.73x` and `4.47x`. `hand.fk-R` produces each maximum. Compression core acceleration reaches `1.68x`. Clear-flight and the legs/feet do not trigger the diagnostic rule.

Three hard-projection metrics were then tested across the full 881-sample reconstruction. All preserve the published COM/contact/orientation gates and every authored pin. A uniform metric reproduces the baseline worst transition score of `15.8978`. A balanced `16x` upper-body penalty lowers it to `11.2043` (`0.7048x` baseline). Increasing distal penalties through `64x` worsens the score to `13.2806`, because global hand orientation inherits parent-chain corrections. Local coordinate weights alone cannot represent the visible hierarchy correctly.

The two boundary spikes occur in the quarter-frame intervals next to authored contact pins: `14.75 -> 15` and `33 -> 33.25`. The balanced projector amplifies the smooth source-path upper-body speed from `31.62` to `62.25 rad/s` in compression and from `31.74` to `62.37 rad/s` in recovery. A world-orientation-aware metric returns both boundaries to within `0.01%` of the source speed while remaining inside the published final spatial gates. It misses the stricter internal `2e-5` knot target because contact error settles around `4.6e-5` to `5.4e-5`; this negative strict-gate result remains recorded.

The source-relative result matters. Compression's source speed is `0.87x` the largest recorded upper-body speed for that phase, while the artificial recovery source is already `4.56x` the corresponding single-clip envelope. Forcing recovery down to the recorded value would change the stress request's authored timing or pose intent. The next solver must minimize correction amplification relative to the authored source, with recorded phases informing group weights rather than overriding artist inputs.

No method is promoted. The next bounded experiment is a coupled boundary-window SQP with source-relative upper-body world-orientation residuals, explicit endpoint and pin anchors, and unchanged final spatial gates. Full-trajectory acceleration, visual quality, other motions/rigs, learned behavior, forces, animator usability, and Cascadeur comparison remain unqualified.
