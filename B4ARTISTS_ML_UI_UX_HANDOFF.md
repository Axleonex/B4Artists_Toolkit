# B4Artists ML UI/UX Handoff

## Objective

Turn B4Artists Machine Learning from a tested collection of animation operations into a clear, animation-centered Bforartists workflow. The target experience is inspired by Cascadeur's immediacy: an animator should see what the tool can do, understand the next action, manipulate visible controls, and review the result in the animation editors without reading source documentation.

This milestone concerns workflow, presentation, feedback, and editor integration. Preserve the verified solver behavior unless a UI integration test proves that a backend change is necessary.

## Why this handoff exists

The first hands-on animator review failed the usability goal. The animator reported:

> Clicking through the buttons feels like nothing is happening. The features are unclear, and nothing useful appears in the animation windows. The expected experience was closer to a Blender/Bforartists version of Cascadeur.

That report is consistent with the implementation. The addon passes its current automated correctness checks, but those checks do not establish that an animator can discover or complete the workflow.

Do not describe the addon as ready for normal animator use until the acceptance criteria in this document pass.

## Current verified state

- Addon version: `0.37.51` public beta.
- The solver and repair baseline passed the eight S4 review shards with zero remaining findings.
- The current host-independent regression group passed 83 tests.
- The current native Bforartists regression group evaluated 47 tests: 10 passed and 37 were skipped because the optional BoneForge checkout was not configured.
- The native tests verify selected operations and save/reload behavior. They do not verify that a new animator understands the interface.
- Learned temporal quality, independent animator review, and a direct Cascadeur comparison remain unqualified.

## Root cause

The usability failure is architectural rather than a single broken button.

1. `b4artists_ml/ui.py` registers one panel: `B4ML_PT_main`.
2. That panel exists only in `VIEW_3D` → `UI`, under the `B4Artists ML` tab.
3. No B4ML panels, menus, markers, or contextual controls are registered in the Timeline, Dope Sheet, Graph Editor, or NLA Editor.
4. The single panel contains rig mapping, support, flight, contacts, cleanup, secondary motion, quadruped tools, whole-body posing, pose capture, generation, and review in one long vertical layout.
5. Several advanced sections require `state.candidate_action`, but the UI does not present that dependency as a visible workflow stage.
6. Pose capture can change only internal addon state. Its confirmation is the `state.status` string at the bottom of the panel, commonly outside the visible scroll area.
7. Operators report failures through transient Bforartists messages. The panel does not provide a prominent persistent error with a corrective next action.
8. Whole-body posing creates scene targets, but the panel does not provide a strong mode transition, viewport focus action, control legend, or unmistakable indication that the animator must manipulate those targets in Object Mode.
9. Candidate actions are reviewed by scrubbing the ordinary timeline. There is no dedicated before/after view, range display, candidate track, or animation-editor visualization.

The backend can therefore succeed while the product appears idle.

## Existing workflow hidden in the panel

The current intended sequence is:

1. Select an armature or a mesh bound to an armature.
2. Run **Inspect / Refresh Rig Mapping**.
3. Start **Whole-Body Pose** or **Assisted Pose**.
4. Switch to Object Mode and move the generated targets.
5. Solve the pose and keep it as a pose anchor.
6. Repeat at another frame.
7. Capture at least two key poses.
8. Generate an interpolation or whole-body preview.
9. Review the candidate action by scrubbing.
10. Keep or discard the candidate.
11. Run contacts, cleanup, flight, or secondary motion against the candidate when applicable.

The product must make this sequence visible. Users should not have to infer it from enabled and disabled buttons.

## Product direction

Build an animation workspace around three persistent regions:

### 1. Workflow panel

Replace the long undifferentiated panel with a compact stage-based interface:

- **Setup** — active character, rig compatibility, mapping result, and a clear repair action.
- **Pose** — create/manipulate controls, solve, and keep a pose.
- **Motion** — captured poses, range, interpolation method, and preview generation.
- **Polish** — contacts, cleanup, flight, and secondary motion.
- **Review** — source/candidate comparison, keep, discard, and restore.

Always show the current stage, completed stages, the next recommended action, and why an unavailable stage is locked.

### 2. Viewport interaction

The viewport must visibly communicate active B4ML state:

- Focus or frame newly created pose targets.
- Use recognizable colors and shapes for hands, feet, pelvis, chest, head, elbows, and knees.
- Show a compact legend while a posing session is active.
- Display contacts, support, center of mass, trajectories, and collision bounds only when relevant.
- Provide direct **Solve**, **Preview**, **Keep**, and **Cancel** controls close to the active task.
- Show whether the animator should be in Pose Mode or Object Mode and provide a one-click mode correction.

### 3. Animation-editor integration

Add useful B4ML context to the Timeline and Dope Sheet first. Graph Editor and NLA integration can follow after the core workflow passes usability testing.

Minimum Timeline/Dope Sheet behavior:

