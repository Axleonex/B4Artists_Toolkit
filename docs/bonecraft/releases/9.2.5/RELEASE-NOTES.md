# BoneCraft 9.2.5 — Starter Rigs catalog tab

- Removes the Starter Rigs controls from the top-left viewport header.
- Places all nine starters in one native catalog named **Starter Rigs**.
- Uses the host's original shelf callbacks and native asset import.
- Keeps **Add → Armature → Starter Rig Catalog** for dependency-aware generation and fitting.
- Updates the add-on and export-sidecar version stamps to 9.2.5.

After installing, open the catalog menu at the left of the bottom asset shelf,
choose **All** libraries and check **Starter Rigs** once. Its tab appears beside
the other catalog tabs. Tab visibility is controlled by the host; this setting
has no Python API, so installation cannot enable it automatically.

The targeted starter suite passes in Bforartists 5.2.0, including all nine rigs,
catalog metadata, dependency failures, fitting, library ownership, native
callback restoration and Add-menu access. See the package receipt for archive
and source-parity checks. The 9.2.5 archive is available from the repository's
release index; the latest tagged GitHub Release remains 9.2.3.

Native-window verification confirms the rightmost tab, all nine starters when selected,
and removal of the top-left controls. [Screenshot](ui/starter-rigs-selected.png).
