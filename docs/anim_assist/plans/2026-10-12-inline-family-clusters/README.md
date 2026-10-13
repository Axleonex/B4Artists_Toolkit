# Inline Family Clusters and Configurable Quick Buttons — Implementation Plan

**Date:** 2026-10-12

**Status:** Implemented and locally committed; 12.5.0 candidate is Needs Review. The Plan 04 owner checkpoint remains pending.

**Approved direction:** Inline family clusters plus configurable quick selection.

**Baseline:** Anim Assist 12.4.0, commit `56a69c1`.

**Local candidate:** 12.5.0. [Usage screenshots](../../releases/12.5.0/USAGE.md), [qualification and known findings](../../releases/12.5.0/qualification.md), [owner checkpoint](../../releases/12.5.0/UAT.md).

Implementation commits: `74e50e4`, `f81e861`, `c1102af`, `eb5c36b`. All four plan summaries are recorded here. Native Redo and trail geometry findings remain unresolved; actual Bforartists acceptance is pending. No public push or owner-app installation occurred. The qualification report also records the test-profile overwrite incident and the corrected isolation guard.

## Goal

Put chosen animation actions directly beside their family menu above the Timeline. A visible quick button invokes its existing operator in one click. Let the owner choose quick buttons through native checkboxes, with choices retained across scenes and restarts.

**Architecture:** Extend the existing action catalog with deterministic quick-selection metadata and native add-on preference fields. Draw the selected actions beside their permanent family menus through the existing Timeline dispatcher; use native header panning for excess width.

**Tech stack:** Python, Blender/Bforartists bpy RNA preferences and native UILayout, existing Anim Assist operators and local ZIP packaging.

**Executing agent:** Follow the four GSD plans sequentially and re-route each concrete coding scope before work; no automatic subagent fan-out is required by this planning packet.

The selected layout replaces the 12.4.0 arrangement of seven menus followed by a separate quick section and More. On narrow windows, keep the selected actions on a horizontally pannable header; do not automatically move them into More. Panning is an additional interaction when a button is outside the viewport. This design cannot make every selected button simultaneously visible at every width.

## Work sequence

One GSD phase, four sequential plans. Each plan depends on the previous one.

| Wave | Plan | Deliverable |
| --- | --- | --- |
| 1 | [01-01](01-01-PLAN.md) | Stable action IDs, family membership, quick labels, defaults, and persistent preferences |
| 2 | [01-02](01-02-PLAN.md) | Inline clusters and a central gear popover with family-specific checkboxes |
| 3 | [01-03](01-03-PLAN.md) | Settings transfer, dispatch parity, scrolling, cancellation, and native usability evidence |
| 4 | [01-04](01-04-PLAN.md) | Local 12.5.0 candidate, package receipt, screenshots, and honest verification status |

## Proposed default row

```text
Gear | Tween ▾ 25% 50% 75% Drag | Curves ▾ Smooth |
Timing ▾ -1f +1f Ripple | Keys ▾ Range Ends |
Pose ▾ Mirror Sel | Bake ▾ Bake Object | Motion ▾ Show Trails
```

This is one horizontal row. The line breaks above are for document readability. Gear moves to the start so configuration remains reachable at the initial scroll position. Seven family menus remain available even when none of that family's actions are selected as quick buttons.

The default set is an editable planning choice, not a measured ranking of the owner's most-used commands. Every one of the 70 catalog presets can be selected. Fixed family and catalog order are retained; arbitrary reordering is outside this milestone.

## Contract and evidence

- [Requirements](REQUIREMENTS.md): measurable endpoint and plan coverage.
- [UI and behavior contract](DESIGN.md): preferences, labels, scrolling, scope, and recovery.
- [Source research](RESEARCH.md): existing code to reuse and known constraints.
- [Plan review](PLAN-REVIEW.md): dependency and completeness review; no product-test claims.

Public plan files in this directory are the maintained source. A local, ignored `.planning/` snapshot supplies the normal GSD PROJECT, REQUIREMENTS, ROADMAP, STATE, CONTEXT, UI-SPEC, RESEARCH, VALIDATION, and four PLAN files. Refresh that snapshot from these files after a plan edit; do not edit both copies independently. Existing `.planning/review-evidence` is retained.

## Execution handoff

Read `.planning/STATE.md`, then `.planning/ROADMAP.md`, and the plan summaries. Automated tasks are complete; continue from the Plan 04 owner checkpoint and outstanding qualification findings. Resolve the Code Router lane again before any additional coding scope. No independent review is claimed.

Use the installed GSD execute-phase workflow for Phase 1. Do not rename or switch branches as part of planning. Local work-branch commits are allowed; pushing, merging into main/release, and public release publication require the owner's separate confirmation under the repository rules.

The plan task text is retained as the approved specification. Actual outcomes and limits are recorded in the summaries and release qualification; the milestone is not marked complete.
