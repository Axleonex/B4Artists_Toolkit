# Gate audit — configurable toolbar

2026-10-14. The implementation author also wrote these tests. This is not an
independent review. Numerical expected values are explicitly calculated from
the fixture, rather than copied from the operator result. Tests use synthetic
animation in the real stock host; they do not establish production-rig quality.

| Gate | Input/mechanism | Concrete failing state | Red evidence | Verdict |
| --- | --- | --- | --- | --- |
| Catalogue effects | 80 fixture effects, independently specified numeric/selection/pose/clipboard/trail expectations | Mirror both selected bones using a source already overwritten by the first write | Original exact-package Mirror Selected failure, baseline evidence | Sound for covered fixtures |
| Native row sliders | Actual pointer events, eight tools × two modes, expected values in check_slider_live | Smooth shows 30% but leaves the middle key at 4 instead of 2.95 | Paper: error exceeds 1e-4 and unchanged snapshot fails | Sound for covered fixtures |
| Absolute preview/cancel | Before/live/after full key and handle snapshots; pure transaction repeated preview | Second preview compounds first; Esc retains changed handle coordinates | Pure tests seed these states; exact snapshot comparison catches them | Sound |
| Undo/redo | Native ed.undo/redo against independently captured before/committed snapshots | Redo returns pre-edit B50 state | Baseline nested-dispatch failure, undo-diagnostic evidence | Sound |
| Trail geometry | Sampled world positions compared with evaluated fixture positions | Animated object translation applied twice | Original fast-trail offset failure | Sound for fixture |
| Library safety | Protected/duplicate/malformed/future input cases, snapshot preservation, restart | Duplicate name overwrites saved record; version 2 import changes unrelated prefs | Pure rejected-input assertions plus native future-schema rejection | Sound for covered records |
| Geometry/input | Rectangle bounds/non-overlap, real effective UI scale/header positions, view2d/frame changes | More extends past region; native pan/play never changes state | Paper: bounds/view/frame assertions fail | Sound for measured cells; screenshots only corroborate |
| Disable cleanup | Actual active preview disable; observed original cleanup invocation, restoration and keymap counts | Animation restores but active operator timer never removed | stress-qualified failure before finalization repair | Sound; test wrapper observes cleanup without replacing its behavior |
| Package identity | Strict inventory, AST parse, four versions, byte-for-byte installation, SHA256 | Installed module or ZIP byte differs; executable appears in ZIP | Paper: installation equality/inventory/version/binary rejection fails | Sound |
| Human usability | Owner follows 02-UAT.md in their workspace | Owner cannot find the drag/settings/layout actions or sees flashing | No owner result yet | Unverified; no automated substitute |

All except human usability are load-bearing for local technical qualification.
Human usability is load-bearing for claiming owner acceptance. Still-image
existence, Python compilation, FINISHED operator status and case counts alone
are not accepted as functional evidence. Unsupported platform/DPI/rig cells are
listed in qualification instead of counted as passes. An independent review
would strengthen the author-written numerical and lifecycle gates.