- Mark captured pose anchors and label their role.
- Distinguish source action, candidate action, accepted contacts, flight intervals, and protected priority frames.
- Show the active generation/review range.
- Provide contextual actions for capture, preview, keep, discard, and restore.
- Selecting an anchor or contact marker should update the active item in the B4ML panel.
- Editing or retiming an item should immediately update its visible marker.

Do not build decorative panels that duplicate the sidebar. Editor integration must expose animation timing or review information that belongs in that editor.

## Required interaction rules

- Every button must produce an immediate visible result, a persistent success message, or a persistent error with a corrective action.
- Disabled controls must explain their unmet prerequisite in the visible UI.
- A user must never need to scroll to the bottom of the panel to learn what the last click did.
- Starting a task must reduce the interface to the controls needed to finish or cancel that task.
- Preview operations must show the affected frame range and whether the source or candidate is currently visible.
- Source animation, candidate animation, kept result, and restored source must have distinct visible states.
- Destructive-looking actions must state whether they are previews, copies, or commits.
- Terms such as `candidate_action`, `payload`, `backend`, and internal units must not appear in animator-facing copy.
- “Machine Learning” claims must match qualified behavior. Procedural features should be labeled procedural.

## First implementation slice

Deliver a narrow end-to-end humanoid journey before reorganizing every feature:

1. Select a supported Rigify humanoid.
2. See a setup card with a clear compatibility result.
3. Start whole-body posing.
4. See and manipulate framed viewport targets.
5. Solve and keep poses at two frames.
6. See both pose anchors in the Timeline or Dope Sheet.
7. Generate a pose-blending preview.
8. See a persistent source-versus-candidate review state.
9. Keep or discard the candidate.
10. Restore the source action.

Contacts, cleanup, flight, secondary motion, quadruped workflows, learned temporal motion, and advanced mapping controls should remain accessible through an **Advanced** area until this primary journey is understandable.

## Suggested code ownership

- `b4artists_ml/ui.py` — current properties, operators, and monolithic panel. Split presentation without changing operator semantics initially.
- `b4artists_ml/workflow.py` — source/candidate action lifecycle, anchors, review state, and active rig selection.
- `b4artists_ml/body_preview.py` — whole-body target lifecycle and viewport posing state.
- `b4artists_ml/contact_visualization.py` — existing viewport overlay pattern to reuse for other visible states.
- `b4artists_ml/contacts.py` and `b4artists_ml/quadruped_contacts.py` — contact state and review synchronization.
- `b4artists_ml/cleanup.py`, `flight.py`, and `secondary_motion.py` — advanced operations whose prerequisites need visible explanations.
- `b4artists_ml/__init__.py` — addon metadata and any new UI module registration.

Prefer adding focused UI modules over extending the existing 2,800-line `ui.py` panel. Keep operators and solver modules independent from editor drawing code.

## Testing requirements

Add tests for observable workflow behavior rather than mirroring layout code.

Automated checks must cover:

- Correct workflow stage for no selection, unsupported rig, mapped rig, active posing session, captured anchors, candidate preview, and kept result.
- A visible reason for every locked primary action.
- Persistent success and failure feedback after primary actions.
- Anchor/contact/interval marker synchronization after add, remove, retime, accept, reject, keep, discard, restore, undo, save, and reload.
- No loss or mutation of the source action while previewing.
- UI registration in each supported editor and clean unregistration.
- Bforartists-native screenshots or state assertions for the primary journey.

Preserve the existing math, contact, cleanup, pole, and save/reload regression suites.

## Human usability acceptance

The milestone is complete only when an animator unfamiliar with the implementation can perform the first implementation slice without source documentation or coaching.

Observe at least these outcomes:

- The animator identifies where to begin within 30 seconds.
- The animator can explain what will happen before generating a preview.
- Every click produces feedback the animator notices.
- The animator can tell source and candidate animation apart.
- The animator finds pose anchors in an animation editor.
- The animator can keep, discard, and restore without fear of losing work.
- The animator can explain why a locked feature is unavailable.
- No critical step depends on discovering a message at the bottom of a scrolled panel.

Record confusion, misclicks, task completion time, and any question the animator asks. A passing S4 code review does not replace this test.

## Definition of done

- The primary humanoid journey passes native Bforartists automated tests.
- All existing protected regressions remain green.
- The addon exposes meaningful timing/review state in the Timeline or Dope Sheet.
- The viewport makes active controls and results visually obvious.
- Persistent feedback replaces silent-looking state changes.
- One independent animator completes the journey unaided.
- The public-beta documentation and addon description accurately describe the delivered experience.
- A new installable ZIP is built and smoke-tested in a clean Bforartists profile.

## Out of scope for the first slice

- Reproducing every Cascadeur feature.
- Replacing Bforartists' full animation workspace.
- Claiming learned-motion quality before its separate qualification gate passes.
- Rewriting verified collision, contact, or motion math solely to support a new layout.
- Polishing every advanced workflow before the primary posing-to-preview journey works.

## Immediate next action

Create a UI architecture plan and a low-fidelity Bforartists prototype for the first implementation slice. Test that prototype with the same animator who reported the current failure before migrating contacts, cleanup, flight, secondary motion, or quadruped tools into the new workflow.
