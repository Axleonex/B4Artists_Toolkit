# Procedural humanoid vertical slice v12

Date: 2026-09-10  
Runtime behavior: experimental 0.20.2; the sealed matrix used identical code with 0.20.1 version metadata  
Result: 32/32 automated cases passed

## Scope

This milestone freezes the optimized procedural floor that future learned motion must beat. It runs reach, crouch, walk, run, jump, land, turn and difficult transition on four independently constructed humanoid profiles: the BoneForge-compatible procedural builder, generated Rigify basic/default rigs and an FBX roundtrip Unity-style imported hierarchy.

Every case uses the installed Bforartists host and current add-on behavior. The benchmark drives whole-body posing, gravity flight and contact correction, then checks Keep, Restore, save/reload, exact source-action restoration and unchanged priority anchors. Fixed world contacts, support-plane provenance, grounded anatomical task axes, master-root yaw and counted reach preflight adjustments are part of the frozen protocol.

The protocol SHA-256 is `18a1d76a3836aa852d00a6c0bf904ea1a837b763a9ecae6bb6c847913aa311e4`. The aggregate SHA-256 is `25e4284d5490263014975d6e4885fc627a5cb9d426e640143228645b954edb95`. The aggregate records the exact SHA-256 of every tested runtime Python file, report, saved `.blend` file and host log. The final 0.20.2 package differs from that tested runtime only in the version tuple; the package receipt proves the normalized 0.20.1 source hash and exact archive contents.

## Automated results

| Gate | Worst result | Acceptance |
|---|---:|---:|
| Priority matrix error | 0 | <= 0.0002 |
| Pin residual | 0.000009762 | <= 0.0002 |
| Requested pin error / body scale | 0.000005039 | <= 0.0002 |
| Reach preflight adjustment / body scale | 0.021401 | <= 0.03 |
| Skeletal stretch fraction | 0.000011552 | <= 0.002 |
| Contact-plane spread / body scale | 0.000001820 | <= 0.0002 |
| Penetration / body scale | 0.005625 | <= 0.01 |
| Contact position error / limb length | 0.000189207 | <= 0.0002 |
| Contact orientation error | 0.000690534 rad | <= 0.001 rad |
| Flight error / body scale | 0.000000328 | bounded |

The matrix evaluates 13,704 contact checks over 12,596 validation frames. Every case preserves its source action exactly and passes candidate save/reload. The largest finite rotation-velocity jump is 1.454691 rad/s; it remains recorded for later motion-quality comparison.

## Runtime and memory

The times below are complete in-process case times. Memory is the Bforartists process working set. Generation-step maxima are benchmark instrumentation, separate from the actual-window cooperative callback measurements in `PROCEDURAL-PROXY-PERFORMANCE-v0.20.2.md`.

| Profile | Median case | Slowest case | Median working set | Peak working set | Max generation step |
|---|---:|---:|---:|---:|---:|
| BoneForge | 12.23 s | 17.08 s | 219.4 MiB | 227.0 MiB | 165.4 ms |
| Rigify basic | 23.85 s | 40.31 s | 275.6 MiB | 282.9 MiB | 216.0 ms |
| Rigify default | 43.44 s | 60.62 s | 359.3 MiB | 379.2 MiB | 296.8 ms |
| Imported Unity | 6.83 s | 11.20 s | 209.8 MiB | 214.9 MiB | 143.1 ms |

Compared with sealed v11, Rigify-basic median case time falls 24.3%. Rigify-default median falls 39.5%, its slowest case falls 55.6%, median contact correction falls 74.7%, and maximum contact correction falls 72.8%. The default-Rigify run remains the slowest case at 60.62 seconds, so end-to-end workflow latency still needs work.

## Corrected evaluator path

V11 exposed a valid dependency-closed evaluator that completed dense Rigify fitting but was rejected during shape publication. The curve publisher re-read copied proxy anchors and compared the intentionally reduced proxy rest signature against the source rig signature. The public path then silently repeated the solve on all 706 bones.

V12 passes the already-validated source anchor snapshot into shape publication. A focused saved-scene diagnostic changes from a `Rig structure/rest pose changed` rejection after 6.58 seconds to a complete 114-bone proxy solve with full-rig verification. The repaired run reports the same `0.0001123901` position error and `0.000690534` rad orientation error while the contact stage drops from 98.70 to 28.00 seconds in that diagnostic.

## Claim boundary

This is an automated procedural floor. `learned_motion_promoted=false`: no temporal model was accepted, exported or bundled. Scripted interaction and correction counts are not human usability evidence. Motion appearance is unrated, an independent animator pass is missing, and no equivalent Cascadeur task comparison has run. Quadrupeds, dynamic collision/secondary motion and the optional entitlement-aware connector remain unfinished.

All durable case artifacts complete before the known post-result `ucrtbase.dll` access violation. The v12 runner exposed status `11`; prior runs exposed unsigned Windows status `3221225477`. Every v12 log identifies the same module, and clean shutdown remains unqualified.

Primary evidence: `training/b4artists_ml/results/procedural-vertical-slice-v12/aggregate.json`.
