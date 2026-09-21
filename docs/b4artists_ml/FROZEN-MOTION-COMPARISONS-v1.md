# Frozen motion comparisons

These three short animations show why the previous sequence models were not promoted. They compare the reference motion, the procedural shape control and both previous direct seeds. They use fixed, earliest development windows with a 32-frame gap and surrounding context, selected by clip identity before rendering. No weights from the current tangent experiment were read.

All panels share camera, timing and scale within each case. Playback is half speed. The plots show 17 semantic joint positions in canonical coordinates; they do not show mesh deformation, bone twist, contact forces, full performances or the Bforartists interface. These are research inspection artifacts, not independent animator assessments or evidence of Cascadeur parity.

| Excerpt | Animation | Middle frame |
|---|---|---|
| Marching | [GIF](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/138_01.gif) | [PNG](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/138_01-middle.png) |
| Run | [GIF](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/141_03.gif) | [PNG](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/141_03-middle.png) |
| Jump distances | [GIF](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/141_04.gif) | [PNG](../../training/b4artists_ml/results/frozen-sequence-visuals-v1/141_04-middle.png) |

The running and jumping middle frames were visually inspected for render readability: labels are legible, all four skeletons remain visible, and panel framing is consistent. That inspection is an author render check, not a motion-quality score. The previous models visibly differ from the reference in these frames; the numerical development report remains the authority for their failed acceptance gates.

Source motion: the existing CMU Motion Capture Database research corpus, via the retained Bruce Hahne conversion and pinned una-dinosauria/cmu-mocap revision 09a07f54f3bbb58797325f009282d0b2048a2871. Original source hashes, window identities and projected-prediction hashes are recorded in training/b4artists_ml/results/frozen-sequence-visuals-v1/report.json. Existing provenance and usage restrictions remain applicable. No new motion files were downloaded.
