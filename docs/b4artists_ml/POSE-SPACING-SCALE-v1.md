# Scale Later Pose Spacing v1

Status: verified development source in 0.37.0; newer than the frozen 0.36.0 package.

Click the outward-arrow scale button beside any saved priority pose except the last. The dialog keeps that pose fixed and applies a 0.25x through 4x factor to every later pose frame. Values below one compress the sequence; values above one expand it. Pose data, easing, Breakdown Bias, Departure Hold, Arrival Hold, name suffixes, collection storage order, source Action, and rig state remain exact.

Dialog admission is factor-independent. A default expansion that exceeds a bound cannot prevent the animator from opening the dialog and choosing a valid compression. The backend validates the edited factor and independently float32-rounds every destination. Frames must remain ordered, separated, within Blender's absolute range and the 240-frame span. Consecutive intervals and pivot-relative offsets must remain within one percent of ideal after storage. Expansion writes last-to-first and compression first-to-last. The shared transaction reconstructs exact semantic rows after mid-write clear/remove/add/move callbacks.

`training/b4artists_ml/results/pose-spacing-scale-v1.json` passes 8/8 focused tests. SHA-256: `9da3f7be75d13dbfac0024e768dee79e37c5617ce07d4a233e4cb90d854bba20`.

`training/b4artists_ml/results/pose-spacing-scale-affected-v1-regression.json` passes 105/105 tests across ten affected suites, including Ripple Pose Retime, on one 44-file runtime set. SHA-256: `74266dace099d7a8ed0eda33aaa5141b5610f306fadb3dc1b39ac221e4b33939`.

`pose-spacing-scale-ui-v1.json` records the foreground dialog, a 2x scale around frame 6, one native Undo and Redo, preview at moved frame 16, and source recovery. Report SHA-256: `0a7a80e1fb84716a774e554c1e04c57f3ff2153ef1ad2aa3129e6277f46a57b8`. Screenshot SHA-256: `b237ab90f8874e525f263c92671cdbee07a223b4c013802edc1207871c782e57`.

The host completed every assertion before its known shutdown access violation; shutdown is not labelled clean. This is deterministic timeline authoring. It does not infer timing or intent, learn motion style, improve physical plausibility, or qualify Cascadeur parity.
