# Anim Assist 12.10.0

## Stage toolsets

Block, Spline, Polish and Deliver each have their own toolset on the bottom Timeline row. **All** stays the condensed overview of every family, now drawn in the same compact style (below).

Each stage starts from a fixed default set: the Recommended tools for its families plus tools for that phase of work:

| Stage | Adds by default |
|---|---|
| Block | Breakdown presets -25/25/50/75/125 (in place of the 25/50/75% and Push/Pull buttons); Inbetween, Distribute Inbetweens; Select Range/All/Ends, Grow left/right, mark Keyframe/Breakdown/Extreme/Moving Hold |
| Spline | To Spline; Neighbors, Ease and Smooth sliders; Set Reference with To Reference and Amplify popouts; Auto Clamped/Vector/Free handles; a Trails show/hide toggle for checking arcs |
| Polish | Timing Scale as an inline slider with presets 80/90/110/120 (in place of the four spacing buttons), Timing Offset slider, Ripple slider with presets -1/1, Snap; Select Opposite, Mirror Active, Swap |
| Deliver | Bake Preview Range, Smart Bake, Reduce slider with presets 0.001/0.01/0.05, Bake Keys to Integer Frames; One-Click Proxy & Bake; Location, Rotation, World and Parent proxies, then Bake Session and Remove Proxies, and Remove All Proxy Sessions |

