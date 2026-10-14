# BoneCraft 9.2.4 — repository build

Fixes the Task Board and native Grab/tool cycling in Bforartists.

- Keeps Place Rig Markers and Build Mechanism outside native toolbar groups, preventing separator entries from breaking Grab/Move and tool cycling in Object and Pose modes.
- Open Health Check calls the registered Run Validation operator and displays a refreshable results popup.
- Accepts an armature or a parented / Armature-modifier-bound avatar mesh.
- Reports a disabled validator package or failed registration clearly.
- Quick Wins remains the top three recommendations; Remaining Tasks excludes those cards and omits empty categories.
- Updates source and export-sidecar version stamps to 9.2.4, with seven-language UI labels.

Host regression tests pass for task counts, collapse, selection, validator availability, popup dispatch/results and refresh. Native popup appearance is not visually verified. The installable ZIP is included in the repository; no 9.2.4 GitHub Release has been published.

## Rebuilt 9.2.4 ZIP

The repository ZIP is rebuilt from source commit `a7b0c40` to include the Grab correction.
Its package payload changes only `autorig/tools.py` and `mechanisms/tools.py`.
The add-on and export version remain 9.2.4. This replaces the earlier 9.2.4 archive
with SHA-256 `311399bf7cc7341d8125a2195ec701f5c3c485b7757820166281109ea742f0dd`.
The package receipt records the replacement checksum and source-parity checks.

The extracted ZIP passes the toolbar-cycle and Task Board host suites in Bforartists 5.2.0,
including Object/Pose activation, reload, legacy separator cleanup and disable/re-enable.
