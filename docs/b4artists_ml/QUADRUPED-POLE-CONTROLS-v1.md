# Quadruped Pole Controls v1

Development 0.35 adds **Flip Side** and body-scale **Set Distance** beside each schema-4 quadruped Pole Target. Flip Side places one helper opposite the limb's current evaluated bend ray while preserving its radius. Set Distance moves that helper along its current ray to an animator-requested distance from 0.1 to 4 body scales without changing its direction.

The operations support generated Rigify cat, horse, and wolf rigs. They preserve the selected helper object, every other target, target options, the source Action and slot, rig pose, IK/FK and Pole Vector modes, Spine Follow, Neck Share, Auto Key, and live source animation. Both operations invalidate the prior solve signature and metrics so **Keep as Pose Anchor** requires another solve. Concise side-first panel labels keep all four pole rows distinguishable at narrow Bforartists panel widths.

Admission rejects legacy schemas, unknown labels, playback, active animation workflows, native motion layers, locked position or scale channels, stale or externally controlled helpers, changed source bindings, unsupported helper animation or parenting, malformed distances, singular rays, and altered rig transforms. Post-update validation detects dependency-handler interference across the complete helper topology and rig object transform, including `matrix_parent_inverse`. Full rollback restores owned state; if a different workflow starts during the edit, rollback restores only the selected Pole Target while preserving the new workflow's state.

## Evidence

- Focused Bforartists: 8/8 tests. Flip Side covers all four limbs on generated cat, horse, and wolf; Set Distance preserves independent ray oracles; solve and Keep remain valid; save/reload survives; visible operators have native Undo/Redo; hostile inputs and lock state fail atomically; dependency handlers and a parented-rig parent-inverse mutation are detected and rolled back.
- Affected Bforartists: 136/136 tests across 18 suites on one frozen 44-file runtime source map.
- Foreground Bforartists: the visible generated-wolf workflow flips a fore pole, sets its distance to 0.62 body scales, performs native Undo and Redo, and preserves the source Action, slot, pose, modes, helper identity, payload, and requested distance. The screenshot verifies side-distinguishable labels at the recorded narrow panel width.
- Serial read-only review: PASS after object-transform, helper-lock, active-workflow, evidence-binding, tooltip, and narrow-label findings were closed.

Evidence files:

- `training/b4artists_ml/results/quadruped-pole-controls-focused-v1.json` — SHA-256 `80e95f645199dac8c0ab94b0b730704ba70d2d2aafc6bec7df4eae588820b5a8`
- `training/b4artists_ml/results/quadruped-pole-controls-affected-v1-regression.json` — SHA-256 `23b054eb364e476a5c07b88ec180abee52aa85e040b689a979a1aaa293a69f9f`
- `docs/b4artists_ml/quadruped-pole-controls-ui-v1.json` — SHA-256 `9479eff32b0104ec544ac11150e34b22be9806159d90f9c91e8de56b070f853d`
- `training/b4artists_ml/cache/quadruped-pole-controls-ui-v1.png` — SHA-256 `04d99c0cf40fc6111d8cf72d2f658b071f948354de539aaad8f5571324f91233`
- `docs/b4artists_ml/quadruped-pole-controls-routing-v1.json` — SHA-256 `ca46b809da852a236bf44b72e3a4eb14fa107d6700de058be4a5b303ccab38cc`
- `training/b4artists_ml/results/quadruped-pole-controls-v1-final.json` — SHA-256 `e5749f612b66d3f313889e0cfced58d604467115d180bf82f14a4b6f93dbd199`

Every Bforartists run completed its assertions and wrote fresh evidence before the known `ucrtbase.dll` shutdown failure. A clean host exit is not claimed.

These controls use deterministic current-frame geometry. They do not provide learned quadruped motion, animated-range Pole Vector conversion, imported/custom-rig support, gait generation, physics refinement, human usability evidence, or Cascadeur parity. The full project goal remains incomplete.
