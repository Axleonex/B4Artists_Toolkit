# Private preview phase profile

The remaining costs are now attributed more precisely. The unchanged default-Rigify reach/hold workflow ran serially after training and development evaluation completed. One unprofiled pass was followed by one cProfile pass, using the same saved reference as the earlier ABBA benchmark. Production source hashes match that benchmark.

| Measurement | Unprofiled | Profiled (diagnostic only) |
|---|---:|---:|
| Total measured work | 24.051 s | 27.728 s |
| Longest tick | 0.445 s | 0.625 s |
| 95th-percentile tick | 0.068 s | 0.070 s |

Both passes preserved the source action, pose modes, anchors and object/action/scene inventory, and produced exactly identical candidate curves, including handles. Profiling changed the number of coalesced ticks, as expected from time-based scheduling; it did not change the output.

The longest unprofiled tick completed the final generator work, cleanup and publication. In the profiled run, `_publish` accounted for 0.510 seconds and its `smooth_copy` child for 0.325 seconds. These instrumented values identify work to inspect, not production-latency guarantees.

The profiled source guard ran 1,090 times and accumulated 11.159 seconds. Its visible-state `matches` check accounted for 7.999 seconds; `raw_pose` accumulated 6.070 seconds across 1,180 calls, and `_channels` was called 818,480 times. These are inclusive cumulative call times: child totals overlap and must not be added together. The body solver also remains substantial (`solve_steps`: 14.022 cumulative seconds).

## Next bounded optimization

First investigate reducing allocations and redundant traversal in visible-state comparisons while checking the same source properties at every existing boundary. Do not skip guards, reduce validation frequency, assume a dependency-graph notification covers every edit, or weaken cancellation/source-recovery requirements. Any optimization needs equivalent edit-detection tests and serial measurement against the current implementation.

Separately examine candidate publication and smoothing. Cooperative publication would need an isolated incomplete action and atomic final assignment, plus cancellation/save/load/undo cleanup while publication is pending. Do not expose partially written candidate animation or treat the current recovery contracts as optional. The profile identifies this work; it does not establish that a safe incremental publication implementation exists yet.

This was a headless diagnostic, with no UI event latency or independent human usability measurement. The native process again exited 3221225477 after successful assertions; clean host exit remains unqualified. The experimental 0.19.1 release has not been changed.

Evidence: training/b4artists_ml/results/private-phase-profile-v1/report.json and process.json. The original full goal, gates, deadline and evaluation ceiling remain unchanged.
