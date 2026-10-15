# Anim Assist: NLA sidebar design

Status: owner approved; implemented in local Anim Assist 12.8.0. See the release qualification for tested support and limits.
Baseline: Anim Assist 12.7.1, bottom-only Timeline toolbar.
Owner requirement: support both arranging motion clips and layering additive
corrections in the same NLA sidebar. Review Graph and Dope Sheet separately.

## 1. Editor roles

| Editor | Primary work | Interface language |
|---|---|---|
| NLA | Arrange clips and combine track contributions | Clip, track, source action, influence, scene time |
| Dope Sheet | Create poses and adjust key timing across channels | Pose, breakdown, inbetween, key, channel |
| Graph | Adjust values, interpolation and curve shape | Curve, value, handle, selected keys |

Use the same Anim Assist styling across all three; give each its own order
and selection contract. No wholesale copy of the Dope Sheet or Graph panels.

Alternatives considered: copying Dope Sheet keeps familiar pose controls but
puts key tools ahead of clip tools; copying Graph keeps an action-oriented
structure but foregrounds curves and handles. A dedicated NLA arrangement
with reusable drawing helpers fits both requested NLA workflows.

## 2. Experience contract

- User/job: an animator assembles clips, then adds corrections without losing
  the source motion or accidentally editing every instance of an action.
- Known: the supplied screenshot shows a Mixamo action in Dope Sheet and NLA.
  The owner explicitly wants arrangement and additive corrections equally
  accessible. The current add-on has NLA panel foundations but no dedicated
  NLA sidebar or strip-aware tool set.
- Inferred: scope, source sharing and action-editing state need to be visible.
- Assumed: object and armature transform animation are the first supported
  correction targets. Other owner/channel types need separate qualification.
- Arrangement path: select clips, move/align/sequence them, adjust duration,
  preview the result, undo or keep the edit.
- Correction path: select a source clip, create a separate neutral correction
  action/track, author the correction, then tune its contribution and preview.
- Editing path: select a source clip, enter native Tweak Mode, edit the action
  in Dope Sheet or Graph, finish editing, resume strip arrangement.
- Success: the active target and scope are explicit, the intended strips or
  keys change, unrelated data stays intact, and undo restores the prior state.
- Onboarding: contextual empty-state guidance only; no first-run wizard.

## 3. Sidebar layout

Native NLA sidebar, Anim Assist tab. No overlay over the NLA canvas.

```text
Anim Assist
Clips: arrange, blend, correct

Armature / Walk                  [active clip]
3 clips selected / source shared [actual context]
[Edit Action] [Dope Sheet] [Graph]

v Arrange & Time
  Scope: 3 selected clips
  [-1f] [+1f] [Move]
  [Align Starts] [Align Ends]
  [Sequence Clips]
  > Timing Options

v Blend & Corrections
  Scope: active clip / Walk
  [New Correction]
  [Edit Correction]
  Blend mode: Combine
  Influence: [--------- 1.00]
  > Blend Options

> Actions & Tracks
> Bake & Finish
> Quick Shelf
```

This is a structural sketch, not a pixel-accurate screenshot. At narrow widths,
long action labels occupy full-width rows rather than being truncated.

### Always-visible target and navigation

Show the owner, active strip and source action. Show selected strip count and
whether the source is shared. Use a real action-reference check, not the raw
datablock user count presented as a number of clips.

Edit Action enters native Tweak Mode for that strip. While tweaking, show
Editing Action and an unmissable Finish Editing button. The editor buttons
are explicit navigation: reuse a suitable visible editor when available;
otherwise switch the current area to the requested editor. Preserve the NLA
space so the native editor selector can return to it. Never split, join or
resize areas automatically. Do not silently change another editor's pinned
target or overwrite its unrelated action.

Display source-action frames separately from scene frames when showing both;
a scaled or repeated clip must not imply they are the same time range.

### Arrange & Time — open by default

Direct actions: nudge one frame, native interactive move, align starts/ends,
and sequence selected clips. No fold around each individual action.

