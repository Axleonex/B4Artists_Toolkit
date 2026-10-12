# Current manual coverage

These manuals describe the published Anim Assist 12.1.3 and Ghost Tool 4.2.0 source as of 2026-10-11. Ghost Tool remains a prerelease pending final owner usability acceptance.

| Manual | PDF pages | Commands | Help topics | Property definitions | Missing inventory entries |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Anim Assist 12.1.3](../anim_assist/AnimAssist_User_Manual.md) / [PDF](../anim_assist/AnimAssist_User_Manual.pdf) | 144 | 426 | 474 | 531 | 0 |
| [Ghost Tool 4.2.0](../ghost_tool/GhostTool_User_Manual.md) / [PDF](../ghost_tool/GhostTool_User_Manual.pdf) | 37 | 43 | 10 | 209 | 0 |

Each manual combines artist workflows with a full source reference. Every PDF page has a footer number, and every contents entry has a clickable chapter link and its printed PDF page number. The builder recalculates those page references until pagination is stable and saves the same references in the Markdown source. The counts include source-defined internal commands, operator arguments, user settings, and stored-record fields; they are not counts of separate visible buttons.

An AST inventory of the shipped Python modules, excluding tests, was compared with the manuals. Every inventoried command ID, help-topic ID, and property definition is represented. Every command ID and help-topic ID also appears in the searchable PDFs. The [coverage manifest](coverage.json) records inventory entries and source/manual hashes. All PDF pages were rendered for visual review; checks also cover text bounds, empty pages, contents destinations, and metadata. Rebuild the PDFs with `python docs/build_current_guides.py` using ReportLab.

The workflow descriptions were checked against implementation, including these corrections to older help claims:

- Anim Assist layer selection changes the active list entry. Authors must choose the receiving Action explicitly before adding keys. Evaluate Stack applies the combined transforms at the current frame; this build does not install general frame-change stack evaluation. Stored layer toggles do not universally intercept native key insertion.
- Anim Assist lipsync PREVIEW updates cues and live drivers; SHIPPED writes output keys. Mark polished keys as Manual Overrides before rebaking. Rhubarb remains unverified; amplitude-based processing has host-test evidence.
- Ghost Tool Physics Stamp replaces keys on the target axis inside the inclusive range and preserves keys outside it. Stamp values are direct archetype values scaled by amplitude. An existing location curve is required, and active NLA is rejected.
- Ghost Tool uses Shift+B for box selection. Shift+G is shared with path-handle dragging; a nearby handle receives priority. Import/export descriptions follow the current identity and merge behavior.

This is source and documentation coverage. It does not establish successful interactive use of every feature on every rig or replace release verification and owner acceptance. The manuals retain those limits beside the relevant workflows. Add-on source and installation ZIPs are unchanged by this documentation update.
