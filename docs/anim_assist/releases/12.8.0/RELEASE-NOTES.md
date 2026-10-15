# Anim Assist 12.8.0

## Editor-specific animation sidebars

Open **NLA Editor → Sidebar → Anim Assist**. Arrange & Time and Blend & Corrections start open together. Actions & Tracks, Bake & Finish and Quick Shelf start closed. The top summary names the owner, active clip, source Action, selection count, scene range and source range.

- Nudge selected clips, align their starts/ends to the active selected clip, or sequence them from that clip's start. Timing uses scene frames. Adjust Last Operation changes step or gap. Locked or overlapping batches are rejected before mutation.
- Edit source keys through native Tweak Mode. Finish Editing returns to clip arrangement. Dope Sheet and Graph navigation reuse a suitable unpinned editor or switch the current area; the editor selector returns to NLA.
- Create an independent neutral **Combine** transform correction above the source motion. Select its new clip, then Edit Correction. Creation supports object and pose-bone transform channels. Constrained/driven rigs and unsupported source channels are blocked with an explanation.
- Influence keys at 0%, 50% and 100% change the active clip's native influence curve at the playhead. Adjust Last Operation supports another value. Automatic blend envelopes and animated influence remain native strip settings.
- Duplicate Independent copies the Action; Duplicate Linked shares it. Make Unique separates selected source Actions. Shared references, mute and Solo exclusion are identified.
- Bake the active clip owner's evaluated transforms to a new retained Action. Original Actions, clips, constraints and parents remain. The output stays unassigned. **Use Latest Bake** separately assigns it and disables NLA evaluation. Active constraints must be muted or removed before using evaluated baked transforms to prevent applying constraints twice.

## Graph Editor and Dope Sheet

Graph emphasizes direct curve shaping, interpolation and handle controls. Breakdown sampling settings are labelled Breakdown Options and placed with pose tools. Dope Sheet combines Block & Tween, promotes selection, and gives Bake & Finish its own section. Handle-side selection stays in Graph; Dope Sheet retains advanced handle types. Macro authoring and setup live in Scene Properties.

Selected-key interpolation now changes selected editable visible keys only. Key Manager timing commands honor editor visibility and channel locks. Empty editor selections do not broaden into the active object's full Action. These helpers support object Actions; detached pinned Actions and non-object sources are explicitly identified as unsupported rather than silently targeted.

The existing Timeline toolbar remains **bottom-only**, with the 12.7.1 placement implementation unchanged. This is an add-on ZIP for the existing Bforartists installation.

## Install

Install `b4_anim_assist_v12.8.0.zip` through Preferences → Install from Disk, then restart Bforartists. Existing Timeline layouts and settings are retained. The new sidebar is available through the NLA header's Anim Assist menu as well as its sidebar tab.

See [qualification](qualification.md) for measured checks and limits.
