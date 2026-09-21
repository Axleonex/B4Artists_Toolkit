# Native flight performance, 0.14.0

Measured under the frozen PERFORMANCE-NATIVE-FLIGHT-v1.md protocol, sequentially after other intentional host work completed. Bforartists executable X:/5.1.0/bforartists.exe uses Blender core 5.2.0 Alpha build dd23ab17120d; Windows 11 / Ryzen 7 5800XT, host Python 3.13.9 and NumPy 2.3.4, four BLAS threads. The final 0.14.0 source and protocol hashes are recorded per case.

| 60-frame rig | First solve | Warm solves | Step p95 range | Maximum step | Abort call | Sampled working-set growth |
|---|---:|---:|---:|---:|---:|---:|
| BoneForge | 14.07 s | 14.35-14.98 s | 26.77-28.77 ms | 45.15 ms | 6.15 ms | 4.81 MiB |
| Default Rigify | 22.34 s | 23.46-23.97 s | 41.49-49.61 ms | 91.98 ms | 42.10 ms | 2.61 MiB |

Both 60-frame cases passed every frozen timing, cancellation, memory, unused-action and generation-quality budget. First solve means after rig/fixture creation in a fresh process, not disk-cache-cold startup. The working-set figure is the largest sampled growth above the prepared fixture, not an allocation peak. Abort excludes event dispatch; maximum preceding cancellation-probe step plus abort was 42.71 ms and 106.65 ms respectively.

Both 240-frame cases failed numerical acceptance: acceleration error p95 was 0.100933 for BoneForge and 0.100618 for default Rigify, against the unchanged strict 0.1 world-units/s^2 threshold. Their generation attempts took about 80 and 112 seconds before rejection. These are unsupported cases, not passing latency measurements. No accuracy gate was loosened. Source recovery after these observed failures is checked separately by native-long-recovery-v1.

Final packaged real-window native UI events passed with 103 cooperative steps, p95 36.17 ms, maximum 53.58 ms and 5.38 seconds including the short UI journey. That fixture is ten frames and provides no whole-product latency or independent usability guarantee. The test receipt is docs/b4artists_ml/native-ui-v5.json.

Every host process still exited with the separately reproduced shutdown access violation, 3221225477. Assertion success does not clear host lifecycle acceptance. Learned temporal inference, complete workflow performance, production meshes, hardware diversity and equivalent Cascadeur efficiency remain unverified.

Evidence: training/b4artists_ml/results/native-flight-performance-v1-process.json and its four per-case reports; logs and protocol/script hashes are retained. Source/pose/action/collection recovery is a separate requirement from successful long-clip generation.
