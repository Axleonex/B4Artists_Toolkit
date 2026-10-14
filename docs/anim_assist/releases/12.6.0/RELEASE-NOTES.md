# Anim Assist 12.6.0 — native Timeline toolbar

Windows x64 release for custom Bforartists 5.2.0, with the matching Anim Assist
12.6.0 add-on. The custom application supplies the genuine native second row.

## Toolbar

The patched Bforartists application supplies a genuine native Timeline
TOOL_HEADER above the native playback/keyframe row, with native sizing and
minimum-height handling. Anim Assist fills it with seven inline families,
configurable direct buttons, Search, Pin and family options. On fresh startup,
both rows appeared without dragging in the observed 100% and 150% UI-scale
captures.

The add-on alone cannot add the native region to an official unpatched
Bforartists application; there it uses the existing Timeline header. There is
no separate helper editor or recurring geometry repair.

## Action access

The searchable and pinnable catalogue exposes 89 existing Anim Assist actions
across Tween, Curves, Timing, Keys, Pose, Bake and Motion. All 70 prior dispatch
mappings, 13 default quick actions and 17 prior quick presets are preserved.
The local build exposes existing clipboard, reference bookmark, object matching
and configured rig switching operations. Clipboard pastes copied key times
with its configured offset; reference recall sets a reference frame; matching
targets objects.

Search finds actions outside the visible quick buttons. Pin places an action
in its family for one-click use. The Gear controls quick selection and Reset;
family options open their supported settings. Observed live examples include
Nudge Right, Copy, Tween options, and the breakdown-anchor tooltip. This
catalogue improves access to Anim Assist's current tools; it does not provide
full AnimBot algorithm or gesture parity.

## Local install

The local archive is named
`Bforartists_5.2.0_AnimAssist_12.6.0_Windows_x64.zip`. Extract it and start
`Launch Anim Assist (isolated).cmd`, then install the included
`AnimAssist/b4_anim_assist_v12.6.0.zip` and enable Anim Assist. The launcher
keeps this build's preferences, scripts and data files in an adjacent profile.
Keep it separate from other Bforartists installations.

The application archive SHA256 is recorded in the local release receipt. The
matching add-on ZIP is 577,101 bytes with SHA256
`60d4c7f10d9f14adde17e0cd5269bb07d4a4fc8f96810a4cd6e67903e5e73193`.

## Qualification

The available-host matrix passed: all 80 immediate effects in patched and
unpatched Bforartists, all nine native modal tools with commit/cancel, migration,
persistence, multi-window/maximized lifecycle and native animation controls.
Validation repaired maximized re-enable, Ease prerequisites and Action Offset
preference/handle/cancellation defects. See [qualification](qualification.md).

Editor-border captures include sampled frames during 100%/150% drags. Window
resizing has settled render coverage only; universal absence of flicker and
Windows display-DPI transitions are not certified. Production-rig and full
AnimBot algorithm parity are outside the fixture coverage.
