# Coupled ground continuity diagnostic v2

Follow-up to the66passing spatial samples in v1. No solver or tolerance change. Use quarter-frame sampling throughout both ground intervals, plus offsets2^-1through2^-8frames approaching takeoff15and landing33. Record original and projected evaluated control quaternions. Compute normalized-quaternion geodesic angular secants in seconds; inspect their response to temporal resolution. No naturalness threshold is invented and no pointwise pass qualifies the temporal workflow. Keep qualified=False.

Same frozen three input scenes,24iterations, translation limits, contact/COM/orientation/length gates, source restoration and resource/deadline boundaries as v1. This is the adaptive measurement stage of the same authorized coupled-contact investigation; canonical route failed before host application and native continuation stays within training/docs. Preserve all v1evidence. No generation or production change.

## Measured outcome

The66sparse and402dense actual-rig samples all meet the frozen spatial gates. Original channels, actions, objects and input scene bytes are preserved. This is468pointwisechecks, not468independent animations. Maximum dense errors:

| Rig | COM / trunk length | Contact / leg length | Max iterations | Near-takeoff angular secant (rad/s),0.5frame to1/256frame |
|---|---:|---:|---:|---|
| boneforge | 0.00019145 | 0.000000217 | 4 | 21.61 to 230.89 |
| rigify_basic | 0.00019969 | 0.000000199 | 5 | 15.28 to 39.15 |
| rigify_default | 0.00019969 | 0.000000199 | 5 | 15.28 to 39.15 |

BoneForge angular secants grow strongly as the sampling interval shrinks. Rigify settles near39rad/s; its finite value does not establish acceptable animation. The analytic straight-leg limit provides a plausible explanation for BoneForge: for fixed two-link lengths, knee bend near full extension varies with the square root of remaining extension, so nonzero extension speed can produce an unbounded bend rate. This is an inference about the restricted leg/root method, not a proof that every whole-body solution to the user request is impossible.

Decision: retain the production contact/flight overlap rejection. The new alternating projection is useful as a constrained spatial building block, but it must not be baked into a purportedly natural transition. A temporal solver must detect incompatible pose/contact/timing choices, preserve priorities, and test velocity/acceleration/limits across complete motions. Toe roll, contact release and altered authored pose are distinct animator choices; do not silently use them to pass the frozen request. Nearby learned fits remain paused. Full learned-motion and Cascadeur/human qualification remain open.

All six native processes completed assertions then returned the existing3221225477shutdown fault. No runtime file, model, data split, release, commit or install changed. The dense-script creation initially encountered a shell quoting SyntaxError before any process started; corrected quoting created the intended unchanged algorithm. Source/metric validation is author evidence, not an independent review.
