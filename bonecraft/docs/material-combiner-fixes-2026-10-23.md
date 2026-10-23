# Material combiner and MMD fixes ? 2026-10-23

Current local packages: BoneCraft 9.2.15 (Bforartists) and BoneForge 9.0.15
(standard Blender). Original archives are preserved. Nothing was published.
Each distinct repair increments the patch version once.

| BoneCraft | BoneForge | Fix |
|---|---|---|
| 9.2.6 | 9.0.6 | MMD extension installation, detection and PMX import repair |
| 9.2.7 | 9.0.7 | Material classification: modern DITHERED opacity and linked/constant alpha |
| 9.2.8 | 9.0.8 | Material combiner preserves connected Principled tint, mapping and alpha graphs while baking |
| 9.2.9 | 9.0.9 | Combiner handles render-hidden sources and restores original visibility on Revert |
| 9.2.10 | 9.0.10 | Preserve excluded material datablocks and shared references during atlas assembly |
| 9.2.11 | 9.0.11 | Reject deleted or changed analyzed material sources before creating an atlas backup |
| 9.2.12 | 9.0.12 | Final rebuilt atlas mesh exports atlas_uv as UV0 when source UV retention is off |
| 9.2.13 | 9.0.13 | Material-count estimates and results count atlas slots on every output mesh and reset on Revert |
| 9.2.14 | 9.0.14 | Color-only meshes without authored UVs receive the baked UV layer during final assembly |
| 9.2.15 | 9.0.15 | Active-group Select All/Deselect All, folded source details and clearer reviewed bake workflow |

Fresh ZIP installations pass the five generated-fixture host checks: material
classification, actual tint/alpha pixels, mixed-mesh Accept/Revert, stale-source
cancellation, and color-only meshes without UVs. The mixed-mesh check protects
shape keys, geometry, parent relationships, transparent material references,
UV0, visibility and accurate slot counts. The 13 MMD regressions pass for each
product, and the repaired MMD source is unchanged from its earlier host tests.

BoneForge was tested in standard Blender 5.2.2 LTS. BoneCraft was tested in the
installed Bforartists 5.2.0 binary (Blender base 5.3.0 Alpha). Version stamps,
CRC and exact source parity are recorded beside each ZIP. BoneForge remains
free of Bforartists host gates. BoneCraft retains its Bforartists requirement.

Detailed local evidence: `BoneForge_Free/tests/combiner-evidence/summary.json`
at the Blender_Addons project root. The README in that directory documents
baseline failures, commands, exclusions and limits. Production-avatar content
and visible file-browser behavior remain manual checks. The MToon fallback
remains; the new evaluated shader graph path handles a directly connected
Principled surface. Metallic/ORM baking remains explicitly blocked by preflight.

Source: BoneCraft changes are in the isolated
`B4Artists_Tools/.claude/worktrees/bonecraft-mmd-925` checkout based on `a1092dc`,
not the older outer Ghost Tool work branch. No commit, merge or push was made.

UI selection checks pass from fresh ZIP installs in both hosts. Select All skips missing
textures and keeps other groups and the other source list unchanged. Detailed source
information is optional; Copy Debug is under Advanced Options. Visual window appearance
and interactive undo/redo were not verified by the headless tests.
