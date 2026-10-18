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

See the [October 15 manual review](../../docs/releases/2026-10-15/manual-review.md) for the source comparisons and documentation checks across all three add-ons.

The English source and all six translated editions cover BoneCraft **9.2.5**, including the native Starter Rigs catalog tab, current tool paths, Task Board instructions and chapter 11 release notes. Start with chapter 1 for tabs, nested sections, selection requirements and Scene Properties visibility. Chapter 6 explains how to enable Starter Rigs once in the shelf catalog menu; the old top-left viewport starter controls were removed.

Every edition includes the full illustrated chapter 6 Simple Human/mannequin/Auto-Rig/IK-FK workshop and chapter 12 Crescent Rose tutorial: eight FBX preparation steps, 30 Mechanisms steps, and the same 92 shared screenshots with translated captions and image descriptions. Screenshots retain their historical 9.1.2 capture labels, and the narrated video retains its 9.1.3 test scope; neither is presented as a new 9.2.5 capture. Use the current navigation map when a historical screenshot differs from the current layout.

The translations are machine-generated and are not certified professional translations. English control names and object/bone identifiers are retained where needed to match the screenshots. The [9.2.5 validation report](reviews/manual-translations-9.2.5.md) records structural, image, link and PDF checks. The [earlier English interface audit](reviews/english-manual-interface-9.1.2.md) remains historical evidence.

## PDFs

Build a PDF of each language's manual (needs Chrome or Edge, and Python with the `markdown` package: `pip install markdown`):

```
python scripts/build_manual_pdf.py            # all languages
python scripts/build_manual_pdf.py en ja      # some
```

The reviewed 9.2.5 PDFs are available in [manual/pdf/](manual/pdf/):

| Language | PDF |
|---|---|
| English | [BoneCraft_Manual_en.pdf](manual/pdf/BoneCraft_Manual_en.pdf) |
| 中文 | [BoneCraft_Manual_zh.pdf](manual/pdf/BoneCraft_Manual_zh.pdf) |
| Français | [BoneCraft_Manual_fr.pdf](manual/pdf/BoneCraft_Manual_fr.pdf) |
| 日本語 | [BoneCraft_Manual_ja.pdf](manual/pdf/BoneCraft_Manual_ja.pdf) |
| 한국어 | [BoneCraft_Manual_ko.pdf](manual/pdf/BoneCraft_Manual_ko.pdf) |
| Português | [BoneCraft_Manual_pt.pdf](manual/pdf/BoneCraft_Manual_pt.pdf) |
| Español | [BoneCraft_Manual_es.pdf](manual/pdf/BoneCraft_Manual_es.pdf) |

The default build output remains the local folder named by `DEFAULT_OUT`; use `--out docs/manual/pdf` when running from `bonecraft/` to rebuild these repository PDFs. Each edition's page numbers follow its own layout.

## Examples

- [IK/FK practice](../examples/ikfk/README.md) — both rig types shown in the beginner video.
- [Mannequin workshop](../examples/mannequin/README.md) — the Simple Human preview and completed Auto-Rig training examples used in chapter 6.

`../examples/crescent-rose/` — Crescent Rose rigged with Mechanisms, and the files the manual's chapter 12 tutorial starts from.

## More

- [BoneCraft Rigging Suite](BoneCraft_Rigging_Suite.md) — the production rigging suite in detail.