Timing Options contains nudge step, alignment reference, sequence gap,
duration scale, repeat and range tools. Selected clips are the default scope
for batch actions. Per-strip fields explicitly identify the active clip;
they must not appear to change the entire selection.

Sequence orders selected clips by their existing scene-time start, with track
order as the tie-breaker; the active clip supplies the initial start anchor.
Gap defaults to zero. It moves selected clips only and preserves action data.
When track overlap or a locked target prevents a valid result, report the
specific target and leave the operation unapplied rather than partially move
the selection. Alignment is limited to track combinations that permit it.

### Blend & Corrections — also open by default

Both requested workflows remain visible; there is no arrangement-versus-
correction mode switch. Keep the primary correction actions and active clip
influence/blend mode visible; fold automatic blending, blend-in/out,
extrapolation and reference-frame configuration into Blend Options.

New Correction is a new feature, not an existing button being relocated.
It creates an independent Action and a track above the source motion. Initial
contribution must be neutral so adding it does not change the evaluated pose.
Use the native blend semantics suitable for the qualified transform channels;
do not assume one universal additive neutral value for every channel type.
Zero translation, identity rotation and neutral scale have different roles.

The design favors native Combine semantics for qualified transform correction
tracks, with the actual mode visible. Changing an ordinary absolute-motion
clip to Add does not automatically convert its contents into useful deltas.
Unsupported rigs/channels must explain the limitation instead of creating a
misleading correction clip. Neutral setup, rotations, constraints and authored
correction behavior require qualification before this button can ship.

Edit Correction is enabled only for a recognized, compatible correction
action. Ordinary clips still use Edit Action. Track mute/solo is available
in Actions & Tracks, using native properties rather than a parallel layer
evaluation system.

### Actions & Tracks — closed initially

Duplicate Independent and Duplicate Linked are distinct commands with clear
tooltips. Include Make Unique, rename, mute, solo and track movement here.
Linked duplicates remain explicitly shared; no automatic unique-copy policy.
Push Down and Stash appear only where an editable active action permits them,
with an explanation when unavailable. Do not add an unrelated action browser.

### Bake & Finish — closed initially

Bake to New Action uses an explicit target and scene-time range. Preserve the
original strips and source actions. The interface identifies the output Action
and range after completion; activating that output is a separate explicit step
so the result is not unintentionally evaluated together with its source stack.

Remove Empty Tracks is separate from baking and scoped to the stated owner.
Never automatically delete source actions, collapse a stack or remove backups.
Do not expose the existing generic bake panel until its evaluated NLA behavior
and output ownership have been qualified.

### Quick Shelf — closed initially

Only NLA-qualified commands are eligible. Saved macro steps must carry their
target domain; a key-editing macro cannot silently run against a strip target.
No automatic copying of the Dope Sheet's system/setup panel into this group.

## 4. State and scope rules

| State | Presentation and permitted action |
|---|---|
| No owner or clip | Keep sections visible; explain what to select. Offer existing-action clip creation only when its prerequisites hold. |
| One editable Action clip | Arrangement, blend controls and source-action navigation are available. |
| Multiple selected clips | Timing actions name their batch scope; blend settings still name the active clip. New Correction requires one source clip. |
| Shared source Action | Show Shared Action and Make Unique. Explain that source key edits affect other references. |
| Tweak Mode | Show Finish Editing; disable strip rearrangement that requires leaving Tweak Mode. Do not silently exit and re-enter it. |
| Muted/solo tracks | Show evaluation state; a valid operation must not pretend an inaudible/muted contribution is visible. |
| Transition, meta or sound strip | Identify its type. Expose only compatible operations; do not silently recurse into a meta strip. |
| Locked or read-only target | Explain the restriction; reject an invalid batch before applying changes. |
| Scaled/repeated/reversed action clip | Keep action and scene time distinct. Generic key-editing helpers are not used without proper remapping. |

Scope follows the NLA editor's selected editable strips and their real owners
and action slots. It must never fall back silently to an arbitrary active
object's Action. Settings tuned before a gesture belong to that gesture's
options; completed undoable actions expose their parameters through Adjust
Last Operation. Persistent strip properties remain native editable fields.

## 5. Visual direction

