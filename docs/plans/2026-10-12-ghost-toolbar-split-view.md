# Ghost toolbar in split viewports

Owner direction on 2026-10-12: keep the complete existing toolbar layout in every viewport, as in the main viewport. This directly approves the layout correction; no new visual design is needed.

## Design and experience contract

Subject: animators using multiple Object/Pose 3D viewports.
Treatment: native Bforartists UI tool; inherit the user's host theme, palette, font and control dimensions.
Layout: the existing full row, in its existing order, at every viewport width and UI scale. Native horizontal header panning handles overflow. The current width-based Ghost-only and More layouts are removed. Existing behavior in other modes is retained.
Known evidence: the owner's screenshots show the Ghost-only row in both narrower Animation viewports; source chooses MINIMAL below 1150 scale-adjusted pixels and COMPACT below 1800. The owner explicitly rejects this layout difference.
Approaches considered: lowering thresholds still changes the layout at some widths; smaller icon-only buttons change the approved labels. Keeping the full native row satisfies the requested consistency with the smallest change.
Happy path: open or split a viewport, see the same toolbar groups, pan horizontally to groups beyond its width, use their existing actions/options.
Recovery: existing Hide/Show Toolbar remains available; missing targets keep options accessible and actions disabled with existing feedback.
Preservation: scene frame, targets, cached previews, live-update defaults, native controls and display preferences.
Onboarding: no new flow; document native horizontal panning.
Success: identical recorded toolbar controls/order at wide, compact and narrow widths in Object and Pose modes, including scaled UI; native split-view screenshot and checks; no sampling during drawing.

## Implementation plan

1. Add a regression comparing complete toolbar controls at several widths/scales and run it against the current implementation to demonstrate failure.
2. Remove the width bands, hysteresis cache and compact renderer branch from `ghost_tool/ui_panel.py`. Keep mode behavior, native append, control labels and callbacks.
3. Update native test expectations and add `tests/test_ghost_toolbar_split.py`: exercise Animation's multiple viewports, native horizontal panning, resizing, hide/show and frame/cache preservation. Use a disposable Bforartists config and screenshot the native row.
4. Run the focused UI/display/cache/authoring suites in native Bforartists, inspect the split-view capture, record results and update the guide with a candidate status.
5. Commit locally on the work branch. Published 4.2.7 assets and historical receipts remain intact. Present the reviewed change before merge/push approval.

Self-review: no new surfaces, dependencies or unresolved design choices; the finite endpoint is the verified local correction. Small-view overflow remains native scrolling, so fitting all full-size buttons simultaneously into every width is not claimed.

Release follow-through: the owner confirmed merge on 2026-10-13. The correction is packaged as 4.2.8, with current repository references and the PDF manual updated. Historical 4.2.7 artifacts remain intact.
