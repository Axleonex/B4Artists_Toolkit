# Imported humanoid workflows in 0.16.0

The working adapter recognizes the bundled BoneForge Mocap Humanoid, Unity
Humanoid and Unreal Mannequin conventions and validates actual FK spine,
shoulder and limb parents. It does not convert arbitrary rig controllers or
mechanisms. These three tested conventions are a milestone within the original
rig-compatibility requirement; they do not complete all imported rigs or the goal.

## Actual import and control spaces

The new fixture is directly authored from explicit limb/body dimensions, with
nonzero bone rolls, a root ancestor, an extra animated accessory, and weighted
triangular skin samples. It calls the installed host's FBX exporter/importer.
No BoneForge/Rigify builder is used for these fixtures. FBX is test setup, not a
new importer dependency in the add-on. Original BoneForge JSON maps are unchanged.

FBX reconnects the pelvis to its root in these files. The initial adapter attempt
correctly refused to translate that connected pelvis. The implemented adapter
uses the first unconnected ancestor for translation, retains the original pelvis
for skeletal orientation/COM semantics, and includes ancestry in pose snapshots
and anchors. Bone connections, rest matrices and source animation are not edited.

Captured root channels are authored controls in the interpolation candidate:
inside the interval they are reinterpolated with the other captured channels.
This does not promise an unchanged candidate root curve between anchors. The
original action, including root and accessory keys, remains intact and recoverable.
Unowned accessory curves remain copied through contact correction. Mechanism
ancestry, constrained/driven dependencies and nonuniform/reflected bone scales
are rejected with explicit diagnostics. Those dependencies are rechecked during
an active whole-body session.

## Evidence so far

- imported-baseline-v1: all three names recognized; whole-body entry rejected
  without mutation on 0.15.1 behavior.
- imported-adapter-v1: actual connected FBX pelvis translation rejection retained.
- imported-adapter-v6: nine tests pass across the three FBX conventions, different
  proportions/rolls, positive uniform object scaling/rotation, blended skinning,
  priority world-joint positions, source recovery, malformed dependencies, live
  selective pin/rotation/pole intent, actual save/reload, local learned completion
  with active joint limits, contacts, COM and editable native flight results.
- live-pose-ui-imported-unity-v1 and corresponding mocap_humanoid/unreal_mannequin
  reports: actual-window keyboard target transforms, stale-fit cancellation,
  active-fit Undo/Redo, Escape, Keep rejection/success, save/reload, Cancel, and
  disabling pass. These are automated lifecycle checks, not animator assessment.

Representative geometric normalized pin errors: Mocap 0.00012132, Unity
0.00013602, Unreal 0.00008167, all below the existing 0.0002 gate. FBX rest-head
roundtrip maximum error across those cases is below 0.0000028 scene units. These
are synthetic fixture measurements, not production model quality claims.

## Review correction and final qualification

The initial capture integration incorrectly reused full assisted-posing topology
checks. Two regressions verified against the old package are fixed: ordinary
capture remains available for nonstandard limb parents and partial imported
profiles. An additional legacy FK test now verifies its established Keep-visible /
Cancel-restore behavior. Whole-body Keep continues to restore the source pose.

All 245 pre-existing cases ran this turn. After the imported-only capture fix,
12 imported cases and 31 foundation cases passed on the final behavior; the other
214 cases retain actual preceding-runtime hashes plus an AST check showing that
their non-imported capture behavior is unchanged. The composed total is 257 unique
cases in 23 suites. Failed development tests and the mistaken zero-case foundation
selector remain in the evidence; they are not counted as passing cases.

The exact 0.16.0 ZIP passes 95 offline cases in 11 groups and packaged actual-window
lifecycle checks on all three imported conventions. Loaded module hashes and ZIP
bytes match the current source. The only runtime change after source qualification
was the byte-verified version literal. The generic runner records worktree hashes;
old-release comparisons use their fixture's actual loaded-package hashes instead.

See package-test-v0.16.0.json and imported-regression-v1.json. No package is installed,
committed or pushed. The previous 0.15.1 archive is unchanged. Actual host assertions
terminate before the known ucrtbase.dll shutdown crash; host lifecycle qualification
still fails. The expanded N-panel requires scrolling and clips long labels at its
default width, as visible in the retained screenshot.

## Remaining scope

These meshes are independent synthetic weighted samples, not production character
surfaces. Rigify deform-only skeletons, other import conventions, intermediate
twist-chain variants, arbitrary constraints/spaces and quadrupeds remain open.
The two existing pose networks are unchanged. No learned temporal motion, visual
quality improvement, independent usability pass, universal latency result, or
Cascadeur comparison is implied. Full original goal requirements remain intact.
