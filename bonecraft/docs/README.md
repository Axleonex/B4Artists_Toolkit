# BoneCraft documentation

**Current release: BoneCraft 9.2.17.**
[Download the installable ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/bonecraft-v9.2.17/BoneCraft-BFA-9.2.17.zip) ?
[Release notes](../../docs/bonecraft/releases/9.2.17/RELEASE-NOTES.md) ?
[Export naming guide](export-bone-naming.md).
The release adds Unity/Unreal naming choices and fixes export from Pose/Edit
Mode. Existing manual review dates and screenshot capture labels below are
historical; the linked export guide supplies the 9.2.17 instructions.


## Manual

Start with the [IK/FK beginner walkthrough](tutorials/ikfk-beginner.md): a narrated video, control-name reference and downloadable practice file containing Quick Rig and Auto-Rig examples. Motion was captured with BoneCraft 9.1.3 in Bforartists 5.2.0; the guide records the tested scope and a Rigify forearm twist limitation.

| Language | Start here |
|----------|------------|
| English | [manual/en/index.md](manual/en/index.md) |
| 中文 | [manual/zh/index.md](manual/zh/index.md) |
| Français | [manual/fr/index.md](manual/fr/index.md) |
| 日本語 | [manual/ja/index.md](manual/ja/index.md) |
| 한국어 | [manual/ko/index.md](manual/ko/index.md) |
| Português | [manual/pt/index.md](manual/pt/index.md) |
| Español | [manual/es/index.md](manual/es/index.md) |

The translations are machine-translated from the English edition.

See the [October 15 manual review](../../docs/releases/2026-10-15/manual-review.md) for the source comparisons and documentation checks across all three add-ons.

Reviewed October 15, 2026 against BoneCraft 9.2.4: the interface maps, moved-tool paths, Task Board instructions and chapter 11 release notes in all seven editions covered 9.2.4 at that review. Start with chapter 1 for tabs, nested sections, selection requirements and Scene Properties visibility. BoneForge has its own standard-Blender manual in the [BoneForge repository](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender/blob/main/docs/BoneForge_Documentation.md).

The illustrated English workshops retain screenshots captured with 9.1.2; their capture labels are historical, and the current navigation map gives the 9.2.4 locations. The six translated editions still lack the illustrated chapter 6 expansion and chapter 12 (Crescent Rose). Their interface guidance is updated, but use English for those workshops. See the [earlier English interface audit](reviews/english-manual-interface-9.1.2.md) for the scope of the original workshop checks.

## PDFs

Build a PDF of each language's manual (needs Chrome or Edge, and Python with the `markdown` package: `pip install markdown`):

```
python scripts/build_manual_pdf.py            # all languages
python scripts/build_manual_pdf.py en ja      # some
```

The PDFs are written to the folder named by `DEFAULT_OUT` in the script (`--out` picks another folder). They are not kept
in the repository.

## Examples

- [IK/FK practice](../examples/ikfk/README.md) — both rig types shown in the beginner video.
- [Mannequin workshop](../examples/mannequin/README.md) — the Simple Human preview and completed Auto-Rig training examples used in chapter 6.

`../examples/crescent-rose/` — Crescent Rose rigged with Mechanisms, and the files the manual's chapter 12 tutorial starts from.

## More

- [BoneCraft Rigging Suite](BoneCraft_Rigging_Suite.md) — the production rigging suite in detail.
