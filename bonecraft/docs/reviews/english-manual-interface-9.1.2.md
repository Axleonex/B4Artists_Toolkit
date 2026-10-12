# English manual interface audit — BoneCraft 9.1.2

Checked 2026-10-10 against `releases/BoneCraft-BFA-9.1.2.zip`, the latest BoneCraft package in this checkout. This does not establish the latest public release on GitHub.

**Result (updated 2026-10-11):** the confirmed English text corrections below are retained. The Crescent Rose tutorial has now been replayed against the running 9.1.2 release, with 52 annotated English images and rebuilt, validated examples. Its English review package awaits owner confirmation before translations. Other manual tools remain source-audited unless explicitly exercised in the tutorial; this is not a claim that every BoneCraft feature received an interactive test.

## Confirmed corrections

| Area | Before | Corrected instruction | Packaged source evidence |
| --- | --- | --- | --- |
| Preferences | Shelf Width was missing | Widen Narrow Shelves; Left 240 / Right 260 px defaults; manual resizing is retained | `core/prefs.py:69–79,386–399` |
| Properties locations | Armature data could be read as containing all sections | Armature tools have their own copies; Rig Builder, Mechanisms and CATS sections use Scene instead | `core/properties_mirror.py:34–69`; `taskboard/sidebar.py:1541–1603` |
| Wizard navigation | Back, Cancel and Next described at both top and bottom | Back/Cancel at top; Next below applicable steps; Generate Rig and Close Wizard replace Next on later steps | `autorig/wizard.py:2025–2056` |
| Quick Rig | Diagnostic and Rigify controls had no fold location | Troubleshooting holds diagnostics and conditionally Inspect Active Rig Controls or Generate Control Rig | `taskboard/sidebar.py:615–635,669–674` |
| Mannequin prerequisite | Suggested it created a figure with a new rig | Requires an existing armature or its child mesh; Quick Rig can supply the armature | `autorig/mannequin.py:1310–1319,1666–1678` |
| Mannequin actions | Regenerate used new settings; Remove deleted the rig | Regenerate uses saved settings; Remove deletes only the preview mesh; Add Mannequin uses scene settings and replaces the preview by default | `autorig/mannequin.py:1338–1346,1367–1380,1472–1526` |
| Mannequin settings | Main settings appeared to be directly below the buttons | Options holds core controls, with Advanced inside; use Add Mannequin to apply changed scene settings | `autorig/mannequin.py:1583–1629,1680–1687` |
| Weight recalculation | Smart shortcut and full settings were insufficiently distinguished | Full Skin controls precede the action; Smart Automatic Weights opens a target/rig/mode dialog; Clothing needs a source mesh | `weights/weight_tools.py:83–110,344–371` |
| CATS advanced weights | Advanced Recalculation implied full controls appeared there | It expands a location hint for BoneCraft → Skin → Weight Tools | `vrchat/cats/cats_panel.py:617–632` |
| Delta Mush / Chain Dynamics | Persistent folds and post-click parameter locations were omitted | Settings folds and existing-setup actions documented; creation parameters adjusted in Adjust Last Operation | `weights/delta_mush.py:194–215`; `advanced_rigging/chain_dynamics.py:63–80,330–358` |
| Proximity Wrap | Listed parameters without their location or release limitation | Driver first; Options fold; rest-pose requirement; falloff/distance stored but not applied to binding; Unbind disables the modifier | `weights/proximity_wrap.py:55–115,134–142,194–225` |
| CATS layout | Blanket claim that settings follow actions | Required inputs and Fix Model switches remain above actions; Visemes overwrite setting is inside Options | `vrchat/cats/cats_panel.py:228–245,291–315,337–358`; `vrchat/cats/translate.py:874–912` |

Source paths in the evidence column are inside the package's `boneforge/` folder; the corresponding checkout is `bonecraft/boneforge/`.

## Other interface areas checked

- Default tab sides and independent Scene Properties visibility.
- Add → Armature, Pose → BoneCraft, Weights → BoneCraft and Object → Mechanisms access; Pose/Weights shelf buttons and narrow icon layouts.
- Place Rig Markers and Build Mechanism toolbar workflows.
- Avatar Tools versus VRChat Tools group names and guide navigation paths.
- Weight Mirror, Transfer, Flood to Custom, Weight Table, Spline IK, Ribbon, Pose Blend and Corrective Edit parameter locations.
- Mechanisms section order and Sequence recording labels: Move Slider to End → Record Step N.

These are source checks of locations, controls and instructions, not a claim that every tool was exercised with a real rig.

## Completed Crescent Rose interface replay

The isolated Bforartists 5.2.0 test host loaded the packaged BoneCraft 9.1.2, English interfaces, default theme, Show Helpers and Scene Properties visibility. Both Tool Shelf and Scene Mechanisms copies were inspected. The owner's ordinary Bforartists sessions were kept separate.

All eight FBX preparation steps and 30 Mechanisms steps were executed through the interface. The refreshed chapter documents mode/keymap differences, plate and strut picks, both current sequence recording-button states, target-entry numbering, end-state arming and Test restoration. The old screenshot caveat is removed because all 52 retained chapter images now come from this release replay. Read the [execution report](crescent-rose-english-execution-2026-10-10.md) for the validation and raw-capture evidence.

The earlier session with no BoneCraft result was not used as release evidence. The later isolated host, candidate tests and actual GUI captures supersede that limitation for this tutorial. No translations have started; the owner's completed-English confirmation is still pending.

## Validation

- English-only `test_manual` passed after these corrections: all 13 Markdown files, chapter structure, links, bold UI labels, images and size limits.
- Joined English HTML rendered; all internal links resolve.
- `git diff --check` passed.
- Validation used the packaged source and temporary Python dependencies; no test assertions were suppressed. Language scope was explicitly English. The six translations remain outside this pass.
- The initial text audit was committed locally as `9fd0374`; the completed tutorial refresh is a separate local work-branch commit. No push or merge is part of this execution.
