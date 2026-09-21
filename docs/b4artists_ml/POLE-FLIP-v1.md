# Flip Pole Side v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive, and no 0.33 package has been created.

## Animator workflow

Each supported Hand and Foot row now shows **Flip Side** beside **Align Bend** on a dedicated action row. Flip Side places the owned elbow or knee helper opposite the limb's current evaluated bend plane. Enable Elbow Direction or Knee Direction, then solve to request the opposite bend. The operation preserves the toggle, rig pose, source animation and helper distance, using the same 0.4-body-scale stability minimum as Align Bend. Distinct hover descriptions explain the two actions.

Stop Live Solve and finish or cancel a running solve first. A straight limb has no stable side to invert, so the action rejects it without changing the helper or rig. Parented, constrained, animated, driven, replaced, non-finite or delta-transformed helpers also fail before mutation.

## Architecture and compatibility

Align and Flip share one evaluated semantic-limb implementation. Both convert the displayed helper through the saved motion transform, project the middle joint away from the root-to-end axis, and move only the owned helper. Align uses the projected bend; Flip uses its negative. The ordinary geometric pole residual and all existing solve gates remain unchanged.

Focused tests cover BoneForge, generated Rigify Basic/Default, Rigify Basic/Default metarigs and an independently authored Unity-style FBX humanoid. All four hand/foot helpers, operator wiring, invalid-state rollback and enabled Foot R solve/reload/Keep behavior are covered.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/pole-flip-v1.json` | Six adapters, four helpers, rejection and solve/reload/Keep | 4/4 pass | `11946f75e80c196837adc4ae30f3366a1ee4f61d0eee4e42843e5ad1e9d72019` |
| `training/b4artists_ml/results/pole-align-after-flip-v1.json` | Refactored Align compatibility | 4/4 pass | `ea1d611877f80c0a6382070f3df37b8736ad00c6548fc513ac21b180cf98231f` |
| `docs/b4artists_ml/body-preview-ui-vpole-flip-v1.json` | Rigify Default foreground modal/Escape/Undo/Redo/Keep journey | PASS | `38604ce87cfd67f595bf0cb4600abefa109221be40d97342c13fafbfebc5a64d` |
| `training/b4artists_ml/cache/body-preview-ui-vpole-flip-v1.png` | Screenshot from the passing foreground journey | Captured | `70ed26903b914bcd943de3e81eb6474963df2cd760e77095665979baf7dc583c` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing preview lifecycle; historical filename retained | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |

The six focused opposite-direction errors range from `3.19e-7` to `9.68e-7` radians. The real-window Rigify Default operation reaches `1.63e-7` radians and the modal solve finishes at `6.12e-7` after 1,588 evaluations and 9.46 seconds of solver work. The affected Flip, Align, Context Preview and Base suites pass 51/51 methods.

The inspected screenshot shows both action labels fully readable at the narrow test sidebar width. The direction toggle occupies its own row, and Align Bend and Flip Side occupy the row beneath it.

All assertions complete before the installed Blender 5.2 Alpha host's known `ucrtbase.dll` shutdown crash. The process exits are not described as clean.

## Execution and claim boundary

Harness/profile is Codex workspace; authorization tier is `workflow_scaffolding`. Prime stopped in its configured `uv` trampoline before emitting either `recommended_lane` or `actual_lane`; no lane is inferred and no remote patch was applied. Fresh native identity validation remains unavailable because the installed Windows runtimes lack `rfc8785` or `jsonschema`, so this slice used serial execution and review under the existing fail-closed policy. No activation, package, commit, merge or push occurred.

Flip Side is procedural pole-target ergonomics. It exposes an animator-requested alternative bend direction; it does not infer natural pose intent, change learned weights, qualify learned motion, or establish Cascadeur parity.
