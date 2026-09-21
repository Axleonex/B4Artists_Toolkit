# Canonical sequence-model feasibility v2

Current research status: the original goal is ACTIVE and incomplete. Experimental addon0.19.0 is unchanged. The new direct and diffusion sequence backends remain research-only.

## Representation correction

The v1 corpus builder used legacy temporal_data world rotations without each bone's rest-axis calibration. The actual runtime and protected benchmarks use b4ml-semantic-observations-v1. This mismatch was found while preparing the evaluation adapter. The verified task-owned v1 worker was stopped after16completed epochs, before any validation or confirmation access. Its plan, cache, log and progress are retained. No v1corpus model was promoted or completed.

V2 uses the existing semantic_motion_data encoder and a shared sequence_packet_v2 constructor. Five new checks cover exact protected-target agreement, world position/orientation round trips, global similarity and bone-roll invariance, hidden-target isolation, and the real07_01 training clip. A further six provider checks cover matching training/inference requests, exact priorities, query independence, masked context, stationary holds, output-cache isolation and weight identity. Together with the seven request checks,18tests pass.

The same784,921-parameter backbone, two objectives, fixed seeds and fit recipe remain. The corrected one-clip80-step feasibility fits reduce training-probe loss from0.07312 to0.001887 direct and0.005880 diffusion. CPU PyTorch/NumPy differences remain below5e-7. These are in-sample implementation checks and cannot establish motion quality.

The actual native host runs exported corrected research weights at2,33and120frames. All six cases preserve authored values exactly and repeat identically. At120frames, three NumPy runs take about0.0503seconds direct and1.004-1.012seconds diffusion. These synthetic backend timings exclude rig fitting and viewport events. The host still exhibits its separately documented shutdown access violation after completing assertions; clean process exit remains unqualified.

## Fixed corpus experiment

The corrected corpus has exactly the same5,778windows, source frame indices, context flags and observation patterns as v1, across78existing training clips. Gaps8/16/32/64/96include boundary-only, middle-full-pose and sparse interior position/orientation observations. Rest calibration frame0 is excluded from motion data. Every source and bucket hash is rechecked before fitting. Corrected compressed buckets total419,161,242bytes; both retained caches together remain below the1GiB cache cap.

Four canonical fits are planned: direct and diffusion, each with seeds20260909and20260910,60fixed epochs and1800seconds maximum per fit. No development checkpoint selection or additional local variants are authorized by this experiment. Both original development partitions and all acceptance thresholds remain unchanged. The six sealed confirmation clips remain absent. Training-only progress is recorded separately from motion quality, native usability and Cascadeur comparison.

A benchmark provider now converts the same calibrated Observations into a fixed full-sequence grid before answering queries. Output therefore does not depend on the number/order of requested sample times. Explicit authored priorities are restored exactly. Identical observed poses retain the existing default hold behavior; broader intent/style conditioning remains unfinished. This provider is not installed into the addon.

## Architectural next work

Retain the measured host profile in SEQUENCE-FEASIBILITY-v1.md:21-frame default-Rigify generation takes43-46seconds, mostly scene restoration/guard/rig work rather than the inference backend. Investigate solving on a private working rig and reusing sequence state while keeping all source-change, cancellation, constraint and recovery checks. This remains a design hypothesis requiring actual-rig equivalence tests.

Next: finish the fixed canonical fits, freeze their hashes, evaluate against the unchanged projected procedural controls and original old/new development gates, and report failures without opening confirmation. Correctness and performance improvements do not establish natural motion or independent animator acceptance. Human usability, full physics, style/intent, production rig/mesh coverage, quadrupeds, connector and equivalent Cascadeur comparison remain required.

Evidence directories: sequence-feasibility-v2, sequence-portability-v2, sequence-corpus-v2 and sequence-corpus-training-v2 under training/b4artists_ml/results. V1evidence remains as a rejected preparation attempt. No addon runtime edits, installs, downloads, paid services or Git history changes occurred.
