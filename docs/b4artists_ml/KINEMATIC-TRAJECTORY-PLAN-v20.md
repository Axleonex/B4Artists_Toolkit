# Motion input conditioning experiment v20

This is one prospectively fixed learned experiment. The original scope, data splits, strongest procedural controls and all numerical qualification gates remain unchanged. Addon0.17.2 remains the experimental installable artifact; no temporal weights are bundled.

## Training-only rationale

The v19 network predicts dimensionless trajectory coefficients, then multiplies them by observed joint-motion amplitudes. Its inputs include absolute endpoint changes and velocities, so the learned map must infer motion-size divisions and duration products. The v20 map performs these known arithmetic operations explicitly. This encoding is procedural; only the supervised predictor is learned, and it must still demonstrate improvement beyond every procedural baseline.

For each joint, divide endpoint position/rotation deltas by the same observed amplitudes used in the decoder. Multiply incoming/outgoing velocities by interval duration before dividing. Exactly zero amplitudes map to zero descriptors. Keep153 start-pose and55 rest/mask/time features, normalize306 motion features, and append34 position/rotation amplitudes. The resulting548 features retain absolute duration/frame time and let the network reconstruct all original motion descriptors. The original514-input network could not reconstruct magnitudes from normalized features alone.

The initial map omitted those34 explicit magnitudes. Initial tests reconstructed with external amplitudes, which was weaker than claiming that the network input retained all information. Original sources and receipt remain archived; `kinematic-features-prefit-correction-v20.json` records the correction before fitting. The final audit reconstructs using only548 features. Across7358 training windows, maximum reconstruction error is7.11e-15 and normalized-descriptor time-scaling difference4.44e-16. The theoretical endpoint/incoming/outgoing position bounds1/2/2 and rotation bounds pi/2,pi,pi hold. Synthetic stationary, unavailable-context and malformed-input checks pass. No validation or confirmation motion enters this audit.

## Fixed model and selection

Use the same64-unit tanh hidden layer,612-value C0 trajectory readout, observed output amplitudes and shape reference as v19. The34 extra inputs add2176 weights. Keep40 epochs, batch64, learning rate0.001, hidden-fit regularization0.0001, velocity weight0.01, acceleration weight0.0001 and exact final-readout regularization0.01. Four training-only catalog-prefix folds diagnose transfer; one full fit follows. No grid, no validation-driven selection, no new downloads.

Seven pre-fit calculus and learning checks pass: explicit trajectory objective equivalence, finite-difference gradients, actual supervised hidden learning, exact readout stationarity/improvement, priority and hidden-label independence, serialization and stationary residuals. The original successful receipt matches unchanged source bytes. An unnecessary duplicate invocation later reached the receipt overwrite guard; it did not replace that proof or reveal a mathematical failure. The incident and command-sequencing lesson are recorded in `kinematic-prefit-repeat-guard-v20.json`.

Freeze weights before evaluating old validation, v19-added validation and their union. Both validation partitions are already exposed development data. Require every original gate independently in each partition and exact equality of all six retained per-partition procedural control reports. Repeat all five hidden and five exact readout fits for six byte-identical model artifacts; runtime comparisons are not inferred from concurrent research runs.

Six untouched confirmation clips remain absent unless all development gates pass and immutable model/report/plan checks permit a blind confirmation run. A development pass alone does not qualify the original goal, justify runtime promotion or establish Cascadeur parity. Subsequent actual-rig checks separately verify moving/stationary editable output and source recovery on eight existing fixtures.

The original physics, style/timing and partial-body interpolation, performance, broader humanoid/quadruped, optional connector, distribution and independent human/Cascadeur comparison requirements remain. The same goal ID,50 total evaluations and15-hour resumed cap remain in force.
