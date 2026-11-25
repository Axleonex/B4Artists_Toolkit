# BoneCraft 9.2.19

The Auto-Rig wizard's placement axis locks now behave as labelled for every marker type. Finger markers obey the lock (they previously resolved against the face-marker list and silently ignored it), a locked axis survives the surface snap instead of being dragged to whichever surface point the snap picks, and an unplaced midline marker locks to the mesh's centreline rather than to world X=0, so bodies modelled off the origin start their midline markers on-body.

Marker auto-detection is noticeably more accurate and no longer produces collapsed guesses. The arm trace runs on a finer voxel grid so thin forearms stay connected; when a trace still collapses, shoulder/elbow/wrist fall back to a proportional split along the arm at review-band confidence instead of three joints stacked on one point. On the box-humanoid benchmark the median marker error dropped from 8.4% to 4.4% of body height and the worst case from 37.2% to 10.3%; on the mannequin example the arm joints are now distinct and plausible. Toe and heel proposals are clamped to the ground plane.

Existing saved sessions and rigs are unaffected; the wizard's placement toolbar and its defaults are unchanged. The new placement axis-lock behaviours are covered by `tests/test_axis_lock_host.py`; the 9.2.18 mechanism-form regression (`tests/blender_bonecraft_mechanism_forms.py`) still verifies `passed: true` on Bforartists 5.3.0 Alpha with the 9.2.19 source.

This is the standalone Toolkit release. The release archive includes the runtime modules, assets and GPL license; native host results and publication verification are recorded separately.

Download: [BoneCraft-BFA-9.2.19.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/bonecraft-v9.2.19/BoneCraft-BFA-9.2.19.zip).

`package.py` rebuilds the archive from staged repository bytes and writes `package-receipt.json`. Stage source changes first. Rebuilding refuses to replace a different existing archive.
