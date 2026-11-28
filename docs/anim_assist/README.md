# Anim Assist 12.11.2 candidate documentation

This edition covers the local, unpublished 12.11.2 candidate. The published standalone download remains at 12.11.1.

- [English user manual](AnimAssist_User_Manual.md) · [English PDF](AnimAssist_User_Manual.pdf)
- [Download the published 12.11.1 standalone add-on ZIP](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.11.1.zip)
- [12.11.1 release notes](releases/12.11.1/RELEASE-NOTES.md) · [Current changelog](../../anim_assist/CHANGELOG.md)
- [Recorded 12.11.0 Drivers qualification](releases/12.11.0/qualification.md)
- Historical: [12.10.0 stage-toolset qualification](releases/12.10.0/qualification.md) · [12.9.1 stage qualification](releases/12.9.1/qualification.md) · [12.8.0 editor qualification](releases/12.8.0/qualification.md)

The manual includes the sound-strip setup fix at source revision `7ec664d`, reviewed on November 20, 2026. It covers all seven Timeline families and five stage rows, Find and +N, sliders, tool settings and named layouts. It also covers the Dope Sheet, Action Graph, adaptive Drivers and NLA workflows, plus Scene Properties tools.

Current guidance includes full-height toolbar hit targets, outside-click settings dismissal, hover positioning and single-tooltip behavior from 12.10.1–12.10.3. It explains 12.11.1's native Find/menu Undo behavior and the separate direct-toolbar checkpoint. Driver instructions cover target inspection, native variable/expression settings, selected-channel response edits, active-only modifiers and read-only diagnostics.

Use the standalone ZIP with an existing Bforartists installation. The separately supplied custom/native test build already enables its bundled Anim Assist in factory preferences. It needs no second ZIP installation. This describes the proposed integration, not inclusion in released official Bforartists. Standard Blender is unsupported.

The Timeline row is a bottom canvas overlay above the scrollbar. It is not another header or a separate application. The Anim Assist sidebar tab's position relative to native tabs can vary. Find it by its name.

Screenshots appear beside the matching instructions and are embedded in the English PDF. Most panel illustrations retain their 12.11.1 capture labels. The new Lipsync figure shows the 12.11.2 candidate after successful setup on official Bforartists 5.2.3, Blender 5.3 Alpha base. Targets remain unassigned and no cues have been baked. The supplied custom 5.4 Alpha build lacks Audaspace audio support; see troubleshooting for its sound-strip limitation. Source review and PDF checks do not replace runtime testing. Read each historical qualification's scope and limits before applying it to another build or rig.

The [12.5.0 quick-tool guide](releases/12.5.0/USAGE.md) and separate-strip screenshots remain historical. The [archive](archive/) retains the earlier 12.0.1 PDF. See the [release index](../../releases/VERSIONS.md) for publication status.

Rebuild the English PDF from the repository root:

```powershell
# [PowerShell]
python docs/anim_assist/build_manual_pdf.py
```

The recipe requires ReportLab and embedded Noto Sans regular/bold fonts. It reads Windows Fonts by default. Set `ANIM_ASSIST_MANUAL_FONT_DIR` for another local font directory. Its PDF links resolve to the corresponding repository pages.

[Manual review, October 15, 2026](../releases/2026-10-15/manual-review.md) records earlier comparisons and limits across all three add-ons. It does not certify this edition.
