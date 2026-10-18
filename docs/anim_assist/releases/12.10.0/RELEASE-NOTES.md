# Anim Assist 12.10.0

## Stage toolsets

Block, Spline, Polish and Deliver each have their own toolset on the bottom Timeline row. **All** is unchanged: it stays the condensed overview of every family.

Each stage starts from a fixed default set: the Recommended tools for its families plus tools for that phase of work:

| Stage | Adds by default |
|---|---|
| Block | Inbetween, Distribute Inbetweens, Push/Pull Previous/Next; Select Range/All/Ends, Grow left/right, mark Keyframe/Breakdown/Extreme/Moving Hold |
| Spline | Set Reference Frame, Reference and Push/Pull popouts, Neighbors and Ease sliders, Auto Clamped/Vector/Free handles |
| Polish | 80/90/110/120% spacing, Timing Offset slider, Ripple, Snap; Select Opposite, Mirror Active, Swap |
| Deliver | Bake Preview Range, Smart Bake, Reduce Keys, Bake Keys to Integer Frames; Translation, Orientation, World-Space and Parent-Space proxies, then Bake Session and Remove Proxies, and Remove All Proxy Sessions; Refresh, Diagnose and Hide Trails |

- **Customise each stage** in Toolbar Settings: Row Stage chooses the setup you edit, Family offers that stage's families, and each tool can be Hidden, Button, Popout or Inline, labelled or iconed, and reordered. **Reset Stage to Defaults** restores one stage; **Restore Recommended Layout** restores everything.
- **Stage dropdown:** when the row is too narrow for the five tabs, the single stage button opens a list of All, Block, Spline, Polish and Deliver. One click opens it and it stays open while you hover; click a stage to switch. Clicking the button again, clicking anywhere else or pressing Esc closes it, without acting on what is underneath. A short Timeline shows the five stages as a row above the button. Ctrl+Wheel still cycles. The button is slightly wider for its arrow, so on very narrow rows one more tool may move into More.
- **Saved layouts** store All and all four stages together (Save As, Load, Update Saved, Rename, Delete).
- **Amounts are shared:** range, default, presets, slider width and snapping are the same in every stage.
- **Shorter row labels** for tools that showed internal names, for example 80% instead of T80, Mark Key instead of Type Keyframe and All Keys for Select All Visible. They apply wherever these tools appear, including All.
- **Shortcuts follow the shown stage:** right-click Tool Settings, Search pins and More act on the stage the row shows. A tool from a family the stage does not show is pinned into All, with a note.

## New toolbar actions

Four existing Bake tools are now on the Timeline toolbar (93 actions in total): **Bake Preview Range**, **Bake Keys to Integer Frames** (same rounding as Round Key Times, with a timing snapshot Reset Timing restores), **One-Click Proxy & Bake** (row label Proxy & Bake) and **Remove All Proxy Sessions**.

## Fixed

**One-Click Proxy & Bake** (Bake sidebar, pie menu and now the toolbar) had two bugs in 12.9.x and earlier:

- It flattened the object's location animation: the proxy stayed at the current position, so the bake recorded a still object. It now records the object's world motion on the proxy first, so the baked keys follow the original motion.
- It removed every helper of an open proxy session, including proxies made for other objects, without baking them. It now works in a session of its own and leaves other sessions alone.

## Upgrading from 12.9.x

- Stages start from the fixed default set above, not from your All tools. Tools you added to All stay in All until you add them to a stage.
- Your saved toolbar record is upgraded in memory and stored in the new format the next time you change toolbar settings. Anim Assist 12.9.x cannot read the new format; reinstalling 12.9.x afterwards falls back to the Recommended layout.

## Install

Install `b4_anim_assist_v12.10.0.zip` through Preferences → Install from Disk, then restart Bforartists.

See [qualification](qualification.md) for measured checks and limits.
