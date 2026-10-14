# BoneCraft 9.2.4 — repository build

Fixes the Task Board in the latest BoneCraft 9.2.3 codebase.

- Open Health Check calls the registered Run Validation operator and displays a refreshable results popup.
- Accepts an armature or a parented / Armature-modifier-bound avatar mesh.
- Reports a disabled validator package or failed registration clearly.
- Quick Wins remains the top three recommendations; Remaining Tasks excludes those cards and omits empty categories.
- Updates source and export-sidecar version stamps to 9.2.4, with seven-language UI labels.

Host regression tests pass for task counts, collapse, selection, validator availability, popup dispatch/results and refresh. Native popup appearance is not visually verified. The installable ZIP is included in the repository; no 9.2.4 GitHub Release has been published.
