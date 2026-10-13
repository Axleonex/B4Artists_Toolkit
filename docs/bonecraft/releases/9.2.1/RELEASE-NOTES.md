# BoneCraft 9.2.1

Fixes the starter rig shelf hiding Bforartists' other asset libraries.

- Keeps the native bottom asset shelf and its ordinary asset drag/drop.
- Includes BoneCraft Rigs alongside the existing libraries in the same selector.
- Makes the Starter Rigs switch filter only BoneCraft rigs.
- Keeps the separate Starter Rig Catalog's Rigify checks, fitting and delayed drag insertion.
- Restores native callbacks when upgrading from the previous shelf override.

Install **BoneCraft-BFA-9.2.1.zip** through Edit > Preferences > Add-ons > Install
from Disk, then restart Bforartists. Select All in the library selector and the
All catalog tab to browse assets across libraries.

The bottom shelf uses native armature-asset import. Use Starter Rig Catalog for
dependency-aware generation and fitting. Starters are skeletons/metarigs, not
generated Rigify control rigs.

## Verification

Bforartists 5.2.0 / Blender 5.3.0 Alpha, build 0a1ca45552db: the host regression
passes for all nine generators, native Object/Material/Collection/World/Geometry
Nodes filtering, the rig-only switch, in-place reload migration, dependency
failure handling, selected-mesh identity, fitting, redo controls, drag cancellation
and exact callback restoration. The library ownership tests and pure naming tests
also pass. The GUI check confirms the native shelf, preservation of the existing
libraries, ordinary asset visibility and successful nine-rig popup opening.

The 233-file ZIP passes CRC and embedded-version checks. Every packaged file
matches source byte-for-byte. The fix was applied to current repository 9.2.0;
the other tools were preserved.

SHA256: `0903581df3053ba3795aad8f8458696a99ead02c1dceff6e44e0562ab530c55b`.
