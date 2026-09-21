# Private sequence projection research

The measured source-restoration bottleneck can be reduced by solving on an isolated working rig while guarding the source at each public chunk. This is a research prototype; the installed addon remains unchanged.

| Reference | Original seconds | Private seconds | Maximum returned chunk | Channel difference |
|---|---:|---:|---:|---:|
| boneforge-reach_hold | 5.767 | 4.520 | 0.063 s | 0.0 |
| boneforge-root_yaw | 8.016 | 6.181 | 0.057 s | 0.0 |
| rigify_basic-reach_hold | 19.047 | 14.961 | 0.099 s | 0.0 |
| rigify_basic-root_yaw | 27.329 | 21.367 | 0.064 s | 0.0 |
| rigify_default-root_yaw | 65.805 | 46.693 | 0.197 s | 0.0 |

These five cases preserved source animation and inventory, passed preview/discard, cancelled cleanly and rejected a newer source edit without overwriting it. Default-Rigify reach also matched exactly in the earlier v1 experiment. Measurements overlap GPU training, are not randomized, and include test assertions; they establish neither cold/warm performance nor viewport responsiveness. v2 timing includes guards and cleanup.

The lifecycle owner passed 15 headless cases: cancellation and the registered host-change callback at six preparation/solve boundaries, newer-edit rejection, actual paused save/reload, and successful preview/discard. The first lifecycle test assumed that a coalesced public chunk would return every internal phase and failed at observing after eight successful cases. That failed attempt remains in results/private-sequence-lifecycle-v1. Version2 exposes a zero chunk budget for deterministic boundary testing; its successful solve retains the 20 ms budget. This fixes the test observability assumption, not an addon bug.

All completed native cases retained the known post-assertion ucrtbase.dll access violation as an unqualified host exit. Actual interactive undo/redo and cancellation during callbacks remain unverified.

## Integration decision

Keep the private-rig direction, but do not promote this prototype yet. Production integration needs an explicit transaction dependency instead of cloned Python function globals, normal job ownership/lifecycle tests, independent review where available, and an isolated end-to-end latency check. Bound-mesh/dependency fidelity and stale-source detection must remain protected.

The sequence model remains interchangeable behind the calibrated skeleton representation; geometric projection and contact/priority validation remain mandatory after generation. Faster projection does not establish learned motion quality, physics quality or Cascadeur parity.
