# BoneCraft 9.1.2 manual translation validation

The owner activated translations on 2026-10-12 after completing the English workshops. All six existing languages now cover the same twelve chapters and index, including the Simple Human/mannequin/Auto-Rig/IK-FK workshop and Crescent Rose Mechanisms tutorial.

| Language | Markdown files | PDF pages | Screenshots |
|---|---:|---:|---|
| fr | 13 | 160 | 92 unchanged |
| es | 13 | 158 | 92 unchanged |
| pt | 13 | 158 | 92 unchanged |
| zh | 13 | 145 | 92 unchanged |
| ja | 13 | 149 | 92 unchanged |
| ko | 13 | 149 | 92 unchanged |

## Translation and review

Prose, headings, captions, image descriptions and navigation text were machine-translated using Google's public translation service, then edited for rigging terminology, interface control names and preserved technical settings. Previously reviewed native headings were reused where they still match the English structure. The FK/IK comparison was rewritten in each language. Chinese hinge and slide instructions were corrected after preservation checks caught omitted selection clauses. Japanese image descriptions were shortened while retaining the step reference; full instructions and captions remain alongside each image.

These are machine-generated translations with technical postediting and sample review, not a professional native-speaker certification. Each index retains its machine-translation notice and explains that screenshots use the English interface.

## Verification

- Full repository manual test passed for English, Chinese, French, Japanese, Korean, Portuguese and Spanish: file parity, headings, links and anchors, navigation, notices, image files, English UI labels and chapter-size limits.
- Every English inline-code token is retained with its original value. Language-specific ordering and repeated mentions are allowed. Code samples and asset names remain English.
- All six combined HTML manuals have valid internal targets.
- Each translated edition references the same 40 Rig Builder and 52 Crescent Rose screenshot files. SHA256 comparisons confirm all 92 image files are unchanged.
- Six PDFs were built with Chrome. Chapter ranges were derived from their own PDF destinations and rebuilt until stable. Every physical page has its localized footer and correct page/total numbers.
- Representative rendered pages were inspected for readable text and preserved layout.

PDFs are generated review artifacts under `G:/LapArt/output/bonecraft-manual/9.1.2-translations/review/` and remain outside Git, following the repository's PDF policy. The companion JSON records hashes and chapter ranges. No add-on runtime code was changed. Publication uses a clean work branch based on `origin/main`; push requires the owner's confirmation phrase.
