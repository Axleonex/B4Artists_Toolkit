# Relative cohort loss experiment v22

The training-only audit found that the largest quarter of466cohorts contributes79.91% of the current fitting error and the largest tenth58.07%. Best procedural positional MSE spans approximately5.32e-6 to1.07 in the rest-normalized coordinates. These are in-sample gate diagnostics from group-excluded parent proposals, not independent gate validation.

Three fixed development ablations retain learned v20 rotations and independently use linear, Hermite or shape positions. None passes the unchanged quality gates. Combined position ratios are1.1342,1.0541 and0.9961 respectively, compared with0.9238 for v21. Learned rotations alone do not explain the mixture's average position gain. All ablations are exposed development diagnostics and are not promoted.

Test one training-loss change with the v21 architecture, inputs, feature normalization, parent experts, initial weights and optimizer settings fixed. Allocate half the sample-weight mass by the original equal-cohort method. Allocate half according to inverse best procedural position MSE per training cohort, floored at1% of the median positive cohort error. Use training labels only for those normalization estimates. Each cohort's mass is divided equally among its windows. Zero relative strength exactly reproduces the entire v21 fit in the pre-fit check. Nine weighting tests pass; the original14 predictor checks remain pinned and unchanged.

The mixture's inference and serialization format remain exactly v21; only trained gate weights differ. Fit once, freeze before loading either development set, repeat exactly, and run actual-rig recovery checks. Require all original gates on old/new/combined without dilution. Keep all six fresh confirmation clips absent unless development passes. No grid, post-evaluation tuning, parent retraining, addon changes, downloads, costs or publication.

Original goal ID, endpoint, passed floors/history,50total evaluations and the unchanged15-hour resumed deadline remain. This loss experiment does not complete the full learned animation product or establish Cascadeur parity.
