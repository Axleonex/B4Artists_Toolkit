# Getting Started

[← Contents](index.md)

## What is BoneCraft?

BoneCraft is an add-on for Bforartists that helps you rig characters and props, and prepare 3D avatars for VRChat, VRoid / VRM and MMD. It adds panels and buttons that automate the most tedious steps: building a rig, painting weights, fixing bone names, setting up lip sync and eye tracking, and exporting.

**What BoneCraft cannot do:**
- It cannot model or sculpt your avatar's body shape
- It cannot create textures or materials from scratch
- It cannot upload to VRChat directly (you still need the VRChat Creator Companion / SDK)

---

## BoneCraft and BoneForge

BoneCraft runs only in Bforartists (the Blender fork). For standard Blender there is a separate add-on, BoneForge, with a smaller set of tools. Install one or the other, never both. In standard Blender, BoneCraft does not load: it shows one notice with a button to get Bforartists.

BoneForge 9.0.0 and later target standard Blender. BoneCraft is the separate Bforartists add-on. Both have Auto-Rig Wizard, Quick Rig, Mannequin and the shared CATS/Material Atlas tools. BoneCraft also has Mechanisms, the Control Picker and its production control-rig, joint-detection and profile-export tools. Similar placement does not add those tools to BoneForge.

## Installing BoneCraft

**What you need:**
- Bforartists (BoneCraft is tested on Bforartists 5.2)
- The BoneCraft `.zip` file

**Steps:**

1. Open Bforartists.
2. Open **Edit** → **Preferences** → **Add-ons**.
3. Click **Install from Disk…** and pick the BoneCraft `.zip` file.
4. Tick the checkbox next to BoneCraft to enable it.
5. Expand BoneCraft's entry to see its settings: **Language**, **Tabs**, **Shelf Width**, **Show Helpers** and the **Tools** list.

**You should see:** the BoneCraft and Rig Builder tabs on the left Tool Shelf (press **T**) and the CATS tab on the right sidebar (press **N**).

## Where things are

Tab names select a workspace group. Setup Rigging, Skin, Review, Avatar Tools and Facial are expandable sections inside those tabs, not separate tabs. The paths below use the English UI labels; translated labels depend on the Language preference.

| Tab | Default location | Sections |
| --- | --- | --- |
| Rig Builder | Left Tool Shelf (T) | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | Left Tool Shelf (T) | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | Right sidebar (N) | CATS, Avatar Tools, VRChat Tools, Import / Export |

| Tool | Open this path |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

Select an armature for rig and viseme-library controls; select a mesh in Object Mode for Delta Mush and Proximity Wrap. Lip Sync requires an armature in Pose Mode. Expand the section triangle to show its buttons. Options folds hold optional settings; tools that run immediately can be adjusted in Adjust Last Operation before running another operation.

These are three different facial workflows: CATS viseme generation creates mouth shape keys, Viseme Library / Lip Sync stores poses and keys animation, and Facial maps existing shape keys for VRChat or configures face tracking. UVToolkit-derived controls are in CATS → Material Atlas → Override Inherited Settings → UV Packing; this is the shared atlas workflow, not the full standalone UVToolkit add-on.

**Move a tab:** open **Edit** → **Preferences** → **Add-ons** → BoneCraft → **Tabs**. Each tab has a show switch and two buttons, Left and Right. A change applies at once. While a tab is hidden, its Left and Right buttons turn grey, but they still work.

**Properties editor:** Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools and Import / Export are also shown in the Properties editor's Scene tab while **Scene Properties** is on in Preferences → Tabs. This switch starts on. Click its **Show** button to hide or show all of these sections; blue means they are shown. It does not change the viewport tabs or the Armature data tab. With an armature selected, BoneCraft's armature tools also appear in the Armature data tab, independently of these visibility switches. Rig Builder, Mechanisms and the CATS sections use the Scene tab instead. To remove a tool everywhere, switch its package off in the **Tools** list, or disable the add-on.

