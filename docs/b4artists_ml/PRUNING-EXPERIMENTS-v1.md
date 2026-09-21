# Rejected pruning optimizations v1

Both proposed pruning changes were rejected and the exact0.17.4 implementation was restored. No new release was created. Fixed five-profile comparisons found identical poses, authored signatures, solver metrics and source recovery, but neither approach reduced the target pause.

| Approach | Baseline worst tick | Candidate worst tick | Prune tick ratio | Total-work ratio | Verdict |
|---|---:|---:|---:|---:|---|
| 64-bone batches | 58.54 ms | 63.97 ms | 1.091 | 1.073 | REJECT |
| Native bulk deletion | 62.37 ms | 72.97 ms | 1.176 | 1.005 | REJECT |

The prospective gates required default Rigify pruning-tick ratio<=0.70, worst-tick ratio<=0.95 and total-work ratio<=1.10, plus exact pose/signature/metric and source parity on all five profiles. Separate base/current/current/base comparisons were used for BoneForge/default Rigify and base/current for the other profiles, with two solves per run. Timings were uninstrumented and no other host experiments ran concurrently. The same thresholds were retained for both approaches.

The batch approach returned to Object mode and original context after every64removals. Repeated mode transitions and per-yield validation failed to reduce the measured pause. Its candidate and unexecuted boundary tests are preserved in results/pruning-rejected-v1; the full331-case prospective regression was not run after failed speed gates.

The bulk approach used a native selected-bone deletion. Its initial private-context call failed the operator poll; an explicit edit-object context then exposed the need for explicit selected-bone context. Those failures, source snapshots and reports remain preserved. The corrected operation disabled mirrored deletion only on the private copy, exposed its bone visibility/selection, and required the exact dependency set afterward. The selected-bone operation is documented in the [Blender API](https://docs.blender.org/api/5.2/bpy.ops.armature.html#bpy.ops.armature.delete); its context requirements were also checked against [Blender source](https://github.com/blender/blender/blob/main/source/blender/editors/armature/armature_edit.cc). No source code was copied into the add-on.

A focused check passed on default Rigify, basic Rigify and the default metarig: required bones and evaluated matrices, original bone/collection visibility and selection, original context and cleanup remain intact. The same generic source-isolation check also passes after restoration, including source mirror settings. It is retained as tests/test_b4artists_ml_proxy_isolation.py (one unittest with three rig subcases). The old330-case/31-suite coverage is retained under unchanged runtime hashes; this is not a fresh331-case full run.

All host processes still record the known3221225477shutdown failure after completed assertions. This is separate from the missing report during the initial operator-poll failure. Runtime and every byte in the0.17.4ZIP match again, and prior models/confirmation ownership remain unchanged. Full responsiveness, learned motion, physics/refinement, rig/quadruped coverage, connector, distribution, supported-host lifecycle, independent animator assessment and equivalent Cascadeur comparison remain incomplete.

The next performance investigation should measure repeated preview decoding separately, before selecting a cache strategy. Any cache must return independent mutable records, compare exact current payloads, preserve every live structural/target validation, and remain bounded and local. Do not infer an optimization from a profiler cost center alone. The original endpoint,50total evaluations and fixed15-hour resumed deadline remain unchanged.
