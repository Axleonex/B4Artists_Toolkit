# Ghost Tool 4.3.1 documentation

Ghost Tool 4.3.1 documents the current direct viewport toolbar and compact inline Timeline controls. Ghosts and Paths have independent Before/Ahead counts. Click main actions, hold their buttons for parameters, choose Wire or Solid directly, and use persistent Drag Markers for repeated edits. Advanced tools remain in Settings.

[4.3.1 user guide](GhostTool_User_Manual.md) | [4.3.1 PDF](GhostTool_User_Manual.pdf) | [Toolbar reference](toolbar/README.md) | [4.3.1 release notes](releases/4.3.1/RELEASE-NOTES.md)

## Current tools

The top toolbar offers Ghost Tool on/off, Ghosts display with Before/Ahead counts, Wire/Solid, Paths display with its own counts, Add Selected Path, Follow Selection, Drag, Pin, Markers Display, Arc Style, Spacing Ticks and Settings. Arc Style opens Solid, Speed Colored and Fade directly. Generate and Clear remain in advanced controls rather than repeating as top-row icons.

Drag remains active across marker edits until toggled off or Escape. Pin toggles the picked marker's pinned state; multiple pins are supported. Markers Display has a top-toolbar hold menu that shares sampling with Paths. The bottom Timeline strip retains its earlier inline layout.

Compare retains scoped snapshots, independent variants, binding, JSON transfer and native Undo/Redo. Snapshot restoration includes captured marker records and a display refresh. The manual explains live updates, native transform gestures and the difference between pinning markers and adding path targets.

## Installation and publication status

The current source and guide version is **4.3.1**. No 4.3.1 installation archive or standalone GitHub Release is produced by this documentation update. The [last published 4.2.11 ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.11/b4_ghost_tool_v4.2.11.zip) retains its original version and does not install the latest toolbar update. Install a package built from the complete current `ghost_tool` folder to use 4.3.1; restart Bforartists after replacing an installed add-on.

## Evidence and history

The direct-tool implementation passed 188 targeted background checks before this metadata/manual update. These are implementation results, not qualification of a newly packaged 4.3.1 ZIP. No new functional tests are claimed here.

Earlier release notes, downloads and receipts keep their original versions and checksums. The [4.2.11 receipt](releases/4.2.11/package-receipt.json) records that build's startup checks and incomplete shelf-width verification; this update makes no new shelf-width fix claim. See the [release index](../../releases/VERSIONS.md) for historical archives.
