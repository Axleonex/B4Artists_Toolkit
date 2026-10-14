# Add-on Timeline row

Approved by the owner: "okay do that" after the in-Timeline row explanation.

Anim Assist draws a narrow toolbar in the Timeline canvas beside the native
header, below a top header or above a bottom header. This is an add-on overlay,
not a new header region. Native header controls remain in their original row.
No application patch, helper editor or resize-repair timer. A collapsed Timeline
gets room once during initialization when native border resizing is available;
later manual resizing is retained. A completely collapsed canvas cannot display
the band. This is a physical layout limit, not a hidden preference.

## Experience and visual contract

Treatment: UI/tool. Use Bforartists theme header background, button surface,
text and selected colors; BLF UI font at the application UI scale. Fallback
palette: background #303030, button #505050, ink #EEEEEE, disabled #999999,
accent #477DA8. Match the native header height with a thin separating line.

Seven permanent families retain configurable one-click quick actions. Search
and Settings remain visible. At narrow widths, remove overflowing quick buttons
into More rather than extend the native header or draw inaccessible controls.
All family menus remain reachable. Explicit hide is reversible through the
Anim Assist menu and preferences; enabled by default. Saved pins remain intact.

Use the supported POST_PIXEL draw handler and native Dopesheet keymaps for
operator dispatch, rather than an always-running modal mouse interceptor.
Bforartists' required 2D Gizmo flag is not exposed to Python. Hover provides
operator help and unavailable reasons. Input outside the band remains native.
The band covers a narrow part of the canvas; it does not move frame/key geometry.
With a top header, the frame ruler sits between the native header and the band
so Bforartists' native frame indicator cannot obscure a button.

## Acceptance

In unmodified Bforartists: row visible on startup without dragging; native row
not lengthened; direct action, modal action/cancel, family menu, Search, Settings
and pin changes work; header top/bottom, narrow/wide resize, maximization,
hide/show, disable/re-enable and saved preferences work. Scrubbing, key selection,
playback and undo remain native outside the band. Capture actual rendering.
Do not claim universal absence of flicker from sampled observations.
