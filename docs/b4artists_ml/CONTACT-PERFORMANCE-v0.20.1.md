# Contact workflow performance - experimental 0.20.1

## Result

The default-Rigify foot-contact workflow now meets its frozen automated responsiveness gate. The exact extracted package completed three actual-window suggestion, review, correction, Keep and Restore Source journeys. Every measured cooperative callback stayed below 50 ms, every correction completed below 8 seconds, and the corrected contact error remained below `2e-4` evaluated limb lengths.

The 0.20.0 baseline correction took approximately 17.0 seconds. The final 0.20.1 package took 6.56 seconds median and 6.72 seconds maximum across three runs, a 60.5% reduction at the conservative maximum. Suggestions took 0.30-0.30 seconds. The worst suggestion callback was 35.28 ms and the worst correction callback was 42.87 ms.

## What changed

- Contact fitting samples at quarter-frame intervals and validates cubic output adaptively at quarter and midpoint positions. This retains continuous-curve checks while avoiding an unconditional eighth-frame fit.
- Dependency, driver and constraint discovery yields more often while constructing private evaluators.
- Suggestion sampling uses `scene.frame_set` to restore the untouched action between observations and reserves the full pose and rig-mode restore for finalization.
- Complete-rig verification no longer repeats a view-layer update already performed by `scene.frame_set`.
- Metric assembly, serialization, candidate publication and commit are separate modal callbacks.

## Evidence

- Source regression: 45 unique suites, 429 tests, no failures, errors or skips, all against one runtime hash.
- Source actual-window trials: three of three pass; correction maximum 6.13 seconds; suggestion/correction callback maxima 30.15/39.60 ms.
- Exact archive workflows: 13 established offline cases with 9,813 dense contact checks and blocked outbound network/process calls, plus four contact-suggestion tests.
- Exact archive UI: three of three actual-window journeys pass with maximum contact error 5.465894e-05 limb lengths.
- Archive: `releases/b4artists_ml_v0.20.1.zip`, SHA-256 `f845bc973e1c61ae44631c0b44b07df9cd7092acd0729212f2ec4a7fac4d546b`.

Two pre-final timing reports are retained. One exposed a 51.9 ms publication callback and led to finer publication boundaries; the other exposed a 52.7 ms suggestion callback and led to removal of redundant per-sample pose/mode restores. They are failed candidate evidence, not part of the passing release claim.

## Limits

This qualifies one automated default-Rigify contact workflow on this machine. It does not establish zero latency, all hardware responsiveness, manual animator usability, broad action quality or Cascadeur parity. A known `ucrtbase.dll` access violation still occurs after Bforartists writes passing reports, so clean host shutdown remains unqualified. One broader Rigify hand-orientation workflow has previously taken about 10.76 seconds and remains outside this foot-contact performance gate. The next product milestone is the fixed procedural vertical slice across four humanoid rig families and seven action families.
