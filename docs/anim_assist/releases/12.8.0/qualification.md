# Anim Assist 12.8.0 qualification

Host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`, OpenGL. Checks use a new file and an isolated configuration/scripts directory. The personal installed add-on and preferences were not modified.

## Functional checks

The ZIP was extracted into the isolated profile, enabled and exercised in the actual application. These are synthetic fixtures, not a certification of arbitrary production rigs.

| Check | Evidence |
|---|---|
| Multi-owner nudge, sequencing, alignment, locked-batch atomicity and unchanged source keys | `evidence/behavior.json` |
| Overlap and empty selection reject without partial writes | `evidence/behavior.json` |
| Shared Action Make Unique retains its assigned slot | `evidence/behavior.json` |
| Euler/quaternion correction: neutral creation, authored location/rotation/scale and zero influence | `evidence/behavior.json` |
| Constrained owner rejected without orphan data | `evidence/behavior.json` |
| Quaternion pose-bone correction: neutral creation, authored offset and zero influence | `evidence/behavior.json` |
| Bake preserves stack, Action/slot, frame and evaluated motion; output retained and unassigned | `evidence/behavior.json` |
| Bake ownership survives renaming; another object taking the old name cannot receive it | `evidence/behavior.json` |
| Invalid output slot rejects before assigning a bake | `evidence/behavior.json` |
| Graph native filters, selected-only interpolation, empty selection and Drivers exclusion | `evidence/behavior.json` |
| Native mesh keying inserts three frames, visible in Graph and Dope Sheet | `evidence/behavior.json` |
| Native Tweak Mode on shifted/scaled/repeated/reversed clips; arrangement disabled during editing | `evidence/interactions.json` |
| Native track reordering with no selected clips; clips retain their tracks | `evidence/interactions.json` |
| Independent versus linked duplication | `evidence/interactions.json` |
| Owner-specific Push Down/Stash, including refusal when NLA evaluation is off | `evidence/interactions.json` |
| Existing Action clip creation on an empty owner | `evidence/interactions.json` |
| Undo/redo restores scene positions | `evidence/undo-redo.json` |
| Saved workspace reload retains enabled add-on, visible sidebar and bake owner identity | `evidence/workspace-reload.json` |

The behavioral suite has 11 groups; the native interaction suite has 5. Each includes explicit assertions and cancellation cases. The initial failures in implementation were corrected and rerun; the listed evidence is the final result for this package.

`tests/test_anim_assist_layout.py` registered 98 panels and checked editor homes, parents, menus and preference descriptions, then unregistered without leftover panels. Five Timeline layout regression tests passed. Package syntax, CRC, metadata and source hashes were inspected.

## Interface checks

Actual screenshots and measured region widths are in [evidence/images](evidence/images/). The sidebar uses native regions, panel sizing, theme and fonts. All three editors were captured at 220, 280 and 360 pixels at UI scale 1. Long target names wrap; short primary button labels retain full descriptions in tooltips. Routine curve/breakdown/clip actions are directly visible in their initially open sections. Advanced settings remain folded.

- [NLA, 220 px](evidence/images/nla_editor-220.png)
- [NLA, 280 px](evidence/images/nla_editor-280.png)
- [Graph, 220 px](evidence/images/graph_editor-220.png)
- [Dope Sheet, 220 px](evidence/images/dopesheet_editor-220.png)

No automatic editor split, join or resize is part of the add-on. The qualification harness alone drags native sidebar edges for width checks.

## Review and limits

Separate read-only spec and quality reviews found issues in track-command scope, source navigation, bake ownership/activation, nullable source Actions and shared-reference counting. Those findings were fixed and rechecked. The automated review selector recommended S3; its formal review remained advisory/inconclusive because it lacked a host-evidence receipt. It invoked zero reviewers. This document's evidence comes from the native checks and separate code reviews, not that selector's classification result.

- Corrections support unconstrained object/pose transforms. Driven or constrained rigs, unresolved bones and non-transform source channels are blocked. Constraint baking preserves the source constraints; activation requires them muted or removed.
- Generic key helpers support object Actions. Detached pinned Actions and non-object sources are identified as unsupported. No Action fallback is used when native editor scope is empty.
- Transition/meta/sound strip editing is not exposed. Shared-reference warnings do count Actions inside meta strips.
- The Quick Shelf contains a small fixed set of NLA-qualified shortcuts. It does not run existing key-editing macros against strips.
- External production files, all possible rig types and other host builds are not covered by these checks.
- The Timeline overlay, catalog, configuration and slider implementation match the 12.7.1 baseline. Placement remains bottom-only.

UI rules: actions precede folded options, new actions have NLA header-menu access, group headers are plain, unavailable states remain visible and scope is named. Existing scene settings are retained rather than changing their ownership during this release. **Deviations:** the editor-specific day-to-day sidebar actions are retained as expressly approved by the owner; header menus provide their additional standard access.
