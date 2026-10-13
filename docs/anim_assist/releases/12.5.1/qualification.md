# Anim Assist 12.5.1 layout qualification

Date: 2026-10-12. Result: targeted normal-GUI layout checks pass on a Blender stand-in; actual Bforartists acceptance remains open.

## Root causes

12.5.0 creates the second row using a Text Editor. Its synchronization checked adjacency but did not restore the row height after resizing. In the baseline reproduction, an outer-border drag increased the strip from 30 to 210 pixels while the native Timeline stayed 208 pixels tall. That reproduces the oversized editor body shown in the owner's screenshot.

The old minimum allowed only 12 pixels below the native header, consuming the frame ruler and key canvas. The old split also assumed that the new copy was always above the original; horizontal factors at or below 0.5 create the lower copy. The patch reserves 48 scaled pixels below the header and requires a factor above 0.5.

An attempted timer-driven `screen.area_move` repair passed with event simulation but failed in a normal GUI session. It was removed. Its native poll requires the screen's actual active mouse region to be null. The final repair uses native join/split and keeps the original Timeline as the surviving editor. Source inspection: [Blender screen operators](https://github.com/blender/blender/blob/v5.1.2/source/blender/editors/screen/screen_ops.cc) and [screen splitting](https://github.com/blender/blender/blob/v5.1.2/source/blender/editors/screen/screen_edit.cc).

## Final runtime checks

The host executable resides in a proxy directory whose name satisfies the add-on guard. It is **standard Blender 5.1.2**, with no native Bforartists Tool Shelf property. No result below is claimed as Bforartists validation. The final process ran without `--enable-event-simulate`; actual border drags used Windows Computer Use. The isolated fixture had an animated cube, frame 6, and keys at frames 1, 11 and 21.

| Case | Observation | Result |
| --- | --- | --- |
| Initial two rows | One strip, 31 px; Timeline 177 px, window/key region 151 px | Pass |
| Outer border dragged upward 180 px | Strip restored to 30 px; Timeline 358 px, window/key region 332 px | Pass |
| Internal divider dragged down to hide keys | Temporary large Text Editor and short Timeline recover to strip 30 px and Timeline 358 px; same native Timeline pointer | Pass after timer update |
| Disable extra row | Strip rejoins; one native Timeline, 387 px; keys, frame and view retained | Pass |
| Enable on short native Timeline | No extra strip is created; native header and shortcuts remain | Pass |
| Enlarge short Timeline by actual mouse drag | Exactly one strip reappears above the same native Timeline; key area visible | Pass |
| Change UI scale to 150% | Exactly one paired strip, 38 px; native Timeline 158 px with 38 px header and 120 px window region | Pass |
| Fresh final-ZIP session at 100% | One paired strip and visible native keys | Pass |
| Save and reopen isolated fixture | One paired strip, 31 px; native Timeline 177 px, frame 6 and keys retained | Pass in the same process |
| Create inverted native pair with a lower Text Editor copy | Old strip replaced with one 31 px row above the original native Timeline; native pointer preserved | Pass after timer update |

The mouse-drag runtime was staged from the generated ZIP before the final changelog entry was moved to the top. That rebuild changed documentation only; the final archive's Python files match every staged runtime Python file byte for byte. The final ZIP was then extracted and launched in a fresh normal GUI for the reopen and inverted-pair checks. No formal test suite was added or run for this patch.

The first normal GUI diagnostic controller exited when its evidence JSON write raced with a reader holding a file lock. The controller was corrected to tolerate that diagnostic-file condition before the fresh final-ZIP session. This was a fixture exception, not an add-on failure. The save emitted built-in brush-material path warnings; reopen completed and the observed layout and keys were retained.

## Package checks

The builder records 203 entries, 201 syntax-parsed Python files, four matching 12.5.1 version fields and exactly six changed package files relative to 12.5.0. All 70 dispatch presets, seven groups, 13 defaults and 17 original quick presets are preserved. The old 12.5.0 ZIP is unchanged. Hashes and source digests are in [package-receipt.json](package-receipt.json).

## Evidence

- [Normal GUI after outer resize](after-resize.png): thin toolbar, native ruler and visible key canvas.
- [Enabled on a short Timeline](short-timeline.png): native Timeline retained; second row waits for sufficient height.
- [150% UI scale](scale150.png): one row with native keys visible.
- [Geometry and runtime/source evidence](layout-evidence.json).

The diagnostic profile directories existed before launch, and the controller asserted that Blender's resolved CONFIG matched the isolated directory. This run did not save user preferences or install into the owner's profile. The previous preference-overwrite incident remains documented in the [12.5.0 report](../12.5.0/qualification.md); this patch does not claim to restore it.

## Open checks

Actual Bforartists extension installation, the owner's original saved workspace, full application restart with saved preferences, multiple Timelines/windows, fullscreen and direct add-on disable remain unverified for 12.5.1. Native B50 Redo and trail-position findings are outside this layout repair. The phase remains **Needs Review**. Routing authorized scoped native continuation after the provider was unavailable; no independent review or broad qualification pass is claimed.
