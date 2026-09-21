# Shared-observation temporal model experiment v12

Status: research-only, failed model acceptance. Full goal remains incomplete.
The installed-package candidate remains 0.16.1; this experiment changes no add-on runtime, bundled weights, Ghost Tool, Anim Assist or Git history.

## Frozen experiment

The common encoder provides 667 features: four known poses, rest geometry, context masks and timing. Ridge and 128-center RBF readouts learn four temporal coefficients for 17 calibrated joint positions/orientations. These are supervised regressors, not neural networks or Cascadeur implementations. All eight planned candidates and both procedural controls use identical full 23-joint physical-ancestry projection initialized only from authored endpoints. Endpoint constraints, root/terminal orientations and fixed physical edges are retained. Hidden labels never enter prediction or projection initialization.

The original data identities, 2912 training windows from 31 clips and 480 validation windows from 10 clips, and all quality gates remain unchanged. No development/confirmation partitions are read, no new data is downloaded and no paid service is used. Validation is used for selection and is not blind confirmation.

Before any fitting, a synthetic small-proposal test caught an overshooting projection step that returned the initializer. Bounded per-frame backtracking corrected it with the same 48-step budget. The unchanged test then passed. The initial protocol is preserved at `training/b4artists_ml/results/semantic-motion-protocol-v12-pre-fit-initial.json`; the final frozen protocol records this correction. No model or gate was retuned after validation.

## Quality results

| Candidate | Projected validation position error | Selection result |
|---|---:|---|
| Linear control | 0.09355840 | Best position control |
| Hermite control | 0.09386265 | Best combined position/rotation score overall |
| Best learned: motion RBF, 128 centers, width 1.5, regularization 0.01 | 0.10356407 | Research trial 7; rejected |

The best learned candidate is 10.69% worse than the best projected position control. Its rotation, velocity and acceleration ratios are 1.1773, 1.1207 and 1.1122. Worst cohort position ratio is 5.184 against the unchanged 1.1 maximum. Endpoint and true physical-edge checks pass. A procedural winner cannot satisfy the learned-motion requirement. No temporal weights are bundled or exposed as a qualified UI option.

`results/semantic_motion_v12/report.json` contains every candidate and cohort, not only the winner. The complete separate-process rerun in `results/semantic_motion_v12_repeat/` reproduces all eight candidate NPZ files, both selected artifacts, selection, protocol, manifest and every reported quality metric exactly. Runtime timing metadata is excluded from report equality. `results/semantic-model-reproduction-v12.json` records hashes; all frozen source hashes were also rechecked.

## Diagnostic interpretation

| Raw output before projection | Training position error | Validation position error |
|---|---:|---:|
| Linear | 0.19333403 | 0.09289431 |
| Hermite | 0.17331804 | 0.09361024 |
| Best learned | 0.19808059 | 0.10396870 |
| Four-coefficient fit using hidden labels | 0.02046448 | 0.00758716 |

The last row is an explanatory representation-capacity bound using hidden labels. It is never a runtime predictor, selection candidate, projection initializer or qualification result. It indicates that the coefficient basis can represent much more of these trajectories than this learned readout predicts. It does not prove that the missing motion is identifiable from sparse observations.

Projection slightly improves the learned validation position error (0.10396870 to 0.10356407); the regression is already present before projection. Unweighted coefficient MSE improves only from 0.59257 to 0.56740 on training and 0.08802 to 0.08714 on validation, while trajectory position degrades. This supports investigating training-objective/conditioning and readout capacity before changing the rig fitter. It does not isolate a single causal failure. Training and validation motion distributions differ, so their absolute errors must not be compared as a simple generalization gap.

Next research should freeze a trajectory-aware loss/representation experiment using training-only diagnostics or internal training folds to select design choices. Compare against these retained projected controls with the same quality/cohort gates. Add explicit continuity/rotation behavior rather than relying solely on coefficient MSE; use the oracle only for representation diagnosis. Do not conduct another arbitrary width sweep or reinterpret already observed confirmation as unseen data.

## Actual-host integration and limitations

The exact best-learned artifact was passed through real Bforartists rig projection, candidate-action generation, exact priorities and Discard/source restoration on all eight fixtures: BoneForge, basic/default Rigify generated rigs, basic/default metarigs, Mocap, Unity and Unreal. All eight engineering checks passed. These are bounded authored fixtures; naturalness, production coverage, multiple-priority/context/partial-body learned workflows and human assessment are not established.

Inference for seven interior queries took 1.58-2.28 ms in this diagnostic; complete generation/preview/discard took 0.69-4.21 seconds, highest on default Rigify. These are single-run diagnostic timings, not a cold/warm or comparative responsiveness benchmark. Interactive temporal generation remains pending.

The four focused native suites passed all 32 assertions/cases (10 new predictor/projection cases plus 22 existing kinematic/data regressions). The host again exited with its previously observed shutdown access violation 3221225477 after assertions. Host lifecycle acceptance remains failed. Current runtime/package bytes are unchanged, preserving the previous 303 native / 110 offline / two actual-window package checks without claiming they were rerun here.

Evidence: `results/semantic-model-host-v12.json`, `results/semantic-model-host-v12-process.json`, `results/semantic-model-native-v12-regression.json`, `results/semantic-model-diagnostic-v12.json`. Paths under results are relative to `training/b4artists_ml/`.

Distribution rights, full physics/refinement, quadrupeds, performance, optional entitlement-aware connector and independent animator/Cascadeur comparison remain unresolved full-goal requirements. No new full implementation milestone is credited for this rejected experiment.