**Shelf Width:** Widen Narrow Shelves starts on. It widens shelves holding BoneCraft tabs once if they are below the Left or Right minimum: 240 and 260 pixels by default, at 1× UI scale. A shelf you drag narrower afterwards stays at your chosen width. Turn the switch off to manage widths yourself; its width fields become inactive.

**Menus and built-in Tool Shelf tabs:** you can also reach tools from the 3D Viewport's header menus:

| Location | Tools |
| --- | --- |
| Add → Armature | Quick Rig, Auto-Rig Wizard, Mannequin for Active Rig |
| Pose → BoneCraft (Pose Mode) | Pose tools, the picker, bone collections, rig setup and checks |
| Weights → BoneCraft (Weight Paint mode) | Flood fill, mirror and normalize weights |
| Object → Mechanisms (Object Mode) | Add parts, joints and links; test motion |
| Tool Shelf → Pose or Weights → BoneCraft | Buttons for common pose or weight operations |

The Pose and Weights shelf buttons show text when the shelf is wide and become an icon grid when it is narrow. Hover an icon to read its tooltip. These access points use the same tools as BoneCraft's own tabs; their availability follows the enabled tool packages.

**Viewport tools:** Place Rig Markers places the Auto-Rig Wizard's next marker when you click the mesh; Build Mechanism starts a guided joint or link when you click a part. See [Rig Builder](06-rig-builder.md#auto-rig-wizard) and [Mechanisms](07-mechanisms.md#joints-and-links-one-example-each) for their setup and controls.

**Run first, adjust afterwards:** tools such as Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK and Delta Mush run when clicked. Immediately afterwards, use the Adjust Last Operation panel in the viewport to change their options. Adjust before running another operation. Other panels put optional settings in a fold below the action buttons; expand it when you need those settings. A panel that needs a different selection may stay visible and explain what to select.

**Show Helpers:** BoneCraft explains its sections with short "what / when" lines and "How this works" notes. Untick **Show Helpers** in the add-on's preferences to hide them. In the Avatar Tools section, **Compact Mode** is a shortcut for the same switch.

**Language:** the **Language** setting in the add-on's preferences changes BoneCraft's own panels to English, 日本語, 한국어, 中文, Français, Português or Español.

**Fix Model first, every time:** in the CATS tab, always start with **Fix Model** before any other CATS tool. The CATS pipeline uses a ledger to track which steps you have done, and each tool warns you if you run it out of order. See [The CATS Pipeline](04-cats-pipeline.md).

**Quick panel:** press **Ctrl+Shift+R** in the 3D Viewport to open BoneCraft's rig panel as a pop-up under the cursor.

---

## Where Should I Start?

Choose the description that best fits you:

> **"You are a person who has a brand new 3D model file (FBX, OBJ, or Blender file) and wants to rig it for VRChat from scratch."**
> → Go to [Guide 1: Get Your First Avatar Into VRChat](02-guides-a.md#guide-1-get-your-first-avatar-into-vrchat)

> **"You are a person who made your avatar in VRoid Studio and exported a VRM file."**
> → Go to [Guide 2: Bring a VRoid Avatar into VRChat](02-guides-a.md#guide-2-bring-a-vroid-avatar-into-vrchat)

> **"You are a person who has an MMD model (PMX file) and wants to use it in VRChat."**
> → Go to [Guide 3: Bring an MMD Avatar into VRChat](02-guides-a.md#guide-3-bring-an-mmd-avatar-into-vrchat)

> **"You are a person who already has a rigged avatar but it won't upload because the bones have wrong names."**
> → Go to [Guide 4: Fix Your Avatar's Bone Names](02-guides-a.md#guide-4-fix-your-avatars-bone-names)

> **"You are a person who has a rigged avatar and wants to get it fully VRChat-ready — lip sync, eye tracking, clean mesh, all at once."**
> → Go to [Guide 13: Get Your Avatar VRChat-Ready with CATS](03-guides-b.md#guide-13-get-your-avatar-vrchat-ready-with-cats)

> **"You are a person who wants to fix a specific problem."**
> → Go to the [Quick-Fix Index](10-reference.md#quick-fix-index)

Next: [Guides 1–7](02-guides-a.md)
