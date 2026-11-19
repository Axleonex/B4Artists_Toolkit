# BoneCraft 9.2.18

Mechanism forms now store captured control values under `control_values`, avoiding the reserved `values` RNA identifier diagnostic in newer Bforartists builds. Earlier hosts still registered that property; the diagnostic alone did not mean saved forms were unusable.

Older saved forms remain readable without changing their storage when they are displayed, converted to the mechanism model, or applied. An explicit Save Form replaces that form with the new storage. Existing rig controls and interface locations are preserved.

This is the standalone Toolkit release. Its mechanism-form regression script is `tests/blender_bonecraft_mechanism_forms.py`; native host results and publication verification are recorded separately. The release archive includes the runtime modules, assets and GPL license.

Download: [BoneCraft-BFA-9.2.18.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/bonecraft-v9.2.18/BoneCraft-BFA-9.2.18.zip).

`package.py` rebuilds the archive from staged repository bytes and writes `package-receipt.json`. Stage source changes first. Rebuilding refuses to replace a different existing archive.
