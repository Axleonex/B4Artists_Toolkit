# Tutorial: Crescent Rose with Mechanisms

[← Contents](index.md)

<!-- Print layout is scoped to this illustrated chapter; the shared renderer is unchanged. -->
<style>
@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--what-you-built"] { break-before: page; break-after: avoid; }
}
</style>

## What you will build

Crescent Rose is the scythe that is also a rifle. In this tutorial you rig a model of it with Mechanisms, so that one slider turns the scythe into the rifle and a second slider folds the rifle into its compact form. On the way you use every joint and link Mechanisms has today except Gear Link: eight Hinges, three Slides, a Telescope, a Piston and a Follow, then two Sequences and three Forms.

The forms are teaching poses for this fan-made model. Mechanisms does not detect collisions or make a physically engineered replica: inspect clearances when adapting the rig.

The result is the file `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Open it any time to compare.

## Before you start

- The files: `examples/crescent-rose/CrescentRose_parts.blend` is the model already split into 15 part objects; start the tutorial from it. `CrescentRose_Mechanisms.blend` is the finished rig.
- Time: allow a separate session for FBX preparation and another for the Mechanisms lesson; these are substantial exercises, not timed speed runs. Save checkpoints between stages.
- Words: read "What Mechanisms does" in [Mechanisms](07-mechanisms.md) first: it defines part, joint, link, handle, Sequence and Form.
- Language: the screenshots show Bforartists in English with BoneCraft's panels in English. BoneCraft's own panels follow the **Language** setting in its preferences; the rest of Bforartists follows Bforartists' interface language. If your Bforartists is in a language BoneCraft does not translate, its panels stay English and this edition still applies.
- Starting route: use P1-P8 below for the original FBX, or skip to Step 1 with the prepared file. Both routes use the same 15 parts.
- Version: instructions and genuine interface captures were checked with BoneCraft `9.1.2` in Bforartists `5.2.0`, using its default keymap.

Red numbered marks identify what to click, type into, or inspect. Follow each image's numbered action key in order (1, then 2, then 3). Numbers restart in each image. A boxed result is a check; a circled part or button is the interaction target.

## Prepare the original FBX (P1-P8)

Skip this section if you are using `CrescentRose_parts.blend`. Work in a new file and keep the source FBX and its `CrescentRoseTextures` folder together. These steps were replayed in Bforartists 5.2.0 with the default keymap. Use the visible mode menu: Tab can toggle overlays in this keymap rather than enter Edit Mode.

### P1 - Import the FBX

Start with an empty scene. Choose **File > Import > FBX (.fbx) (Legacy)**, select `CrescentRose.fbx`, and leave import Scale at `1.00`. Use the Legacy importer for this recipe. The Outliner contains a root and three material meshes: `Black01`, `Blades01`, and `Red01`. Press Numpad 3 for Right view and Home to frame them.

![P1: Legacy FBX import options with Scale 1.00](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select CrescentRose.fbx. 2: Keep Scale at 1.00. 3: Click Import FBX; use the Legacy importer.*

### P2 - Preserve placement and set the size

In Object Mode select the three meshes. Use **Object > Parent > Clear and Keep Transformation**. Remove the now-unused root from your working scene. With all three meshes selected, use **Object > Apply > Rotation & Scale**. The imported weapon is approximately `0.32 m` tall. Scale all three together by `6.25` (in this Bforartists keymap, Ctrl+R starts Scale; type 6.25 and confirm), then apply Rotation & Scale again. The complete weapon is now approximately `1.997 m` tall. Do this once; the prepared shortcut is already scaled.

![P2: clear parenting while preserving placement](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Press F3 and search Clear Parent Keep Transform. 2: Choose Clear and Keep Transformation. Repeat for all three meshes before removing the root.*

![P2: applied rotation and scale on the imported weapon](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1: After scaling the three meshes together by 6.25, apply Rotation & Scale; Rotation must read 0. 2: Scale must read 1 on all axes.*

An individual object's Dimensions field measures only that material mesh. Check the combined bottom-to-top extent when measuring the weapon. All three objects must show rotation zero and scale 1 before separation.

### P3 - Connect the materials

Switch to the Shading workspace and Material Preview. For each of the three materials, load its matching `BaseColor`, `Metallic`, `Roughness`, and `Normal` images from `CrescentRoseTextures`. Connect Image Texture Color to the matching Principled BSDF input. BaseColor uses **sRGB**; Metallic, Roughness, and Normal use `Non-Color`. For Normal, insert a **Normal Map** node, keep `Tangent Space`, connect image Color to its Color, and connect its Normal output to Principled BSDF Normal. Keep the existing UVs.

![P3: four texture maps and Tangent Space Normal Map connected for the black material](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Connect BaseColor Color to BSDF Base Color. 2: Keep BaseColor on sRGB. 3: Set all data maps to Non-Color. 4: Connect Normal image > Normal Map > BSDF Normal, using Tangent Space.*

![P3: all three materials in Material Preview](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Check the blade material. 2: Check the red/black body materials in Material Preview; no pink missing textures.*

Repeat the same connections for the blade and red materials. Check each image's color space after choosing it; the setting belongs to the image. The weapon should be red, black and metallic, with no pink missing textures.

### P4 - Separate loose pieces

Select all three material meshes, choose **Edit Mode** from the viewport mode menu, select all geometry, then use **Mesh > Separate > By Loose Parts**. Return to Object Mode. There are **37** mesh objects at this point. Their generated numeric suffixes can vary, so identify them by position and shape.

![P4: enter Edit Mode and choose By Loose Parts](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Switch to Edit Mode and select all geometry. 2: Press F3, search Separate Loose, and choose By Loose Parts.*

![P4: the 37 loose pieces after separation](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Check the object total is 37 after separation. 2: Use the Outliner to select pieces by shape and location; suffixes can vary.*

### P5 - Join the 15 moving groups

Select the pieces that must move together and use **Object > Join** (Ctrl+J). Rename the resulting object in the Outliner. For paired pieces on opposite sides, orbit the view to select both; check the selection before joining. Work from the blade tip inward, then the receiver and pole. The table lists every source island; a material name describes its appearance, not its final object name.

| Final object | Pieces to combine | Mesh vertices after joining |
|---|---|---:|
| `BladeTip` | Black tip-joint knob and metal tip spike | 252 |
| `Blade2` | Two metal second-segment plates and two red covers | 1000 |
| `Blade1` | Two metal first-segment plates nearest the head | 512 |
| `HeadMount` | Black rear block, top cap and core; two red inner plates and two thin top covers | 1395 |
| `PlateL` | One red outer head plate on negative X | 676 |
| `PlateR` | One red outer head plate on positive X | 676 |
| `RearSpike` | Two metal spike blades, two red pivot caps and two red mount plates | 1194 |
| `Receiver` | Black body and small knob, metal ring above the bolt, long red housing | 2609 |
| `Grip` | Red grip block below the receiver | 194 |
| `Magazine` | Black tube beneath the body | 96 |
| `Bolt` | Red bolt cylinder and its two knob pieces | 362 |
| `Pole` | Metal lower shaft and red collar | 148 |
| `ButtSpike` | Metal bottom spike | 110 |
| `StrutBase` | Thin red rod between receiver and head | 34 |
| `StrutRod` | Black notched sleeve around that rod | 108 |

There must be **15 meshes and 9,366 vertices** in total. Do not merge the outer plates into Blade1, or the two strut pieces together. The strut already has two separate pieces; no bisect is needed. Step 2 repeats the finished part names and their later parenting.

![P5: all 15 moving groups named in the Outliner](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Rename every joined group in the Outliner to match the 15 names in the table.*

![P5: the two Blade1 source plates selected before joining](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select the two metal Blade1 plates on opposite sides. 2: Verify both objects are selected, then use Join and rename the result Blade1.*

![P5: Object menu Join command](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Open Object after selecting only the pieces of one group. 2: Choose Join (Ctrl+J). This menu crop identifies the command; use the two-piece selection shown above.*

### P6 - Centre the origins

In Object Mode select all 15 meshes. Choose **Object > Set Origin > Origin to Geometry** and set the operation's Center option to `Bounds Center`. Check rotation zero and scale 1. The objects still have no parents and there is no armature. These are convenient preparation origins; Step 6 later moves the mechanism pivots to their actual joints.

![P6: Object > Set Origin > Origin to Geometry](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Open Object. 2: Hover Set Origin. 3: Choose Origin to Geometry; set Bounds Center in the operation options.*

![P6: the centred Blade1 origin with applied transforms](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: The orange origin is now centred on the mesh. 2: Confirm Rotation 0. 3: Confirm Scale 1. Mechanism pivots are moved later.*

### P7 - Resize and pack the textures

In the Image Editor select each of the **12 used maps** (four per material). Choose **Image > Resize**, set width and height to **1024**, confirm, then choose **Image > Pack**. Repeat for every used map. Packing the resized image preserves those pixels inside the blend; do not overwrite the source JPEGs. Check Material Preview afterward.

![P7: Image menu packing a resized 1024 by 1024 texture](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Choose Image > Resize and enter 1024 for width and height. 2: Check the resulting 1024 x 1024 dimensions. 3: Choose Pack. Repeat for all 12 used maps.*

### P8 - Save and reopen the prepared file

Save your working copy as `CrescentRose_parts.blend`. Reopen it and check the named 15 meshes, their transforms, and the red/black materials. All 12 maps should remain available without relying on the original texture directory. Use Right view and Home again, then continue with Step 1.

![P8: the prepared file reopened with the textured weapon intact](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Open File for Save As, then Open to reload your working copy. 2: Confirm the 15 named meshes survived. 3: Check the materials; the title bar identifies the reopened file.*

## A. Open the file

### Step 1 — Open the parts file

Open `examples/crescent-rose/CrescentRose_parts.blend`. Switch the viewport to Material Preview shading, and press Numpad 3 for the Right view: the blade points left, the butt spike down. Press Home to frame the weapon.

![Step 1: the parts file in the Right view](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click Material Preview. 2: Press Numpad 3 until the view says Right Orthographic; press Home to frame the weapon.*

**What you should be seeing:** The scythe in red and black, about 2 m tall, with nothing selected.

### Step 2 — Meet the parts

The Outliner lists the 15 objects. Each one is a piece that moves as one block:

| Object | What it is | Rides on |
|---|---|---|
| `Receiver` | The rifle body with the scope, trigger and sight | the rig |
| `Grip` | The grip under the receiver | `Receiver` |
| `Magazine` | The cylinder magazine | `Receiver` |
| `Bolt` | The bolt | `Receiver` |
| `Pole` | The lower shaft and its collar | `Receiver` |
| `ButtSpike` | The spike at the bottom | `Pole` |
| `HeadMount` | The head block the blade hangs from | `Receiver` |
| `Blade1` | The first blade segment, nearest the head | `HeadMount` |
| `Blade2` | The second segment | `Blade1` |
| `BladeTip` | The tip | `Blade2` |
| `RearSpike` | The spike on the back of the head | `HeadMount` |
| `PlateL`, `PlateR` | The outer side plates of the head | `HeadMount` |
| `StrutBase` | The thin rod between the receiver and the head | `Receiver` |
| `StrutRod` | The notched sleeve around that rod | `HeadMount` |

![Step 2: the 15 part objects in the Outliner](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Identify the three blade segments. 2: Match the body, head and pole names to the table. 3: Keep StrutBase and StrutRod as separate objects.*

For the original FBX, follow P1-P8 above. The supplied prepared file was made through those interface actions; the repository preparation script provides a reference grouping table.

### Step 3 — Find Mechanisms

Open the BoneCraft tab on the left Tool Shelf (if hidden, press T over the viewport and choose Tools from the Region Toggle menu) and expand **Mechanisms**. Widen the shelf by dragging its right edge until the panel text has room. As an alternative, the same Mechanisms section is available in **Properties > Scene** when Scene Properties is set to Show in BoneCraft preferences. The screenshots use the Tool Shelf. With a mesh active and no rig yet, find **Add Parts from Selection** at the top of the section. Select all the parts in Step 4 before clicking it; the numbered subsections become usable after parts are added.

![Step 3: the Mechanisms section of the BoneCraft tab](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click the BoneCraft tab. 2: Expand Mechanisms. 3: Find Add Parts from Selection; select the meshes before using it.*

## B. Parts

### Step 4 — Add Parts from Selection

Hover the viewport and press A to select all 15 objects. Click **Add Parts from Selection**.

![Step 4: all parts selected, Add Parts from Selection](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Hover the viewport and press A to select the 15 meshes. 2: Click Add Parts from Selection.*

**What you should be seeing:** A new armature, "Mechanism Rig", appears in the Outliner with the parts under it. The mesh objects remain selected after the operation. **1. Parts** lists the 15 parts, and the BoneCraft tab now starts with the rig's Overview, which you can collapse.

### Step 5 — Rides on

A part rides on the part it is attached to. Click `Blade1` in the **1. Parts** list, open the "Rides on" menu under the list and choose `HeadMount`. Do the same for every part in the table of step 2. `Receiver` keeps "the rig".

![Step 5: Blade1 rides on HeadMount](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Blade1 in the Parts list. 2: Open Rides on and choose HeadMount. Repeat using the parent table.*

### Step 6 — Pivots

A hinge turns around its part's pivot. The blade segments, the head and the grip must turn at their joints, not at their centres. With `Blade1` selected in the list, click **Edit Pivot**, select the marker, press Ctrl+W for Move in Bforartists, click where the segment meets the head, and click **Apply Pivot**. Work in the orthographic side view so the sideways pivot position stays unchanged. Repeat for `Blade2` (where it meets `Blade1`), `BladeTip` (where it meets `Blade2`), `HeadMount` (its lowest point, where the strut meets it), `Grip` (its top edge), `RearSpike` (where it meets the head), `PlateL` and `PlateR` (the centre of the round bolt where Blade1 meets the head), `StrutBase` (its bottom) and `StrutRod` (its top). The screenshot's marker position is a guide; a few millimetres make no visible difference.

![Step 6: select the part and click Edit Pivot](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Select Blade1 in Parts. 2: Click Edit Pivot; then move and apply the marker as shown next.*

![Step 6: Blade1's pivot marker at the joint, Apply Pivot](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Move the pivot marker to the blade joint with Ctrl+W. 2: Click Apply Pivot to keep that location.*

## C. The head

### Step 7 — Add Joint → Hinge

Open **Add Joint → Hinge**. A guided build starts: the header and the status bar tell you what to do at each step.

![Step 7: the Add Joint menu, Hinge](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Open Add Joint. 2: Click Hinge. The guided build now waits for a part.*

### Step 8 — Click the head

The header says "click the part that turns". In the Right view the outer plate sits in front of the head, so click the head's rear block, behind the plates (the circle). If the header names `PlateR`, press Esc, restart **Add Joint > Hinge**, and click further back. If you need to hide an obstruction, do it before starting the guide. The guide consumes ordinary keyboard shortcuts while active.

![Step 8: click the head's rear block](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click the rear black block of HeadMount, behind the red outer plate. Check the guide names HeadMount.*

### Step 9 — Press X, then Enter

The header now asks for the axis. Press X: the head turns around the sideways axis, and the guide previews the motion in a loop. Press Enter to keep it.

![Step 9: the axis step](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Follow the axis prompt: press X, then Enter. 2: Watch the head rotate around its pivot before confirming.*

**What you should be seeing:** `HeadMount Hinge` in the **2. Joints & Links** list, and its slider in **4. Controls**. Use these sliders in Object Mode. To use the viewport bone handles, select the armature and switch to Pose Mode.

### Step 10 — Limits

With `HeadMount Hinge` selected in the list, set **Min** to 0 and **Max** to 120. Positive values turn the head down and back. Keep the 120-degree travel limit; the Rifle sequence will use a 90-degree target together with the blade hinges.

![Step 10: Min 0, Max 120](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select HeadMount Hinge. 2: Set Min to 0. 3: Set Max to 120; double-click the number, type, and press Enter.*

### Step 11 — Test

Click the row's play button. The head sweeps to 120° and back, and the pose is restored.

![Step 11: Test on the hinge's row](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click the small play triangle on the HeadMount Hinge row. Watch the sweep and return.*

## D. The blade chain

### Step 12 — Three more hinges

Repeat steps 7 to 10 for `Blade1`, `Blade2` and `BladeTip`: **Add Joint → Hinge**, click the segment, X, Enter, then **Max** 120. Each segment rides on the one before it, so the three hinges form a chain.

![Step 12: the three blade-segment hinges and the separate head hinge in the list](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Create and select each blade hinge: Blade1, Blade2, BladeTip. 2: Set Max to 120 for each; use X as its axis.*

### Step 13 — Try the chain

Collapse **2. Joints & Links** to make room and expand **4. Controls**. In Object Mode, set `Blade1 Hinge`, `Blade2 Hinge` and `BladeTip Hinge` to 60 degrees, one at a time. Double-click a numeric field, press Ctrl+A, type the value and press Enter. The later segments move with the earlier ones and the chain curls. Set all three values back to 0 before continuing.

![Step 13: the three blade hinges at 60 degrees in Controls](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Enter 60 in each of the three blade sliders. 2: Check the chain curls together. Return all three sliders to 0.*

## E. Plates and strut

### Step 14 — Hinges on the plates

Add a Hinge on `PlateR` the same way, **Max** 30. `PlateL` is hidden behind the head in the Right view: press Ctrl+Numpad 3 for the Left view, add its Hinge, and come back with Numpad 3.

![Step 14: PlateL Hinge and PlateR Hinge](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Make both PlateR and PlateL hinges; use the opposite side view to reach PlateL. 2: Set each Max to 30.*

### Step 15 — Add Link → Follow

One handle should move both plates. Before starting the guide, press Numpad 1 for Front view, select `Blade2` and use F3 > Frame Selected to bring the head close. The two outer plates appear at the left and right edges. Open **Add Link > Follow**, click `PlateL` at the left edge (the leading part), then `PlateR` at the right edge (the following part), and press Enter.

![Step 15: Front view exposes both outer plates for the Follow picks](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click PlateL first, the leading part. 2: Click PlateR second, the following part. Press Enter.*

### Step 16 — Ranges

With the new Follow selected, verify the automatically populated **Source Range** 0…30 and **Target Range** 0…30. Rename it `PlateR Follow` in **Name**.

![Step 16: Source Range and Target Range](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Name the link PlateR Follow. 2: Check Source Range is 0 to 30. 3: Check Target Range is 0 to 30.*

### Step 17 — Add Link → Piston

The strut must keep pointing between the receiver and the head while the head folds. Before starting the guide, press Numpad 3 for Right view, select `StrutRod` in the Outliner and use F3 > Frame Selected. Open **Add Link > Piston**. Set this close view first; navigation shortcuts are consumed while the guide is active.

![Step 17: the Add Link menu, Piston](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Open Add Link after framing StrutRod. 2: Choose Piston; the guide asks for the cylinder first.*

### Step 18 — The cylinder and the rod

Click the cylinder part first: `StrutBase`, the thin rod, which shows in the sleeve's notches. Then click the rod part: `StrutRod`, the sleeve. Use the close view to click the exposed red rod first, then the black sleeve. The guide's cylinder/rod roles describe the link ends; this model's object names describe its source pieces. Press Enter to accept, rename the link `Head Strut`, and leave **Stretch** off.

**What you should be seeing:** Change `HeadMount Hinge` in Controls: the strut follows, each part aimed at the other. Restore the value to zero.

![Step 18: the piston guide, exposed red cylinder then black sleeve](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1: Click the exposed red StrutBase first. 2: Click the black StrutRod sleeve second. Press Enter.*

![Step 18: Head Strut settings with Stretch off](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1: Rename the link Head Strut. 2: Leave Stretch unchecked; then test HeadMount Hinge and restore 0.*

## F. The rifle

### Step 19 — Grip and rear-spike hinges

**Add Joint → Hinge** on `Grip`, X, Enter, **Min** 0, **Max** 90. Repeat on `RearSpike`, X, Enter, **Min** 0, **Max** 90. Then select `RearSpike Hinge` in the list and change its `Axis X to -1`, leaving Y and Z at 0. This reverses its fold direction so the rear spike turns back toward the folded head in Compact; keep Grip on positive X. Confirm that both `Grip Hinge` and `RearSpike Hinge` appear in the joint list. These two controls fold the grip and rear spike for the compact form in Step 25.

![Step 19: Grip Hinge, Max 90](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1: Select Grip Hinge. 2: Keep Axis X at 1, Y and Z at 0. 3: Set Max to 90; keep Min at 0.*

![Step 19: RearSpike Hinge with Axis X -1 and Max 90](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select RearSpike Hinge. 2: Set Axis X to -1. 3: Set Max to 90; keep Min at 0.*

### Step 20 — Magazine and Bolt Slides

**Add Joint → Slide** on `Magazine`, press Z, Enter, **Max** 0.04. Then a Slide on `Bolt`, Z, Enter, **Max** 0.06. Slides measure in scene units: 0.06 is 6 cm.

![Step 20: Magazine Slide, Z axis and Max 0.04](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Magazine Slide after Add Joint > Slide. 2: Use the Z axis (Z = 1, X = Y = 0). 3: Set Max to 0.04; keep Min at 0.*

![Step 20: Bolt Slide, Z axis and Max 0.06](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Bolt Slide after Add Joint > Slide. 2: Use the Z axis (Z = 1, X = Y = 0). 3: Set Max to 0.06; keep Min at 0.*

### Step 21 — Pole Slide

A Slide on `Pole`, Z, Enter, **Max** 0.6. Positive values move the pole up into the receiver. Set `Pole Slide` to 0.6 in **4. Controls** to see the shaft retract, then restore it to zero.

![Step 21: Pole Slide settings, Z axis and Max 0.6](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Pole Slide after Add Joint > Slide. 2: Use the Z axis (Z = 1, X = Y = 0). 3: Set Max to 0.6; keep Min at 0.*

### Step 22 — Pole Telescope

**Add Joint → Telescope**. Click `Pole` (the base), then `ButtSpike` (the segment), press Enter, press Z, press Enter. Set **Length** 0.2. Its separate control moves the spike up to 20 cm along positive Z, into the pole in this model. Test it and restore zero.

![Step 22: guided Telescope picks, Pole as base and ButtSpike as segment](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click Pole as the base. 2: Click ButtSpike as its segment. Press Enter, then Z, then Enter.*

![Step 22: Pole Telescope settings, Z axis and Length 0.2](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Pole Telescope. 2: Check Z is its axis. 3: Enter Length 0.2; test the control and restore zero.*

## G. Sequences

### Step 23 — Add Sequence

In **3. Sequences**, click **Add Sequence**, and double-click its name in the list to rename it `Scythe to Rifle`. Press Enter.

![Step 23: Add Sequence](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click Add Sequence. 2: Double-click the new name and type Scythe to Rifle. Press Enter.*

### Step 24 — Record a motion group

Click **Move Slider to End**: the sequence's slider jumps to `100%` and the button becomes Record Step 1. Now pose the first motion group with the sliders in **4. Controls**: `BladeTip Hinge` 70 and `Blade2 Hinge` 120. Click Record Step 1. This stores two target entries, one for each moved handle, and resets those two joint sliders to zero.

![Step 24: Move Slider to End before posing the first group](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click Move Slider to End once. The button changes to Record Step 1.*

![Step 24: Record Step 1 with Blade2 at 120 and BladeTip at 70 degrees](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Enter Blade2 = 120 and BladeTip = 70. 2: Click Record Step 1; both targets are stored and the joint sliders reset.*

*Remaining motion groups.* Recording remains armed after each capture. Pose the next group and click the displayed Record Step button; do not arm it again:

| Motion group | Pose these handles | Record button after the preceding groups |
|---|---|---|
| 2 | `Blade1 Hinge` 10 and `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

