# Current build verification - 2026-10-11

These are fresh runs of the latest local builds on Bforartists 5.2.0, Blender runtime 5.3.0 Alpha, build `0a1ca45552db`.

| Build | Input | Result |
|---|---|---|
| Anim Assist 12.1.3 | Exact install ZIP | 170 internal tests, 26 repair checks and 16 workflow checks pass; exit 0 |
| Ghost Tool 4.2.0 | Exact install ZIP | 320 checks across 17 suites pass; exit 0 |
| BoneCraft 9.1.2 | Current source | Full host suite passes: 19 ALL PASS and 35 PASS markers; exit 0. Crescent Rose parts and rig reload checks pass. |

All archived Python files parse and all ZIP CRC checks pass. Anim Assist and Ghost Tool source match their packages. BoneCraft's only raw-byte difference is newline encoding in `boneforge/__init__.py`; source content is identical.

## Full SHA256 hashes

- Anim Assist: `b30547b2afacbe1f56d0d8066ac7e607aeaa24297aa8612d9482272a37b493e1`.
- Ghost Tool: `16a354dc92d694734f5aa76b788c7f926f0c1a24081f1b343e1a8312477cd181`.
- BoneCraft: `9901bdb98da47384522b5137df58e8722f7d4f8c6e20cf1d835630c6bbaafa63`.

## Scope and limits

The actual-host runs close the previously pending Bforartists reruns for Anim Assist 12.1.3 and Ghost Tool r4. Earlier stand-in reports are historical evidence, not the current gate.

Background Anim Assist checks do not establish every interactive operator or real-window usability. Optional Rhubarb was not exercised. Ghost's final owner pointer/usability acceptance remains pending; automated success does not accept the candidate. Other host builds are not verified by these runs.

BoneCraft's English manual covers the current interface and its Crescent Rose tutorial. Six translated editions include 9.1.2 release notes, but their usage chapters and Crescent Rose tutorial are not yet synchronized to the English edition. Use English for current controls.

No GitHub publication is claimed. Machine-specific raw logs are retained locally. The portable summary in `summary.json` records the test counts and archive identities.
