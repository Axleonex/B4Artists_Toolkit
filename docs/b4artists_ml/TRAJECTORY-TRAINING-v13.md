# Trajectory-space learning v13

Research result: improved over v12, still rejected by unchanged quality gates. No runtime/package or bundled-model change. The full standalone/Cascadeur comparison goal remains incomplete.

## What changed and why

V12 predictions were already inaccurate before rig projection; coefficient MSE barely improved despite large representable trajectory capacity. V13 therefore learns the same 667-observation/17-joint/four-coefficient predictor by minimizing generated trajectory errors directly. It solves a coupled quadratic normal system over all four coefficients, preserving each window's physical duration and uniform sampling dt. Optional first and second finite-difference error terms penalize velocity and acceleration errors. Rotation6 coordinate error remains a linear chordal surrogate, not geodesic or physics-aware training.

The four prospective ablations use the existing 128-center motion RBF, width 1.5, regularization 0.001/0.01, and either position/rotation6 only or velocity 0.01 plus acceleration 0.0001. No widths, centers or gate thresholds were tuned against validation. Four complete catalog-prefix-excluded folds inside the 2912 training windows select one specification. Each fold fits its own normalization and centers only on its training subset. Catalog groups are not asserted to be independent actors.

Trial 3 (regularization 0.01 with both derivative terms) won pooled internal held-out position + 0.1*rotation. The full-training model and SHA were persisted before loading the 480 validation windows. All projected baseline results exactly reproduce v12. The final candidate and controls use the same known-anchor-only 23-joint physical projection. No confirmation data was accessed, and historical confirmation remains previously observed.

## Results

| Model | Projected validation position | Ratio to best position control |
|---|---:|---:|
| Linear control | 0.09355840 | 1.0000 |
| Hermite control | 0.09386265 | 1.0033 |
| V12 learned candidate | 0.10356407 | 1.1069 |
| V13 learned candidate | 0.09579884 | 1.0239 |

V13 reduces the position gap from 10.69% worse to 2.39% worse; acceptance requires at least 5% better. Rotation ratio 1.0792 exceeds 1.02, velocity 1.0755 exceeds 1.05, and worst cohort 4.1439 exceeds 1.1. Acceleration 1.0404 now passes its unchanged 1.05 limit. Endpoint and true physical-edge checks pass. The procedural Hermite control still wins the combined validation score; no learned temporal model qualifies for promotion.

The complete independent repeat reproduces every non-runtime report field and all 18 NPZ artifacts (sixteen internal-fold fits plus final learned and overall-selected artifacts) exactly. Final learned SHA: `f6392f11df2f71b6d6ced5bd86a3d65f77ea0b5a29f933f3d3a62ab754f4e390`. Source hashes stayed fixed throughout both fits. See `training/b4artists_ml/results/trajectory-model-reproduction-v13.json`.

## What the diagnostic changes next

On training data, raw position error improves from linear's 0.193334 to 0.190841, but contextual Hermite reaches 0.173318. The weighted regularized trajectory design has about 10.74 effective degrees of freedom per output out of 516 possible coefficients, computed as sum(lambda/(lambda+regularization)) for the data normal matrix. This is a conditioning/capacity diagnostic, not a proof that a particular larger model will generalize.

The loss correction helps but does not resolve the feature/readout limitation. The next coherent experiment should test learned nonlinear features with the trajectory objective, reusing existing local neural-network infrastructure where suitable. Choose the bounded architecture/regularization through training-only diagnostics and excluded training groups. Verify gradients and exact endpoints, retain a zero-residual control, measure inference/fit costs, and apply the same physical projection and full quality gates. Do not simply weaken regularization: excluded-group selection favored the stronger regularizer here. Do not conduct another validation-driven width sweep.

## Engineering verification and limits

Five new tests independently compare grouped normal equations with dense least squares, finite-difference objective gradients, temporal oscillation penalties, invalid timing/labels, trained objective reduction, exact priority preservation, hidden-label isolation and save/load/repeatability. All five pass on desktop and in Bforartists. With the preserved predictor, projection, observations and kinematics suites, 37 focused native cases pass.

The exact learned artifact produced editable candidate actions with priority/source recovery on all eight authored rig fixtures: BoneForge, basic/default generated Rigify, basic/default metarigs, Mocap, Unity and Unreal. Each source was restored. Complete fixture generation/preview/discard took 0.53-2.99 seconds in this one diagnostic; these single-run timings are not a comparative latency benchmark. Multiple-priority/context/partial-body/style learned acceptance, production rig coverage and independent animator assessment are still absent.

Bforartists again terminated with its already observed shutdown access violation 3221225477 after the assertions. Host lifecycle acceptance remains failed. Add-on runtime and package 0.16.1 are unchanged, so previous 303 native / 110 offline / two packaged-window checks remain evidence for exactly those bytes; they were not rerun or counted as new work here.

Evidence files: `results/trajectory_motion_v13/report.json`, `results/trajectory_motion_v13/selection_frozen.json`, `results/trajectory_motion_v13/folds.json`, independent `results/trajectory_motion_v13_repeat/`, `results/trajectory-fit-diagnostic-v13.json`, `results/trajectory-model-native-v13-regression.json`, `results/trajectory-model-host-v13.json`, and `results/trajectory-model-host-v13-process.json`, all relative to `training/b4artists_ml/`.

Full learned-motion, physics/refinement, broad rigs/quadrupeds, licensing, responsiveness/resources, optional connector and independent usability/comparative requirements remain. No full implementation milestone, parity, release, install, commit or push is claimed.
