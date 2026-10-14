# Native Timeline toolbar — tool access requirements

Owner requirement, 2026-10-12: provide the same practical access to animation tools as AnimBot's toolbar. This supplements the [native application design](2026-10-12-native-timeline-toolbar-design.md). Status: design requirements and source inspection; no implementation or functional parity pass.

Reference: [AnimBot's official tool documentation](https://animbot.ca/tooltips/en/), consulted 2026-10-12. It documents button actions, continuously adjusted tools, secondary options, a slider popup and command search. The access design below uses Bforartists conventions and original UI controls.

## Required interaction

1. **Direct actions:** every mapped available animation action can be pinned beside its family and run with one click. Common actions must not require opening a family menu first. The existing 13 defaults remain; users can add/remove pins without changing families or losing saved preferences.
2. **Continuous adjustments:** expose existing tween, curve and timing modal controls with visible adjustment feedback, commit and Esc cancellation. Direct slider gestures or popup sliders must use verified native interaction and the actual operator's supported range. Do not claim an identical gesture or overshoot range from an icon alone.
3. **Options and variants:** keep the primary action immediate. Native secondary controls expose relevant scope, variants and operator options; document whether the primary action executes or starts a modal operation. Preserve native tooltips and Adjust Last Operation where the target supports it.
4. **Search:** add a permanently visible Search control alongside Gear. Search the full validated toolbar catalogue by ordinary tool names and established equivalent terms. A search result executes its mapped action or can be pinned. Search must not depend on visiting the sidebar.
5. **Full catalogue access:** preserve all 70 existing presets and their identities. Expand the catalogue for additional existing matching actions after their context and parameter requirements are checked. Do not restrict coverage to the old 70 entries.
6. **Stable visibility:** unavailable actions keep their position and explain their prerequisite. Shrinking width uses native header scrolling. Height changes must not remove controls or recreate editor areas.

## Existing source coverage

This is a starting inventory for access work, not proof that the underlying algorithms match another application's results.

| Area | Existing Anim Assist source | Access work |
| --- | --- | --- |
| Pose tweening | `timeline_catalog.py`: B25/B50/B75, DRAG and bounding-key insertion presets | Carry over direct pins and the existing anchor/mask explanations |
| Curve adjustment | NEIGHBORS, FRAME, EASE, AMPLIFY, SMOOTH and handle presets | Retain each tool's actual gesture, selected-key scope and reference settings |
| Timing | Nudges, scale presets, ripple, time insertion/removal and reverse | Preserve direct actions; clarify scope and key-time changes |
| Key selection/types | Selection range, ends, growth and key-type presets | Keep each eligible variant pinnable |
| Mirroring and matching | Existing pose family and `p8_match_ops.py` | Preserve rig prerequisites; assess additional matching operators for the catalogue |
| Object baking | Existing bake family | Preserve evaluated-object scope and range/step settings |
| Motion display and live offset | Existing motion family | Carry over existing prerequisites and known limitations |
| Key clipboard | `p2_key_ops.py`: `copy_selected_keys`, `paste_keys_at_frame` | Add validated direct presets to Keys; these are absent from the old catalogue |
| Reference bookmarks | `curve_tool_ops.py`: `add_bookmark`, `remove_bookmark`, `recall_bookmark` | Make reference-bookmark access available in Curves after parameter validation; naming must describe reference-frame behavior |
| Rig space switching | `p8_switch_ops.py`: compensation, range baking and switch operators | Assess configured rig operations for Pose access and direct pins; preserve configuration prerequisites |

## Functional boundaries identified

- The current key-time offset controls move key times. They have not established the nonmoving-key behavior documented for AnimBot's Time Offsetter. An added shortcut cannot close that algorithm gap.
- `p7_manage_ops.py:AA_OT_p7_temp_pivot` creates a cursor-positioned helper with no owner constraint. It is not established as AnimBot's editable Temp Pivot. Use an accurate helper label if exposed.
- `recall_bookmark` changes `scene.anim_assist.reference_frame`; it does not move the playhead. Label it as setting a reference, not navigating a time bookmark.
- Clipboard operators provide existing selected-key copying/pasting. Additional animation insertion/replacement modes require separate verified mappings or new implementation; they must not be invented as labels.
- Any other documented feature without a checked counterpart remains unmapped until its backend and behavior are investigated. A full AnimBot feature-parity claim is outside the evidence established so far.

## Completion record

The implementation must maintain a coverage matrix with: reference capability, Anim Assist operator/preset, category, direct pin availability, search entry, scope, required parameters, gesture, options location, observed result and remaining functional difference. Classify each as working access, available but not yet wired, partial functional match, unmapped or not verified.

Tool access acceptance fails if a mapped available action is menu-only and cannot be pinned, a primary action forces an unnecessary options dialog, a result calls the wrong operator/context, or a missing backend is represented by a nonfunctional button. Require observed native use for the exposed controls before calling access complete.

No AnimBot assets, source code or tooltip text are copied. This requirement concerns original controls and functional tool access. The compiled native application and add-on are still pending; this document does not claim the controls have been built.
