# Secondary Load From Active v1

Status: verified development 0.37 source; not included in the frozen 0.36.0 package.

## Workflow

Select an assigned pose control and make it active. In Secondary Motion, use **Load From Active**. The panel recalls that control's complete Selected Force, Selected Mass, Application Offset (Local), and Rotational Inertia values. Edit the recalled fields and use Assign Load to update the current selection or transfer the setup to other selected controls.

Recall does not rewrite the stored assignment, touch the candidate or source Action, change selection, or run a solver. The operator requires Pose Mode, an active selected recognized control, the active candidate, a valid rig-bound load record, no competing workflow owner, and an assignment on the active control. Failure leaves all four visible values unchanged. Native Undo and Redo move between the prior panel values and the recalled values.

Schema-1 force/mass assignments recall an exact zero local offset and rotational inertia 1. Schema-2 force-at-offset assignments recall all stored values. The command uses the same strict record validation and Bforartists-only runtime surface as assignment and solving.

## Verification

Eight focused Bforartists tests cover complete schema-2 recall, schema-1 defaults, exact stored-assignment and animation preservation, unassigned active controls, active-versus-selected admission, Pose Mode admission, corrupt records, and all ten competing workflow owners.

- `training/b4artists_ml/results/secondary-load-from-active-focused-v1.json`: 8/8, SHA-256 `54b8f30b4f938029acf5c5599af245ea131a36e935630b89b6ede01bfd21fb16`.
- `training/b4artists_ml/results/secondary-load-from-active-affected-v1-regression.json`: 151/151 across eleven suites on one frozen 44-file runtime, SHA-256 `8ddab61fe4d126a8cb0d03b3144b779f81aa9cbd6f8cfd67a870aa950d9da11b`.
- `docs/b4artists_ml/secondary-load-from-active-ui-v1.json`: passing foreground assignment, recall, assignment Undo/Redo, recall Undo/Redo, cooperative torque solve, solve Undo/Redo, Restore Input, synchronous solve, Keep, and Restore Source, SHA-256 `69e18dab34d5c84b33e89760bd63acff1c657bcf9a073bfb1bf8ceeea25f6c18`.
- `training/b4artists_ml/cache/secondary-load-from-active-ui-v1.png`: visible full-width Load From Active, Assign Load, and Clear Load actions with all four settings and the assigned count, SHA-256 `61dcf14c8d9be2f304d752c5fac009871ebf617fe7ed1204c1fb2c16ff761a39`.

The foreground journey completed 96 cooperative solve steps with 10.6143 ms p95 and 19.2492 ms maximum. Bforartists exited with the established `ucrtbase.dll` child shutdown fault only after the assertions and report completed; clean shutdown is not claimed.

## Claim boundary

This is a deterministic authoring convenience for explicit per-control load settings. It does not infer physics values, select controls automatically, couple forces through a rig, learn from edits, improve the underlying motion model by itself, or establish Cascadeur parity.
