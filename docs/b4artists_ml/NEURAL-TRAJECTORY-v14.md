# Learned nonlinear trajectory features v14

Result: reproducible trained neural model, rejected quality. Runtime/package 0.16.1 and both bundled pose models remain unchanged. The full product and comparative goal are incomplete.

## Experiment and verification

The prospectively frozen four configurations use the existing local NumPy tanh/Adam infrastructure: 64/128 learned hidden units, 612 temporal coefficient outputs, weight regularization 1e-5/1e-4, forty epochs, batch64 and learning rate 0.001. Output weights start at zero, giving the known-pose baseline. Each training fold independently fits normalization; standardized motion features are clipped at eight units. The verified trajectory loss includes rotation6 coordinate error, velocity 0.01 and acceleration 0.0001. It is a surrogate loss, not dynamics-aware or geodesic training.

Five new tests verify compressed loss against explicit generated trajectories, finite-difference gradients for every network parameter family, actual hidden-feature learning with zero regularization, objective reduction, exact priorities, hidden-label isolation, reproducibility and invalid serialization/training inputs. All five pass on desktop and in Bforartists. The six focused host suites total 42 passing cases. A passing synthetic learning test is not evidence of motion quality.

The same four catalog-prefix-excluded training folds select trial3 (128 units, regularization 1e-4). The chosen specification is refit on all 2912 training windows, and its weights/hash are frozen before loading the 480 validation windows. No new data or confirmation partition is read. Validation has historical research exposure; catalog groups are not proven independent actors. Every projected control metric exactly matches v12.

The complete independent rerun reproduces all 18 NPZ artifacts and every non-runtime report field exactly. Selected learned SHA: `c35ff72970b0b836b07d9e3a21f301609bd6f28a57ee8519ad86d4cc96fb4d01`. All frozen source hashes remain exact. See `results/neural-trajectory-reproduction-v14.json`.

## Quality and generalization

| Quantity | Result |
|---|---:|
| Projected validation position | 0.11771930 |
| Position ratio to best projected control | 1.2582 (fails required <=0.95) |
| Rotation ratio | 1.2947 (fails <=1.02) |
| Velocity ratio | 1.3256 (fails <=1.05) |
| Acceleration ratio | 1.3034 (fails <=1.05) |
| Worst cohort position ratio | 8.4822 (fails <=1.1) |

Endpoints and true physical-edge invariants pass. The procedural Hermite control wins the combined validation score. V13's learned position ratio 1.0239 remains better than this v14 candidate, but v13 is also unqualified. There is no model or acceptance promotion.

On the same training-window inventory, the full-fit neural raw position error is 0.13355 versus linear 0.19333 and Hermite 0.17332. Excluded-group neural predictions instead reach 0.23861. This supports a fitting-versus-transfer problem; adding capacity did not solve generalization. The largest absolute excluded-group regressions include contextual 32-frame intervals in 90_02, 13_01 and 13_29. `results/neural-trajectory-diagnostic-v14.json` retains aggregate, gap/context and cohort details. These diagnostics use training data only and do not retune the frozen experiment.

## Concrete stationary-motion defect

A separate controlled diagnostic repeats one observed training pose per clip across both priorities and both context slots, for 8/16/32-frame gaps with/without context. This produces 186 input cases per model, using no hidden labels. It checks proposed motion before physical projection.

| Frozen model | Maximum position drift (normalized coordinates) | Median case maximum | Maximum rotation drift (radians) |
|---|---:|---:|---:|
| V12 RBF | 0.66498 | 0.06769 | 0.75130 |
| V13 trajectory RBF | 0.14581 | 0.01597 | 0.15255 |
| V14 neural | 2.34298 | 0.12499 | 3.11461 |

All three models can invent movement even when every observed pose is unchanged. This is a concrete authored-intent failure, independent of the aggregate validation result; it does not by itself explain every failure. See `results/stationary-anchors-v14.json`. These are controlled diagnostics, not new acceptance claims or hidden-label oracles.

Next work should condition learned residual magnitude on actual observed positional/angular change and context velocity, with exact stationary preservation and continuous behavior as observed motion approaches zero. Train and evaluate the conditioned representation prospectively, rather than merely clipping a failed model after looking at validation. Preserve known priorities, context masking, training-only design selection, physical projection, all original quality gates and historical holdout exposure. Explicit cyclic or stylistic intent remains part of the wider workflow; identical observations alone cannot identify an unobserved loop.

## Actual rigs and remaining scope

The exact frozen neural artifact produced editable candidate actions on all eight authored fixtures: BoneForge, basic/default generated Rigify, basic/default metarigs, Mocap, Unity and Unreal. All priority and source-restoration checks passed. The controlled stationary diagnostic above was not run through these rig fixtures; it tests proposals only. One-run generation/preview/discard timings were 0.62-3.62 seconds and are not comparative latency evidence.

Bforartists again returned shutdown access violation 3221225477 after the assertions. Host lifecycle remains unqualified. Existing 303 native / 110 offline / two packaged-window evidence applies to unchanged runtime/package bytes and was not rerun here. No release, install, commit or push occurred; Ghost Tool and Anim Assist are unchanged.

Evidence paths under `training/b4artists_ml/`: `results/neural_trajectory_v14/`, `results/neural_trajectory_v14_repeat/`, `results/neural-trajectory-native-v14-regression.json`, `results/neural-trajectory-host-v14.json`, `results/neural-trajectory-host-v14-process.json`, and the diagnostic/reproduction files cited above.

The original learned motion, multi-priority/partial-body/style/contact integration, physics/refinement, production rigs/quadrupeds, distribution rights, performance/resources, optional connector and independent animator/Cascadeur comparison remain unmet. No full implementation milestone is credited for this rejected experiment.
