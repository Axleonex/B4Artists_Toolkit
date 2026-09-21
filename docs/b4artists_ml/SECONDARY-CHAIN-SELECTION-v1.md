# Bounded direct-chain selection in development 0.37

Development 0.37 adds **Select Direct Chain** to the existing deterministic Secondary Motion panel. The animator chooses an active pose control, a direction, and a maximum of 2-32 controls. The helper follows only an eligible direct parent hierarchy or a single eligible child at each step, selects the validated result, and enables **Couple Selected Chain**. It reduces repetitive selection setup before the existing editable rotation-chain solver.

## Workflow

1. Generate or reopen an animation candidate and enter Pose Mode.
2. Open **Secondary Motion**, choose **Local**, enable **Rotation** and **Couple Selected Chain**.
3. Make one intended control active.
4. Choose **Toward Children** or **Toward Parents**, set **Maximum Controls**, and click **Select Direct Chain**.
5. Review the highlighted controls. If the helper replaced a selection you need, click **Swap Previous Selection**. Clicking it again reapplies the derived chain.
6. Adjust propagation and spring settings, then run **Preview Secondary** through the existing copied-candidate workflow.

The helper accepts only controls present in every captured pose with complete editable rotation curves. Recognized rig-profile controls and non-deforming custom controls are eligible; unrecognized deform bones are not. It rejects structural Rigify/BoneForge names, hidden or unselectable controls, partial rotation locks, driven rotations, muted/locked/modified curve groups, child branches, topology gaps, stale candidates, active workflows, non-Pose-Mode use, incompatible World/location-only settings, and invalid bounds. A parent walk stops at the first ineligible direct parent. A child walk stops when no eligible direct child remains and rejects ambiguity when more than one eligible direct child exists.

Selection is published only after the complete chain validates. An injected selection-write failure restores the exact prior selection, active bone, chain mode, status, and previous swap record. The swap record is bound to the armature bone signature, runtime Action/slot identity, and exact candidate curve token. It revalidates locks, drivers, visibility, capture coverage, editable curves, and direct topology before restoring a coupled chain; malformed, stale, or cross-candidate records fail before mutation. If the selection replaced by the helper had coupling enabled but was not itself a valid chain, its selection and active bone remain reversible while coupling is safely restored Off. The candidate action, source action, anchors, pose values, curves, and rig structure are unchanged by selection or swapping.

Bforartists does not restore pose-bone selection through native Redo in the tested host. The explicit two-way **Swap Previous Selection** action provides the qualified reversible selection workflow within the current editing session. Its pointer-bound record stays usable after an ordinary Save and is cleared after file load, Undo, or Redo so it cannot target reconstructed datablocks. Existing Secondary Motion candidate output retains its separate Undo/Redo, Restore Input, Keep, Discard, save/reload, and source-recovery behavior.

## Evidence

- Focused host regression: 16/16 tests pass on BoneForge and generated Rigify Default, including both traversal directions, operator and backend mode/settings gates, every busy owner, custom/deform admission, stale eligibility, exact Action/slot binding, save/reload lifecycle, injected-failure rollback, bound selection swapping, and solver handoff. Evidence: training/b4artists_ml/results/secondary-chain-selection-affected-selection-v1.json, SHA-256 f920ab7a1ba2087ede618d375fd6b7ee540cd1f336b9d7a317d513953a86d9ec.
- Affected host regression: 66/66 tests pass across direct-chain selection, the complete selected-control secondary solver, visible-state recovery, and base registration/recovery on one frozen 44-file runtime set. Every child and the aggregate bind the common runner and affected driver, and all runtime, test, and harness bytes are rechecked before publication. Evidence: training/b4artists_ml/results/secondary-chain-selection-affected-v1-regression.json, SHA-256 811c19c5ed57d5f9ee0f9593bd49d072c6f4ad2376c92d00ec75caeb663e69a0.
- Foreground Bforartists journey: the sidebar operator selects the Rigify chain; real Ctrl-Z/Ctrl-Shift-Z events clear volatile swap ownership; a new session-local swap restores and reapplies the selection; and the result enters the existing editable chain solver. The launcher and host agree on 49 frozen runtime/test/runner/fixture inputs, and a bounded source-Action digest matches before and after. Evidence: secondary-chain-selection-ui-v1.json, SHA-256 18ea1d14a415d78f3c7bd96fdc4c38f8c3d118bb30a6538f1814c8926f343371.
- Python compilation passes for the runtime, tests, affected runner, and foreground runner.
- The known Windows ucrtbase.dll host shutdown fault still occurs after successful in-process reports; clean shutdown is not claimed.

This feature uses deterministic hierarchy and curve validation. It does not detect which controls represent hair, cloth, tails, flesh, or props; simulate deformable volume; learn secondary behavior; validate visual quality; or establish Cascadeur parity. Independent animator review remains open. Frozen release 0.36.0 is unchanged and no development 0.37 package has been published.
