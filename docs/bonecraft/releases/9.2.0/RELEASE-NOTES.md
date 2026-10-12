# BoneCraft 9.2.0

Adds a complete starter rig catalog to Rig Builder. All nine thumbnails are visible from the start: Basic Humanoid, Simple Human, Full Human, Basic Quadruped, Cat, Horse, Wolf, Bird and Shark. Use the catalog selector to filter Humans, Quadrupeds and Other Animals.

- Basic Humanoid works without Rigify. Selecting or dropping a Rigify starter while Rigify is inactive offers **Enable Rigify & Add Rig** or Cancel. Acceptance continues with the chosen starter; cancellation or a missing generator adds nothing.
- The viewport header's **Starter Rigs** switch returns to the regular asset shelf and saves the choice. **Add → Armature → Starter Rig Catalog** opens the same chooser as a popup. A single **Enable Rigify** button is also available in the header.
- Click a thumbnail or drop inside the viewport. A selected mesh is fitted by default; automatic weighting and control generation start off and remain available in Adjust Last Operation. Without a mesh, use Quick Rig's **Fit Dropped Rig** afterwards.

These starters are skeletons/metarigs. Inspect joint placement before weighting or generating a control rig. The bundle contains the eight Rigify presets supplied by the tested host plus BoneCraft's Basic Humanoid. A host version without a selected preset reports that limitation.

## Install or update

Download **BoneCraft-BFA-9.2.0.zip** from this release and use **Bforartists → Edit → Preferences → Add-ons → Install from Disk**, then enable BoneCraft. Restart Bforartists after replacing an older installation so the new shelf callbacks load. The package root remains `boneforge` so existing preferences carry over. This build requires Bforartists.

## Verification

The starter catalog passed targeted checks on **Bforartists 5.2.0**, underlying Blender 5.3.0 Alpha, build `0a1ca45552db`: all nine actual assets and previews, available generators, dependency failures, selected-mesh identity, fitting, library ownership and cleanup, shelf switching and native-callback restoration. Actual viewport click/drop, dependency Cancel/Enable & Add, and undo/redo passed. All five focused host modules also pass when loaded from the extracted 9.2.0 release ZIP. The versioned ZIP passes CRC checks and matches every packaged source file byte-for-byte; it excludes Python caches and Blend backups.

[Starter catalog UI evidence](https://github.com/Axleonex/B4Artists_Toolkit/tree/bonecraft-v9.2.0/docs/bonecraft/starter-shelf-implementation) · [English Rig Builder guide](https://github.com/Axleonex/B4Artists_Toolkit/blob/bonecraft-v9.2.0/bonecraft/docs/manual/en/06-rig-builder.md)

The UI strings include all supported languages. The English guide documents this catalog; the six translated manuals still lag the current interface.

SHA256: `655ad55bfac32b461d66c915ba4ab8c85252779cf59a14a2af84b6e9f4429f77`.
