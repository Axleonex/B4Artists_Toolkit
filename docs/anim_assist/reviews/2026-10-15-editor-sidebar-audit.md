# Graph Editor and Dope Sheet sidebar design audit

Date: 2026-10-15. Baseline: Anim Assist 12.7.1 (`f1d94a0`).
Method: inspect registered layout, panel drawing and relevant operator scope;
compare with the supplied screenshot and editor roles. No runtime tests run.
This is a design/source audit, not a functional certification of every tool.

## Conclusions

| Editor | Current design | Verdict |
|---|---|---|
| Graph | Select, Shape Curves, Retime, Clean Up, Pose & Rig, Quick Shelf | Appropriate overall organization; fix misleading placement, excessive nesting and scope contracts. |
| Dope Sheet | Block, Inbetween, Time, Mirror & Match, Keys & Channels, Shelf & Macros | Appropriate pose/timing emphasis; combine overlapping groups, promote selection and make baking discoverable. |
| NLA | No dedicated Anim Assist sidebar | Add its own strip/track organization; do not copy either sidebar wholesale. |

Graph supports editing property values, handles and curve shape; Dope Sheet
primarily presents keys across time and channels. Both can share some tools,
but they need different emphasis and an explicit target scope.

## Findings

### 1. High: selected-key tooltip conflicts with whole-action mutation

`operators/keymanager_ops.py:54` defines Batch Set Interpolation. Its tooltip
at line 59 promises selected keys. Execution at lines 69-80 instead fetches
all curves from the active object's action and assigns interpolation to every
key without checking selection. The panel calls it from Batch Interpolation
in `ui/panels.py:17`, in both Graph and Dope Sheet.

Required before redesign implementation: make Selected Keys the explicit
default contract, with Whole Action as a separately named scope if retained.
Do not change only the panel label while keeping a contradictory tooltip.
Keep this source-confirmed mismatch distinct from the reported missing-key
issue; this audit does not establish a connection to that issue.

### 2. High: “visible curves” needs a real editor-visibility contract

`core/context_utils.py:30` describes visible curves but iterates all objects
in the view layer at line 43. It checks curve hide/mute/lock flags, but does
not resolve the current editor's complete filtering or selected-owner scope.
Advanced selection operators use this helper, including Select All Visible
Keys (`operators/p2_select_ops.py:36`).

Separately, `operators/curve_tool_ops.py:27` and
`operators/keymanager_ops.py:46` fall back to the active object's action when
the selected-editable-curve list is empty. These contracts differ.

Design consequence: display and enforce the editor-local target. Empty
selection must not silently mean all keys in an action. The exact runtime
effects of editor filters, shared actions and action slots still need checking;
this is a scope concern, not a claim that every selection command fails.

### 3. Medium: primary actions are hidden behind nested folds

`ui/layout_homes.py:263` adds DEFAULT_CLOSED to every child panel, even inside
the initially open Shape Curves or Block group. The default Graph compact
setting is False (`core/properties.py:134`), and individual curve tools have
another closed child panel (`ui/panels.py:95` onward).

The supplied Dope Sheet screenshot shows the same pattern: Block is open, but
Breakdown, Presets and Modal Breakdown remain folded.

Recommendation: put common actions directly in the main group body. Keep
advanced settings and uncommon tools folded. Do not require Group -> Tool
Panel -> Action for routine work. This follows the owner's earlier feedback
that repeated submenu/fold navigation is too slow.

### 4. Medium: Graph “Interpolation Options” is misidentified

`ui/layout_homes.py:51` places `ANIMASSIST_PT_p3_interpolation` under Shape
Curves. Its body (`ui/p3_panels.py:398`) contains quaternion/Euler awareness,
tangent matching, missing-key behavior and visual-transform options.
`operators/p3_breakdown_ops.py:87` reads these into BreakdownOptions.

These are breakdown/pose sampling options, not ordinary Constant/Linear/
Bezier curve interpolation. Meanwhile the actual interpolation and handle
buttons are inside Key Manager, itself under Clean Up.

Recommendation: move real interpolation and handle actions into Shape Curves.
Relabel/rehome the current panel as Breakdown Options with its associated
pose/tween tools; avoid an unexplained settings panel separated from its action.

### 5. Medium: shared Key Manager overexposes handle tools in Dope Sheet

`ui/panels.py:15` draws one body for Graph (`:247`) and Dope Sheet (`:272`).
It includes left/right handle selection and handle types as well as key types,
interpolation and timing commands.

Recommendation: Graph keeps handle-side selection and curve-shaping controls.
Dope Sheet prioritizes key types, temporal selection, interpolation and timing.
Handle type can remain an advanced interpolation setting, since Dope Sheet
can still apply it; handle-side selection belongs with the visible handles
in Graph. Share drawing helpers, not the whole mixed panel body.

### 6. Medium: bake is concealed by the Dope Sheet group label

`ui/layout_homes.py:72` places `ANIMASSIST_PT_p7_bake_ds` under Mirror & Match.
The panel is labelled Bake (`ui/p7_panels.py:388`). Baking is useful in this
editor, but its parent does not tell the user where to find it.

