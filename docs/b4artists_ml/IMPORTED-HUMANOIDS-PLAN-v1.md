# Imported humanoid behavior: prospective implementation plan

Source audit after 0.15.1 finds that rigs.detect_rig recognizes the BoneForge
Mocap Humanoid, Unity Humanoid and Unreal Mannequin maps, and posing.bindings
checks their direct FK limb chains. body_solver.mapping then rejects every one
of these profiles. Naming support therefore does not provide the required
whole-body animation workflow. The next original-scope milestone addresses
actual behavior on these three imported humanoid conventions.

## Scope and approach

Enter the canonical coding-plan route before implementation. Audit the mapped
body/limb hierarchy, writable controls, rest transforms and root ancestors using
actual armature data. Add an explicit adapter for validated plain FK humanoids;
never treat a name match alone as permission to write generated mechanism bones.
Keep the bundled BoneForge source maps unchanged. Preserve existing generated
BoneForge/Rigify behavior, and retain clear unsupported diagnostics where an
imported topology, constraint or control space lacks verified handling.

Do not silently ignore an unmapped root ancestor, keyed root motion, twist/extra
bones or mesh deformation. Decide and test how their source transforms are
retained during posing, anchor capture, interpolation and restoration. Any
unsupported dependency must be detected before mutation and named precisely.
Rigify deform-only rigs, further import variants, quadrupeds and general
production-asset coverage remain requirements in the full goal; this milestone
cannot redefine that endpoint or count a three-profile subset as full coverage.

## Required evidence before the milestone passes

1. Build and retain independent authored plain-FK skeleton/mesh fixtures for the
   three conventions, with multiple proportions/rest orientations and explicit
   root ancestry. Use actual host file export/import where supported and verify
   the imported hierarchy, control spaces and bound mesh. Merely renaming a
   previously accepted Rigify fixture is insufficient evidence.
2. Run the complete integrated path: inspect, sparse whole-body targets, selective
   pins/rotations/poles/limits, live/manual preview, Keep as Anchor, multiple
   priority anchors, interpolation preview and Keep/Discard/source recovery.
   Exercise support/contact/native-flight paths as applicable and keep their
   separate physics/quality limitations visible.
3. Verify unchanged priority poses, source actions/keys, non-owned bone channels,
   rig data and mesh ownership. Measure actual evaluated joint and mesh results,
   existing numerical gates, unsupported-case rollback and failure recovery.
4. Cover actual save/reload, Undo/Redo and disabling for the imported workflow,
   including authored root motion. Protect all previously supported profiles.
5. Document exact tested import formats, skeletons, proportions, behavior and
   remaining unsupported cases; qualify an installable local package offline.
   No new learned-quality, independent usability or Cascadeur claim is implied.

The original goal, historical evidence/floors, human-usability requirement,
50-total evaluation ceiling and existing 15-hour resumed-run deadline remain
unchanged. No imported-adapter runtime edits have been made for this plan yet.
