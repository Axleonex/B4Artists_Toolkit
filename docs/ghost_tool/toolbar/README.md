# Ghost Tool 4.2.11 viewport toolbar

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

Ghost Tool 4.2.11 keeps the complete Object/Pose toolbar in every viewport, at every width and UI scale. Buttons keep the same labels and order as the wide layout. When a row overflows, middle-mouse drag it horizontally to reach the remaining buttons. Resizing or splitting a viewport does not move tools into **More** or a Ghost-only layout. Other modes retain their existing Ghost menu.

Earlier 4.2.7 used width-based layouts. The complete split-view toolbar was introduced in 4.2.8; see its [verification](split-view-verification.md).

Choose **Hide Toolbar** in Ghost to hide its controls while keeping previews, targets, settings and the native Tool Settings row. To restore it, choose **View > Show Ghost Toolbar** or enable **Show Ghost Toolbar** in preferences. This also reveals Tool Settings if you hid that native region through View controls. Hiding the native region later remains your choice until you explicitly show the toolbar again. Leaving Top Toolbar does not close native regions.

Location and Ghost-control visibility apply across ordinary viewports. Save preferences normally to retain them. Each viewport keeps its own native region alignment and visibility.

## Source and release status

The current source and regular Latest release are **4.2.11**. Install [b4_ghost_tool_v4.2.11.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.11/b4_ghost_tool_v4.2.11.zip). The exact 4.2.11 ZIP passes 123 focused startup and toolbar checks in Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha), build hash 0a1ca45552db: 80 background checks, 35 native split-view checks and eight saved-preference startup checks. The startup isolation profile disables width writes. A separate width run passes ten preliminary checks for the initial N-panel match and manual resize preservation, but its preference-reset check fails when displayed and stored widths disagree; the guard declines the write. Later fallback and scale checks were not reached. JellyTest.blend has not been tested. See the [package receipt](../releases/4.2.11/package-receipt.json).

## Left shelf width and header placement

Ghost Tool 4.2.11 is designed to widen a narrow Ghost shelf once to match an already open right N-panel. With the N-panel closed, its intended default is 240 px at 1x UI scale. It leaves wider shelves and later manual resizing alone. Widen Narrow Shelf in Ghost preferences defaults on; turn it off to manage the width yourself. Changing that switch or relocating the display permits another default-width check. Initial matching and manual resize preservation pass, but the full width suite is incomplete; see the [verification status](../releases/4.2.11/package-receipt.json).

The standalone Ghost Tool button in the main viewport header is removed. The Ghost menu, master switch, generation actions and all section dropdowns remain in the Tool Settings row below. In Top Toolbar mode, use View > Show Ghost Toolbar or its preference checkbox to recover hidden controls.
