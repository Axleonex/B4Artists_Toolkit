# Anim Assist 12.1.3 user guide

Current local build: 12.1.3. This guide covers installation, the current interface, common workflows and the fixes in this release. Detailed tool descriptions are available through the add-on's Help controls.

## Install and set up

Download `releases/b4_anim_assist_v12.1.3.zip`. In Bforartists, open Edit > Preferences > Add-ons > Install from Disk, select the ZIP and enable Anim Assist. Install the ZIP directly. Its internal package name is `B4_anim_assist`.

Open Properties > Scene > Anim Assist > Setup and run First Run Setup once. This creates the Quick Shelf. Setup can also create an Anim Assist workspace. The optional Shift Alt D pie shortcut is off by default; enable or rebind it in Settings.

This is a Bforartists add-on. The exact ZIP was verified on Bforartists 5.2.0, with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`. Other builds were not verified by that run.

## Find the tools

- Graph Editor: press N and open the Anim Assist tab. Groups are Select, Shape Curves, Retime, Clean Up, Pose & Rig and Quick Shelf.
- Dope Sheet: press N and open the Anim Assist tab. Groups are Block, Inbetween, Time, Mirror & Match, Keys & Channels and Shelf & Macros.
- Properties > Scene: open Anim Assist. Tools are grouped by This Pose, Whole Animation, Rig and Face, followed by Setup, Settings and Help.
- The editor header menus provide common tools, panel access, the Anim Assist workspace and Open in Separate Window.

Use the help controls for the selected tool's prerequisites and settings. When a command is unavailable, read its prerequisite message and select the required keys, objects or bones.

## Key editing and timing

Work on a saved copy of your animation. Select the relevant animated object or pose bones and select the keys you want to affect in the Graph Editor or Dope Sheet.

Use the Breakdown tools to create in-betweens between neighboring poses. Midpoint uses the middle value; Favor Previous, Favor Next and Weighted change the balance. Inspect the resulting pose and curves before continuing.

Use Scale Keys and Offset Keys to adjust timing. Explicit values supplied to those operators are retained. Ripple shifts following keys; inspect both the selected range and later animation after using it.

Tag and Protect controls mark important keys. Check protection before cleanup. The Match and Mirror tools need the appropriate object or pose-bone selection and mapping; use Setup when pair or switch detection is required.

## Search, Recents and Quick Shelf

Search provides access to existing tools. Completed tools enter Recents with the newest first. Repeat Last reads that newest entry. Cancelled tools and commands that still need modal input are not recorded as completed actions.

Version 12.1.3 also reads older files' Recents by timestamp, fixing the old oldest-first order. The stored list is reordered the next time a tool is recorded. Clearing Recents leaves it empty.

Toggle Shelf Mode cycles through the supported modes. Use the shelf and menus to access tools; their entries retain the existing operator identifiers.

## Animation layers and lipsync

Set up the rig and animation layers before baking. In the Face and Setup sections, configure the lipsync target, audio and viseme wiring. Resolve any missing-layer or missing-WAV guidance before Bake Lipsync.

Amplitude analysis is available without an external phoneme tool. Rhubarb is optional and needs its executable configured. The verification for this release used Amplitude; it did not exercise Rhubarb.

Live Preview and Baked identify the lipsync state. Bake or Rebake writes automatic keys to the configured target. Mark Manual preserves the selected manual work during rebake; Clear Auto Keys removes automatic output while retaining manual keys.

On modern Action slots, 12.1.3 reuses the layer Action's only slot. It no longer creates a second slot that the layer stack would ignore. Clear Auto Keys and Mark Manual also avoid creating slots. Saved target and preview/baked choices survive file reopening.

## Verify and recover

After changing timing, matching or lipsync, inspect the result in the viewport and animation editors. Save, reopen and inspect the scene before relying on it for production. Use native Undo to recover from an unwanted operation; real-window interaction remains outside the background regression run's scope.

Report the add-on version, Bforartists build, command and reproducible steps when opening an issue. A small scene that reproduces the problem is useful.

## Release verification

The exact 12.1.3 archive passed 170 internal tests, 26 repair checks and 16 workflow checks on the recorded Bforartists host. Checks included panel layouts, enable/load/disable, timing, matching, mirroring, layers, lipsync rebake with manual-key preservation, the single Action slot and legacy Recents order.

These checks do not establish every interactive tool or all supported host versions. See `releases/12.1.3/VERIFICATION.md` for the scope and archive checksum.
