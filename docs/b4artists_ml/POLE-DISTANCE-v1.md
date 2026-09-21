# Pole Distance v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive, and no 0.33 package has been created.

## Animator workflow

Every supported Hand and Foot pole now uses a circular in-front helper that is visually distinct from the arrow-shaped pose target. Its row exposes the last requested normalized value followed by **Set Distance**. The requested value is the radial helper distance from the evaluated elbow or knee in body-scale units. The supported range is 0.1 to 4.0, and a new preview starts at 0.4. Directly dragging a helper does not rewrite the request; Align Bend and Flip Side synchronize it to the distance they preserve or stabilize, clamping a manually dragged helper to the supported maximum when necessary.

Set Distance moves only the owned pole helper along its current radial direction. It preserves the enabled direction toggle, rig pose, source animation, helper ownership and preview lifecycle. The direction can therefore be established manually, with Align Bend, or with Flip Side before changing its reach.

Stop Live Solve and finish or cancel a running solve before setting distance. A missing, replaced, parented, constrained, animated, driven, non-finite, delta-transformed or joint-centred helper is rejected before mutation. A native motion layer moved after preview start is also rejected so placement and solving cannot use different display frames. Invalid numeric values fail without changing the helper, setting, pose, status or source data.

## Architecture and compatibility

The operation evaluates the semantic limb through the active adapter, requires the current native motion transform to match the saved preview-start transform, converts the displayed helper through that frame, normalizes the current middle-joint-to-helper vector and reapplies the requested body-scale distance. It validates the resulting displayed transform and canonical distance before publishing the setting. Align Bend and Flip Side use the same frame invariant. The distance operation does not change the pole-direction residual or solver.

Focused tests cover BoneForge, generated Rigify Basic/Default, Rigify Basic/Default metarigs and an independently authored Unity-style FBX humanoid. They also cover all four hand/foot helpers, actual operator and UI wiring, display shape, requested-value semantics for direct/Align/Flip placement, the supported-distance cap, invalid-state rollback, large-world-coordinate native-motion-frame rejection and enabled Foot R solve/reload/Keep behavior.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/pole-distance-v1.json` | Six adapters, four helpers, rejection and solve/reload/Keep | 5/5 pass | `5ebe669c4893c441964e211f2cc7e6df548d38f3a54178abb3a4b7152b35ee8d` |
| `training/b4artists_ml/results/pole-flip-after-distance-v1.json` | Existing Flip compatibility | 4/4 pass | `11946f75e80c196837adc4ae30f3366a1ee4f61d0eee4e42843e5ad1e9d72019` |
| `training/b4artists_ml/results/pole-align-after-distance-v1.json` | Existing Align compatibility | 4/4 pass | `ea1d611877f80c0a6382070f3df37b8736ad00c6548fc513ac21b180cf98231f` |
| `docs/b4artists_ml/body-preview-ui-vpole-distance-v1.json` | Rigify Default foreground modal/Escape/Undo/Redo/Keep journey | PASS | `3d4971981b9bf3c6516dfbef3dc752699c62a9e6c99deab79ad61b2ace90e107` |
| `training/b4artists_ml/cache/body-preview-ui-vpole-distance-v1.png` | Screenshot from the passing foreground journey | Captured | `75374beb37b6e98bf4d4aa3fc9669b9623908e0e01805961137d85354a6e5b4b` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing preview lifecycle; historical filename retained | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |

The focused six-adapter result reaches 0.85 body scales within `4.79e-8`, with direction-vector change below `1.71e-7`. The real-window Rigify Default journey reaches `0.8500000493`, changes direction by `4.61e-8`, and finishes the modal solve at `9.55e-6` radians after 1,603 evaluations and 9.57 seconds of solver work. The affected Distance, Flip, Align, Context Preview and Base suites pass 56/56 methods.

The inspected screenshot shows `0.85` and **Set Distance** fully readable at the narrow test sidebar width. Circular in-front pole helpers are visible at the elbows and knees.

All assertions complete before the installed Blender 5.2 Alpha host's known `ucrtbase.dll` shutdown crash. The process exits are not described as clean.

## Execution record and claim boundary

Harness/profile: Codex workspace. Authorization risk tier: `workflow_scaffolding`. Declared paths were the two runtime modules, the focused and context tests, this document and the scoped 0.33 planning/user documents. The required Prime preflight stopped in its configured `uv` trampoline with `entity not found` before emitting `recommended_lane` or `actual_lane`; neither lane is inferred. The execution-value policy SHA-256 was `74041cc3740f3165b7a3280583628c2fbe21b60b626d08045eb0560771492466`, and the active adaptive policy SHA-256 was `c0dce1c33ee9d164c51df0ceab2e8022e9e8a35ae98a0bb1f7c33c5e731502a2`. The task had zero lane escalations and continued as one serial native packet under the policy's recoverable pre-host-apply fallback. Validation was the focused 5-test suite, three existing affected suites, the 33-test base suite, a real-window Bforartists journey, screenshot inspection, AST/JSON/whitespace/conflict checks and serial review.

Pole distance is procedural posing ergonomics. It does not infer pose or motion, change learned weights, qualify learned motion, or establish Cascadeur parity. No activation, package, commit, merge or push occurred.
