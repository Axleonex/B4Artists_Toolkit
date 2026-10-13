# Ghost Tool 4.2.9 viewport toolbar

The toolbar keeps Ghost actions in the native viewport **Tool Settings** row beneath the main header. Ghost Tool defaults to **Top Toolbar**, with **Show Ghost Toolbar** enabled. **Top Header** has been removed from Display Location; saved Top Header choices migrate to a visible toolbar. Right Sidebar (N), Left Tool Shelf (T), and their saved choices remain available. Existing toolbar visibility choices are retained.

With native headers aligned at the top, the toolbar appears beneath the main viewport header. Native tool and mode controls retain their position and behavior. The toolbar follows the viewport's native header alignment.

## Generate and inspect

The toolbar directly exposes Ghosts On / Turn On Ghosts, Marker options, Onion Skin options, Motion Paths, Edit Motion, Compare, Physics, Look and Settings. Each named section button opens its existing dropdown. Show Markers and Show Onion Skin remain adjacent one-click actions. Ghost retains the overall menu and Hide/Show Toolbar recovery.

**Show Markers** generates and displays markers from your animation. **Show Onion Skin** generates and displays mesh previews. These are actions, so clicking either can refresh its preview. The adjacent arrows open **Marker options** and **Onion Skin options** without generating anything.

The first checkbox in each options popover is **Show cached markers** or **Show cached skin**. Use it to hide or show the existing preview without rebuilding it. Hidden markers cannot be picked or box-selected. Other displays, such as motion paths and saved comparison references, retain their own controls.

**Clear All Ghosts** in Marker options removes both markers and onion skins. Use the cached visibility checkbox when you only want to hide markers.

Marker options retain **Marker Targets**, frame range and **Live Update Markers**. Skin options retain the character sources, frame counts, fade and **Live Update Skin**. Live updates remain disabled by default. Existing scene choices are preserved. This toolbar does not change the animation sampling or settled-refresh behavior.

**Motion Paths**, **Edit Motion**, **Compare**, **Physics**, **Look** and **Settings** open their shared feature controls. Compare keeps Save Snapshot and each named reference's Restore action together. Marker Targets, Capture Targets and Snapshot Targets remain independent folds.

## Keep the viewport clear

Ghost Tool 4.2.9 keeps the complete Object/Pose toolbar in every viewport, at every width and UI scale. Buttons keep the same labels and order as the wide layout. When a row overflows, middle-mouse drag it horizontally to reach the remaining buttons. Resizing or splitting a viewport does not move tools into **More** or a Ghost-only layout. Other modes retain their existing Ghost menu.

Earlier 4.2.7 used width-based layouts. The complete split-view toolbar was introduced in 4.2.8; see its [verification](split-view-verification.md).

Choose **Hide Toolbar** in Ghost to hide its controls while keeping previews, targets, settings and the native Tool Settings row. To restore it, open **Ghost Tool** in the main viewport header and choose **Show Toolbar**. This also reveals Tool Settings if you hid that native region through View controls. Hiding the native region later remains your choice until you explicitly show the toolbar again. Leaving Top Toolbar does not close native regions.

Location and Ghost-control visibility apply across ordinary viewports. Save preferences normally to retain them. Each viewport keeps its own native region alignment and visibility.

## Source and release status

The current source, repository ZIP and regular Latest release are **4.2.9**. Install [b4_ghost_tool_v4.2.9.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.9/b4_ghost_tool_v4.2.9.zip). The release's [package receipt](../releases/4.2.9/package-receipt.json) records exact source matching and 89 passing focused tests/checks in native Bforartists 5.2.0. Earlier archives and the [original toolbar verification](verification.md) retain their tested versions.
