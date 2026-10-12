# Ghost Tool 4.2.6 viewport toolbar

The approved toolbar source update keeps Ghost actions in the native viewport **Tool Settings** row. Choose **Edit > Preferences > Add-ons > Ghost Tool > Display Location > Top Toolbar**. Your existing location preference is retained when upgrading; Top Header remains the default. Right Sidebar (N) and Left Tool Shelf (T) remain available.

With native headers aligned at the top, the toolbar appears beneath the main viewport header. Native tool and mode controls retain their position and behavior. The toolbar follows the viewport's native header alignment.

## Generate and inspect

**Show Markers** generates and displays markers from your animation. **Show Onion Skin** generates and displays mesh previews. These are actions, so clicking either can refresh its preview. The adjacent arrows open **Marker options** and **Onion Skin options** without generating anything.

The first checkbox in each options popover is **Show cached markers** or **Show cached skin**. Use it to hide or show the existing preview without rebuilding it. Hidden markers cannot be picked or box-selected. Other displays, such as motion paths and saved comparison references, retain their own controls.

**Clear All Ghosts** in Marker options removes both markers and onion skins. Use the cached visibility checkbox when you only want to hide markers.

Marker options retain **Marker Targets**, frame range and **Live Update Markers**. Skin options retain the character sources, frame counts, fade and **Live Update Skin**. Live updates remain disabled by default. Existing scene choices are preserved. This toolbar does not change the animation sampling or settled-refresh behavior.

**Motion Paths**, **Edit Motion**, **Compare**, **Physics**, **Look** and **Settings** open their shared feature controls. Compare keeps Save Snapshot and each named reference's Restore action together. Marker Targets, Capture Targets and Snapshot Targets remain independent folds.

## Keep the viewport clear

Wide toolbars expose every feature. Compact toolbars place Compare, Physics, Look and Settings under **More**. Narrow toolbars use **Ghost** for full access in the same feature order. Complete feature groups move together. Native horizontal header panning remains available when the viewport is especially narrow.

Choose **Hide Toolbar** in Ghost to hide its controls while keeping previews, targets, settings and the native Tool Settings row. To restore it, open **Ghost Tool** in the main viewport header and choose **Show Toolbar**. This also reveals Tool Settings if you hid that native region through View controls. Hiding the native region later remains your choice until you explicitly show the toolbar again. Leaving Top Toolbar does not close native regions.

Location and Ghost-control visibility apply across ordinary viewports. Save preferences normally to retain them. Each viewport keeps its own native region alignment and visibility.

## Source and release status

The current source and repository test ZIP are **4.2.6**. Download [b4_ghost_tool_v4.2.6.zip](../../../releases/b4_ghost_tool_v4.2.6.zip?raw=1). Its [package receipt](../releases/4.2.6/package-receipt.json) records the exact archive, source matching and 178 passing checks/cases. The existing 4.2.5 ZIP is retained as history and predates this toolbar. No new GitHub Release has been published. The [original toolbar verification](verification.md) belongs to the initial 4.2.5 source candidate; native Bforartists acceptance remains pending.
