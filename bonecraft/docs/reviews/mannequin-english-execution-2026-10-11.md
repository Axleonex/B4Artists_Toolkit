# English mannequin workshop execution report

Completed for owner review on 2026-10-11. English only; translation remains gated on direct owner confirmation.

## Delivered

The Rig Builder chapter now contains 40 illustrated steps in prerequisite order: eight Simple Human/metarig-to-mannequin steps, 22 rigless-input/Auto-Rig steps, and ten weight-validation/IK/FK steps. Each has a genuine interface screenshot, numbered red boxes or circles, and a matching caption. The first-avatar guide, Control Layer reference and contents link to the workshop.

The English PDF has 149 numbered pages. The workshop occupies pages 35–76. Each numbered step keeps its instructions, image and caption together. Both checkpoints are supplied in `examples/mannequin/`; the final example is deliberately posed to match the IK/FK comparison.

## Release and evidence

- Release: `releases/BoneCraft-BFA-9.1.2.zip`, SHA256 `9901bdb98da47384522b5137df58e8722f7d4f8c6e20cf1d835630c6bbaafa63`.
- Host: isolated Bforartists 5.2.0, underlying Blender 5.3.0 Alpha build `0a1ca45552db`. The Preferences screenshot displays add-on 9.1.2 and its isolated installation path.
- Real desktop captures: `G:/LapArt/output/rig-builder-captures/9.1.2/en/*.raw.jpg`, with capture metadata JSON. Interface contents were not synthesized.
- Reproducible annotation geometry: `docs/manual/images/rig-builder/circles.json`. Use `scripts/annotate_manual_images.py`'s `annotate(raw_jpg, destination_png, spec)` API for these JPEG captures; the older CLI assumes raw PNG filenames.
- Hashes, capture metadata, final rig checks and PDF results: `mannequin-english-evidence-9.1.2.json` beside this report.
- PDF and HTML: `G:/LapArt/output/bonecraft-manual/9.1.2-en-review/`.

## Findings incorporated into the guide

| Observed behavior | Documented route |
| --- | --- |
| Simple Human differs from BoneCraft Basic Humanoid | Identify the Rigify 29-bone preset explicitly |
| Mannequin is generated from an armature | Convert the neutral preview to mesh, clear its parent, remove vertex groups, and hide the old metarig to obtain rigless input |
| Anatomical/filtered preview was unsuitable for this exercise | Use Universal, Neutral, Medium, Joined output with Joint Smoothing |
| Scene Properties marker placement did not accept viewport clicks | Enable the viewport Rig Builder tab and place markers there |
| Smart Detection guesses were poor on the capsule mesh | Manually review/correct landmarks from front and side, including precision points and heels |
| Completion offers another mannequin despite an existing input mesh | Build Control Rig, then Close Wizard; do not add another mannequin |
| BoneCraft Collections panel failed to draw in this host | Use native Bone Collections Solo stars and In Front |
| Initial arm weights moved the upper arm with the forearm | Include the failed pose test, Bone Heat recalculation with backup, and corrected pose result |
| IK and FK use different controls | Show FK elbow rotation, snap to IK, select/move the wrist target, then snap back to FK |
| Oversized screenshots reduced the first PDF's print scale | Constrain image bounds and place each step on its own page |

## Validation

- English manual structure, sizes, image existence, naming and links: PASS using the existing manual test in an English-scoped scratch copy. Host commands, numeric settings and file identifiers use inline-code formatting; product UI labels retain the manual's existing convention. No translation content or test source was changed.
- Joined HTML has no unresolved chapter or heading targets.
- Final saved rig: 58 bones, 1,480 mesh vertices, zero vertices without deform weights, one Armature modifier targeting the generated rig, and an existing hidden weight backup.
- Read-only headless pose-response checks: left/right forearm FK controls affect 113/117 vertices; left/right shin FK controls affect 262/262 vertices. The validation process did not save changes to the example.
- GUI inspection verified the corrected elbow bend, IK endpoint movement and pose-preserving return to FK.
- PDF: all 149 footers match their physical page number and total; all 40 new images render within bounds; all 52 Crescent Rose images remain present. The full new workshop was reviewed in rendered contact sheets, with the opening pages rechecked after removing orphan section headings.
- Git whitespace check: PASS.

This is a capsule training preview, not production human topology. The guide was executed by the author in the tested host; an independent novice replay and exhaustive animation/export validation were not performed. The documentation describes the successful GUI workflow without changing add-on behavior. Experimental nearest-island weights were rejected and are not in either supplied example.

## Translation gate

No translations were edited or generated. Complete the owner's English review before planning or executing translated text or screenshots.
