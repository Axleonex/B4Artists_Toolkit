# World-space secondary dynamics — experimental 0.25.0

## Implemented workflow

Secondary Motion now offers Local and World simulation spaces. Local retains the 0.24 channel-space behavior. World samples the selected controls after the candidate, parent hierarchy, rig constraints, object transform and native motion-layer transform have evaluated. It follows their world rotations and positions, then converts the requested result back through each control's actual rig space and publishes ordinary editable action curves.

World location motion can use scene gravity with an adjustable influence. Optional planar collision represents each selected control pivot as a point with an artist-set clearance. It uses the authored support plane or the existing static planar Contact Surface, including bounded mesh participation. Bounce and surface friction adjust normal and tangential velocity. Collision is evaluated from the simulated point at each step, rather than from the uncorrected target.

Every captured priority pose remains exact. A priority pose that conflicts with collision clearance is rejected instead of being silently moved. The retained input action, cancellation, stale-input guards, repeated preview, Restore Input, Keep/Discard, Undo/Redo, save/reload and Restore Source lifecycle remain unchanged.

The backend is `implicit_selected_control_secondary_v2`. It is deterministic physics assistance and contains no learned weights.

## Evidence

Nine host-independent tests cover stable local and world vector/quaternion dynamics, gravity, exact priority envelopes, plane response, bounce/friction, simulated-position bounded-mesh participation, hostile sample steps and invalid settings. Eight real Bforartists tests cover the prior local workflow plus world rotation/location under animated parent controls on BoneForge and full generated Rigify, selected-control gravity, planar collision, conflicting priority-pose rejection, evaluated-rig reconstruction and composition with flight.

The complete same-hash regression passes 465 tests in 49 suites on one 37-file runtime hash set. The deterministic archive passes 42 focused checks while an audit hook denies outbound resolution/process calls; no runtime call is attempted. The exact-package real-window Rigify journey loads the add-on from the extracted archive and passes cancellation, generation, Undo/Redo, Restore Input, Keep and Restore Source. Its 77 cooperative steps measure 27.07 ms p95 and 37.12 ms maximum. Eight raw collision samples are resolved from 0.052155 world units to zero reported final penetration, with maximum evaluated world-location reconstruction error below `2.7e-7` world units.

Package: `releases/b4artists_ml_v0.25.0.zip` (308,382 bytes; SHA-256 `73838652eb575b4d471da4f8d4b51686cbbd82696f22d9afb79f63d5e1a156b1`). It is ready for local testing.

The installed Bforartists 5.1 / Blender 5.2 Alpha host still exits through the previously isolated `ucrtbase.dll` shutdown access violation after writing passing reports. This is not a clean process exit.

## Boundaries

This stage acts on explicitly selected transform controls and applies one setting set per preview. It does not infer hair, cloth, tails, flesh or props, simulate deformable volume or connected particle chains, solve control-control/self/arbitrary mesh collision, handle moving/deforming surfaces, calculate joint torque, or provide continuous-time collision guarantees. Collision uses the selected control pivot plus clearance, not the visible mesh volume.

The feature is not learned motion and does not establish Cascadeur parity. Learned temporal acceptance, production-character and independent animator review, quadrupeds, the optional connector, blind comparison and equivalent-task Cascadeur measurements remain required by the full goal.
