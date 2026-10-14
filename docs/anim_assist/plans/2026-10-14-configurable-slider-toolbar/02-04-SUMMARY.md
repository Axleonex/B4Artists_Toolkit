# Plan 02-04 summary

New canvas row uses preferred family order and right-side utilities. Two default
inline sliders, direct-drag Timing Scale popout, exact-value fields, default reset
and custom presets share verified transactions. Original actions remain reachable
through Search/More/family menus. Search pins now update actual display modes.
Native staged Toolbar Settings lists all 89 tools; per-tool settings provide
eligible display modes, width, range/default, precision/sensitivity/snap/presets
and access to shared scene options. Non-scalar tools offer only Hidden/Button.

Five pure layout tests pass over width/scale/top/bottom/all-pins cells. Found
and fixed missing Settings at width250/scale2 by compacting utility labels.
Saved configuration is unchanged by adaptive geometry. No helper editor or
continuous area-repair loop is introduced. Sliders cancel on area-size changes;
load/undo/unregister hooks clear active transactions and transient values.

Stock-host real row input passes six default slider cases (Breakdown/Smooth
inline and Scale popout, commit/cancel), six undo/redo checks, actual settings
opening and cancel-without-mutation. Native screenshots show the row and
anchored Scale feedback. Settings screenshots are initially area crops and
must be recaptured as full-window images for final panel review.
Evidence: evidence/row/ui-coverage.json and slider-actions.json.

Actual settings acceptance, extended-range, full lifecycle and named-layout
checks are final-suite gates, not declared passed here. Native row remains a
canvas band, with original fully-collapsed/min-height limits. Upcoming library
UI is Plan 02-05. No publication; governed preflight unavailable, scoped native
continuation. Next: user-named layout UI and persistence.
