# Observed curve-confidence experiment v23

The previous loss change reduced failed cohorts but worsened the dangerous long-gap case. Test whether explicit descriptors of the proposed curves help the learned gate recognize unreliable candidates. Both old candidates remain frozen.

Append 48 features to the original 548 inputs: twelve per expert from nine fixed normalized times. For each expert, take mean/max positional excursion from linear, normalized speed, normalized acceleration, incoming/outgoing tangent mismatch, and semantic-edge length deviation from linear. Divide positional quantities by observed per-joint motion amplitude and edge quantities by rest semantic-edge length, mapping zero denominators to zero. Apply log1p to nonnegative summaries. These are descriptive signals, not joint limits, calibrated probabilities or physical guarantees.

Keep the original v21 equal-cohort loss, 32 tanh hidden units, four softmax weights, 40 epochs and frozen v20 parent. The 48 additional input rows add 1536 weights. Use exactly the same nine-point descriptor calculation at training and inference. Each training row uses the parent that excluded its catalog group; never derive parent-dependent training features from a model fitted on that row. Raw observations remain the same four known poses (two when context is absent).

Eighteen pre-fit checks pass, including finite-difference calculus, explicit trajectory loss, real supervised learning, feature shape and retained inputs, scaling/translation invariance, proposal sensitivity, invalid inputs, masked context, stationary and exact priorities, label separation and model serialization. Fit one configuration, freeze before either exposed development set, repeat independently, and exercise actual-rig editable recovery. All existing controls and gates remain unchanged; keep six fresh confirmation clips sealed unless all development gates pass.

Runtime, v0.17.4 package, other addons, publication boundaries, original goal endpoint and the 50-evaluation/15-hour resumed limits are unchanged. No downloads, paid services or installation are part of this experiment.