Recommendation: put it under Bake & Finish in Dope Sheet. In Graph, keep the
less frequent pose/match/bake utilities in a clearly labelled secondary group.

### 7. Medium: settings appear before the actions they configure

Breakdown opens with Factor & Mode before its actions (`ui/p3_panels.py:81`).
Retime starts with anchor/pivot and scale fields before its action buttons
(`ui/p6_panels.py:76`). The bake panel similarly leads with range/channels.

Recommendation: primary actions first, then clearly grouped scope and Options;
use Adjust Last Operation for supported completed operations. Distinguish
configuration sliders from actual live-preview sliders. This is a design
recommendation; converting property ownership must not break existing operator
behavior or silently discard saved settings.

### 8. Low: visual and advanced-procedure consistency

Group headers currently draw icons (`ui/layout_homes.py:152`), contrary to
the current Bforartists UI rule for add-on panel headers. The Dope Sheet's
Shelf & Macros group also includes the system/setup panel (`:80`).

Recommendation: plain section headers with consistent text labels. Keep a
small Quick Shelf in each editor; leave macro authoring, setup and recovery
in their appropriate settings/procedure homes, with links where useful.

## Proposed revised order

### Graph Editor

Target summary / selection scope, followed by:

1. Select & Channels.
2. Shape Curves — open initially; direct Smooth, Push/Pull, Ease and blend
   actions, with real interpolation/handle controls nearby.
3. Retime — key-time operations, with their scope and pivot explicit.
4. Clean Up — redundancy, diagnostics and protected-key handling.
5. Pose & Bake — secondary pose/match tools and baking; breakdown options stay
   beside any exposed breakdown action.
6. Quick Shelf.

Keep the current action-based structure. Do not replace it with NLA-style
clip controls or the Dope Sheet's stage terminology. Driver curves and other
unsupported curve sources must be identified rather than treated as Actions.

### Dope Sheet

Target summary and a compact direct-selection row, followed by:

1. Block & Tween — open initially; combine the current Block and Inbetween
   group bodies, keeping quick breakdowns and common inbetween actions visible.
2. Timing — existing key-time tools and Anim Offset, with clear action/scope.
3. Keys & Channels — key types, range/structural selection and channel isolation.
4. Pose & Match — mirroring, matching and related pose utilities.
5. Bake & Finish — baking plus relevant final checks.
6. Quick Shelf.

This retains a pose-to-timing workflow, moves key selection ahead of secondary
rig utilities and gives baking an identifiable home. Handle-side editing is
offered through Graph navigation; advanced handle type remains available.

## Implementation boundaries and follow-up

- This audit proposes changes; it does not alter current registration or tools.
- Fix selection-scope and target semantics before moving those actions into
  more prominent positions. Layout polish cannot establish data correctness.
- Do not merge the add-on's private animation-layer engine with native NLA
  tracks. `core/p11_layer_engine.py:11` documents its separate Action storage.
- Animation Layers and Lipsync sidebar variants are defined in source but are
  not registered in Dope Sheet/Graph; their current registered homes are moved
  to Scene Properties by `layout_homes.py`. They were not counted as visible
  misplaced sidebar panels merely because class definitions exist.
- Later runtime review should cover empty selection, editor filtering, shared
  multi-slot actions, Tweak Mode, undo/cancel, narrow widths and existing tools.
  No tests are added or run under this design-only request.
- Preserve the bottom-only Timeline and the 12.7.1 release during design work.

## Rule review

R1/R5: current action/settings order needs revision. R3/R4: retain existing
menu/tool access; no new operators were added in this task. R6/R7: use native
fields/checkboxes and plain panel headers in the proposal. R9: keep one sidebar
home per feature with editor-specific useful copies. R10/R11: visible unavailable
states and truthful scope/tooltips are required. R12: narrow-width fit is not
runtime verified. R13: no proposed control may be disconnected from a real
operation. R14: retain familiar editor structure while correcting placement.
No runtime pass or universal usability claim is made.

## External role references

- [Graph Editor curve editing](https://docs.blender.org/manual/en/5.0/editors/graph_editor/fcurves/editing.html).
- [Dope Sheet timing and selection](https://docs.blender.org/manual/en/5.0/editors/dope_sheet/editing.html).
- [NLA clips, shared actions and Tweak Mode](https://docs.blender.org/manual/en/dev/editors/nla/editing/strip.html).

## Implementation follow-up

The owner approved and requested these changes. Local release 12.8.0 fixes selected-key interpolation and editor scope, provides direct primary actions, moves real curve interpolation/handles into Shape Curves, relabels Breakdown Options, separates Dope Sheet baking and relocates procedure panels to Scene Properties. New NLA tools have their own strip/track sidebar. The historical findings above refer to the 12.7.1 baseline, not the updated implementation.

See [12.8.0 qualification](../releases/12.8.0/qualification.md) for actual native-host checks and explicit unsupported-source limits.
