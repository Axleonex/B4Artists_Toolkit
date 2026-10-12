# Ghost Tool 4.2.0 verification

The exact candidate ZIP passed 320 checks across 17 suites on Bforartists 5.2.0, Blender runtime 5.3.0 Alpha, build `0a1ca45552db`. Exit code: 0. Source and package match.

Archive SHA256: `16a354dc92d694734f5aa76b788c7f926f0c1a24081f1b343e1a8312477cd181`.

Draw to Keys, native shelf coverage, council workflow and lifecycle now pass on the actual host. The earlier stand-in failures and blocks do not describe this fresh run. This does not verify other builds. Owner pointer/usability acceptance is still pending.

See the [shared verification](../../releases/2026-10-11/VERIFICATION.md) and [hands-on checklist](UAT.md).

## Publication package cleanup

The published package removes a descriptive comment from `diff_mode.py`. The executable AST and all other entries are unchanged from the package used for the 320 host checks. ZIP CRC and Python parsing pass after repackaging. The receipt retains the original tested checksum.
