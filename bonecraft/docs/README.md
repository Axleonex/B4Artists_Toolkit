# BoneCraft documentation

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

The English instructions have been checked against BoneCraft 9.1.2's packaged interface code. Chapter 6 includes the illustrated Simple Human/mannequin/Auto-Rig/IK-FK workshop. Chapter 12 was replayed in the isolated 9.1.2 host, with 52 annotated images, eight FBX preparation steps, 30 Mechanisms steps and validated example files. See the [English interface audit](reviews/english-manual-interface-9.1.2.md). The other six editions have 9.1.2 release notes, but their usage chapters still need the 9.1 interface updates. Chapter 12 (Crescent Rose) is currently available only in English. Use the English edition for the current controls and workflows.

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
