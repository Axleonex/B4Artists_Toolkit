# Editor sidebars implementation plan

**Goal:** Deliver the approved NLA workflow and editor-specific Graph/Dope Sheet refinements as a validated local add-on update.

**Architecture:** Native sidebar panels and NLA header menus share strip-aware operators. Native context collections define selection; correction Actions use COMBINE transform deltas. Baking uses Blender's evaluated bake helper and restores assignment and stack state. Timeline overlay code stays unchanged.

**Stack:** Python, bpy, bpy_extras.anim_utils; stock Bforartists 5.2.0.

## Execution and authority

Owner approved implementation and native validation. Work only in the existing managed worktree on `codex/anim-assist-editor-sidebar-design`. No publish, push or merge is authorized. Local work-branch commits use Axlbot identity.

Code Router selected actual/recommended `T3_PRIME_OMP`, fingerprint `29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`. Preflight returned `RUNTIME_UNAVAILABLE`: this process cannot host the worker. Continue natively under the Static Native Execution Policy, same scope, zero escalations. Implementation is serial; independent read-only spec and quality review follow integration.

## Tasks

1. Fix editor-local selection in `core/context_utils.py`, `operators/curve_tool_ops.py`, `operators/keymanager_ops.py`. Empty editor collections stay empty; selected interpolation never touches unselected keys. Add focused regression assertions.
2. Create `core/nla_context.py`: resolve native selected/active strips to owners/tracks, shared references, editability and mapping. Never use active object Action as a selected-strip fallback.
3. Create `operators/nla_ops.py`: atomic nudge/align/sequence; guarded native actions; unique duplication; Tweak Mode and editor navigation. Reject locked targets and invalid overlaps before writes; preserve duration and source keys.
4. Add neutral transform correction creation and recognized correction editing to that module. Validate supported rotation/constraint cases and block unsupported paths. New independent Action/track above motion; no change in evaluated pose.
5. Add bake to new retained Action using native evaluated sampling. Restore original Action, slot, blend settings, frame and transforms in finally; output remains unassigned. Separate explicit activation and cleanup.
6. Create `ui/nla_panels.py`, integrate `ui/__init__.py`, `operators/__init__.py`, `ui/layout_homes.py`, `ui/header_menus.py`, `prefs.py`. Target summary; open Arrange/Blend; closed Actions/Bake/Shelf; plain headers, explicit scopes, folded advanced settings.
7. Refine `ui/panels.py`, `ui/p3_panels.py`, `ui/p6_panels.py`, `ui/p7_panels.py`, `ui/layout_homes.py`, `ui/ui_helpers.py`: direct primary actions, Graph shape/interpolation/handles; Dope Block & Tween, selection, separate bake; procedure homes. Preserve existing settings/operator math.
8. Add `tests/nla_sidebar_validation.py` and focused scope tests. Run in an isolated Bforartists profile. Assert neutral correction and authored/zero-weight behavior, timing atomicity, shared Action uniqueness, locked/empty/multi-owner handling, bake preservation, selection filters and empty curve selection. Capture actual editor screenshots at narrow/default widths, inspect them, and record exact limitations.
9. Review spec then quality, fix findings; re-run changed checks. Prepare local 12.8.0 package with matching metadata and documentation under `docs/anim_assist/releases/12.8.0`. Verify ZIP contents, absence of attribution trailers and unchanged Timeline implementation. Local commit only; public links remain on released 12.7.1 until a separately confirmed push.

## Endpoint

Implementation, native checks and screenshots complete; concrete release archive and evidence available locally. Any unsupported case must be blocked and documented, never reported as a passing tool. No personal Blender profile changes and no application patch.

## Execution record

Implementation tasks 1–7 are complete. New native validation and screenshot harnesses are `tests/nla_sidebar_validation.py`, `tests/nla_interaction_validation.py` and `tests/nla_sidebar_screenshots.py`; existing layout tests now cover four distinct homes. A local 12.8.0 ZIP contains 211 files with all four version fields consistent. Package receipts and the release qualification record evidence; publication is not authorized.

Spec and quality reviewers worked read-only. Their scope, bake ownership, null Action, track-order and reference-count findings were fixed. Native tests then checked the actual extracted archive. The review classifier selected S3; the formal run remained advisory/inconclusive without a host-evidence receipt, invoked no reviewer and made no model calls. Native results and separate reviews are reported independently; no formal S3 pass is claimed.

Tasks 8–9 complete: the extracted final ZIP passed 11 behavioral groups, 5 native interaction groups, 98-panel registration/unregistration and 5 Timeline regression tests. Nine actual screenshots have matching measured widths; narrow labels were corrected after inspection. Undo/redo and saved workspace reload passed. Timeline source identity matches 12.7.1. The qualification and package receipts are saved in the release directory. A local work-branch commit closes this implementation; no push or merge is included.
