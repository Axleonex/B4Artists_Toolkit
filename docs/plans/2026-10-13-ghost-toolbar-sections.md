# Named Ghost toolbar sections

The owner selected named section buttons with dropdowns on 2026-10-13. This approves the existing native row with explicitly labelled sections, rather than additional expanded rows.

## Design and experience contract

Subject: animators who want each section in the Ghost dropdown directly identifiable in the viewport toolbar. Treatment: native Bforartists UI tool; inherit the host theme, font, colors, icons and control sizing.

The row keeps Ghost for menu/recovery, adds a direct Ghosts On / Turn On Ghosts toggle, and labels the existing Marker options and Onion Skin options dropdowns. Show Markers and Show Onion Skin stay adjacent one-click actions. Motion Paths, Edit Motion, Compare, Physics, Look and Settings retain their named dropdowns and established order. The same labelled row appears across Object/Pose viewports; native horizontal panning handles overflow.

Known evidence: the owner's screenshot shows all eight section names plus the master switch in the Ghost popup; the current toolbar already names six destinations but hides marker/skin option names behind arrows and the master switch inside Ghost. The owner chose named dropdowns over additional rows. Alternatives: keep arrows (less width, weaker identification), expand all controls into extra rows (more viewport space). The selected flat row preserves the established interface.

Happy path: identify a named section in the row, click its dropdown, adjust the existing shared controls. Generation buttons act immediately. The master toggle uses the same scene property as the Ghost menu, with the same state label.
Recovery: Ghost and the main-header menu retain Hide/Show Toolbar; missing targets keep options enabled and existing disabled-action explanations.
Preservation: opening options and drawing the toolbar preserve the frame, previews, targets and animation. No new sampling or live-update logic.
Onboarding: no new flow; update the manual's section discovery wording.
Success: names and master state are visible in draw checks, generation/options remain distinct, labels are identical across widths/scales, native split-view captures show the named row and scrolling, exact 4.2.9 ZIP passes focused regressions.

## Implementation plan

1. Add a failing draw regression for explicit marker/skin labels and a direct master toggle matching the existing menu's state label.
2. Reuse one master-toggle draw helper in both locations; label the existing dropdowns. Retain operators and all other section destinations.
3. Extend native split checks to assert the named controls in each viewport and capture the row. Run focused UI/location/cache/authoring checks from the exact candidate ZIP.
4. Prepare unpublished 4.2.9 metadata, ZIP, current guide/PDF and release notes. Preserve historical versions and receipts; record package evidence and inspect native screenshots/PDF.
5. Commit locally and present the concrete before/after for merge, push and release confirmation.

Self-review: the request has a finite UI scope, no new theme or backend behavior, and no unresolved design choice. All full-size labels cannot fit simultaneously into every narrow viewport; native panning remains necessary.

## Approved publication

The owner confirmed the merge update on 2026-10-13 after reviewing the prepared 4.2.9 change. Publication uses a regular Latest release with matching ZIP and PDF assets. The package receipt records downloaded asset comparisons and repository metadata after publication.
