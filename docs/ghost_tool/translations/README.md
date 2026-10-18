# Ghost Tool 4.3.1 manual translations

These six editions translate the current [English guide](../GhostTool_User_Manual.md), including all 13 sections and all 59 source blocks. Each edition adds a short translation note. English button and setting names are retained so readers can locate the controls in Bforartists.

| Language | Read online | PDF |
|---|---|---|
| 简体中文 | [使用指南](GhostTool_User_Manual_zh.md) | [中文 PDF](GhostTool_User_Manual_zh.pdf) |
| Français | [Guide d'utilisation](GhostTool_User_Manual_fr.md) | [PDF français](GhostTool_User_Manual_fr.pdf) |
| 日本語 | [ユーザーガイド](GhostTool_User_Manual_ja.md) | [日本語 PDF](GhostTool_User_Manual_ja.pdf) |
| 한국어 | [사용자 안내서](GhostTool_User_Manual_ko.md) | [한국어 PDF](GhostTool_User_Manual_ko.pdf) |
| Português | [Manual do usuário](GhostTool_User_Manual_pt.md) | [PDF em português](GhostTool_User_Manual_pt.pdf) |
| Español | [Guía de uso](GhostTool_User_Manual_es.md) | [PDF en español](GhostTool_User_Manual_es.pdf) |

The translations cover the top and bottom toolbars, Before/Ahead counts, hold menus, repeated dragging, pinning, curve editing, live updates and snapshots. They follow the English guide's verification limits. No professional linguistic review is claimed. Refer to English if wording is unclear; translation does not change the add-on interface language.

The PDFs embed the fonts used for Latin, Chinese, Japanese and Korean text. The [manifest](manifest.json) records the exact English source hash, coverage counts and translated Markdown/PDF hashes. Markdown hashes use UTF-8 with LF newlines.

## Rebuild the PDFs

With Python, ReportLab and the fonts listed in the renderer:

```powershell
python docs/ghost_tool/build_translated_manuals.py
```

The default font directory is the Windows Fonts folder. Set `GHOST_MANUAL_FONT_DIR` to use another directory containing those fonts. Rebuild after updating a translation or the English source, and review every rendered page. The renderer leaves the English manual and installation ZIP unchanged.