- **Stage families:** Block shows Tween and Keys, Spline shows Curves and Motion (arcs are checked while splining), Polish shows Timing and Pose, Deliver shows Bake. Refresh and Diagnose Trails stay in More and Search.
- **Customise each stage** in Toolbar Settings: Row Stage chooses the setup you edit, Family offers that stage's families, and each tool can be Hidden, Button, Popout or Inline (tools with an icon also Label or Icon), and reordered. **Reset Stage to Defaults** restores one stage; **Restore Recommended Layout** restores everything.
- **Stage dropdown:** when the row is too narrow for the five tabs, the single stage button opens a list of All, Block, Spline, Polish and Deliver. One click opens it and it stays open while you hover; click a stage to switch. Clicking the button again, clicking anywhere else or pressing Esc closes it, without acting on what is underneath. A short Timeline shows the five stages as a row above the button. Ctrl+Wheel still cycles. The button is slightly wider for its arrow, so on very narrow rows one more tool may move into More.
- **Saved layouts** store All and all four stages together (Save As, Load, Update Saved, Rename, Delete).
- **Amounts are shared:** range, default, presets, slider width and snapping are the same in every stage.
- **Clearer row labels** for tools that showed internal names or abbreviations, for example 80% instead of T80, Mark Key instead of Type Keyframe, All Keys for Select All Visible, Set Reference, To Reference, Amplify (was Push/Pull, which clashed with Block's Push/Pull buttons), Show Trails, Location Proxy, Rotation Proxy and Clamped (Auto Clamped handles). They apply wherever these tools appear; All keeps Trails so its row is as wide as in 12.9.
- **Scales instead of percentage buttons:** a stage can carry its own slider presets. Block's Breakdown slider has -25, 25, 50, 75 and 125: -25 and 125 give exactly what Push Previous/Next give at the default Push Strength, 25 and 75 what Pull Previous/Next give. Polish's Timing Scale slider has 80, 90, 110 and 120. A stage preset may go past the slider's standard range up to the tool's limit. In a stage, Tool Settings edits that stage's presets; All keeps its own presets (none by default), so All is unchanged.
- **Compact All row:** the Recommended All row keeps the same everyday tools as 12.9 but draws them like the stages: 25%, 50% and 75% become ticks on the Breakdown slider (click a tick to apply it), and -1f/+1f, Copy, Paste, Mirror, Bake Object and Trails become icons (Trails is the show/hide eye). The row is about 200 px shorter, so the five stage tabs return from about a 1,450 px Timeline. Tool Settings has a Presets as Ticks checkbox for every slider, in All and in each stage. A layout you saved or edited in 12.9 keeps its own All row; Restore Recommended Layout gives the compact one.
- **Compact rows:** stage sliders show their presets as click ticks on a wider track (Breakdown -25 to 125, Timing Scale, Ripple, Reduce); clicking a tick applies exactly that preset, and a drag snaps onto ticks. A slider squeezed into a popout shows its presets as buttons again. More icons: Inbetween and Distribute in Block; Set Reference (target) in Spline, where To Reference and Amplify are now inline sliders; the four Pose tools in Polish; Bake Object and the four proxy types in Deliver. Every row fits a 1,397 px Timeline with all of its tools and named sliders.
- **Reduce and Ripple sliders:** Reduce (Deliver) drags the key-reduction tolerance with a live preview of the keys removed; Ripple (Polish) drags how many frames the keys after the playhead move. Esc restores both. Presets 0.01 and 1 give exactly what the old Reduce Keys and Ripple buttons gave. With the compact Deliver row, Reduce shows inline at a 1,397 px Timeline.
- **More icons:** grow selection (key and arrow), Copy and Paste in Block; To Spline (curve) and the handle types (in your theme's Graph Editor handle colours) in Spline; -1f/+1f arrows in Polish. Show and Hide Trails become one **Trails** eye toggle (new action, 96 in total); the separate buttons stay in More and Search.
- **Key-type icons:** in Block, Mark Key, Mark Breakdown, Mark Extreme and Mark Hold show as diamonds in your theme's Dope Sheet key colours and Blender's relative sizes (Breakdown smaller, Extreme larger), so the type reads by shape and size as well as colour; hover for the name. This frees about 210 px, so Copy and Paste now fit on the Block row. Toolbar Settings offers Icon only for tools that have one (key types, handle types, grow, nudges, To Spline/To Stepped, Copy, Paste, Trails); a saved Icon choice on any other tool shows its name.
- **Sliders keep their names on a tight row:** the track gets shorter first; names are dropped only when that still does not fit.
- **Shortcuts follow the shown stage:** right-click Tool Settings, Search pins and More act on the stage the row shows. A tool from a family the stage does not show is pinned into All, with a note.

## New toolbar actions

Four existing Bake tools are now on the Timeline toolbar: **Bake Preview Range**, **Bake Keys to Integer Frames** (same rounding as Round Key Times, with a timing snapshot Reset Timing restores), **One-Click Proxy & Bake** (row label Proxy & Bake) and **Remove All Proxy Sessions**. Two existing interpolation tools join the Curves family: **To Spline** (selected keys to Bezier) and **To Stepped** (selected keys to Constant). 95 actions in total before the Trails toggle.

## Fixed

**Timeline row hover text** kept only three lines, so longer descriptions were cut off, often the reason a tool is greyed out. It now shows in full: the tool's name, what it does, why it is unavailable (in orange), what it works on and what it needs. The box widens to fit the Timeline and moves clear of the playhead.

**One-Click Proxy & Bake** (Bake sidebar, pie menu and now the toolbar) had two bugs in 12.9.x and earlier:

- It flattened the object's location animation: the proxy stayed at the current position, so the bake recorded a still object. It now records the object's world motion on the proxy first, so the baked keys follow the original motion.
- It removed every helper of an open proxy session, including proxies made for other objects, without baking them. It now works in a session of its own and leaves other sessions alone.

## Upgrading from 12.9.x

- Stages start from the fixed default set above, not from your All tools. Tools you added to All stay in All until you add them to a stage.
- Your saved toolbar record is upgraded in memory and stored in the new format the next time you change toolbar settings. Anim Assist 12.9.x cannot read the new format; reinstalling 12.9.x afterwards falls back to the Recommended layout.

## Install

Install `b4_anim_assist_v12.10.0.zip` through Preferences → Install from Disk, then restart Bforartists.

See [qualification](qualification.md) for measured checks and limits.
