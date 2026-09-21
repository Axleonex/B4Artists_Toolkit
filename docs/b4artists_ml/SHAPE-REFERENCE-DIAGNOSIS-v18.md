# Training-only contextual overshoot diagnosis

The known-context Hermite reference scales one-frame boundary slopes by the full gap duration. In training clip09_01, source frames5..133, the long contextual window has raw position error0.5061 versus linear0.2491 and a reference excursion of1.963 body units. A bounded reference reduces error to0.3761 but remains worse than linear. Other training clips reproduce the failure; no validation clips were loaded for this diagnosis.

A PCHIP positional reference uses harmonic interior slopes from known times[-dt,0,duration,duration+dt]. Opposing/zero slopes yield zero tangents. The existing quaternion reference is retained. The [SciPy mathematical description](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html) documents the weighted slope rule; this independent NumPy implementation adds no SciPy dependency. Its bounds apply to position components within a single interval, not anatomy, physical validity or global multi-window continuity.

Six independent reference checks passed, including50 randomized curves, closed-form weighted slopes, endpoint preservation, large contextual excursions, stationary/no-context behavior and invalid timing. The raw training position average is0.17352 versus Hermite0.17332: bounded reference alone is not an improvement overall. It helps32.49% of contextual windows;28.90% of supervised target position components lie outside endpoint bounds. Real motion arcs require a learned residual rather than retaining this bound as a final-motion restriction.

The C0 label-access oracle still reaches0.02046, exactly the previous four-term oracle error: switching cubic references does not remove its trajectory capacity. This oracle reads answers and is never used for inference.

A separate training-only startup check found no duplicate first-motion calibration pose across31clips. Maximum initial sampled speed divided by the clip's95th-percentile speed was0.96488. This narrow result does not prove all data clean, but gives no justification to discard startup windows. All data and evaluation windows remain unchanged.

Evidence: shape-reference-checks-v18.json, shape-reference-diagnostic-v18.json and startup-context-diagnostic-v18.json under training/b4artists_ml/results. Previous goal turn: progress; completed v17 reproduction/actual-rig evidence and evaluation30 are preserved.
