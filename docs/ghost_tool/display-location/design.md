# Ghost Tool display location

Date: 2026-10-12. Status: approved by the user on 2026-10-12.
Target build: current unpublished 4.2.5 candidate, including the completed Compare folds.

## User behavior

Add **Display Location** near the top of Edit > Preferences > Add-ons > Ghost Tool.
It is one persistent dropdown with three choices:

| Choice | Full Ghost Tool home |
|---|---|
| Top Header | Existing 3D Viewport header dropdown; default for current installations |
| Right Sidebar (N) | Ghost Tool tab in the viewport's right sidebar |
| Left Tool Shelf (T) | Ghost Tool tab in Bforartists' left Tool Shelf |

Changing the preference switches the full home immediately. Show the chosen side region and
select its Ghost Tool tab where the native region supports category selection. Keep unrelated
native panels available. Preferences are saved through Bforartists' normal preferences system;
scene-specific animation settings and saved references stay with their scenes.

All homes contain the same controls, including independent Marker Targets, Capture Targets
and Snapshot Targets folds. Open in Separate Window remains reachable from every home.
The top header default preserves the current workflow. No new shortcuts or activation dialogs.

## Implementation boundary

Reuse `draw_ghost_tool` and a shared footer for the full layout. Add a right-sidebar panel and
a left-shelf panel, controlled by the preference in their polls; the main header entry follows
the same preference. Register panels once, rather than rebuilding classes on every choice change.
Use distinct fold prefixes per home and retain stable snapshot UIDs within each region.

Read preferences safely during registration and direct test registration, falling back to Top Header
when the add-on preference entry is unavailable. Detect left-shelf support using
`show_toolshelf_tabs` in SpaceView3D RNA before registering the native TOOLS panel.
If a saved left-shelf choice is loaded on an unsupported host, retain header access and show
an explanation in preferences. Ghost Tool's Bforartists-only installation gate remains.

This is a native UI tool: inherit Bforartists theme palette, fonts, spacing and disclosure arrows.
The left Ghost Tool tab is the full home explicitly requested by the user; existing native
Object/Pose quick-action buttons remain menu/tool access points, rather than additional full homes.
Fold visibility, preference changes and drawing must not modify animation, reference bindings or keys.

## Verification

Check the default and all three preference values, exclusive full-home visibility, immediate
redraw, side-region visibility, persisted choice after restart, registration/unregistration and
missing-preference fallback. Reuse recording-layout tests to check identical controls and target
folds across homes. Run the marker/Compare fold, header, authoring and snapshot identity suites.

Inspect rendered header and right-sidebar layouts on the available Blender stand-in. Left Tool
Shelf usability and native tab selection require Bforartists; mark them unverified if that host
remains unavailable. Package the exact 4.2.5 source and verify ZIP bytes/version/hash after
implementation. Retain historical 4.2.2 and 4.2.3 artifacts and their original evidence.

## Alternatives considered

A persistent enum with registered panels and visibility polls is recommended: the same layout
and operator behavior remain shared, and switching does not tear down active UI classes.
Dynamically relocating a single registered panel would reduce panel classes but adds unregister/
register transitions and couples location changes to separate-window UI. The additional lifecycle
risk does not help the requested preference.

## Scope and review

Implementation covers Ghost Tool preferences, panel placement, focused verification and the
current 4.2.5 candidate package/documentation. It does not change sampling or snapshot behavior.
Self-review: no unresolved requirements, conflicting locations or implementation placeholders.
The only verification limit is the currently unavailable native Bforartists host.

Design preparation route: recommended/actual T1_NATIVE; policy fingerprint
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
