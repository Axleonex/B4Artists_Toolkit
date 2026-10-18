# Ghost Tool 4.3.1

## Versioned tools and documentation

This update sets the add-on's `bl_info` version to **4.3.1** and brings the Markdown/PDF manual, toolbar reference and version summaries into line with the implemented direct-tool UI. The runtime toolbar and marker changes were already merged before this version update; this commit does not change their behavior.

- Direct top toolbar actions with per-tool hold menus and advanced Settings.
- Independent Before/Ahead sample counts beside Ghosts and Paths.
- Explicit Wire and Solid mesh styles, independent of visibility.
- Add Selected Path and Follow Selection beside Paths.
- Persistent Drag Markers and path-handle editing, with toggle-off and Escape exit.
- Pin/unpin multiple markers; Markers Display with sampling shared by Paths.
- Single-click Arc Style choices: Solid, Speed Colored and Fade; separate Spacing Ticks.
- Advanced Compare snapshots, restored captured marker records and refresh after restore.
- Existing compact bottom Timeline layout retained. Snapshot controls stay in Compare; duplicate Generate/Clear icons are absent from the top row.

## Manuals

The [user guide](../../GhostTool_User_Manual.md), [PDF](../../GhostTool_User_Manual.pdf) and [toolbar reference](../../toolbar/README.md) describe the 4.3.1 controls, hold menus, counts, repeated marker edits, pinning, curve smoothing, snapshots and toolbar recovery. They distinguish the overall enable switch, mesh visibility, editable-marker visibility and path visibility.

## Translated manuals

The complete 4.3.1 English guide is translated into six languages, with English UI names retained. Each edition covers the same 13 sections and 59 source blocks, plus a translation note. PDFs embed their fonts. No professional linguistic review is claimed. See the [language index](../../translations/README.md) and [source/hash manifest](../../translations/manifest.json).

- [简体中文](../../translations/GhostTool_User_Manual_zh.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_zh.pdf)
- [Français](../../translations/GhostTool_User_Manual_fr.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_fr.pdf)
- [日本語](../../translations/GhostTool_User_Manual_ja.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_ja.pdf)
- [한국어](../../translations/GhostTool_User_Manual_ko.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_ko.pdf)
- [Português](../../translations/GhostTool_User_Manual_pt.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_pt.pdf)
- [Español](../../translations/GhostTool_User_Manual_es.md) · [PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual_es.pdf)

## Verification and publication status

The existing implementation passed 188 targeted background checks before the metadata/manual update. This includes toolbar, authoring, paths, snapshot, startup and display checks. No new functional test run or native 4.3.1 package qualification is claimed by this packaging change. The previous shelf-width verification limitation remains.

Download [b4_ghost_tool_v4.3.1.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip) and the [4.3.1 manual PDF](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/GhostTool_User_Manual.pdf). Install the ZIP through Edit > Preferences > Add-ons > Install from Disk and restart Bforartists. Source, ZIP metadata, descriptions and manual identify **4.3.1**. The earlier **4.2.11** release keeps its original number and assets.

The [4.3.1 package receipt](package-receipt.json) records ZIP integrity, version metadata and byte-for-byte matching with all 30 source modules. These are artifact checks, not a new functional test run.

ZIP SHA256: `8471c86ac12168bac6d44e2abedb64a6509a979cbb02ba6d72c0829835e12863`.
