# Rig Builder placement — desktop hand check (Bforartists 5.2.0)

Branch: `work/bonecraft-rigbuilder-placement`. Install the add-on from that
branch, then:

1. **Scene tab (permanent).** In the Properties editor open the **Scene** tab and
   scroll down. Below Blender's own panels: **Rig Builder**, then **CATS**,
   **VRChat**, **Import / Export**.
2. **Always shown.** Select nothing, then a camera, a mesh and an armature in
   turn: Rig Builder and the three CATS sections stay in the Scene tab.
3. **Side panels.** With the default sides, the left Tool Shelf has the
   **BoneCraft** and **Rig Builder** tabs; the right sidebar has **CATS** (plus
   Bforartists' Item / Tool / View / Animation). The Object tab no longer shows
   **BoneCraft VRChat**. [Tab sides](tab-sides-handcheck.md) checks the
   Left | Right choice.
4. **Tabs switches affect side panels only.** Preferences → Add-ons → BoneCraft →
   Tabs:
   - untick **Rig Builder** → the Rig Builder viewport tab goes; the
     Scene-tab Rig Builder stays;
   - untick **CATS** → the whole CATS viewport tab goes (CATS, VRChat,
     Import / Export); the Scene-tab sections stay;
   - untick **BoneCraft** → the BoneCraft viewport tab goes; with an armature
     selected, its copy in Properties → Armature data stays.
   Tick them all again.
5. **Same tools in both places.** Open CATS → VRChat → Set Up Humanoid Bones in
   the sidebar and in the Scene tab: same buttons. With Rigify enabled, Quick Rig
   on the Tool Shelf lists the Rigify metarig buttons, as in the Scene tab.
6. **Wizard.** Run the Auto-Rig Wizard end to end (Scene tab or Tool Shelf).
7. **Premade rigs shelf.** In Object Mode open the **BoneCraft Rigs** asset
   shelf (bottom of the viewport; pick it from the shelf selector if
   Bforartists shows its Primitives shelf first). Drag the **Basic Humanoid**
   onto a character. Rig Builder → Quick Rig shows **Dropped rig**: pick the
   mesh, tick **Auto-Weight**, click **Fit Dropped Rig**. The rig stands on the
   mesh and the mesh deforms with it. With both boxes unticked the button
   refuses and the box stays.
8. **Asset library.** Preferences → File Paths → Asset Libraries lists
   **BoneCraft Rigs**. Disable BoneCraft: that entry is gone; any library you
   made yourself stays.
9. **Tool toggle.** Preferences → BoneCraft → Tools → switch **CATS** off and on:
   the Scene-tab CATS sections disappear and come back.

## Known items

- In the narrow Tool Shelf (and a Properties editor narrowed below about
  220 px) Rig Builder uses its compact layout (short labels); widen it for the
  full layout.
- Opening the Tool Shelf's **Utility** tab prints `wizard_bl_idname` errors in
  the console. That is a Bforartists 5.2.0 bug (its own asset-wizard code),
  present with BoneCraft disabled too.
