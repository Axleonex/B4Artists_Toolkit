# Procedural humanoid vertical slice v11

Date: 2026-09-10  
Runtime: experimental 0.20.1  
Result: 32/32 automated cases passed

## Scope

This milestone freezes the procedural floor that future learned motion must beat. It runs eight actions—reach, crouch, walk, run, jump, land, turn and difficult transition—on four independently constructed humanoid profiles:

- the BoneForge-compatible procedural builder;
- generated Rigify basic and default rigs;
- an FBX roundtrip Unity-style imported hierarchy.

Every case uses the installed Bforartists host and the current add-on source. The benchmark drives the existing whole-body posing, gravity flight and contact-correction workflows, then checks Keep, Restore, save/reload, source-action restoration and unchanged priority anchors. Fixed world contacts, support-plane provenance, grounded anatomical task axes, master-root yaw and counted reach preflight adjustments are part of the frozen protocol.

The protocol SHA-256 is `7e7656f454485927d38050a54a6467510b9ad62dd7efd4da5244a785d916b284`. The finalized aggregate SHA-256 is `1b115b3adebe4e37a1b1dc775d93957c530e73bf1064be476f9203fd559f2bfc`. The aggregate also records the exact SHA-256 of every runtime Python file, report, saved `.blend` file and host log.

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

The matrix evaluates 13,704 contact checks over 12,596 validation frames. Every case preserves its source action exactly and passes candidate save/reload. The largest finite rotation-velocity jump is 1.454691 rad/s; the protocol requires it to remain finite and records the value for later motion-quality comparison.

## Runtime and memory

The times below are complete case time inside Bforartists. Memory is the process working set captured in the host. The generation-step maximum is benchmark instrumentation around procedural generation; it is not the cooperative UI callback measurement already qualified for the 0.20.1 contact workflow.

| Profile | Median case | Slowest case | Median working set | Peak working set | Max generation step |
|---|---:|---:|---:|---:|---:|
| BoneForge | 11.86 s | 16.91 s | 219.5 MiB | 227.4 MiB | 154.9 ms |
| Rigify basic | 31.51 s | 53.26 s | 282.7 MiB | 291.6 MiB | 184.7 ms |
| Rigify default | 71.80 s | 136.65 s | 367.2 MiB | 386.3 MiB | 276.0 ms |
| Imported Unity | 6.26 s | 10.73 s | 210.0 MiB | 215.4 MiB | 123.0 ms |

Rigify default is the next clear optimization target: its run case takes 136.65 seconds in-process and its turn case exceeds 100 seconds. These benchmark-stage pauses do not meet the intended interactive experience, even though the separately measured 0.20.1 contact UI callbacks remain below 50 ms.

## Protocol development history

Rejected v1-v10 evidence remains in the results tree. Those runs exposed benchmark defects rather than being erased or recast as product failures:

- v1 used infeasible fully extended targets and invalid contact/flight intervals;
- v2 exposed stale helper `matrix_world` state and scene-lifecycle defects;
- v3-v5 corrected support-plane provenance, world-up yaw and visible motion-layer selection;
- v6-v7 normalized imported floors, measured true skeletal stretch and removed an invalid landing arm lift;
- v8 moved Rigify yaw to the actual master `root`;
- v9-v10 added the requested-pin gate and a grounded anatomical task frame;
- v10 first reached 32/32, but Windows working-set collection was unavailable because of a ctypes handle-width defect;
- v11 fixes that evidence collection and requires memory counters in every report.

## Claim boundary

This is an automated procedural floor. `learned_motion_promoted=false`: no temporal model was accepted, exported or bundled. Scripted interaction and correction counts show deterministic workflow cost; they are not human usability evidence. Motion appearance is unrated, an independent animator pass is missing, and no equivalent Cascadeur task comparison has run. Quadrupeds, dynamic collision/secondary motion and the optional entitlement-aware connector remain unfinished.

All 32 durable reports and `.blend` artifacts complete before the host exits. Bforartists then hits the known post-result `ucrtbase.dll` access violation with exit code `3221225477`; clean shutdown remains unqualified.

Primary evidence: `training/b4artists_ml/results/procedural-vertical-slice-v11/aggregate.json`.
