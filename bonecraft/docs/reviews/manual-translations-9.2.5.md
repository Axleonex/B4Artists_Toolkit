# BoneCraft 9.2.5 documentation and translation review

Reviewed 2026-10-17 against repository source commit `6db5a589253e9dede9f9c92c15100560aaeb59a9`, with the English corrections in this documentation update. This report concerns documentation; it does not claim a new Bforartists runtime qualification or a new tagged release.

## Completed scope

The English manual and all six translated editions target **9.2.5**. Each contains the index and all 12 chapters, including the complete chapter 6 Simple Human/mannequin/Auto-Rig/IK-FK workshop and chapter 12 Crescent Rose tutorial. The six new chapter 12 files include all eight FBX preparation steps, all 30 Mechanisms steps, captions, tables, object identifiers and required model attribution.

The English source now places VRChat export under **CATS > Import / Export > Unity / VRChat** and no longer directs readers to the removed viewport-header Enable Rigify button. Current translated instructions also cover the Starter Rigs catalog tab, dependency handling, Adjust Last Operation, Mannequin removal without deleting its armature, weight/control tools, Task Board and version notes. The project overview, documentation index, suite overview, beginner-video page and current release descriptions are synchronized.

Every edition retains the same **92 screenshot targets in source order**: 40 Rig Builder workshop captures and 52 Crescent Rose captures. Captions and image descriptions are translated; English UI labels and technical identifiers remain where needed to match screenshots.

## Historical evidence and publication status

Screenshot captures remain identified as **9.1.2** and beginner-video footage as **9.1.3**. They were not recaptured or retested as 9.2.5. Their existing limitations remain documented. Model licensing, upstream licensing, the translation notices and the accurate AI-assistance disclosure are preserved.

The 9.2.5 installation archive is a repository download. **9.2.3 remains the latest tagged GitHub Release** at the time of review. This documentation update neither replaces an installation archive nor publishes a release.

## Verification

- `python -X utf8 -W error bonecraft/tests/test_manual.py`: all seven editions pass file sets, matching heading levels, links/anchors, screenshot validity/order, chapter size limits, navigation and translation notices. The checker now recognizes the native Adjust Last Operation label and the Starter Rigs asset-catalog name using source evidence; it also requires translated screenshots to match the complete English sequence.
- `python -X utf8 bonecraft/tests/test_manual_tools.py`: passes.
- `python -X utf8 docs/audit_current_manuals.py`: all current index/changelog versions and documentation links pass after this report is added.
- All seven PDFs were rebuilt with the existing Chrome renderer. Relative output paths now resolve correctly on Windows. Table rows remain together across page breaks; translated print styles use their actual heading identifiers.
- Full PDF text checks find every rendered paragraph/list/heading/table text node, with whitespace and Unicode normalization. Every page contains text; no extracted text falls outside the checked margins. All 92 embedded screenshot images are present in each PDF. Results and SHA256 checksums are in [PDF checks](manual-translations-9.2.5-pdf-checks.json).
- Rendered visual spot checks cover each edition's title/navigation pages, several workshop stages, FBX preparation, Mechanisms and final summary/credits. French/Portuguese troubleshooting rows and Spanish/Korean page-break fixes were checked after correction. These are visual samples, not a claim that every page was individually inspected.
- A separate source reviewer found no material issues in the changed technical claims or substantive translation spot checks across all six languages. This is not native-speaker certification or professional translation review.

| Edition | Markdown files | Screenshots | PDF pages |
|---|---:|---:|---:|
| English | 13 | 92 | 152 |
| Chinese | 13 | 92 | 146 |
| French | 13 | 92 | 155 |
| Japanese | 13 | 92 | 148 |
| Korean | 13 | 92 | 150 |
| Portuguese | 13 | 92 | 155 |
| Spanish | 13 | 92 | 156 |

Total: **1,062 PDF pages** and **11,405 rendered text nodes**, with no missing-node findings.

## Attribution and branding scan

The baseline scan covered 1,394 tracked text files, the text members of the current 9.2.5 installation ZIP, screenshot metadata, PDF metadata and co-author trailers in reachable Git history. No targeted vendor branding or actual co-author credit was found, so none was removed. Existing package checks that prohibit such banners remain intact. New documentation and PDF artifacts were scanned again before commit. No Git history was rewritten.

The installation ZIP remains SHA256 `96cf4a38ff5af26820f7ec6a65a56f72b55ce0683edf359fe5faa0133618b1fb`. Both GPL license files remain SHA256 `498d32907f132c2cd7d3ae269f304aed87156293f63e724b83d9f62ed787d55a`.

## Execution and remaining limits

The coding router selected `T1_NATIVE` for the small documentation-renderer/checker changes, policy fingerprint `29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`. Translation writing and source verification used separate documentation agents in the same local worktree. No paid API was used.

The guides remain machine-translated and their screenshots remain in English. This update is prepared on a local work branch; pushing or merging requires the owner's separate confirmation.
