# BoneCraft documentation

## Manual

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

The English source and all six translated editions cover the BoneCraft 9.1.2 interface. Each edition contains the illustrated Simple Human/mannequin/Auto-Rig/IK-FK workshop and the Crescent Rose Mechanisms tutorial. The translated instructions, captions and image descriptions reuse the same 92 English screenshots and numbered callouts; control names are retained in English to match those images. Each PDF has page numbers and chapter ranges calculated for its own language.

The translations are machine-generated and reviewed for technical terminology, structure, links and preserved settings. They are not certified professional translations. See the [English interface audit](reviews/english-manual-interface-9.1.2.md) and [translation validation report](reviews/manual-translations-9.1.2-2026-10-12.md).

## PDFs

Build a PDF of each language's manual (needs Chrome or Edge, and Python with the `markdown` package: `pip install markdown`):

```
python scripts/build_manual_pdf.py            # all languages
python scripts/build_manual_pdf.py en ja      # some
```

The PDFs are written to the folder named by `DEFAULT_OUT` in the script (`--out` picks another folder). They are not kept
in the repository.

## Examples

`../examples/mannequin/` — the Simple Human preview and completed Auto-Rig/IK-FK training examples.

`../examples/crescent-rose/` — Crescent Rose rigged with Mechanisms, and the files the manual's chapter 12 tutorial starts from.

## More

- [BoneCraft Rigging Suite](BoneCraft_Rigging_Suite.md) — the production rigging suite in detail.
