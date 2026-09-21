# Ground velocity feasibility v1

Question: is the steep ground-transition rotation a limitation of leg-only pose correction, or does the current authored endpoint also challenge coordinated torso/arm motion? Reuse the three exact saved grounded-jump scenes at takeoff15and landing33. No pose/contact/timing edits.

Compare root plus six leg FK rotations against root plus the existing whole-body adapter rotations/effectors. Variables are world translation in trunk lengths and local rotation vectors in radians. Measurements are displayed COM/trunk, ankle position/leg length, and ankle quaternion-vector displacement. Desired COM velocity comes from the frozen ballistic endpoints/gravity; both ankle velocities and angular velocities are zero. This compares total instantaneous velocities, not a delta added to the existing native driver velocity. The current frame and native displacement stay fixed during differentiation.

Central differences at0.001,0.0005,0.00025. Least squares rcond0.0001; preserve rank/singular spectrum and residuals for every epsilon. Root/rotation variable normalization defines the minimum-norm diagnostic; it is not a uniquely optimal physical action. Verify proposed increments over1/30,1/120,1/480seconds on the actual host, without keying or saving them. These finite increments test the linearization and are not a solved trajectory or a motion-quality gate. No new naturalness threshold or global impossibility claim.

Restore channels after each variant, retain all actions/drivers/objects/input bytes. At most900seconds internal/1000seconds per serial rig process and original deadline1789053845. No fits, downloads, source changes or retries. The canonical code router failed before application with the known uv trampoline spawn error; authorized DEGRADED_NATIVE_CONTINUE stays within training/b4artists_ml and docs/b4artists_ml, no prohibited boundary crossed. Same goal, checkpoint67,100evaluation cap and deadline. Author diagnostics are not independent review.

## Completed comparison

All three actual-rig runs completed both boundary poses and both control sets across all three finite-difference sizes. Every temporary pose was restored; source channels, actions, drivers, objects and input scene bytes remain unchanged. At epsilon0.00025, takeoff results are:

| Rig | Leg-only peak local control rate (rad/s) | Whole-body peak local control rate (rad/s) | Whole-body largest-rate control |
|---|---:|---:|---|
| boneforge | 3239.62 | 33.09 | clavicle.fk-L |
| rigify_basic | 81.97 | 27.78 | shoulder.R |
| rigify_default | 81.97 | 27.78 | shoulder.R |

The whole-body rates are stable across the tested finite-difference sizes. The leg-only BoneForge result is highly sensitive and has a very small singular value; numerical rank15 and a tiny linear residual must not be interpreted as a physically useful solution. These are minimum-norm solutions under the declared coordinate metric, not minimum-maximum-speed or force-optimal solutions. They do not prove global infeasibility.

The whole-body finite updates still produce material COM/contact errors over1/30second. Errors shrink with shorter steps, demonstrating that the local derivative is useful but its direct increments are insufficient as animation. COM velocity residuals are normalized by trunk length; the reported contact residual combines normalized ankle linear velocity and angular velocity terms and is not a distance or collision measurement. The source stand pose is repeated at takeoff/landing, so symmetric results are not independent motion diversity.

Decision: retain the coupled spatial projection and whole-body derivative model as research building blocks. The next candidate must solve a continuous sequence with endpoint velocities, contacts, priority poses and temporal regularization together; a pose-by-pose bake or direct Jacobian increments are not qualified. Do not silently replace fixed ankle contacts with toe pivots, change authored poses or retime the frozen request to create a pass. Alternative contact geometry may be evaluated only as a separately declared request. No model is promoted and nearby training remains paused.

The current host again exits3221225477after completed assertions. All4731previously protected artifacts remain unchanged. This is author research evidence, not independent usability or Cascadeur comparison.
