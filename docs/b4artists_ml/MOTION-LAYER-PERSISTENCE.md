# Persistent native motion ownership

The internal `motion_layer.py` component places the original rig and its bound meshes in an excluded evaluation collection and displays a native collection instance. Original actions, transforms and data remain on the original objects. Recovery uses persistent Blender ID references, so renames and saved files preserve the original collection destinations. Keep retains the managed layer; Restore restores source memberships and removes only owned generated data.

This component is not imported by the released UI or flight workflow. Release 0.13.1 remains byte-identical across all 32 packaged files. It is not a new release or completed animation feature.

## Validation

- 14 host tests pass: partial-move rollback, Keep/Restore, rename/reload, multiple view layers, deleted generated data, damaged records and original destinations, shared-scene rejection, foreign instances/members/collection links, user child collections and parented objects. Invalid active-object metadata now fails before recovery changes collection membership.
- Actual BoneForge, generated basic/default Rigify and basic/default metarigs pass with rotation/translation and uniform scale 1.7. Synthetic triangles are bound to every deform bone. Geometry is unchanged on rehousing; translation error is below 4.8e-7 world units; direct animator-control edits deform the displayed instance. Five saved samples per rig reload identically without importing the addon. Source recovery in a fresh process returns exact original sampled geometry and collection membership.
- Workbench renders show only the translated instance, with zero source-side opaque pixels. Saved playback and rendering pass with auto-execution disabled and no addon import. This rendering fixture is a simple bound cube.
- Every Bforartists host process still exits 3221225477 after passing assertions. Clean host lifecycle is not accepted.
- All previous 38 flight-maintenance evidence hashes verify. All prior frozen input files retain their original fingerprint; existing regression evidence is carried by byte identity, not represented as a fresh run of all 185 tests. New component checks are fresh.

## Remaining integration

Connect native flight generation and source-space/displayed-world transformations to the existing preview, posing, contact and support workflows. Add complete motion-result archival (driver formulas are currently lost when the generated instance is removed, although its action is retained), selective application, source selection, cancellation, Undo/Redo and integrated save/reload. Additional attached object types, production rigs and multiple-character interaction need acceptance evidence. Source recovery does not recreate user-deleted original collection destinations; it fails before mutation and requires an explicit recovery destination.

The earlier 60-frame native flight prototype remains separate; long default-Rigify flight still lacks accepted precision/performance. Learned temporal quality, momentum and secondary motion, quadrupeds, independent usability and equivalent Cascadeur comparison remain incomplete. No parity or superiority is claimed.

## Evidence integrity

Real-rig harness v1 failed because it retained transient depsgraph wrappers. V2 corrected sampling but compared candidate modes against pre-preview source modes; v3 fixed that baseline. V4 verifies the final runtime safeguards. Failed logs are retained. The unit-run v3 initially wrote its 14-test report to the old v1 path; that old JSON is no longer historical evidence. Its versioned logs remain, and v3/v4 have separate correct reports. Only v4 is used for current unit acceptance.

The canonical review is INCONCLUSIVE: checkpoint policy allowed S1 while S2 was required; no independent reviewer was invoked. Nothing was committed, staged, pushed or installed.
