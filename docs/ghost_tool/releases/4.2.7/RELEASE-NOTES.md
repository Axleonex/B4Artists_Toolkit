# Ghost Tool 4.2.7

Ghost Tool now starts with a visible Top Toolbar beneath the main viewport header, in the native Tool Settings row.

- Top Header has been removed from Display Location. Available homes are Top Toolbar, Right Sidebar (N), and Left Tool Shelf (T).
- Saved Top Header settings migrate to a visible toolbar. Sidebar, Tool Shelf and explicit toolbar visibility choices retain their saved values.
- Hide Toolbar preserves previews and settings. The main-header Ghost Tool menu provides Show Toolbar recovery.
- Live Update Markers and Live Update Skin still default off. This release changes display defaults and migration; it adds no new backend jitter repair.
- Source version, current download links, repository description and Markdown/PDF guides identify 4.2.7. Earlier archives and receipts retain their original versions.

Download [b4_ghost_tool_v4.2.7.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.7/b4_ghost_tool_v4.2.7.zip). In Bforartists, use Edit > Preferences > Add-ons > Install from Disk, then restart after updating. Save preferences normally to retain migrated settings.

The exact archive passes **148 checks/cases in Bforartists 5.2.0** without a host-gate patch: 118 background checks and 30 GUI checks covering fresh defaults and legacy-header migration, Object/Pose, missing targets, cached visibility, hide/show recovery and reload. See the [package receipt](package-receipt.json). Production-rig acceptance, complete keyboard navigation, theme variants and a full visual check of every display location remain unverified.

This is a regular release marked Latest, with the matching ZIP and PDF guide in the [GitHub release](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.7). The repository archive is byte-identical to the downloadable asset.
