# BoneCraft 9.2.0 release package verification

The actual `BoneCraft-BFA-9.2.0.zip` was extracted to a temporary directory and loaded in Bforartists 5.2.0 / Blender 5.3.0 Alpha, build `0a1ca45552db`, with factory startup. The runner asserted that the imported add-on came from that extraction and reported version `(9, 2, 0)`.

| Focused host module | Result |
|---|---|
| `test_starter_shelf_host` | PASS |
| `test_quick_rigs_asset_host` | PASS |
| `test_rig_assets_host` | PASS |
| `test_dropped_rig_host` | PASS |
| `test_ui_access_host` | PASS |

Process exit: **0**. Completion marker: `RELEASE ZIP HOST SUITE PASS`.

The package contains 233 unique files, nine starters, the `boneforge` root and 9.2.0 metadata. Every archive entry matches source bytes and the archive inventory matches the source inventory after excluding Python caches and Blend backups. CRC checks pass. The only runtime source change since the tested starter-catalog merge is the version number. The package receipt records the full ZIP and host-log hashes.

Earlier native viewport click/drop, dependency cancellation/activation, and undo/redo evidence remains in [starter-shelf-implementation](../../starter-shelf-implementation/README.md). The headless suite emits the existing missing-preference and repeated-panel-registration diagnostics from direct registration; all assertions pass.

[Package receipt](package-receipt.json) | [Release notes](RELEASE-NOTES.md)
