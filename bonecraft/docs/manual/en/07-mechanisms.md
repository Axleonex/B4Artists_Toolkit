# Mechanisms

[← Contents](index.md)

## What Mechanisms does

Mechanisms turns hard-surface parts into a working mechanical rig: hinges,
slides, telescopes, pistons, gears, followers and whole transformations played
by one slider. It builds ordinary Blender bones and constraints, so you can see
and change everything it makes, and the rig works in Blender without scripts.
Engines receive the `DEF-` bones. Export of baked mechanism motion to engines
comes later (see Limits of this version).

BoneCraft ships the tools, not a weapon. You bring the parts.

A complete worked example, with a screenshot for every step, is [Tutorial: Crescent Rose with Mechanisms](12-crescent-rose.md).

Words used in the panels and in this page:

| Word | Meaning |
|---|---|
| *Part* | A piece that moves as one solid block: an object, or a loose piece of one mesh. A part can ride on another part. |
| *Joint* | How a part may move: Hinge (turns), Slide (moves), Telescope (extends nested segments). |
| *Link* | What moves a part for you: Piston, Gear Link, Follow. |
| *Handle* | The bone you drag in the viewport. Each joint has one. Its value is also a slider in the panel. |
| *Sequence* | A transformation played by one slider, made of steps. |
| *Form* | A saved set of handle and Sequence values, such as "Stowed" or "Rifle". |

## Where it is

- **BoneCraft tab → Mechanisms** in the 3D Viewport. The BoneCraft tab is on
  the left Tool Shelf (press **T**) unless you moved it to the right sidebar
  (**N**) in Preferences. It sits between Skin and Review. It shows when a mesh
  is active (to start a rig) or when an armature with mechanisms is active; otherwise
  it explains what to select.
- **Properties editor → Scene tab → Mechanisms**, right after Rig Builder. It is
  shown while Preferences → Tabs → Scene Properties → Show is on. With nothing
  usable selected it shows one line: "Select a mesh
  to start, or an armature with mechanisms." Switching the BoneCraft viewport tab
  off does not remove it. The Scene Properties switch hides the Scene copy only.
  The `mechanisms` tool switch (**Preferences → Add-ons → BoneCraft → Tools**)
  removes the tool from every location.
  Scene-tab sections start collapsed, so click **Mechanisms** to expand it.
- **Object menu → Mechanisms** gives shortcuts to add parts, joints and links,
  and to test motion.
- **Viewport toolbar → Build Mechanism** starts a guided joint or link from a
  click on a part, in Object Mode or Pose Mode. Add the parts first, then select
  the mechanism rig or one of its parts and choose the type in the tool header.

Inside Mechanisms there are four subsections: **1. Parts**, **2. Joints &
Links**, **3. Sequences** and **4. Controls**. They appear once the rig has
parts. Before that you see only **Add Parts from Selection**.

Every button is one undo step. If a build fails, everything it changed is put
back and the panel shows the reason.

## Parts

1. Select the part objects (or one mesh made of loose pieces) in Object Mode.
2. Click **Add Parts from Selection**.
   - Several objects: one part per object. Each object is parented to its part's
     bone and stays where it is.
   - One mesh with loose pieces: one part per piece. Each piece gets a vertex
     group for its bone and the mesh gets an Armature modifier.
   - The first time, BoneCraft makes the rig (an armature) for you.
3. Select a part in the list to edit it.

For each part:

- **Rides on:** choose the part this one moves with. A child part follows its
  parent part. "the rig" means it rides on the rig's root.
- **Size** sets the bone length, which sets the handle size.
- **Edit Pivot** puts a marker on the part. Drag it to where the part should
  turn or slide from, then click **Apply Pivot**. The part's bones move there
  and the object stays in place.
- **Apply Transforms** appears when an object part has unapplied rotation or
  scale. Click it. Unapplied transforms tilt the axes.
- The **X** button removes the part. It refuses while a joint, link or other
  part uses it, and names them.
