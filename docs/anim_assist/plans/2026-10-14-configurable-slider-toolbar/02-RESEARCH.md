# Source research and constraints

Read on 2026-10-14 at product commit b05f243. This is source inspection,
not new runtime verification.

| Existing source | Observation / consequence |
| --- | --- |
| anim_assist/ui/timeline_catalog.py | 89 action presets, 13 default quick controls; canonical GROUPS currently puts Curves before Timing. Set separate toolbar family order without losing catalogue IDs/dispatch. |
| anim_assist/ui/timeline_overlay.py | row_layout currently starts Search/Settings; native pixel handler and keymaps consume band input. Add scalar control geometry and a transient drag overlay; don't recreate editor splitting. |
| anim_assist/prefs.py | Dynamic per-action Boolean preferences, package-aware get_prefs and shared quick settings. Explicitly migrate old selections once. |
| anim_assist/operators/p3_modal_ops.py | Breakdown snapshots/replaces curves and clamps factor to -1..2; current hold/release commit already exists. Preserve anchor behavior, pose restoration and scene factor on cancel. |
| anim_assist/core/p3_properties.py | Breakdown factor bounds and scene masks/targets; toolbar must not silently replace these. |
| anim_assist/operators/curve_tool_ops.py | Five scalar curve modals use factor and core math; currently commit on later left press/Enter. Snapshot values and move handles; adapt input explicitly rather than assuming release works. _addon_prefs hardcodes anim_assist; use package-aware preference access when touched. |
| anim_assist/operators/p6_modal_ops.py | Scale starts at factor 1, minimum .01; offset is frames. Current commit on later left press. Existing snapshot includes key times/handles; reuse retime math. |
| anim_assist/core/p6_retime_math.py | Existing scale/offset algorithms and snap semantics are the authority. |
| anim_assist/operators/anim_offset_ops.py | OFFSET is a live transform-propagation session, not a single numeric slider. Test actual edit/propagate/cancel workflow. |
| anim_assist/operators/settings_ops.py | Settings JSON import/export uses actual preference package; include versioned layout record and validate before assignment. |
| tests/unpatched_timeline_validation.py | Enumerates nine interactive entries and runs 80 immediate effects; uses fixture/assertions from native_timeline_validation.py. Test controller must assert profile isolation before launch/save. |
| tests/check_timeline_overlay.py | Existing native input events and area-coordinate lookup; 37-step historical acceptance is not full tool coverage. |
| tests/observe_timeline_overlay.py | Small request-driven GUI harness; needs asserted CONFIG/script paths and fixture cleanup for the new runs. |
| docs/anim_assist/releases/12.6.1/qualification.md | Prior effect/layout/lifecycle evidence with explicit canvas/min-height limitations. Avoid general no-flicker claims. |

Existing .planning state chiefly describes old milestones and is ignored by
Git. Keep historical entries but point the active scope at this tracked packet.
Prior B50 Redo and trail-offset findings must receive targeted fresh checks;
neither old failures nor old passes settle current behavior without reruns.

Routing: runtime doctor healthy. First classifier invocation rejected the
directory .planning; corrected invocation declares individual regular files.
Correct classification T3_PRIME_OMP; Windows preflight returned relay
RUNTIME_UNAVAILABLE. Native documentation continuation is allowed by policy.
No hosted execution, independent review or paid model call occurred.
