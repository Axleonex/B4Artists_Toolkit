# Sequence-model feasibility and host bottleneck

The original goal is ACTIVE and incomplete. This stage responds to the architecture reassessment. The 0.19.0 runtime and archive are unchanged.

## Native generation profile

One serial Bforartists process loaded the saved default-Rigify reach/hold reference. Four unprofiled runs used off/on/on/off smoothing, followed by one cProfile run. Every run preserved source animation, modes, anchors and action inventory after Discard. These are headless timings, not viewport interaction measurements or verified OS-cold latency. A brief GPU environment probe occurred during this period; no other task-owned Bforartists job ran concurrently.

Measured generation work was43.15-46.34seconds for21frames. Unsmooth publication took0.104-0.121seconds; smooth publication0.406-0.414seconds, including0.264-0.269seconds of smoothing. Maximum unprofiled step was0.474seconds with smoothing and0.171seconds without it. The cProfile run has overhead and must not replace those measurements.

Of53.46profiled generation seconds,33.87seconds were attributed to Transaction.pause, including restore/guard work. Nested cumulative times overlap and must not be summed: VisibleState.restore17.84seconds, raw_pose10.62seconds, guard10.19seconds, and dependency updates11.16seconds across2298calls. Publication/smoothing is a small fraction of total generation cost.

The next host architecture experiment should keep source animation untouched while solving the entire sequence on an isolated working rig, reuse the working rig/session where valid, and publish only the validated candidate. This is a measured design hypothesis, not an implemented optimization. Existing source-change detection, cancellation, recovery and final rig checks cannot be removed to obtain a speedup. The private rig must reproduce the real rig's constraints and evaluated output; shared mutable rig state or dependency-graph side effects must be excluded.

## Local learning path proved at feasibility scope

An existing portable Python3.13.9 / PyTorch2.10.0+cu130 installation successfully ran CUDA forward/backward on the RTX5070. Packages and ComfyUI services were not changed. CPU NumPy inference avoids adding PyTorch to the addon. ONNX Runtime exists in the research Python but its export dependencies are absent; ONNX is not needed for these candidates.

A prospectively frozen plan defines two objectives on an original784,921-parameter noncausal temporal-convolution backbone: direct full-sequence residual prediction, and conditional clean-residual diffusion with20-step deterministic DDIM sampling. Six dilated residual blocks exchange information across time. This is not the former per-frame MLP or interpolation selector, and is not claimed as a CondMDI reproduction.

Both candidates ran80optimizer steps on four windows from one previously authorized training clip07_01. Training-probe loss fell0.06637 to0.001946 for direct prediction and0.005227 for diffusion. This deliberately tests fitting capacity; it is not evidence of generalization or a comparison of final animation quality. Maximum allocated CUDA memory was84,332,544bytes. Each inert NPZ export is3,154,142bytes and is explicitly research-only.

Seven request-boundary tests pass, including hidden-value perturbation/NaNs, partial position/orientation masks, malformed observations, exact authored-control restoration and independent immutable request copies. Actual trained outputs preserve authored observations exactly. Nonlocal input perturbation changes another frame's prediction. CPU PyTorch versus NumPy maximum absolute differences were4.17e-7 and8.35e-7; repeated sampling with the fixed seed is exact. One four-by33-frame NumPy inference took about0.0074seconds direct and0.140seconds diffusion. These single measurements exclude rig solving, are not120-frame qualification, and establish no viewport responsiveness.

## Next acceptance work

Before broad fitting, freeze the training-only window/mask/augmentation manifest, bounded compute recipe and deterministic validation commands. Keep all old development gates, exposed-data labels and six sealed confirmation clips intact. Evaluate old/new development separately against unchanged projected baselines; add multi-pose/partial-control and longer sequence checks without diluting existing regressions. Check direct and diffusion runtime parity at supported sequence lengths. Neither candidate is installed, distributed, or qualified. Learned style/contact intent, physical refinement, humanoid rig/mesh breadth, quadrupeds, connector, human usability and equivalent Cascadeur comparison remain open.

## Research and data suitability

The CondMDI official implementation is MIT, but its pretrained models use HumanML3D and its dependencies/datasets have separate terms. None of those weights, assets or dependency code was imported. Its conditional sequence design is relevant research, not proof of the best local architecture: https://github.com/setarehc/diffusion-motion-inbetweening and https://arxiv.org/abs/2405.11126 .

LAFAN1 was considered but not selected because its publisher labels the dataset CC BY-NC-ND4.0: https://github.com/ubisoft/ubisoft-laforge-animation-dataset . The existing pinned CMU/Hahne data and publisher-use evidence remain the current source. The conversion notice states no additional restrictions and describes the artificial first-frame pose and retargeting limitations: https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt . The CMU homepage timed out during this pass; its earlier project provenance record remains preserved.

Evidence: training/b4artists_ml/results/shape-isolated-profile-v1 and sequence-feasibility-v1; sequence_feasibility_plan_v1.json. No new source assets, paid services, addon runtime edits, installation, commit or push.
