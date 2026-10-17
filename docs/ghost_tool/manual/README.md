# Ghost Tool 4.3.1 translated manuals

These six machine-translated editions cover all 13 sections of the corrected English Ghost Tool 4.3.1 guide. Control names stay in English so readers can match the interface. They are not certified professional translations.

| Language | Read online | PDF |
|---|---|---|
| English (source) | [English](../GhostTool_User_Manual.md) | [PDF](../GhostTool_User_Manual.pdf) |
| 中文（简体） | [中文](zh/GhostTool_User_Manual.md) | [PDF](zh/GhostTool_User_Manual.pdf) |
| Français | [Français](fr/GhostTool_User_Manual.md) | [PDF](fr/GhostTool_User_Manual.pdf) |
| 日本語 | [日本語](ja/GhostTool_User_Manual.md) | [PDF](ja/GhostTool_User_Manual.pdf) |
| 한국어 | [한국어](ko/GhostTool_User_Manual.md) | [PDF](ko/GhostTool_User_Manual.pdf) |
| Português | [Português](pt/GhostTool_User_Manual.md) | [PDF](pt/GhostTool_User_Manual.pdf) |
| Español | [Español](es/GhostTool_User_Manual.md) | [PDF](es/GhostTool_User_Manual.pdf) |

## Source and scope

Source commit: `6db5a589253e9dede9f9c92c15100560aaeb59a9`.

English Markdown SHA256: `a8ef2ef0de3e88ec8577e79d234b260939575f7c1bf4c68e677061c70887f80a`.

This batch translates Ghost Tool only, using the six languages already offered by the toolkit's BoneCraft documentation. It does not mark the older BoneCraft translations as current, or change Anim Assist manuals. The standalone toolbar reference remains in English; its controls and behavior are covered in the translated user guides.

The translations preserve the existing shelf-width limitation and distinguish the previous 188 implementation checks from the 4.3.1 packaging checks. Documentation checks do not substitute for running the add-on in Bforartists.

## Rebuild PDFs

Install Python's `reportlab` package. The English-only default build remains supported. For these six editions, the renderer embeds Arial, Microsoft YaHei, Yu Gothic and Malgun Gothic from the Windows Fonts directory; use `--font-dir` to supply another directory containing those fonts. Missing fonts stop the build rather than silently replacing characters.

[PowerShell]

```powershell
python docs/ghost_tool/build_manual_pdf.py fr pt es zh ja ko
```

Build a single edition by naming its language code. PDF links are resolved relative to each edition and point to the corresponding files on GitHub. The translated URLs become publicly accessible once the files are published.

See [validation](validation.md) for source tracking, structural checks and PDF review.
