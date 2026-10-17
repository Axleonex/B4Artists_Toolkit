# Ghost Tool 4.3.1 translation validation

Validated against source commit `6db5a589253e9dede9f9c92c15100560aaeb59a9` on 2026-10-17.

## English source audit

The current source metadata, English guide, English PDF and published release identify Ghost Tool 4.3.1. The repository's existing `docs/audit_current_manuals.py` passed the Ghost manual/PDF version and content checks. Direct source inspection confirmed the direct toolbar actions, per-tool hold menus, independent Before/Ahead fields, shared Paths/Markers sampling, persistent Drag Markers, pin controls and ten-snapshot limit.

English Markdown SHA256: `a8ef2ef0de3e88ec8577e79d234b260939575f7c1bf4c68e677061c70887f80a`.

The broader repository audit still reports older BoneCraft translations. This batch does not claim that those editions are current.

## Translated editions

| Edition | Sections | Source blocks covered | Added provenance block | PDF pages |
|---|---:|---:|---:|---:|
| French | 13 | 59 | 1 | 5 |
| Portuguese | 13 | 59 | 1 | 5 |
| Spanish | 13 | 59 | 1 | 5 |
| Simplified Chinese | 13 | 59 | 1 | 4 |
| Japanese | 13 | 59 | 1 | 5 |
| Korean | 13 | 59 | 1 | 4 |

Each edition preserves the source section and paragraph order, numerical sampling example, ten-snapshot capacity, installation version and links, safety checks during restoration, live-update defaults and original verification limitations. English control names remain in the text. Translations distinguish retained path targets from individually pinned edit markers.

The guides are machine-translated. Structural validation and technical review do not certify native-language fluency or professional translation quality.

## Artifact checks

- All translated Markdown blocks are present in their PDF's extracted text after whitespace/format normalization.
- All translated guide local links resolve; PDF link destinations match the corresponding Markdown targets resolved from each edition's directory.
- Regular and bold font character maps cover every character used by the translated guides. Unicode fonts are embedded in the PDFs.
- All PDF pages contain text, and extracted text bounds remain inside the page margins.
- Every page was rendered and visually reviewed in contact sheets for clipping, overlap, missing glyphs and pagination. Korean's initial trailing one-line page was removed by reducing translated paragraph spacing from 9 to 8 points; its final PDF has four pages.
- The renderer's default English invocation was exercised in a temporary directory. Its normalized output text matches the existing English PDF. The checked-in English Markdown and PDF were not regenerated.
- Per-edition Markdown/PDF hashes and check results are recorded in [validation.json](validation.json).

The renderer adds optional language arguments and configurable font location. No add-on runtime source or release archive was changed. These documentation checks do not rerun or extend the earlier 188 implementation checks.

## Execution and publication

The coding router selected `T1_NATIVE` for the renderer change; policy fingerprint `29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.

Files were prepared in an isolated local worktree based on the published source commit. This validation does not mean the translations have been pushed, merged, attached to a GitHub release or published.
