# Tab sides desktop hand check

For the owner, on Bforartists 5.2.0. The automatic tests move the panels but
cannot look at the viewport, so this list does. Do the items in order. Each
item says what you should see.

Start with a fresh scene and BoneCraft enabled. Open the left Tool Shelf (**T**)
and the right sidebar (**N**) in the 3D Viewport.

1. **Defaults.** Look at both sides of the viewport.
   - Expected: the Tool Shelf's tab strip shows **BoneCraft** and
     **Rig Builder**; the sidebar shows **CATS** next to Bforartists' own tabs.
     BoneCraft's sections (Setup, Skin, Mechanisms, Review …) are readable at the
     Tool Shelf's default width; drag the Tool Shelf wider and they reflow.

2. **Preferences rows.** Open **Preferences → Add-ons → BoneCraft → Tabs**.
   - Expected: three rows, each a show switch then **Left | Right**:
     BoneCraft (Left), CATS (Right), Rig Builder (Left).

3. **Move CATS left.** Click **Left** on the CATS row.
   - Expected: at once, with no restart, CATS leaves the sidebar and appears in
     the Tool Shelf's tab strip with all its sections (CATS, VRChat,
     Import / Export). No errors in the Info editor or the system console.

4. **Move BoneCraft and Rig Builder right.** Click **Right** on both rows.
   - Expected: both tabs move to the sidebar at once. Open BoneCraft →
     Mechanisms: its four subsections are there and work (Add Joint starts the
     guided build).

5. **Hidden tab.** Untick **CATS**.
   - Expected: the CATS tab disappears and the CATS row's Left | Right buttons
     turn grey. Grey buttons still respond: click **Right**, then tick CATS
     again. CATS shows in the sidebar.

6. **Tool switch.** In **Tools**, switch **Control Picker / Rig UI** off. Move
   the BoneCraft tab to the other side, then switch the tool on again. Then
   switch **Mechanisms** off and on.
   - Expected: no error. **Control Picker** comes back inside BoneCraft →
     Animate, and Mechanisms inside the BoneCraft tab, both on the side the
     BoneCraft row names.

7. **Restart.** Save preferences, restart Bforartists.
   - Expected: every tab is on the side you last chose.

8. **Back to defaults.** Set BoneCraft Left, CATS Right, Rig Builder Left.
   - Expected: the layout of item 1.

9. **Properties copies.** Open **Properties → Scene tab**, and with an armature
   selected **Properties → Armature data**.
   - Expected: Rig Builder, Mechanisms, CATS, VRChat, Import / Export and the
     Armature-data BoneCraft sections are where they were before items 3–8.
