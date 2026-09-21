# Expanded motion coverage experiment v19

The original goal and qualification gates remain unchanged. This experiment changes the training corpus while holding the v18 architecture, hidden training, exact readout regularization, sampling rules and all three projected procedural controls fixed.

## Prospectively fixed data

Catalog descriptions and pinned Git blob metadata determined the clip list before motion acquisition. The immutable plan is `training/b4artists_ml/temporal_expansion_plan_v19.json`, SHA256 `8af5a83abffd86b50c1e1f5426f330ad524970dd30475e313b7d02d6cc1d669a`. The 100 MB total and 8 MB per-file caps cover the complete planned set, including six sealed confirmation clips. Development downloads contain 53 verified unique clips, 53,236,133 bytes. No raw data enters the installable addon ZIP.

One candidate, 83_01, is identical to protected validation clip 122_01. Acquisition stopped before storing it, then a recorded pre-fit amendment excluded the duplicate without replacement. Existing manifest rows and their indices remain identical, preserving the earlier deterministic windows. Catalog prefixes are grouping labels, not guaranteed distinct actor identities.

The training-only audit passes on 78 clips from 25 catalog groups: 47 new clips plus the existing 31, 1,026.296 seconds (17.1 minutes) of distinct source motion, and 7,358 training windows. Windows include duplicated context conditions and are not independent recordings. Coordinate round-trip and rigid-transform/uniform-scale checks are below 1e-8. No topology or short-clip exclusions were necessary; short clips contribute only their eligible gaps.

## Fixed selection and qualification

One configuration: 64 tanh hidden units, 40 epochs, batch 64, learning rate 0.001, hidden-fit regularization 0.0001, velocity weight 0.01, acceleration weight 0.0001, shape reference, C0 four-term residual basis, observed-motion channel amplitudes and exact readout regularization 0.01. Four catalog-prefix-excluded training fits diagnose transfer, followed by one full-training fit. No architecture or hyperparameter grid, no old/new validation selection. Repeat all fits for deterministic model reproduction; concurrent runtimes are not latency benchmarks.

After weights freeze, score original validation, six new validation clips and their union separately. Every partition must pass the existing 5% position improvement and rotation, velocity, acceleration, length, worst-cohort and exact-priority/edge safeguards against the strongest of projected linear, Hermite and shape references. Original control reports must remain exactly equal to v18. A larger set cannot dilute an old-validation regression.

The six confirmation clips remain absent from disk until all three development gate sets pass and model, report and acquisition-plan hashes are frozen. The acquisition ledger records confirmation access before any request. Existing exposed confirmation stays exposed. Passing development would only authorize a blind confirmation experiment, not runtime promotion or a Cascadeur parity claim.

## Evidence and limits

Fourteen offline acquisition checks cover plan and source mutation, byte caps, content identity, split duplication, interrupted-request recovery and confirmation access. `temporal-data-audit-v19.json` records actual training coverage and coordinate checks. Fresh actual-rig moving and stationary tests use the resulting weights after fitting.

The corpus remains small. More motion is not proof of learned generalization, timing/style control, physics quality, responsiveness, quadruped support or human usability. Original acceptance requirements and the 50-evaluation/15-hour resumed limits remain in force. No source commit, push, addon installation or publication occurs in this experiment.
