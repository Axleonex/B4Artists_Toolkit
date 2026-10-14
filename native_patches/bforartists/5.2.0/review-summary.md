# Native Timeline source reviews

The initial reviews below were static source inspection. Native validation was
subsequently requested and completed for the available-host matrix; see the
validation supplement and the 12.6.0 qualification report.

## Add-on

Spec review passed after 3b581a2 fixed repeated legacy joins and ID search.
Independent quality review passed after 21d7822 deferred restricted startup-data
access and fixed multi-window disable cleanup. Scoped addon commits are
8f1fc5c, 810de59, 3b581a2 and 21d7822.

## Application

Spec review passed after preserving toolbar intent through normal-header
visibility changes and adding bounded insufficient-space reports. Independent
quality review passed for f63e549b after inactive-space RNA ownership and
warning-cache screen cleanup were fixed. Exactly five C++ files differ from
pinned upstream commit 0a1ca455.

## Integration checkpoint

CMake Release/Ninja configuration succeeded. Actual compilation is running;
native registration, interaction, resizing and saved-layout observations remain
pending. Public integration has not been authorized for this new local release.

Additional integration review found saved inactive Timeline states could show blank rows after disable. Native f5f5501 gates polling/minimum sizing on registered providers; addon1c76f9c applies explicit preference changes to cached Timeline spaces. Independent quality re-reviews passed for both. Native observations remain pending.

## Evidence integrity audit

These are evidence boundaries, not additional tests. Paper falsification uses
the actual packaging script and approved observation criteria. Expected public
baseline mappings come from the existing 12.5.1 archive; new access requirements
come from the owner's approved design. Runtime observations use a prepared Cube
animation in an isolated profile, not production animation or aggregate usage.

| Evidence | Claim supported | Concrete failing state | Verdict |
|---|---|---|---|
| AST parsing of all 201 packaged Python sources | Package has valid Python syntax | A syntax error in any inventoried Python file raises during `ast.parse` | Sound for syntax; no runtime claim |
| Version fields and exact baseline inventory | Package versions agree and original files remain present | A conflicting manifest version, missing source file or extra changed file raises before ZIP replacement | Sound for package consistency |
| 70 prior catalogue dispatch pairs | Existing menu dispatch is preserved | A removed ID or changed operator/property tuple differs from the independent baseline archive and raises | Sound for dispatch preservation; no operator behavior claim |
| 89 target/property mappings | Catalogue points to declared existing operators | Unknown `bl_idname` or undeclared argument raises; incorrect runtime context can still pass | Partial; native use must establish context behavior |
| Source and archive SHA256 records | Identify the delivered bytes | Rebuilt or altered bytes differ from the saved digest | Sound for identity; no usability claim |
| CMake configuration and individual compiled objects | Toolchain accepts configuration and compiled units | Compiler diagnostic prevents the corresponding object | Partial; executable installation and launch remain required |
| Build exit status alone | Application is delivered | Interrupted Ninja returned zero while portable output was absent | Void; excluded from completion evidence |
| Native row screenshots plus region/area snapshots | Two visible rows belong to one Timeline | Missing TOOL_HEADER, zero visible height, marked Text Editor, or changed area count contradicts the approved layout | Load-bearing; pending actual compiled application |
| Geometry recorded during native edge drag | Native resizing retains readable Timeline space | Toolbar oscillation, collapsed key area, or split/join area changes appear in samples/screenshots | Load-bearing; pending. Sparse samples alone cannot establish absence of visual flashing |
| Key snapshots before/after manual direct and modal actions | Tools dispatch and cancel preserves animation | No expected key change on commit, or key/handle changes after Esc, contradict the observation | Load-bearing; pending. Selection-only observations do not establish all 89 algorithms |
| Native lifecycle observations | Visibility and saved preferences survive transitions | Explicit hidden row reappears, preference is lost, unrelated editor changes, or disable leaves a visible empty row | Load-bearing; pending |

Closure requires the load-bearing native observations and real portable output.
Static reviews and hashes cannot substitute for them. The author prepared the
packaging checks, so a separate integration review must inspect their scope and
the actual observations before release completion is claimed.

An independent read-only integration audit reconciled all 203 ZIP paths against
the baseline, found no duplicates, and matched every archived byte/hash to the
current add-on source and receipt. It also inspected dynamic arguments supplied
by `timeline_strip._arguments()` against declarations in the bookmark, mirror,
clipboard and switch operators: all supplied property names exist. This supports
source wiring only. The reviewer corrected coverage claims about fixed-argument
inspection and empty-query popup behavior; native observations remain pending.

## Native validation supplement — 2026-10-13

The compiled native host and genuine unpatched baseline ran explicit integration
assertions on independent fixtures. All 80 immediate effects passed in both
hosts; nine native modal tools passed commit and cancellation. Legacy migration,
restart/save UI persistence, workspace/multi-window/maximized lifecycle and
native playback/scrub/keying/Undo/Redo passed.

Spec review passed before quality review approved the observed source repairs:
maximized re-enable context, Ease prerequisites, and Offset preferences/handles/
full snapshot restoration. The reviewers inspected source; the parent performed
the actual GUI regressions. The validation helper now rejects catalogue actions
without an outcome assertion and requires curve geometry for modal live effects.

The evidence audit retained failed reproductions and fixture/input mistakes,
required valid in-gesture editor framebuffer samples, and verified all 203
installed ZIP files. It explicitly rejected continuous window-drag render
coverage because its samples were outside the input interval. No Windows global
DPI transition, universal no-flicker claim, full production-rig algorithm proof
or full AnimBot parity is certified.

Current evidence: docs/anim_assist/releases/12.6.0/native-evidence/full-validation/
summary.json. Historical pending labels above describe pre-build review gates;
the current qualification report supersedes their runtime status.
