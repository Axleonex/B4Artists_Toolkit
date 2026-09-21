# Projected-risk selector: prospective experiment

The full original goal remains unchanged. This experiment addresses learned temporal quality; it does not replace the animator workflow, physics, rig support, independent usability or Cascadeur comparison requirements.

The training-only proposal diagnostic uses the first window in each of 466 training cohorts. Its hidden-label position oracle improves average position by 10.3%; the existing position-plus-0.1-rotation criterion also passes the diagnostic gates. Neither oracle is deployable. These results justify testing a learned selector, not a quality claim.

Freeze one 596-input, 32-hidden-unit, 12-choice model with 60 epochs, batch size 64, learning rate 0.001 and regularization 0.0001. The candidates combine linear/Hermite/shape/v20 positions with linear/Hermite/v20 rotations. Choice is constant over an authored interval and reads only observed poses, timing and fixed-grid proposal descriptors. There is no per-frame switch, hidden-label access, or mixing of already projected skeletons. Zero motion retains the established exact stationary reference.

Generate actual fitted costs for all 7358 training windows using the same group-excluded v20 parents and unchanged 48-step projection. Optimize the equal-cohort expectation of fitted position error plus 0.1 rotation error, normalized by each training cohort's best complete procedural control. Deploy the fixed argmax; report the expectation/argmax gap and how often selected components use the frozen learned expert. A learned selector is distinct from a new trajectory generator, and procedural selections remain labelled procedural.

Freeze weights before loading either exposed development partition. Keep all original old/new/combined gates, source/model hashes, sampling, physical-edge/priority checks and sealed confirmation ownership unchanged. Reproduce the complete label generation, fit and development evaluation in a second unique directory. Each full run is capped at three hours and 128 MiB of generated files, with four BLAS threads. No downloads or external services are needed.

Twelve selector and six proposal-pool pre-fit checks pass. The initial selector's stationary exact-equality test found a one-ULP procedural-reference difference; the preserved pre-fit correction selects the existing stationary reference without weakening the check. Existing runtime and package 0.17.5 remain unchanged. Passing research gates alone does not qualify a release or complete the goal.
