# Frozen learned shape-reference experiment v18

The original goal remains standalone learned animation and its full workflow/physics/rig/comparison scope. This experiment is a research step; a procedural reference is not substituted for learned motion.

One configuration is fixed before fitting:64 hidden tanh units,40 epochs, C0 four-term trajectory correction, existing supervised trajectory/velocity/acceleration objective and observed-motion amplitude conditioning. The hidden network is trained anew against the bounded positional reference. Each fit is followed by exact readout regression at0.01, the regularization selected by v17's training-only folds. No grid or validation-driven selection is performed.

Four unchanged catalog-group folds diagnose generalization, then one full-training model is fitted and its checksum frozen before validation. The corpus, window identities, old holdouts, normalization ownership, exact physics projection and thresholds stay fixed. Both original projected baselines are rechecked for exact equality. A third projected control uses the bounded reference alone. The learned model must beat the best of all three controls under every original gate; procedural gains cannot qualify the learned model.

Seven pre-fit checks passed: explicit versus compressed trajectory loss, finite-difference gradients, actual hidden-feature learning, exact readout optimum, priorities, label-independent inference, serialization and zero learned correction for stationary observations (related invariants are grouped within checks). Repeat all five hidden fits and five readout fits, requiring six identical serialized artifacts and identical non-runtime results. Compare the same16 moving and16 stationary actual-rig recovery cases after the report is available. These remain separate from corpus, physics, human and Cascadeur quality acceptance.

The test/reproduction jobs use separate output directories. No runtime model, package, installed tool or Git history is changed. Already exposed validation remains research evidence, never blind confirmation. Source code and protocol checksums are embedded in each experiment report.