- **Merge for VRChat** (two or more object parts) joins the object parts into
  one mesh with one vertex group per former object and an Armature modifier.
  Do this last. The joined parts become loose parts of that one mesh. It
  removes every vertex group named after a bone of this armature (other than
  the part's own `DEF-` bone), so merge only parts that are rigged to the
  mechanism rig alone.

You can rename a part's object: parts are tagged on their objects, so the part
finds its object again. A copy of the object (Shift+D) does not take over the
part. If a part's object is deleted, the part shows "Part '<name>' is missing"
with **Reassign** and **Delete**. Other mechanisms keep working.

- **Reassign** uses the mesh you have selected. It refuses a non-mesh, and it
  refuses an object that another object part already uses. Loose parts of one
  mesh may share that mesh.
- **Delete** removes the part (see Editing below for when it is refused).

## Joints and links, one example each

Add a joint with **Add Joint**, a link with **Add Link**. Each choice starts a
guided build. They work from the viewport tab and from the Properties editor's Scene
tab; from the Scene tab the guide uses the largest 3D Viewport on the screen.
Alternatively, activate Build Mechanism in the viewport toolbar, choose the joint
or link type in the tool header, and click its first part. That click starts the
same guide and supplies its first pick. Continue with the picks and axis choices
requested in the viewport; the Add Joint and Add Link menus remain available.

Short rules for every guided build:

- Click parts in the viewport. Clicked parts get an outline and a number.
- Where a step needs an axis, press **X**, **Y** or **Z**, or **A** to align to
  the selection. **Align to Selection** is for angled hinges. It needs the part's mesh
  to still be in Edit Mode with one edge or face selected when you press **A**,
  and the guide ignores **Tab**. So enter Edit Mode on the part's mesh and
  select one edge or face first. Stay in Edit Mode, start **Add Joint →
  Hinge**, click the part, press **A**. If nothing usable is selected the guide
  tells you and you can press another key.
- The last step previews the mechanism moving in a loop. **Enter** keeps it.
  **Esc** removes it.
- The header and status bar show a full sentence for each step. With Show
  Helpers off they show a short label.

Each row of the Joints & Links list has four icon buttons: **Test** (play
triangle), **Edit** (pencil, shows the settings), **Detach** (broken chain) and
**Delete** (X).

After the build, the selected item in the list shows only the settings its
type uses.

### Hinge

Blade Hinge, 0°…90°:

1. Add Parts from Selection with a Blade part.
2. **Add Joint → Hinge**. Click the Blade. Press **X**. Press **Enter**.
3. You get a half-circle handle, `CTRL-Blade`, and a *Blade Hinge* in the
   list. Set **Min** 0 and **Max** 90 (° for a Hinge).
4. Try it: drag the half-circle handle. It stops at 90°. **Set Min** and
   **Set Max** copy the handle's current pose into the limits.

A limit that is under a full turn must stay within −180°…180°. Limits such as
170°…190° are refused with a message. A range of a full turn or more (for
example −180°…180°) spins freely with no limit.

### Slide

Barrel Slide, 0…0.3:

1. **Add Joint → Slide**. Click the Barrel part. Press **Y**. Press **Enter**.
2. You get an arrow handle. Set **Min** 0 and **Max** 0.3 (scene units).
3. Try it: drag the arrow. The barrel slides and stops at 0.3.

### Telescope

Mast with three segments:

1. Make the base and three segment parts.
2. **Add Joint → Telescope**. Click the base. Click each segment from the base
   outwards. Press **Enter**. Press the axis key. Press **Enter** to keep it.
3. You get one arrow handle on the base. **Length** is the total travel;
   **Shares (empty = even)** splits it between the segments. To try custom
   shares, set **Length** to 1 first, then type `0.5, 0.25, 0.25`. The shares
   must add up to the Length, so the tip travels the full length. A typo (for
   example `0.5, abc`) is refused with the same plain message: the shares
   must be numbers, one per segment, that add up to the Length.
4. Try it: drag the one arrow. All three segments extend by their shares.
   **Set Max** sets Length from the handle's pose.

### Piston

Lift: cylinder on the frame, rod on the arm.

1. Give the arm a Hinge first, and set the arm to ride on the frame.
2. **Add Link → Piston**. Click the cylinder part (on the frame). Click the rod
   part (on the arm).
3. You get a Piston with no handle. Each part points at the other's attach
   point. **Stretch** (optional) stretches the rod, for springs and cables.
4. Try it: move the arm's handle. The piston follows. If nothing moves the
   Piston yet, the build works but has no preview and **Test** says so.

### Gear Link

Gear 20:40:

1. Both parts need a joint first. The driving part needs a Hinge. For Gear and
   Belt the driven part needs a Hinge; for Rack it needs a Slide.
2. **Add Link → Gear Link**. Click the driving part. Click the driven part.
3. In its settings set **Source Teeth** 20 and **Target Teeth** 40 (or type a
   **Ratio**). **Kind** is Gear, Belt or Rack. **Reverse** flips the direction.
4. Try it: turn the source. With **Kind** Gear the target turns −0.5× as far
   (+0.5× with Belt). A Gear reverses
   direction, a Belt keeps it, and a Rack turns rotation into a slide (distance
   per radian = **Ratio** × **Pinion Radius**).

How BoneCraft builds it depends on the source Hinge's range:

- Under a full turn: a Transform constraint. It follows everything that moves
  the source, Sequences included.
- A full turn or more: a driver that needs no Python. The target spins forever
  with the source. It follows handles and gears only. The Rig Validator warns
  when a Sequence or Follow would be lost.

### Follow

Blade 0–90° lifts Cover 0–40°:

1. Both parts need a Hinge or a Slide. A source Hinge needs limits under a
   full turn; a free-spinning source is refused.
2. **Add Link → Follow**. Click the leading part (Blade). Click the following
   part (Cover).
3. The ranges start as the full range of each joint. Set **Source Range**
   0…90 and **Target Range** 0…40. Past either end the target holds.
4. Try it: move the Blade handle. The Cover follows.
5. Tick **Curve** to reshape the mapping in the Graph Editor. BoneCraft never
   overwrites your curve (see Editing below).

### Sequence

Record steps to fold a weapon:

1. In **3. Sequences**, click **Add Sequence**. It makes a slider handle
   `CTRL-SEQ-<name>`.
2. Click **Move Slider to End**. The slider jumps to its end (1), and the button
   becomes Record Step followed by the next step number.
3. Pose the handles of the joints for the first step. Click Record Step 1.
   Each handle that moved becomes a step with its target value, and the
   handles go back to zero.
4. Repeat steps 2 and 3 for more steps. Each new step takes the next quarter of the
   slider by default.
5. Set **Target**, the ease (Linear, Ease In, Ease Out, Ease In Out, Snap),
   **Start** and **End** for each step. Outside its slice a step holds its end
   value. Several Sequences can stack.
6. Click **Test**: the slider plays 0 → 1 → 0.

Next to the step-recording button and **Test**, the selected Sequence has **Detach**
(broken chain) and **Delete** (X). A held Sequence (for example a step whose
curve you reshaped) shows its message and a **Restore** button. Restore
regenerates the steps from the record. Keep mine is not offered for a Sequence.

## Test

**Test** (the play button in the list, and in 3. Sequences) sweeps one
mechanism through its full range and back. It writes no keys and puts the pose
back when it ends. Press **Esc** to stop it early; the pose is restored then
too. For a Gear Link or Follow it sweeps the source. For a Piston it sweeps the
joint that moves it. Watch for parts that clash; BoneCraft does not detect
collisions.

## Forms

In **4. Controls**:

- Every joint and Sequence has one slider. It is the handle's own channel, so
  dragging the handle and using the slider are the same thing.
- **Save Form** records every handle and Sequence slider value under a name.
  Rename it in the list.
- **Go to Form** sets every control to the saved values.
- **Go and Key** does the same and also inserts keys on the current frame.
- The **X** next to the list removes a form.

## What BoneCraft builds

For each part:

| Bone | Job | Visible |
|---|---|---|
| `CTRL-<part>` | The handle. Its value is the panel slider. Only Hinge, Slide and Telescope make one. | Yes |
| `MCH-<part>` | Adds the handle and every link, then applies the limits. | Hidden |
| `DEF-<part>` | Copies `MCH-<part>`. The mesh is bound to it. Engines receive this bone. | Hidden |

The bones sit in the collections `Mechanism Controls`, `Mechanism MCH` and
`Mechanism DEF`. A part with no joint has only `MCH-` and `DEF-` bones. A
Telescope's handle is `CTRL-<telescope name>`. A Sequence's is
`CTRL-SEQ-<name>`. A Piston adds `MCH-<part>-aim` and `MCH-<part>-target` bones
for each of its two parts.

The constraints on `MCH-<part>` always come in the same order: Copy Transforms
from the handle, then each link's contribution, then the joint's Limit Rotation
or Limit Location. `DEF-<part>` has one Copy Transforms from `MCH-<part>`.

Everything BoneCraft builds is tagged with its record: constraint names start
with `BC·<id>·<role>`, and bones carry the properties `bc_mech_id` and
`bc_mech_role`. BoneCraft finds its bones by tag, not by name, so you can
rename any bone. A rebuild finds it again and makes no duplicate.

With Show Helpers on, each joint and link has a **How this works** note. It
lists the constraints by name, says what each does, and has a **Select**
button (an arrow icon) to inspect the bone.

Your own constraints, drivers and bones are never touched. A constraint you add
to an MCH bone stays below BoneCraft's after a rebuild.

## Editing and hand edits

- **Value edits** (limits, ratio, ranges, timing, ease, handle look) update the
  existing constraints in place. There is no rebuild.
- **Structural edits** (a Gear Link's **Kind**, a Follow's **Curve**, a
  Piston's **Stretch**) replace that mechanism's constraints and rebuild only
  that mechanism.
- **Changed by hand.** If you edit a BoneCraft constraint (for example a
  Limit), the mechanism's message ends with "(changed by hand)". BoneCraft never overwrites
  it silently. Choose:
  - **Keep mine** copies your values into the record. It refuses what it cannot
    read back, and says to use Restore or Detach.
  - **Restore** throws your edit away and rebuilds from the record.
- A held mechanism also holds every mechanism that uses its bones, until you
  settle it.
- A reshaped curve is the same. If you reshape a Follow's curve (**Curve**
  ticked) in the Graph Editor and then change a value that would replace it,
  such as its Target Range, the Follow's message ends with "(changed by hand)". **Keep mine**
  keeps your curve. **Restore** regenerates it.
- A held Sequence shows its message and **Restore** in **3. Sequences**, with
  **Detach** and **Delete** next to it. Keep mine is not offered for Sequences.
- **Detach** (broken-chain button) deletes the record and the tags but keeps the bones and
  constraints as your own hand-made rig. Detach and Delete both refuse a record
  that another record uses, and name the users.
- **Delete** (X button) removes the record and everything BoneCraft built for it.
- A link loop is refused before anything is built, and the loop is named, for
  example "Blade Hinge → Cover Follow → Blade Hinge would loop."

The Rig Validator and the Task Board report link loops, missing parts, DEF
bones moved from outside their mechanism, drivers that need Python, and Gear
Links that lose a Sequence or Follow. The validator's naming check accepts
hyphens (`CTRL-`, `MCH-`, `DEF-`), and its drivers check warns only on
expressions that need Python, so a clean Mechanisms rig shows no validation
errors — only the one warning about the `root` bone described in Limits of this version.

## Show Helpers

**Show Helpers** is one preference for all of BoneCraft: **Preferences →
Add-ons → BoneCraft → Helpers**. Off hides the teaching text everywhere: the what / when
lines, the **How this works** notes and the full guided-step sentences (those
become short labels). The steps themselves, the lists, Test, warnings and
Blender's hover tooltips always stay.

The VRChat **Compact Mode** button is its shortcut: Compact Mode on means Show
Helpers off.

## Limits of this version

- Click Turn, Track and Linkage mechanisms come later.
- Engine export of baked mechanism motion comes later, after the desktop hand
  check. Until then the `DEF-` bones are the bones to export.
- BoneCraft does not detect collisions. Use Test and look.
- A free-spinning Gear Link follows handles and gears only.
- The rig's `root` bone is in no bone collection, so the Rig Validator's
  collections check warns about it and the Task Board shows "Rig validation
  warnings (1)".

Next: [VRChat Tools](08-vrchat.md)
