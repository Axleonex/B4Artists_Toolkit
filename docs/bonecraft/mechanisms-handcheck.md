# Mechanisms desktop hand check

For the owner, on Bforartists 5.2.0. The automatic tests cannot cover the
viewport, the guided build overlay or the Graph Editor, so this list does. Do
the items in order. Each item says what you should see. See
[Mechanisms](mechanisms.md) for what each word means.

Start with a fresh scene and BoneCraft enabled.

1. **Tool switch.** Enable BoneCraft. Open **Preferences → Add-ons → BoneCraft → Tools**.
   - Expected: **Mechanisms** is listed, and it is on.

2. **Scene tab, nothing selected.** Select nothing. Open **Properties → Scene
   tab**. Scene-tab sections start collapsed, so expand **Mechanisms**.
   - Expected: the order is Rig Builder, then **Mechanisms** (one line: "Select
     a mesh to start, or an armature with mechanisms."), then CATS, VRChat,
     Import / Export.

3. **Viewport tab off.** Switch the BoneCraft viewport tab off (Preferences →
   Add-ons → BoneCraft → Tabs).
   - Expected: Mechanisms stays in the Scene tab. Switch the tab back on.

4. **Build a test weapon.** From primitives, make a small transforming weapon
   that uses all six types: for example a Blade (Hinge), a Barrel (Slide), a
   Mast of a base and three segments (Telescope), a Lift with a frame, an arm
   and a cylinder and rod (Piston), two gears (Gear Link) and a Cover (Follow).
   Select the parts and click **Add Parts from Selection**. Then use **Add
   Joint** and **Add Link** for each type, and **Edit Pivot → Apply Pivot** on at
   least one part.
   - Expected for every guided build: picked parts get an outline and a numbered
     label; the header and status bar show a step sentence; **Esc** removes the
     mechanism; **Enter** keeps it; the preview loops until you press one.
   - Use **Align to Selection** once. Enter Edit Mode on the part's mesh and
     select one edge or face. Stay in Edit Mode, start **Add Joint → Hinge**,
     click the part, press **A**. (The guide ignores Tab, so do not try to enter
     Edit Mode during the guide.) Expected: the hinge axis follows the edge or
     face. If the guide cannot use the selection it says why and lets you press
     X, Y or Z.

5. **Test each mechanism.** Click **Test** (the play-triangle button) on every item in the list.
   - Expected: it sweeps through its range and returns to where it was. No
     keyframes are added (check the timeline and Dope Sheet). Press **Esc**
     during a Test: it stops and the pose is restored.

6. **Sequence.** In **3. Sequences** click **Add Sequence**. Click **Capture
   Step** (the slider jumps to 1). Pose some handles, click **Capture Step**.
   Pose others, click **Capture Step** again. Drag the Sequence slider. Click
   **Test**.
   - Expected: each Capture Step makes steps for the handles that moved and
     returns the handles to zero. Dragging the slider plays the
     transformation. Test plays it forward and back.

7. **Forms.** In **4. Controls** pose the rig, click **Save Form**. Pose it
   differently, **Save Form** again. Then **Go to Form** on each, then **Go and
   Key**.
   - Expected: Go to Form sets every handle and Sequence slider to the saved
     values. Go and Key also inserts keys on the current frame.

8. **Hand edits.** Use a Hinge that a Gear Link drives, and keep Show Helpers
   on. Rename that Hinge's CTRL bone in Pose Mode. In the Hinge's settings,
   expand **How this works** and click the **Select** button (arrow icon) next
   to its `limit` line: this selects the hidden MCH bone. In the Bone
   Constraints tab edit that Limit Rotation by hand (for example Min X). Also
   add your own constraint on that MCH bone. Click another item in the list and
   then the Hinge again; the check runs when you select a mechanism.
   - Expected: the Hinge shows **Changed by hand**. Click **Keep mine**: your
     limit goes into the record (**Min** / **Max** change). Edit the Limit
     again and click **Restore**: your edit is gone.
   - Now force a rebuild with a structural edit: on the Gear Link change
     **Kind** from Gear to Belt and back. (A value edit such as a limit updates
     in place and does not rebuild.) Expected: no duplicate bones, the renamed
     CTRL bone still moves the part, and your own constraint stays below
     BoneCraft's constraints on the MCH bone.

9. **Reshaped curve.** Make a Follow with **Curve** ticked. In the Graph Editor
   reshape the curve of the Action behind its `BC·…·follow` constraint. Then
   change the Follow's **Target Range** and select the Follow in the list.
   - Expected: the Follow shows **Changed by hand**. **Keep mine** keeps your
     curve. Reshape it again and click **Restore**: the curve is regenerated.
   - Do the same for a Sequence: reshape a step's curve, change that step's
     **Target**, and select the Sequence. Expected: **3. Sequences** shows its
     message and a **Restore** button (no Keep mine). Restore regenerates the
     curve. **Detach** and **Delete** are next to **Test** for the selected
     Sequence.

10. **Show Helpers.** Turn **Show Helpers** off in **Preferences → Add-ons →
    BoneCraft → Helpers**, or turn on VRChat **Compact Mode**.
    - Expected: the teaching text and every "How this works" note disappear
      everywhere in BoneCraft. A guided step shows a short label ("Moving
      part") instead of a sentence. Turn it back on and they return.

11. **Merge and validation.** Click **Merge for VRChat**. Run the Rig Validator
    and look at the Task Board.
    - Expected: the merge makes one mesh with one vertex group per former
      object, still moving with the rig. The Mechanisms checks report nothing
      unexpected (loops, missing parts and Python drivers do not appear).
    - The Task Board shows no "Rig validation errors" task: the naming check
      accepts hyphens and the drivers check warns only on expressions that
      need Python.
    - **Known issue, for you to decide (not a pass condition):** the rig's
      `root` bone is in no bone collection, so the collections check warns and
      the Task Board shows "Rig validation warnings (1)". Note what you see.

12. **Save and reload.** Save the file and reload it. Then repeat with **Edit →
    Preferences → Save & Load → Auto Run Python Scripts** turned off.
    - Expected: the rig, records, forms and handles still work after the reload.
      With Auto Run Python Scripts off, every mechanism still moves, including
      a free-spinning gear and the Sequence slider.

Also try: start **Add Joint** from the Properties editor's Scene tab (the
guide works in the largest 3D Viewport); rename a part's object (the part
stays bound); type `0.5, abc` in a Telescope's Shares (a plain error says the
shares must add up); make a Follow from a free-spinning Hinge (refused: the
source Hinge needs limits under a full turn).

When all twelve items are as expected (item 11's known issue noted), the
Mechanisms feature is ready for your "Confirm merge update?".
