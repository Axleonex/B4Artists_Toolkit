# Learned shape-reference result v18

The single prospectively fixed configuration completed and reproduced exactly: five supervised hidden fits and five exact readout fits, six identical serialized artifacts, identical non-runtime reports. All16 moving and16 stationary actual-rig/editable-source-recovery cases passed. The existing host shutdown access violation remains. No temporal model is promoted.

| Projected validation measure | Result | Required |
|---|---:|---:|
| Learned position error, body units |0.080399351|lower than all controls|
| Shape-only procedural position error |0.081010224|explicit comparison control|
| Learned position ratio to best control |0.992459|at most0.95|
| Rotation ratio |1.003059|at most1.02|
| Velocity ratio |1.015899|at most1.05|
| Acceleration ratio |1.066366|at most1.05|
| Worst cohort position ratio |2.742013|at most1.10|

The shape-only reference improves average position by13.412% relative to the original linear control. The learned correction adds only0.754% over that stronger reference. This distinction prevents a procedural gain from being credited as learned animation. Worst-cohort ratio falls from11.739 in v17 to2.742, but remains unacceptable. Endpoint and true physical edge-length checks pass. Position, acceleration and cohort quality gates fail; thresholds are unchanged, with the additional procedural control making the comparison stricter.

Training-only diagnosis shows that the reference bounds remove some excursions but cannot represent all real motion arcs without a learned correction. Startup-frame checks did not justify excluding clips. All old windows, holdouts, model artifacts and failed gates remain. Previously exposed validation is research evidence, never blind confirmation.

Next prioritize a bounded, prospectively specified expansion of distinct motion coverage using the verified publisher terms. Preserve all old holdouts and define any new confirmation set before fitting, without calling catalog groups independent actors. Keep the full learned-motion, physics/refinement, broader humanoid/quadruped, performance, independent usability and equivalent Cascadeur requirements. No new data acquisition is part of v18.

Evidence: shape_trajectory_v18/report.json, shape-trajectory-reproduction-v18.json, shape-trajectory-host-v18.json and stationary-trajectory-host-v18.json under training/b4artists_ml/results. Model SHA256:5da9061208b0e9fbabf08eed6fa8f83961cf5453c63ad38150fb387f73d54e30. Experimental0.17.2 remains the unchanged installable package.