Treatment: UI/tool; operated/multi-state. Inherit the active Bforartists theme
and UI scale. No new colors, custom header icons or novelty widgets.

Fallback design tokens: ground #303030, surface #3C3C3C, button #505050,
primary ink #EEEEEE, secondary ink #B8B8B8, selection accent #477DA8.
Use the native UI font and native sizing. Main actions are text buttons;
settings are clearly labelled native fields and checkboxes. Group headers
carry no icons. Status is expressed in text as well as color.

Target widths: 220, 280 and 360 logical pixels. At 220, reflow navigation and
long action buttons to full-width rows. Avoid nested primary-action folds;
only advanced settings, diagnostics and occasional procedures collapse.
Preserve the user's expansion state after first use.

## 6. Reuse and implementation boundaries

| Capability | Present state | Design consequence |
|---|---|---|
| NLA sidebar mixin and detached panel cloning | Exists in `ui/editor_placement.py` | Reuse placement infrastructure, not incompatible panel bodies. |
| Native move, duplicate, make-single-user, transitions and Tweak Mode | Present in the target host's `space_nla.py` menus | Prefer native operations; add selection/scope guards where needed. |
| Nudge, alignment and sequencing policies | Need strip-aware implementations | Do not reuse key-retiming math unchanged. |
| New neutral correction setup | New capability | Requires its own design/behavior qualification before release. |
| Existing Anim Assist animation layers | Separate Action-backed evaluation engine | Do not represent them as native NLA tracks or reuse their weight controls as NLA influence. |
| Evaluated NLA bake | Native capability exists; existing Anim Assist bake is not certified for this workflow | Qualify context, output assignment and preservation before exposing it. |

Architectural touchpoints for a later implementation plan:

- Add an NLA-specific home and groups to `ui/layout_homes.py`; first replace
  the current Graph-otherwise-Dope group-ID helper with explicit editor IDs.
- New NLA panels, strip-context resolution and strip operators stay separate
  from key/curve operators. Share small drawing helpers and native operators.
- Register every new action in an NLA header menu as well as its sidebar home.
- Scope resolution supplies owner, action slot, strip type, selection and
  timing mapping; drawing is read-only and never creates actions or tracks.
- Do not add a new NLA or Timeline canvas overlay. The Timeline stays bottom-only.

The owner approved these dependencies for implementation. See docs/anim_assist/releases/12.8.0/qualification.md for resulting checks.

## 7. Acceptance requirements

The approved requirements below informed the implementation and focused native-host checks. Production-rig coverage remains limited as documented in the release qualification.

1. Clip movement changes only stated strips; source keys are unchanged.
2. Influence/blend controls affect the named active clip, not another selection.
3. Adding a neutral correction preserves the evaluated motion before authoring.
4. Correction weight zero reproduces the base result; an authored correction at
   full weight gives the intended pose for supported transform types.
5. Shared-action edits are explained; Make Unique actually separates references.
6. Source editing works through native Tweak Mode with shifted, scaled, repeated
   and reversed clips; unsupported mappings are blocked with a useful reason.
7. Undo/cancel, locked targets, empty selection, multi-owner selection, reload,
   area switching and saved workspaces retain valid state.
8. Bake preserves originals and avoids double evaluation of source plus output.
9. Both main workflows are discoverable without opening multiple nested groups.
10. Actual screenshots at the target widths confirm text fit and native styling.

## References

- [Native NLA editing and Tweak Mode](https://docs.blender.org/manual/en/dev/editors/nla/editing/strip.html).
- [Source-based editor sidebar audit](../../anim_assist/reviews/2026-10-15-editor-sidebar-audit.md).
- Existing layout: `anim_assist/ui/layout_homes.py:47`.
- NLA panel foundation: `anim_assist/ui/editor_placement.py`.
- Separate animation-layer engine: `anim_assist/core/p11_layer_engine.py:11`.

## Review status

The owner approved both NLA workflows and implementation, including native Bforartists validation. The local 12.8.0 implementation follows this design with conservative transform correction support. See [release qualification](../../anim_assist/releases/12.8.0/qualification.md) for measured checks, screenshots and limitations.
