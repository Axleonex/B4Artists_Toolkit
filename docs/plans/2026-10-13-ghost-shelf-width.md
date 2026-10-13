# Ghost shelf width implementation plan

Goal: complete the owner's left-shelf width request using BoneCraft's existing guarded width workaround, while retaining the already completed removal of the duplicate main-header button.

Evidence: BoneCraft's `boneforge/core/shelf_width.py` locates the stored ARegion.sizex field from the native width, height, region type and scaled stored width. It writes only a unique match, hides/shows the region to relayout, and widens each region once. BoneCraft's defaults are 240 px left and 260 px right; `tests/test_shelf_width.py` covers its locator and scaling. The previous conclusion that a host change was required described only the public RNA API and missed this existing repository workaround. The earlier local plan's width limitation is superseded by this finding.

Subject: animators reading Ghost controls in the native left Tool Shelf. Treatment: native UI tool, using the host's palette, typography, spacing and widget sizes. Layout: preserve the existing Ghost Tool tab and its complete layout; widen its native region once, rather than replacing it with a popup. The main-header duplicate stays removed; lower-row tools and View recovery remain.

Experience contract: choosing Left Tool Shelf opens the full Ghost controls at the same width as an already open N-panel. If that panel is closed, use BoneCraft's 240 px left default, adjusted for UI scale. Already wider shelves stay wider. Later manual resizing is preserved. Display relocation, an explicit auto-widen setting change or a new file permits a fresh default-width check. Only ordinary viewports with the left Ghost home are eligible; separate Ghost windows and settings editors are excluded. Unrecognized or ambiguous native layouts receive no width write. The user can disable automatic widening in Ghost preferences. Animation, frame, cached ghosts and other display homes are preserved.

Alternatives considered: public width assignment (read-only in the installed host), BoneCraft's fixed 240 px default (usable but does not match an open N-panel), guarded matching of the open N-panel with the proven fallback (selected to satisfy the owner's exact width request). No BoneCraft dependency is introduced into Ghost's standalone ZIP.

Implementation:

1. Add failing pure and policy tests: absent width helper, matching and fallback targets, unique/ambiguous memory layouts, scaling, hidden/other homes, wider/manual overrides, failed writes and clean timer teardown. Tests exercise meaningful failure cases rather than merely counting source lines.
2. Adapt BoneCraft's locator/width-write/relayout in a standalone Ghost helper. Keep its bounded scan, add invalid-parameter and duplicate-candidate guards, and register it after preferences. Add one applicable auto-widen preference and reset the once-only state on explicit relocation.
3. Verify exact copied source in disposable native Bforartists. Measure default and scaled left/right widths, fallback, custom resizing, reload cleanup and preserved toolbar/header behavior. Capture the actual widened Ghost shelf, not a mockup or a manually resized substitute. Keep the native platform gate unpatched.
4. Prepare an unpublished 4.2.10 candidate with matching source, ZIP, current-version guides/PDF, release notes and receipt. Preserve earlier published archives and evidence. Commit on the work branch and present a before/after table before merge/push/release approval.

Quality endpoint: pure/policy and native checks pass, screenshots show readable controls and matching measured widths, the earlier header correction stays intact, and the exact 4.2.10 ZIP matches source bytes. No production-rig or unrelated backend changes are in scope. The owner has already requested the width and supplied BoneCraft as the working comparator; no new visual-design approval is needed. Self-review: scope, fallback, preservation and success criteria are explicit; no placeholders or added styling.

## 2026-10-13 checkpoint

The implementation and exact source-matched 4.2.10 ZIP are prepared; all 15 pure width-policy checks passed. Native validation is blocked before the test script starts: two GUI launches each timed out at 240 seconds, and a separate background startup probe remained alive without output after 60 seconds. No shelf measurements or screenshots were produced. The JSON status report records the attempts. The quality endpoint is therefore incomplete, no full package receipt exists, and the candidate is not ready to merge or publish.
