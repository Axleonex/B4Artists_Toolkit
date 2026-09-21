# Native sampling maintenance 0.14.2

The runtime change reuses the already validated rig mapping and omits full deformation matrices when fitting needs only segment COM. Full deformation checks and cooperative input guards remain active. No trajectory formula, sampling grid or acceptance tolerance changes.

Counterbalanced four-run comparisons on actual transformed rigs (baseline/current/current/baseline on BoneForge; reverse order on default Rigify) produced identical native keyframe values, handles and driver expressions. Mean 60-frame times: BoneForge 14.0848 -> 13.3780 seconds (5.02% lower); default Rigify 22.9627 -> 21.8038 seconds (5.05% lower). This is a small matched local comparison, not broad performance acceptance or a confidence interval. Evidence: training/b4artists_ml/results/native-sampling-comparison-v1-process.json.

The native integration suite passes 14 tests, including new exact endpoint-array parity at five fractional frames on BoneForge, basic/default Rigify and basic/default metarigs. It retains cancellation, external edit handling, Keep/Discard, archive/reopen, deformation, priority and source recovery checks. A separately invoked new test repeats one of those 14 and is not an extra unique case.

The 240-frame fixtures still reject with the same acceleration errors (BoneForge 0.100933; default Rigify 0.100618), preserving actions, objects, collections, raw pose, rig modes and playhead. New long recovery evidence: native-long-recovery-sampling-v1-process.json. The numerical threshold stays 0.1 world units/s^2.

A minimal exact-parabola diagnostic without a rig reproduces 0.1040625 acceleration error at the shifted quarter-frame sample grid. Rounding the analytical parabola once to float32 reproduces that value independently in NumPy; integer-quarter-frame samples give 0.0365625. Querying scene time or factoring the expression does not remove it. This identifies a host storage/measurement precision limitation, not a passing 240-frame result. No acceptance gate was relaxed. Retained diagnostic scripts/results: probe_native_time_precision.py and versions v2/v3; native-time-precision-v1/v2/v3.json. The initial v2 syntax error was corrected before its recorded numerical run.

All host checks still encounter the known shutdown access violation after assertions. No clean host lifecycle, independent animator usability, learned temporal motion or Cascadeur superiority is claimed. The two shipped pose models, Ghost Tool and Anim Assist remain unchanged. Changes are local; no installation or Git publication.
