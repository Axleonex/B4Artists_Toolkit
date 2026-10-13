# Requirements — Inline Family Clusters

Implementation and local packaging are complete. Requirement acceptance is tracked separately below; the milestone remains Needs Review.

| ID | Requirement | Completion evidence | Owning plans |
| --- | --- | --- | --- |
| AA-01 | Draw seven fixed family clusters in Tween, Curves, Timing, Keys, Pose, Bake, Motion order; quick actions appear immediately beside their own family menu. | Recorded draw order and native screenshots | 01-01, 01-02 |
| AA-02 | Any of the 70 catalog presets can be selected as a quick button using a native checkbox. Unchecking removes only its quick copy; its menu entry remains. | Exhaustive preference-to-draw mapping | 01-01, 01-02, 01-03 |
| AA-03 | Quick selections belong to add-on preferences, apply to all Timeline strips, persist through a normal preferences save/restart, and preserve an explicitly empty selection. | Scene switch, two strips, reload and export/import fixtures | 01-01, 01-03 |
| AA-04 | Default quick set is B25, B50, B75, DRAG, SMOOTH, NUDGE_LEFT, NUDGE_RIGHT, RIPPLE, RANGE, ENDS, MIRROR_SELECTED, BAKE_STEP, TRAIL_SHOW. Reset restores exactly this set without changing animation. | Default and reset preference snapshots | 01-01, 01-02, 01-03 |
| AA-05 | Width changes never automatically remove chosen buttons or move them into More; native header panning reaches every chosen action at normal control sizes. | Native 480/800/1280/1920 logical-width captures at 100%/150% scale, including rightmost actions | 01-02, 01-03 |
| AA-06 | Inline and menu copies use the same catalog operator, arguments, invocation mode, unavailable reason, tooltips, and Timeline target. | All 70 mappings plus effect comparisons for every default button and every promoted original shortcut | 01-02, 01-03 |
| AA-07 | Selection, object mode and running sessions change enabled/highlight state only; they do not reorder quick buttons. Buttons explain unavailable prerequisites and actual scope. | Object/Pose, missing selection, Offset state and disabled-button captures | 01-02, 01-03 |
| AA-08 | Preserve the existing strip pairing, native Timeline key area, 12.4.0 operator math, Breakdown anchor explanation, Drag cancellation and native Undo/Redo. | Baseline comparisons and gesture fixtures | 01-02, 01-03 |
| AA-09 | Existing Graph Editor/Dope Sheet toolbar settings remain scene settings; Timeline quick selection has a separate preference home and is not hidden by those legacy scene switches. | Cross-editor/scene configuration checks | 01-02, 01-03 |
| AA-10 | Build a separate local 12.5.0 ZIP with consistent version fields, an explicit changed-file inventory, hash, guide and qualification report. Preserve older ZIPs and release evidence. | Package receipt and exact-ZIP checks | 01-04 |
| AA-11 | Record actual Bforartists rendering and owner task completion separately from stand-in or source-only checks. Do not mark the usability endpoint passed without owner evidence. | Host identity and owner UAT record | 01-03, 01-04 |

## Endpoint

## Execution acceptance status

| IDs | Evidence status |
| --- | --- |
| AA-01, AA-02, AA-03, AA-04, AA-07, AA-09 | Implemented; model/RNA and Blender stand-in checks pass. Actual-host usability remains under AA-11. |
| AA-05 | Partial: seven width/scale cells measured; 1920 logical at 150% display-limited and unverified. |
| AA-06 | Mapping parity passes for all 70; effects partial because trail geometry fails accuracy. |
| AA-08 | Existing dispatcher/operator/lifecycle code preserved; native Redo and selection recovery failures remain unresolved. |
| AA-10 | PASS: exact 12.5.0 ZIP, hash/inventory/version checks, guide and qualification report. |
| AA-11 | UNVERIFIED: actual Bforartists and owner workflow checkpoint pending. |

Details: [qualification](../../releases/12.5.0/qualification.md), [owner tasks](../../releases/12.5.0/UAT.md). The profile overwrite incident is recorded in qualification and has not been restored.

### Milestone endpoint

A local candidate may be packaged with documented outstanding qualification. The milestone passes only when all requirements have measured evidence, every default quick button is reachable and executes correctly, and the owner can complete the scrub-adjust and custom-selection tasks without menu hunting for pinned actions. Missing Bforartists or owner evidence remains pending rather than being relabeled as a pass.

## Deferred

Arbitrary button reordering, automatic usage learning, multiple quick-set profiles, a third row, new animation algorithms, replacement icons, new global scope controls, unrelated sidebar changes, deployment and public publication.
