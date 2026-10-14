---
status: passed
scope: native-workflow-and-local-overhaul
---
# Ship readiness

Exact 12.7.0 native workflow and full functional regression passed before
preparation; details are in SUMMARY.md, REVIEW.md and release qualification.
No new functional test run was needed for the main synchronization: remote
incoming changes contain no Anim Assist source changes. Every one of the 208
current source/package files is byte-identical to the qualified ZIP. Its SHA256
is 47d25fe0568e7685ca46c58fe7cc5310bd34411f76debaf1839d312d61828027.

Preparation checks pass: current source/archive identity; local README links
exist; no outgoing Ghost Tool/BoneCraft source differences from origin/main;
no co-author/generated-by banners in outgoing commit messages. The README raw
ZIP download can only be checked remotely after branch push. No publication
permission is inferred from verification.

Qualified scope: stock Bforartists default/generated workspaces, author review
and synthetic animation. Production/personal rigs, other platforms/themes/DPI,
renamed extension installs and keyboard-only interaction remain unverified.
Fully collapsed canvas still needs expansion. See REVIEW.md for skill deviations
and gate falsifiers; this status does not claim full AnimBot parity or blind UAT.

Prepared action: push feature branch and create a draft PR after exact Confirm
merge update. Main merge/tagged Release remain separate.
