# Ghost panel layout correction

Follow-up: the initial public-API limitation below is superseded by [Ghost shelf width implementation](2026-10-13-ghost-shelf-width.md). BoneCraft already uses a guarded native stored-width workaround; the 4.2.10 candidate adapts that mechanism. The earlier evidence remains as a record of the initial investigation and header-only correction.

The owner requests a readable left shelf matching the opened right N-panel width and removal of only the duplicate Ghost Tool main-header button. The existing lower toolbar and all tools must remain available.

Subject: Ghost Tool users finding the same controls in a readable native viewport layout. Treatment: native UI tool; inherit Bforartists' theme palette, typography, icons and spacing. Layout: retain the complete lower Tool Settings row, remove the standalone main-header entry, and place hidden-toolbar recovery in the existing View menu. No new theme, tab, or animation behavior.

Experience: normal toolbar controls remain unchanged. Hiding either Ghost controls or the native Tool Settings row makes View > Show Ghost Toolbar available. That action uses the existing visibility operator; it preserves ghosts, animation and preferences. Side homes, separate windows and the settings editor retain their existing behavior.

Known evidence: the supplied screenshots show a narrow left shelf and a duplicate upper entry. Source appends the duplicate through VIEW3D_MT_editor_menus. Installed native Bforartists 5.2.0 reports Region.width read-only, exposes no shelf-width preference, and screen.region_scale has no executable sizing properties. The host's operator requires an action-zone drag. Panel layout uses the existing region width; bl_ui_units_x does not resize this region. See host sources: source/blender/makesrna/intern/rna_screen.cc, editors/screen/screen_ops.cc and editors/screen/area.cc in Bforartists/Bforartists.

Width limitation: automatic matching cannot be implemented through the installed supported Python API. Preserve native region sizing; do not substitute a popup, resize another editor, inject desktop mouse events, or write internal memory. Manual divider dragging remains the supported way to match the right panel. This part remains unresolved and must be reported to the owner, not labelled fixed.

Implementation steps:

1. Add a regression requiring no Ghost callback in the main editor-menu row and hidden-toolbar recovery in View; confirm it fails on the previous source.
2. Move only the standalone header callback to conditional View-menu recovery. Preserve all toolbar popovers/operators and the shared popup panel.
3. Run focused display/toolbar regressions, inspect native screenshots, and measure native left/right widths. Keep published ZIPs, PDF and release numbers unchanged while this correction is local.
4. Record results and make a local work-branch commit. Present the exact implemented scope and unresolved width requirement before any merge/push confirmation.

Self-review: no ambiguous tool removal, placeholders, added design choice or backend scope. The user's width request is clear but blocked by the native host API. B4Artists R3 is preserved through View recovery and lower toolbar menus; R9 removes only the redundant copy; R14 keeps this change narrow. R12 automatic readable shelf width remains unresolved.

## Local verification

The changed header-registration regression fails on the previous source (`True is not false`: a Ghost callback remains in the main editor-menu row), then passes after removal. An independent replay of the actual old draw function also shows both the upper toggle and popup button.

28 background tests pass in unpatched native Bforartists 5.2.0: one header-registration regression, 19 display-location checks and eight toolbar checks. Eight additional native checks pass for the clean main header, preserved lower destinations/actions/master switch, installed read-only width API and both hidden-toolbar recovery paths. Native measurements are 132 px Tools region and 220 px right sidebar at default scale. These measurements confirm the width difference; they do not count as a width fix.

The exact local source-copy candidate is `build/ghost-toolbar/panel-layout/ghost-panel-layout-candidate.zip`, SHA256 `cdff547ff1e1b3c249dfe2a3ed5bf6a7d6ce792d5f339f753b090d91cc67307f`. The background log SHA256 is `44e754f8ba01a88b3ff64e4ca4259a4231d613c448e70db11af1e5d7edb9b235`. Native evidence is in that directory's `result.json`, `header-clean-toolbar-preserved.png` and `header-clean-after-recovery.png`; both screenshots are inspected. The final native run retains the exact background-tested source. Earlier GUI harness attempts assumed an appended draw list would exist after removing its only callback and attempted unrelated deferred shelf-tab activation; the harness was corrected and narrowed to the changed header/recovery surface. Neither attempt changed production code.

No production rig, alternate-theme, full keyboard or automatic shelf-resize acceptance is claimed. B4Artists audit: R3 preserves the lower native Tool Settings menu and adds View recovery while honoring the owner's removal of the standalone main-header copy; R5 generation/options controls unchanged; R9 duplicate removed; R10 empty-selection options remain present; R11 uses the existing described visibility operator; R14 bounded source diff. R12 automatic shelf sizing remains unresolved. Other existing panels and action behavior were not re-audited.

The published 4.2.9 archive remains unchanged, SHA256 `527a06294e2ac54724c38416b4368db9e4d5438e1652a4d9e737d1fea3254452`. This is a local work-branch correction, with no release-number change, publication or repository push. Current release guides continue to describe the published build until a follow-up release is approved.
