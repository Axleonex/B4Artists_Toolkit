# Ghost Tool 4.2.6

Repository test build containing the approved persistent viewport toolbar.

- Choose Top Toolbar, Top Header, Right Sidebar (N), or Left Tool Shelf (T) in preferences. Existing location choices are retained; Top Header remains the default.
- Generate markers or onion skins directly, with adjacent named options. Shared feature controls keep settings and independent target folds consistent.
- Show cached markers and Show cached skin change preview visibility without regeneration. Hidden markers cannot be picked or box-selected.
- Compact toolbars use More; narrow toolbars use Ghost for full access. Hide Toolbar preserves previews and settings; the main-header Show Toolbar action restores access.
- Live Update Markers and Live Update Skin retain their default-off behavior and existing native gesture pause. This version adds no new backend jitter repair.
- Source metadata, current README/download links, Markdown/PDF manuals and repository package now identify 4.2.6. Earlier artifacts and test records keep their original versions.

Install [b4_ghost_tool_v4.2.6.zip](../../../../releases/b4_ghost_tool_v4.2.6.zip?raw=1) through Bforartists Preferences > Add-ons > Install from Disk, then restart. Existing scenes retain their saved live-update choices.

The exact package passes **178 checks/cases** in Blender 5.1.2: 117 background checks, 56 native toolbar checks and five native auto-key cases. See [package receipt](package-receipt.json). Only the host registration gate is patched in the test installation. Native Bforartists geometry, Tool Shelf behavior and production-rig validation remain pending.

This build and its matching PDF guide are available from the [4.2.6 GitHub prerelease](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.6). The repository ZIP is byte-identical to the release asset. The original [toolbar design and rule audit](../../toolbar/verification.md) describe implementation decisions; their initial 4.2.5 test evidence is retained as history.
