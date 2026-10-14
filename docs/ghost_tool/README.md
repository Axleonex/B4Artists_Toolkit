# Ghost Tool 4.2.11 documentation

Ghost Tool 4.2.11 defers viewport preference updates until the main loop to correct startup registration access. Its retained width helper widens the left shelf once to match an open N-panel, with a 240 px fallback designed for a closed panel; that fallback was not reached in this native run. It preserves later manual resizing. The duplicate main-header button is removed; all named lower toolbar sections and the direct Ghosts On switch remain. View > Show Ghost Toolbar recovers hidden toolbar controls. It defaults to a visible **Top Toolbar**. Top Header has been removed from display settings; saved Top Header choices migrate automatically. Right Sidebar (N), Left Tool Shelf (T), shared feature popovers, Hide/Show Toolbar recovery and cached marker/skin visibility remain available. Saved sidebar, shelf and toolbar visibility choices are retained.

The exact 4.2.11 ZIP passes 123 focused startup and toolbar checks in Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha), build hash 0a1ca45552db: 80 background checks, 35 native split-view checks and eight saved-preference startup checks. The startup isolation profile disables width writes. A separate width run passes ten preliminary checks for the initial N-panel match and manual resize preservation, but its preference-reset check fails when displayed and stored widths disagree; the guard declines the write. Later fallback and scale checks were not reached. JellyTest.blend has not been tested. See the [package receipt](releases/4.2.11/package-receipt.json).

[4.2.11 user guide](GhostTool_User_Manual.md) | [4.2.11 PDF](GhostTool_User_Manual.pdf) | [Toolbar guide](toolbar/README.md) | [4.2.11 release notes](releases/4.2.11/RELEASE-NOTES.md) | [4.2.11 package receipt](releases/4.2.11/package-receipt.json)

The guides describe the current interface. Detailed tool help remains available inside the add-on.

Choose **Display Location** in Edit > Preferences > Add-ons > Ghost Tool. Switching reveals the selected region and chooses its Ghost Tool tab when supported. Save preferences normally to retain the choice. Other native panels stay available. A left-shelf choice on a host without Bforartists shelf tabs uses Top Toolbar and shows an explanation in preferences.

Install the [4.2.11 ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.11/b4_ghost_tool_v4.2.11.zip). Restart Bforartists after installation. Live updates default off; existing scenes retain their saved choices.

The earlier 3.3.0 PDF is retained under [archive/](archive/) for historical reference. It does not describe the current interface.

See the [release index](../../releases/VERSIONS.md) for the current download, verification and publication status.

Earlier downloads and reports retain their original versions and checksums. The [published 4.2.2 prerelease](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.2), [4.2.5 display-location report](display-location/verification.md), [4.2.5 Compare report](compare-targets/verification.md), and [original toolbar verification](toolbar/verification.md) describe those specific builds.
