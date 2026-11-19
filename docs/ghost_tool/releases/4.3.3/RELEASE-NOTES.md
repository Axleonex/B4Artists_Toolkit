# Ghost Tool 4.3.3

Date: 2026-11-19

Ghost marker and onion-skin sampling now work while Anim Assist's Timeline toolbar is idle. Previously its persistent pointer handler was treated as an unfinished edit, preventing generation.

Only the observed passive `ANIMASSIST_OT_timeline_pointer` is exempted. Actual transforms, gizmos, frame scrubbing, active Anim Assist sliders and unknown modal operations remain protected. Preview live-update defaults and source animation behavior remain as before.

Install the new Ghost Tool ZIP through Preferences > Add-ons > Install from Disk, then restart Bforartists or reload the add-on. This is a Ghost Tool update; no application update is required for this correction.

## Verification

Verified on official Bforartists 5.2.3, build `746e15e13b04` (Blender 5.3 Alpha), using the exact release ZIP and isolated user resources, including extensions:

- Four modal-guard regression tests pass; the idle-observer test fails on the previous published source and passes with this fix. Native/unknown edit guards stay protected.
- Nine startup-registration guard tests and 20 authoring regressions pass.
- A real GUI window with Anim Assist 12.11.0's actual pointer handler generates nine markers at verified frames/world positions and three mesh previews. Source keys and the playhead/subframe are preserved; cleanup, disable and native removal pass.
- ZIP CRC, source/license parity, embedded version and repeated deterministic builds pass. See `package-receipt.json` for the artifact checksum.

This targeted check is not every-operator, production-rig or future-host certification. Initial host-probe results are retained outside the release: an unrelated lazily loaded user extension changed a global handler count before extensions were isolated; the fully isolated replay passes without changing product code.

## Scope

Two release source modules change: the guard in `utils.py` and version metadata in `__init__.py`. Other Ghost Python files remain unchanged. The archive includes the repository license. Production rigs, every operator and future host versions are not certified by this targeted release.