The button number is the number of stored target entries plus one. Recording two handles advances it by two; it does not count recording clicks. The four motion groups above therefore produce six target entries. If you change which handles move, use the number actually displayed.

### Step 25 — The steps

Each recorded target has its own entry under the sequence, showing its **Target**, its ease and its **Start** and **End** on the slider. Give both entries in each motion group the same Start and End: the blade folds first (0…0.25), the plates and the first segment next (0.25…0.5), the head third (0.5…0.8) and the pole last (0.8…1). Before its slice a step stays at its starting value; after its slice it holds its end value. The Start/End fields use 0-1, while the Controls sliders show 0-100%.

Keep each entry on `Ease In Out`. Then add a second sequence, `Rifle to Compact`: first record `Grip Hinge` 90 and `RearSpike Hinge` 90 (two entries, both 0…0.5); then record `Magazine Slide` 0.04 and `Bolt Slide` 0.06 (two entries, both 0.5…1). Its recording button changes from Record Step 1 to Record Step 3 for the second group. After each sequence is complete, click **Cancel** in the capture banner. This ends recording, retains the stored entries, and returns that sequence slider to zero. An overlap warning while armed describes the proposed next recording interval; do not add an extra empty group.

![Step 25: all six targets and time slices in Scythe to Rifle](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Target is the recorded joint value. 2: Choose Ease In Out. 3: Enter Start. 4: Enter End. Repeat these fields for all six entries using the shown values.*

![Step 25: all four targets and time slices in Rifle to Compact](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Grip and RearSpike use Target 90, Start 0, End 0.5. 2: Magazine and Bolt use 0.04 / 0.06, Start 0.5, End 1. Keep Ease In Out.*

![Step 25: end recording with Cancel in the capture banner](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: After finishing a sequence, click Cancel in this capture banner to end recording. This keeps the entries and returns the sequence to zero.*

### Step 26 — Test the sequence

Click **Test** next to the step-recording button. The slider sweeps from 0% to 100% to 0%, then restores its value from before the test. Test `Scythe to Rifle` from Scythe; test `Rifle to Compact` with the first sequence at 100%. Return both to 0% afterward.

![Step 26: the sequence Test button during the fold](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Click Test beside the recording button. 2: Watch the fold and return. Test Compact with Scythe to Rifle at 100%.*

**What you should be seeing:** The blade curls, the plates close, the head folds down along the receiver, and the pole slides up. Then everything comes back.

## H. Forms

### Step 27 — Save Form

In **4. Controls**, with every slider at 0, click **Save Form**, then double-click the new list entry to name it `Scythe`. Set `Scythe to Rifle` to `100%` and save/name `Rifle`. Set `Rifle to Compact` to `100%` as well and save/name `Compact`. Leave all individual joint sliders at zero: the sequences provide their motion. Setting the selected sequence to its end can arm recording again; saving a Form does not record another step. Choosing `Scythe` and **Go to Form** returns both sequences to zero and clears the armed state. Going to Rifle or Compact can arm recording again because the selected sequence is at 100%; do not click Record Step unless you intend to add another target.

![Step 27: Save Form with every slider at 0](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Start with both sequences and every joint at 0. 2: Click Save Form. 3: Double-click the new list entry and name it Scythe; repeat for Rifle and Compact.*

### Step 28 — Go to Form

Click a form in the list and click **Go to Form**. **Go and Key** does the same and keys every control on the current frame, which is how you animate the transformation.

![Step 28: Rifle selected, Go to Form](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select the saved form. 2: Click Go to Form. Go and Key also inserts animation keys.*

### Step 29 — The rifle

![Step 29: the Rifle form](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Rifle. 2: Click Go to Form. 3: Check the sequence percentages against the pictured pose.*

### Step 30 — Compact

![Step 30: the Compact form](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Select Compact. 2: Click Go to Form. 3: Check the sequence percentages against the pictured pose.*

Go back to `Scythe` and save the file.

## What you built

| Record | Bones | What it does |
|---|---|---|
| 15 parts | `MCH-<part>` and `DEF-<part>` | The mesh of each part is parented to its `DEF-` bone |
| 8 Hinges, 3 Slides, 1 Telescope | `CTRL-<part>` | The handles; their values are the sliders in **4. Controls** |
| 1 Piston | `MCH-<part>-aim` and `MCH-<part>-target` | Keep the strut's two parts aimed at each other |
| 1 Follow | none | `PlateR` turns with `PlateL` |
| 2 Sequences | `CTRL-SEQ-<name>` | One slider each |
| 3 Forms | none | Saved slider values |

The refreshed example passed the Rig Validator with no reported issues. It also passed reload checks with Auto Run Python Scripts off, including every individual control and all three Forms.

## Try next

- Tick **Curve** on `PlateR Follow` and reshape the mapping in the Graph Editor.
- Save a fourth form, `Carry`, with the blade folded but the head up.
- Key the forms over frames with **Go and Key**, then export the `DEF-` bones (see [VRChat Tools](08-vrchat.md)).

## Gear Link

Crescent Rose has no geared pair, so this rig has no Gear Link. A Gear Link turns one Hinge when another turns, by a tooth ratio: a crank and a wheel, or a rack that turns rotation into a slide. See [Gear Link](07-mechanisms.md#gear-link).

## Credits

Crescent Rose model by amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; split into parts, scaled and rigged for this tutorial. Crescent Rose is a design of Rooster Teeth Productions; this is a fan-made tutorial asset.

[← Contents](index.md)
