# Shape-aware contact proxy performance — experimental 0.20.2

## Result

Large shape-aware Rigify candidates now retain the dependency-closed contact evaluator through curve publication. The prior code completed proxy fitting, revalidated the copied proxy against the source rest signature, rejected it and repeated the solve on the complete rig. The repair reuses the validated source anchor snapshot at that internal boundary.

The frozen 32-case procedural matrix passes without changing any numerical maximum. Rigify-default median case time falls from 71.80 to 43.44 seconds and its slowest case from 136.65 to 60.62 seconds. Median contact correction falls from 37.87 to 9.57 seconds; maximum contact correction falls from 105.61 to 28.77 seconds.

## Validation

- 45 native suites pass 430 tests against one tested runtime hash, including the new prevalidated-anchor regression.
- Procedural vertical slice v12 passes 32/32 cases across four rig profiles and eight actions, with 13,704 contact checks, 12,596 validation frames and memory counters.
- The exact 0.20.2 archive passes 13 offline workflows under the outbound network/process-denial guard and four contact-suggestion tests.
- Three exact-package actual-window journeys pass. Correction is 5.19 seconds median and 5.50 seconds maximum. Worst suggestion/correction callbacks are 30.40/38.41 ms, below the frozen 50 ms gate. Maximum contact error is `5.465894e-5` limb lengths.
- The exact-package shape workflow reports `geometric_contact_projection_shape_v1_proxy_v1` on Rigify basic/default and retains source recovery.

Archive: `releases/b4artists_ml_v0.20.2.zip`  
SHA-256: `24aa6987ef25a9b6f834e82c10457ab782bc1434f3aa237b585d51de92f70eae`

## Limits

The procedural benchmark still measures tens of seconds for complex full actions, and its generation-stage steps exceed the interactive callback target. Motion appearance and human correction effort remain unrated. No learned temporal model is promoted, and this evidence does not establish full physics, quadruped support or Cascadeur parity. The known post-result Bforartists `ucrtbase.dll` crash remains; exact-package UI runs required the test harness to terminate the child after the durable result because scripted quit did not close the host.
