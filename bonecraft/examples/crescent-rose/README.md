# Crescent Rose — Mechanisms example

Two files:

- `CrescentRose_parts.blend` — the weapon prepared as 15 part objects, ready for **Add Parts from Selection**. Start the tutorial here.
- `CrescentRose_Mechanisms.blend` — the finished rig: eight hinges, three slides, a telescope, a piston and a follow, two Sequences (`Scythe to Rifle`, `Rifle to Compact`) and three Forms (`Scythe`, `Rifle`, `Compact`). Open it, select the armature "Mechanism Rig", and use **4. Controls** in the BoneCraft tab → Mechanisms.

The English tutorial that builds it, with a screenshot for every step: [manual chapter 12](../../docs/manual/en/12-crescent-rose.md). The English walkthrough was replayed with BoneCraft 9.1.2 in Bforartists 5.2.0, including eight illustrated FBX preparation steps and 30 Mechanisms steps. Chinese, French, Japanese, Korean, Portuguese and Spanish tutorial editions are deferred until the completed English result is approved; see [docs/README.md](../../docs/README.md) for the existing manual editions.

Enable BoneCraft 9.1.2 for the Mechanisms controls. Both files contain 12 packed 1024 by 1024 textures. The prepared file is ordinary mesh data; the finished rig loads without enabling Auto Run Python Scripts.

Both examples were rebuilt through the interface for this lesson. The prepared file has 15 meshes and 9,366 vertices, applied transforms and a height of approximately 1.997 m. `scripts/build_crescent_rose_parts.py` supplies the reference piece grouping. The finished file opens in Scythe; use Go to Form to inspect Rifle and Compact.

The forms demonstrate the mechanisms and are not a collision-certified physical design. The checked sequence targets and the negative-X RearSpike hinge are documented in chapter 12. Candidate host tests, every control, linked motion and Form restoration passed; see the [execution report](../../docs/reviews/crescent-rose-english-execution-2026-10-10.md).

## Credit and licence

Crescent Rose model by amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; split into parts, scaled and rigged for this tutorial. Crescent Rose is a design of Rooster Teeth Productions; this is a fan-made tutorial asset. See `LICENSE-model.txt`.
