# Ghost Tool 4.2.8

Split 3D viewports now keep the same complete Ghost toolbar as a wide main viewport. Object and Pose mode show the same buttons, labels and order at every viewport width and UI scale. Tools no longer move into More or a Ghost-only layout when a viewport becomes narrow.

Middle-mouse drag the native Tool Settings row horizontally to reach buttons beyond a small viewport's width. A newly split viewport inherits the row. Hide/Show Toolbar remains available through the main-header Ghost Tool menu and preserves cached previews and settings.

This patch changes toolbar layout only. Live Update Markers and Live Update Skin retain their saved choices and defaults; animation sampling and authoring behavior are unchanged. Other modes retain their existing Ghost menu.

The exact ZIP passes **77 focused tests/checks in Bforartists 5.2.0**: 53 background tests and 24 native split-view checks covering Object/Pose, UI scale, new splits, horizontal panning, hide/show, frame/cache preservation and single header registration. See the [package receipt](package-receipt.json) and [split-view evidence](../../toolbar/split-view-verification.md). Keyboard navigation, alternate themes and production rigs are not covered by this focused verification.

Download [b4_ghost_tool_v4.2.8.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.8/b4_ghost_tool_v4.2.8.zip). Install through Edit > Preferences > Add-ons > Install from Disk and restart Bforartists after updating. The [regular release](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.8) includes the matching ZIP and PDF manual. Earlier packages and their original receipts remain historical records.
