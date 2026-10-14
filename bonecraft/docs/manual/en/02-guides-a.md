# Guides 1–7

[← Contents](index.md)

## Guide 1: Get Your First Avatar Into VRChat

For a practice mesh before using your own avatar, follow the [illustrated mannequin workshop](06-rig-builder.md#illustrated-mannequin-workshop): Simple Human, a rigless mannequin, Auto-Rig, then IK/FK.

> **Time:** About 45–60 minutes for a complete first run
> **Result:** A rigged, VRChat-ready avatar exported for the VRChat SDK

**Before you begin — check these:**
- [ ] Your 3D model is imported into Bforartists (File > Import, choose your format)
- [ ] The model is in a T-pose (arms out to the sides, body upright) — or close to it
- [ ] The model has no obvious broken geometry (no random floating triangles)
- [ ] You can see your model in the 3D viewport as a solid grey shape

---

### Step 1 — Open the Rig Builder

Open the **Rig Builder** tab on the left Tool Shelf (press **T** in the 3D Viewport). The same Rig Builder is in the **Properties** editor's **Scene** tab while Preferences → Tabs → Scene Properties → Show is on. It has three parts: the **Auto-Rig Wizard**, Quick Rig (ready-made armatures) and **Mannequin**.

Expand **Auto-Rig Wizard** and click **Start Auto-Rig**.

You can also start the wizard from the 3D Viewport's Add → Armature → Auto-Rig Wizard menu, then continue in Rig Builder.

---

### Step 2 — Select Your Mesh

The wizard lists the meshes in the scene. Click your avatar's mesh in that list, then click **Next**.

**What you should be seeing:** A line "Selected:" with your mesh's name, then the rig type step.

---

### Step 3 — Choose the Rig Type

Click **Body + Face** for an avatar whose face you want to animate (blinks, expressions, lip sync), or **Body Only** for a body without facial controls. Under Generation Options, **Kinematics** sets IK/FK, IK only or FK only. Click **Next**.

---

### Step 4 — Place Body Markers

This is the most important step. Markers are dots that show BoneCraft where each major joint is: the pelvis, the spine, the neck and head, the shoulders, arms, hands, legs and feet. BoneCraft works out the bones from them.

**The quick way:** in the Smart Detection box, click **Detect Markers**. BoneCraft traces the limbs in your mesh and places every marker, each with a confidence. Click **Accept High** to keep the sure ones, and **Reset Low** to clear the doubtful ones so you can place them yourself. **Guess Markers from Mesh** is a simpler guess from the mesh's proportions.

**With the viewport tool:** for placing several markers, activate Place Rig Markers in the viewport toolbar in Object Mode. The tool header names the next marker and has axis locks and a mirror switch. Click the mesh to place and confirm that marker; the tool moves on to the next unconfirmed marker. When the step is done, click **Next** in the wizard.

**One marker at a time:** each marker has a row of icon buttons. Hover a button to read its tooltip.

1. Click **Place Marker** (the arrow icon) on the marker's row, then click the right spot on your avatar.
2. Click **Confirm Marker** (the check mark) when it sits correctly. **Reset Marker** (the circular arrow) clears a placed marker so you can place it again.

**Symmetry:** **Toggle Symmetry** (the first icon on a left or right marker's row) places the other side's marker whenever you place this one. **Mirror L to R** and **Mirror R to L** copy every confirmed marker to the other side.

When every marker is placed, click **Confirm All Placed**, then **Next**.

---

### Step 5 — Place Finger Markers

Under Finger Detail, choose how many fingers to build: "5 — Full Human Hand" for a standard hand, or fewer (down to "0 — No Fingers"). Click **Guess Finger Markers**. BoneCraft finds each finger from the shape of the hand and traces it from knuckle to fingertip. Adjust any marker that is off, then click **Next**.

---

### Step 6 — Place Face Markers (Body + Face only)

Click **Guess Face Markers**, then adjust the eyes, lids, brows, mouth corners and jaw as needed. Eye markers stay where you put them. Click **Next**.

---

### Step 7 — Review and Generate

The review step lists any warnings and the generation options. Click **Generate Rig**.

**What you should be seeing:** A skeleton (orange bones) inside your avatar, with IK/FK limbs, finger bones and, for a Body + Face rig, a face rig, and your avatar's skin attached to it so it deforms when the bones move. The last step offers **Build Control Rig** for the review options Generate Rig does not apply, and **Close Wizard**; [Rig Builder](06-rig-builder.md) describes both.

> **Skin weights** = numbers that decide which bones move which parts of your avatar's mesh. BoneCraft sets them automatically; you can refine them with the Weight Tools (see [Rig Tools](05-rig-tools.md)).

---

### Step 8 — Map to VRChat's Humanoid Bones

Open the **CATS** tab on the right sidebar (press **N**), expand **Avatar Tools** and then **Set Up Humanoid Bones**. Click **Auto-Map All**: BoneCraft connects your bones to the body slots VRChat uses to move an avatar with you. Click **Normalize Names** to give the mapped bones the names VRChat expects, then **Validate**.

**What you should be seeing:** The required slots (Hips, Spine, Head, LeftUpperArm and so on) each show a bone. Guide 5 explains the slots.

---

### Step 9 — Export for VRChat

In the **CATS** tab, expand **Avatar Tools** → **Export to VRChat**. Set the **Folder** and the **Avatar** name, then click **Export to VRChat (Unity)**.

**What you should be seeing:** The exported avatar in your chosen folder, ready for the VRChat Creator Companion and the VRChat SDK in Unity.

---

**What This Unlocks:** You now have a rigged VRChat avatar. From here you can add hair physics (Guide 6), attach clothing (Guide 7), set up lip sync (Guide 8) and check performance (Guide 9). For a one-stop cleanup and VRChat setup with the CATS tools, see [Guide 13](03-guides-b.md#guide-13-get-your-avatar-vrchat-ready-with-cats).

---

## Guide 2: Bring a VRoid Avatar into VRChat

> **Time:** About 15–25 minutes
> **Result:** Your VRoid avatar ready for VRChat export

**Before you begin — check these:**
- [ ] You have exported your avatar from VRoid Studio as a `.vrm` file, or downloaded it from VRoid Hub as a `.zip`
- [ ] BoneCraft is installed and enabled

---

### Step 1 — Install the VRM Add-on

BoneCraft uses the VRM add-on to read `.vrm` files. In the **CATS** tab, expand **Import / Export** → **VRM / VRoid**. If it says the add-on is not installed, click **Auto-Install Latest from GitHub**. Without an internet connection, download the add-on yourself and use **Install from .zip on Disk…**; **Open Extensions Page** opens its download page.

---

### Step 2 — Import Your Avatar

In the same **VRM / VRoid** section, click **Import VRM…** and pick your `.vrm` file. For a VRoid download, click **Import VRoid (.vroid / .zip)…** and pick the `.zip`.

If you pick a VRoid Studio project file (`.vroid`), BoneCraft shows a "VRoid Studio Project" card instead: a project is not an avatar yet. Export it to VRM in VRoid Studio, then import that file.

**What you should be seeing:** Your VRoid character in the viewport with its skeleton in place.

---

### Step 3 — Map to VRChat's Humanoid Bones

In the **CATS** tab → **Avatar Tools** → **Set Up Humanoid Bones**, click **Auto-Map All**. VRoid skeletons follow a standard layout, so this usually fills every slot. If a slot is wrong, **Fix Humanoid Map** in the **VRM / VRoid** section (under Lint) repairs the usual VRoid name mix-ups.

---

### Step 4 — Fix Bone Names

Click **Normalize Names** in **Set Up Humanoid Bones**. VRoid has its own bone names; this gives the mapped bones the names VRChat expects.

---

### Step 5 — Set Up Visemes (Lip Sync)

VRoid avatars already have the mouth shapes for lip sync. In the **VRM / VRoid** section, click **Map VRoid Visemes**. BoneCraft matches VRoid's shape keys to VRChat's lip-sync shapes.

---

### Step 6 — Hair Physics (Optional)

VRoid hair uses SpringBones. **Convert SpringBones → PhysBones** in the **VRM / VRoid** section turns them into VRChat PhysBones. Guide 6 covers hair physics in more detail.

---

### Step 7 — Export

Export as in Guide 1, Step 9.

**What This Unlocks:** Your VRoid avatar is ready for the VRChat Creator Companion. You can also check performance (Guide 9) before uploading.

---

## Guide 3: Bring an MMD Avatar into VRChat

> **Time:** About 20–30 minutes
> **Result:** Your MMD `.pmx` model ready for VRChat

**Before you begin — check these:**
- [ ] You have a `.pmx` or `.pmd` MMD model file
- [ ] BoneCraft is installed

---

### Step 1 — Install mmd_tools

BoneCraft uses the mmd_tools add-on to read MMD files. In the **CATS** tab, expand **Import / Export** → **MMD / PMX**. If it says mmd_tools is not installed, click **Auto-Install Latest from GitHub** (or **Install from .zip on Disk...** with a downloaded copy).

---

### Step 2 — Import Your PMX File

In the **MMD / PMX** section, click **Import PMX / PMD...** and pick your model.

**What you should be seeing:** Your MMD character in the viewport with Japanese bone names.

---

### Step 3 — Fix Bone Names

VRChat cannot read MMD's Japanese bone names. In the **MMD / PMX** section, click **Convert Bone Names -> Unity**. For names in another language, use the **CATS** tab → **CATS** → **Translate Bone Names**: pick the **Language** and run it.

---

### Step 4 — Clean Up the Model

MMD models often have extra geometry and many separate parts. In the **CATS** tab → **CATS**, run **Fix Model** first, then **Join Meshes** to combine the body parts into one mesh (recommended for VRChat). [Guide 13](03-guides-b.md#guide-13-get-your-avatar-vrchat-ready-with-cats) walks through the whole CATS pipeline in order.

---

### Step 5 — Map to VRChat's Humanoid Bones

In the **CATS** tab → **Avatar Tools** → **Set Up Humanoid Bones**, click **Auto-Map All**. MMD skeletons are close to VRChat's, so most slots fill automatically. For an empty slot, click its button and choose the bone.

---

### Step 6 — Physics and Export

**Convert Physics -> PhysBones** in the **MMD / PMX** section turns MMD's rigid-body hair and skirt physics into VRChat PhysBones. Then export as in Guide 1, Step 9.

**What This Unlocks:** Your MMD avatar is ready for VRChat. You can add hair physics (Guide 6) and set up lip sync (Guide 8) before uploading.

---

## Guide 4: Fix Your Avatar's Bone Names

> **Time:** About 5–15 minutes
> **Result:** The bones VRChat needs renamed to VRChat-compatible names

**Before you begin — check these:**
- [ ] Your avatar is open with its skeleton (armature) visible

---

### Step 1 — Detect the Current Naming Style

In the **CATS** tab, expand **VRChat Tools**, find its Naming group and click **Detect**. BoneCraft shows the naming style it found (for example Mixamo, VRoid or Unity) and a score; **Force Rescan** checks again after you change names.

For bone names in Japanese, Chinese, Korean, Portuguese, Spanish or French, use the **CATS** tab → **CATS** → **Translate Bone Names** instead: pick the **Language** and run it. It converts the names to English in one step.

---

### Step 2 — Rename to VRChat Names

Map the bones first (Guide 5, Step 2), then click **Normalize Names** in **Set Up Humanoid Bones**: every mapped bone gets the name VRChat expects.

**What you should be seeing:** Bone names such as `Hips`, `Spine`, `Chest` and `LeftUpperArm`.

---

### Step 3 — Manual Fixes (If Needed)

The Naming group in **VRChat Tools** also has batch tools for the bones that are left:

- **Find and Replace** — replace one piece of text with another in every bone name
- **Add Prefix** and **Add Suffix** — add text to the start or end of every bone name
- **Remove Prefix** and **Remove Suffix** — strip it again
- **Regex Replace** — the same, with a regular expression

**What This Unlocks:** Correct bone names let the humanoid mapping (Guide 5) work automatically. Without them, VRChat cannot tell how your character should move.

---

## Guide 5: Map Your Avatar to VRChat's Body System

> **Time:** About 10–15 minutes
> **Result:** Your avatar's skeleton connected to VRChat's humanoid movement system

**Before you begin — check these:**
- [ ] Your avatar's bones are named sensibly (see Guide 4 if not)
- [ ] The skeleton is selected
- [ ] You are in **Object Mode** (check the dropdown in the top-left of the viewport)

---

### Step 1 — Open Set Up Humanoid Bones

In the **CATS** tab, expand **Avatar Tools** → **Set Up Humanoid Bones**.

---

### Step 2 — Auto-Map

Click **Auto-Map All**. BoneCraft scans your skeleton and fills the body slots.

> A humanoid slot is like a labelled hook VRChat uses: "Hips go here, Head goes here, Left Hand goes here." BoneCraft matches your bones to these hooks. Humanoid mapping now reads back correctly when you reopen a file.

**What you should be seeing:** The required slots (15: Hips, Spine, Head, both upper arms, lower arms, hands, upper legs, lower legs and feet) and the optional ones (Chest, UpperChest, Neck and others), each with a bone, and the share of required slots that are filled.

---

### Step 3 — Check the Mapping

Click **Validate**. BoneCraft checks that every required slot has a bone and that the hierarchy makes sense.

---

### Step 4 — Fill Empty Slots by Hand

A slot without a bone shows "(click to map)". Click it and choose the right bone. Then click **Validate** again, and **Normalize Names** so the mapped bones get VRChat's names.

---

### Step 5 — Set Up Eye Tracking (Optional)

If your avatar has eye bones, use the **CATS** tab → **CATS** → **Eye Tracking**: click **Auto-Detect** to find the eye bones (or pick the **Left Eye** and **Right Eye** bones), set the limits, and click **Create Eye Tracking**. [Guide 13, Phase 3](03-guides-b.md#phase-3--eye-tracking) explains the settings.

**What This Unlocks:** With the humanoid mapping done, your avatar moves properly in VRChat: IK (inverse kinematics, the system that makes your in-game hands follow your real controllers) works, and your avatar follows your real-world movements.

---

## Guide 6: Add Hair Physics

> **Time:** About 15–25 minutes
> **Result:** Your avatar's hair (and other soft parts) swinging naturally in VRChat

**Before you begin — check these:**
- [ ] Your avatar is open with the skeleton selected
- [ ] Set Up Humanoid Bones is done (Guide 5)

> PhysBone = VRChat's component that makes bones bounce and swing as if they had weight. BoneCraft sets them up on chains of bones: hair, ears, tails, skirts and accessories.

---

### Step 1 — Open Add Hair Physics

In the **CATS** tab, expand **Avatar Tools** → **Add Hair Physics**. It has four parts: Hair Chain Detection, Hair Chain Generation, PhysBone Configuration and Hair Physics Colliders.

---

### Step 2 — Find the Hair Chains

If your hair already has bones, click **Detect Hair Physics Chains**. BoneCraft finds the chains of bones that look like hair (bones linked end to end from a root) and lists each one with its root bone and length.

If your hair has no bones yet, select the hair meshes and use Hair Chain Generation: choose the **Density** (Low, Medium or High: how many chains), then click **Generate**. **Replace** builds them again with a new density.

---

### Step 3 — Choose a PhysBone Preset

Select a bone of a chain. Under PhysBone Configuration, click the preset that fits: **Hair**, **Skirt** (skirts and capes) or **Tail** (tails and ropes).

**What you should be seeing:** The chain's parameters: Pull, Spring, Stiffness, Gravity and Max Angle.

---

### Step 4 — Fine-Tune (Optional)

The panel shows the chain's values; it does not edit them. More Stiffness makes a chain bend less, more Gravity pulls it down, and a smaller Max Angle limits how far it swings. For different values, click another preset, or change the PhysBone component in Unity after you import the avatar.

---

### Step 5 — Add Colliders (Recommended)

Colliders are invisible shapes that stop hair from passing through the head and body. Under Hair Physics Colliders, click **Place Default Colliders** to add standard colliders on the head, shoulders and chest. **Add Collider** and **Remove Collider** add or remove one at a time.

**What This Unlocks:** Your avatar's hair now moves naturally in VRChat when you turn your head, jump or dance. The same steps work for tails, ears, skirts and dangling accessories.

---

## Guide 7: Attach Clothing That Moves With Your Body

> **Time:** About 20–30 minutes
> **Result:** A clothing item attached to your avatar's skeleton, moving with your body

**Before you begin — check these:**
- [ ] Your base avatar has a finished skeleton, and its body is weight painted
- [ ] The clothing item is in the same file (with its own armature if it came with one)
- [ ] The clothing roughly fits around your avatar's body

---

### Step 1 — Open Attach Clothing

In the **CATS** tab, expand **VRChat Tools** and find its Clothing group. It has three parts: Bone Matching, Collision Detection and Clothing Merge.

---

### Step 2 — Match Bones

If the clothing came with its own armature, select it and click **Match Bones**. BoneCraft pairs each clothing bone with the equivalent bone of your avatar (the clothing's left arm with your avatar's left arm, and so on).

**What you should be seeing:** A list of bone pairs: clothing bone → avatar bone. For clothing without an armature, skip this step.

---

### Step 3 — Merge the Clothing

Select the clothing — its armature and meshes, or only its meshes if it has no armature — then Shift-click your avatar's armature last, so it is the active object. Click **Merge Clothing**. With a clothing armature, BoneCraft moves the clothing onto your skeleton and merges the bones; without one, it transfers your body's weights to the clothing meshes.

> Weights (weight painting) = numbers that tell each point of a mesh how much each bone moves it. If your left sleeve has weight on the left arm bone, moving that bone pulls the sleeve with it.

**What you should be seeing:** The clothing under your avatar's skeleton. Moving a bone moves both the body and the clothing.

---

### Step 4 — Check for Clipping

Click **Detect Collisions** to find places where the clothing pokes through the body. Fix them by adjusting the weights there (see the Weight Tools in [Rig Tools](05-rig-tools.md)).

**What This Unlocks:** Clothing that moves naturally with your body. Repeat for each outfit piece.

Next: [Guides 8–13](03-guides-b.md)
