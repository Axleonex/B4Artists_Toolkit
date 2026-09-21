# Native COM flight measurement protocol v1

Freeze before measurement. Reuse the root-flight protocol's budgets without changing quality gates. Actual BoneForge and default Rigify fixtures run 60- and 240-frame airborne intervals at scene gravity. Each process starts factory-clean, builds the real rig, then performs one first-flight-after-fixture and two warm flights. Restore Before Flight separates runs because native layers must be removed before regeneration. This does not measure a cold add-on install or claim continuous live interaction.

Keep all existing COM, priority, relative-bone, rigid-translation and acceleration checks. Record failed generation and rollback rather than substitute a passing short clip. Record all cooperative step times, process working set, peak process working set, cancellation after generated data appears, generated action cleanup and original source/action/modes recovery. A fresh process is launched per rig/span. Run cases sequentially without another intentional host workload after the regression suite ends.

Budgets inherited from the prior flight protocol: complete solve <=45 seconds for 60 frames, <=180 seconds for 240; step p95 <=100 ms, maximum <=250 ms; abort <=100 ms; sampled working set growth <=256 MiB; no unused superseded generated actions. Report numerical acceptance, timing, memory, source recovery and host exit separately. The known factory-host shutdown access violation remains a failed host lifecycle check even when case assertions pass.

This bounded native-flight measurement cannot satisfy full learned inference, complete animator-workflow performance, motion plausibility or independent usability acceptance.
