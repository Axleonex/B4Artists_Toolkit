# Current manual review — October 15, 2026

Scope: documentation for the repository source at `0ff958ad03da9b0ac79f7796ceb7358c6e3759e2`: Anim Assist 12.8.0, Ghost Tool 4.2.11 and BoneCraft 9.2.4. This update changes documentation and its build/audit helpers. Add-on source and release ZIPs are unchanged.

## Findings and corrections

| Manual | Before | Result |
|---|---|---|
| Anim Assist | Markdown/PDF targeted 12.1.3; documentation index targeted 12.7.1 | Rewritten for 12.8.0, with bottom Timeline placement, default/custom sliders, named layouts, current Graph/Dope Sheet groups and NLA workflows. Five-page linked PDF regenerated. |
| Ghost Tool | Markdown, PDF and toolbar guide targeted 4.2.11 | Current version and interface guidance verified; the manual/PDF were retained unchanged. Existing width-helper limitations remain explicit. |
| BoneCraft | Current navigation covered 9.2.4, but all seven changelogs stopped at 9.2.3; translated Task Board descriptions lacked the new card distinction | Added 9.2.4 notes in all seven languages and updated the six translated Task Board sections. English already described the current cards and Health Check. |
| Release index | Anim Assist current row still showed 12.7.1 | Current row now points to the existing 12.8.0 ZIP, receipt, qualification and manual. |

## Interface claims checked against source

These are source/document comparisons, not new application behavior tests.

| Claim | Source inspected | Status |
|---|---|---|
| Anim Assist editor groups, order and initially open sections | `anim_assist/ui/layout_homes.py`, `ui/nla_panels.py` | VERIFIED |
| Eight numeric tools, two recommended inline sliders, Timing Scale popout, four display modes and named layout actions | `anim_assist/ui/timeline_config.py`, `timeline_settings.py`, `timeline_catalog.py` | VERIFIED |
| Bottom-only placement, overflow into More and keyframe separation | `anim_assist/ui/timeline_overlay.py`, `timeline_config.py`; 12.8.0 qualification | VERIFIED |
| Release/cancel, Shift precision, Ctrl snap and typed slider values | `anim_assist/operators/timeline_slider_ops.py` | VERIFIED |
| NLA scene/source scope, sharing, corrections, influence and retained bake activation | `anim_assist/operators/nla_ops.py`, `core/nla_context.py`, `ui/nla_panels.py` | VERIFIED |
| Graph/Dope Sheet key selection scope and unsupported Action sources | `anim_assist/core/context_utils.py`, `ui/layout_homes.py`; 12.8.0 release notes | VERIFIED |
| Ghost Tool display locations, default Top Toolbar, named sections, startup migration and recovery | `ghost_tool/preferences.py`, `ui_panel.py`; 4.2.11 receipt | VERIFIED |
| BoneCraft navigation and current Task Board/Grab fixes | `bonecraft/boneforge/taskboard/sidebar.py`, `panel.py`, `autorig/tools.py`, `mechanisms/tools.py`; 9.2.4 release notes | VERIFIED |

## Reproducible documentation checks

From the repository root, with Python and `pypdf` available:

```powershell
# [PowerShell]
python docs/audit_current_manuals.py
```

The [recorded result](manual-audit.json) checks source versions against manual/PDF titles, compares every manual paragraph/list item to extracted PDF text, checks all seven BoneCraft indexes/changelogs and resolves local Markdown links/anchors across the current guides. It does not fetch external links or run add-on operators.

Failure controls were exercised in memory without editing project files: substituting 12.7.0 in the current Anim Assist guide caused a version failure; injecting a nonexistent Markdown anchor caused a link failure. A paragraph missing from a PDF also fails the content check. Version checks alone do not establish instruction accuracy; the separate source comparisons above cover the changed interface instructions.

Anim Assist's PDF was rebuilt with ReportLab, reopened with pypdf, rendered with PDFium and visually reviewed. The three-page Ghost Tool PDF was also rendered and inspected. Both have readable headings, body text and page footers, without clipped text or missing characters. The Anim Assist PDF includes section bookmarks and live links to the actual 12.8.0 interface captures. Its build is reproducible through `docs/anim_assist/build_manual_pdf.py`.

Print treatment follows the existing quiet manual style: US Letter, 48-point side margins, Helvetica body at 10/14 points, dark ink `#202830` and link accent `#24567a`. The revision was self-edited for structure, source support, paragraph focus and plain language; its sentence pass reduced the draft from 2,134 to 1,918 words. No independent editorial review is claimed.

## Limits retained

- The source/manual comparison does not establish that every operator works on every rig. Existing native application checks remain in each release's qualification/receipt; none were rerun for this documentation update.
- Ghost Tool's preference-reset width guard limitation, unexercised fallback/scale cases and production-file limits remain documented.
- BoneCraft's current interface guidance is updated in all seven editions. Its six translated editions still lack the illustrated chapter 6 expansion and chapter 12; English remains the reference for those workshops. Historical 9.1.2 screenshot labels remain intact.
- BoneCraft PDFs are generated outside the repository and are not tracked here. Previously exported copies were not regenerated or certified by this review; rebuilding from the current source includes these corrections.
- Historical release notes, archived guides and their original qualification claims retain their original versions.
