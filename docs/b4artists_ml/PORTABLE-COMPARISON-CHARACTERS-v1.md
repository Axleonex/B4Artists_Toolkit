# Portable comparison characters v1

Three project-owned procedural humanoids now close the missing Bforartists side of the frozen matched-comparison asset gate. Each profile has one neutral source `.blend` and one FBX that must be used unchanged for both B4ML and Cascadeur in a matched pair:

| Profile | Skeleton height | FBX SHA-256 |
|---|---:|---|
| Standard Humanoid | 1.75 m | `aa6d25a49328304d3595baf6fa03a936aaeb33443cdb5ac8edf2660f73e29d49` |
| Tall Long-Limbed Humanoid | 2.03 m | `5cddbd969217d4beff5eec671496a7471cda3eed6b8320da8b0bbc79305bb5e1` |
| Short Broad Humanoid | 1.49 m | `721a2cba3584aeeb622237cbf522ee1de592e1af5c1d5a528cf26c5ac11a6426` |

The bodies use one common 26-bone Unity-style hierarchy, including nondeforming end bones that preserve leaf lengths through FBX. Each visible mannequin has 160 rigidly weighted vertices and 120 faces. The files contain exactly one armature and one bound mesh, identity object transforms, no Actions, no images, no linked libraries, and no third-party character mesh, texture, or motion data. The block geometry is deliberately simple so appearance does not become a hidden comparison variable.

`training/b4artists_ml/results/portable-comparison-characters-v1-host.json` records three source-file checks and three fresh FBX imports in Bforartists 5.2.0 Alpha. Every import retained all 26 bones and parents, exact quantized vertex positions, polygon topology and per-vertex weights, one bound Armature modifier, complete Unity Humanoid adapter recognition, and an actual deformation response. Skeleton height, shoulder span, hip span, and horizontal arm reach also remain within the frozen tolerances. The final evidence report is `training/b4artists_ml/results/portable-comparison-characters-v1.json`, SHA-256 `2dac0ad8eb5dac31e7e7d7d899bb644f71e715d69bc5c5f1bdeb036aa9b21bee`.

![Standard, tall long-limbed, and short broad neutral characters](../../training/b4artists_ml/results/portable-comparison-characters-v1.png)

The preview is an author presentation and readability check. It is not motion-quality evidence or an independent animator rating.

## Comparison status

`training/b4artists_ml/cascadeur_comparison_protocol_v2.json` supersedes the prospective v1 protocol without changing the eight tasks, matched workflows, metrics, run counts, human-review design, or parity/superiority thresholds. It binds the exact six asset files, the asset manifest, and the Bforartists roundtrip audit before any comparison result exists.

The read-only installation audit now confirms `C:\Program Files\Cascadeur\cascadeur.exe`
is present (file version `2025.3.0.14514`, executable SHA-256
`195005351e8fca2ca0b1a05f94fa45e7fdd0ab43478e10b2bf01d50cddabac15`) and that
all three frozen FBX hashes still match. It deliberately does not launch
Cascadeur or infer edition, entitlement, settings, import behavior, units,
rest pose, or standard-rig mapping. The bounded disposable Cascadeur import audit
passes for all three assets; conversion, all animator sessions, and the learned temporal comparison therefore remain
open. These assets remove the “three assets not frozen” blocker; they do not
establish Cascadeur compatibility, parity, or superiority. See
`training/b4artists_ml/results/cascadeur-installation-audit-v1.json`.

`training/b4artists_ml/cascadeur_import_audit_console_v1.py` was executed in
the installed Cascadeur Python console. The filtered local license audit also
records the active yearly PRO entitlement and export/professional-feature
flags without retaining the account identifier. It uses disposable application scenes
to import each frozen FBX and record joint, mesh, RigInfo, timing, hash and
scene-removal evidence. The resulting `cascadeur-import-audit-v1.json` is a
bounded `PASS`; it does not qualify conversion or matched animation.

The read-only capability probe and validator now also pass in
`training/b4artists_ml/results/cascadeur-capability-probe-validation-v1.json`.
The installed session exposes the FBX loader, rigging window, inbetweening,
AutoPhysics and settings-manager surfaces; `AnimationTool` was not exposed in
this session. All three frozen assets imported with 26 joints and one mesh,
their hashes matched, and their disposable scenes were removed. This remains
API/import evidence only; settings values, conversion, matched animation,
parity and superiority remain unverified.

### Cascadeur import-audit handoff

On the desktop with the installed Cascadeur application open, open its embedded
Python console and execute the following two lines exactly:

```python
exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_import_audit_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-import-audit>', 'exec'))
run()
```

The script is read-only with respect to the frozen FBX files and uses disposable
application scenes. After it returns, preserve the generated
`training/b4artists_ml/results/cascadeur-import-audit-v1.json` and its console
output. A `PASS` here proves only the bounded import/scene-removal audit; it
does not prove conversion, edition or entitlement, animator usability, parity,
superiority, or full-goal completion.

### Cascadeur capability-probe result and reproduction

The read-only capability probe
`training/b4artists_ml/cascadeur_capability_probe_console_v1.py`. It records the
embedded API's exposed FBX, rigging, animation and settings surfaces, then
imports the same three frozen FBX files into disposable scenes and records
behaviour counts before removing those scenes. It does not invoke rig
conversion, change settings, save scenes, export files, or modify the frozen
assets.

With Cascadeur open, load and execute it in the same embedded Python console:

```python
exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_capability_probe_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-capability-probe>', 'exec')); run_with_diagnostic()
```

Preserve `training/b4artists_ml/results/cascadeur-capability-probe-v1.json`,
then run `python training/b4artists_ml/check_cascadeur_capability_probe_v1.py`
from the repository root to reproduce the checksum-bound validation receipt.
This `PASS` improves API and import evidence only; it does not establish
standard-rig conversion, settings export, animation quality, parity,
superiority, or full-goal completion.

### Cascadeur standard-rig preflight

The next disposable step is
`training/b4artists_ml/cascadeur_standard_rig_preflight_console_v1.py`. It
tries the installed `standard.qrigcasc` Quick Rigging template and prototype
generation calls on each imported frozen asset, then removes every temporary
scene. It does not save, export, run animation, or claim final standard-rig
quality or parity.

With Cascadeur open, execute:

```python
exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_standard_rig_preflight_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-standard-rig-preflight>', 'exec')); run_with_diagnostic()
```

Then run `python training/b4artists_ml/check_cascadeur_standard_rig_preflight_v1.py`
from the repository root. A passing receipt remains preflight evidence only;
matched animation and parity are still separate gates.

The known Bforartists host shutdown access violation occurred after the builder, audit, and render wrote complete durable outputs. Those outputs pass byte-level verification; clean host shutdown remains unqualified. The frozen `releases/b4artists_ml_v0.36.0.zip` remains byte-identical at `3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5`.
