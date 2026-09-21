# Boundary-preserving learned trajectories v16

Prospective four-way ablation: linear/contextual-Hermite reference crossed with value-only(C0)/value-and-first-derivative(C1) correction envelope. Preserve v15 observed-motion scales and stationary invariants. Use the selected64-unit tanh configuration, forty epochs and regularization0.0001; do not reopen architecture search. Preserve original data identities, known-only projection, controls and quality gates.

C1 multiplies the existing4*t*(1-t) Legendre basis by4*t*(1-t), so learned corrections and their first derivatives vanish at both priorities. Reference motion is computed only from authored endpoints and available outside context. This preserves the reference's raw proposal derivatives; physical projection is nonlinear and must still pass the original motion-quality checks. Quaternion Hermite uses its existing tangent approximation, not a new claim of exact observed angular velocity.

Before any corpus fit, twelve tests cover explicit/compressed loss, all network gradients, actual feature learning, priority/masked-context/serialization/stationary invariants, analytical endpoint behavior and convergence of nonzero learned correction derivatives toward zero. The unchanged near-correct-curve learning test exposed an Adam overshoot. Its old source/failure are preserved, and bounded per-batch backtracking now passes it without changing the test or acceptance gates. All four ablations use this same repaired optimizer.

Select exclusively through four complete catalog-group-excluded training folds. Freeze the final trained artifact before loading validation; reproduce all18model artifacts independently and require exact prior projected-control metrics. Then run ordinary eight-rig and sixteen stationary-rig candidate/source-recovery checks and186 controlled stationary observations. Failed quality forbids promotion.

No data acquisition, runtime/package mutation, installation or publication. This is one part of the original full learned-animation goal; broader physics, control/rig coverage, performance, rights and independent human/Cascadeur comparison remain required.
