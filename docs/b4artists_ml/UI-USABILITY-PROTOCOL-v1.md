# B4Artists ML UI Usability Session Protocol v1

Status: session protocol for human animator acceptance test.
Companion to `UI-ARCHITECTURE-PLAN-v1.md` §6 Phase 4 and `B4ARTISTS_ML_UI_UX_HANDOFF.md` §Human usability acceptance.
Date: 2026-09-22.

---

## Session overview

### Goal

The same animator who reported the original failure ("Clicking through the buttons feels like
nothing is happening") completes the 10-step humanoid journey without source documentation,
without coaching, and without any button label named in advance by the session operator.

Milestone is complete only when that animator finishes all ten steps unaided.

### Addon version

`1.0.0` (release `ml-v1.0.0`, file `b4artists_ml_v1.0.0.zip`). Updated 2026-09-26; the protocol was
written against the `0.38.0` public beta and the journey is unchanged.

### Required setup

- **Bforartists**: 5.1.2 installed, clean profile or production profile — operator to confirm.
- **File**: a Rigify humanoid blend file prepared in advance and provided to the animator;
  the armature must be mapped and posable (at least one existing keyframe on the source action
  so the Restore step has something to restore to). File is opened before the session begins.
  Prepared 2026-09-26: `G:/LapArt/output/b4ml-usability-session/usability-session-rigify-humanoid.blend`
  (Bforartists 5.1.2 bundled Rigify human rig named `Character`, keys on `torso`, `hand_ik.L`,
  `hand_ik.R` at frame 1, selected, Object Mode). A scripted pilot of all ten steps passed on it.
- **Other add-ons**: disable Anim Assist and Ghost Tool for the session; their header menus and
  panels would change what the animator sees and are not part of this test.
- **Screen recording**: active for the full session, capturing the Bforartists window and the
  animator's voice if think-aloud is used.
- **Note-taker**: a second person watching and recording observations, or the animator
  self-reporting via think-aloud narration throughout. Both methods are valid; document which
  was used.
- **Timer**: visible to the note-taker; started when the N-panel (sidebar) is first opened.

---

## Task script

Read each numbered step aloud to the animator exactly as written. Do not name any button,
menu, or panel label until the step itself has been completed and confirmed. Do not coach.

1. "The character in this file is a Rigify humanoid. Select it — whichever way you normally
   would in Bforartists."

2. "Open the N-panel on the right side of the 3D viewport if it is not already open.
   Find the B4Artists ML section and tell me what it says about this character."

3. "Use what you see in that panel to begin posing the whole body of this character."

4. "You should now have posing controls in the viewport. Move at least three of them to a
   new position at the current frame."

5. "Capture what you have just posed as a key pose. Then move to a different frame, set a
   different pose using those same controls, and capture that one too."

6. "Without me telling you where to look — find where the two key poses you just captured
   are recorded in the animation editors."

7. "Generate a motion preview between the two key poses."

8. "Tell me what you are looking at now — is this your original animation, or something new?
   How can you tell?"

9. "Either keep this preview or throw it away. Your choice — but tell me out loud what you
   expect to happen to your original animation."

10. "Restore your original animation."

---

## Observations to log

One row per criterion. Fill in Yes / No / Notes and elapsed time where marked.

| # | Criterion (from contract §BEHAVIORAL SUCCESS) | Pass (Y/N) | Notes | Elapsed (s) |
|---|---|---|---|---|
| 1 | **30-second start**: animator clicks the correct first action within 30 s of N-panel opening. First action = the rig-check or start-posing control, whichever the animator chooses first. | | | Time from N-panel open to first qualifying click: ___s |
| 2 | **Explains preview before generating**: before clicking to generate, the animator states aloud the frame range and what the operation will produce. | | | Time from step 7 read-aloud to click: ___s |
| 3 | **Every click noticed**: every primary action (check rig, start posing, solve, keep pose, generate, keep/discard, restore) produces a change the animator explicitly notices — verbal acknowledgment, continued action, or spontaneous comment. Log any click that produces no noticed response. | | | — |
| 4 | **Source vs preview distinguishable**: while reviewing, animator identifies which animation is currently playing without reading the action name from the header dropdown. | | | — |
| 5 | **Anchors visible in Dope Sheet**: after step 5, animator finds the two key-pose markers in the Timeline or Dope Sheet without being directed there. | | | Time from step 6 read-aloud to first correct identification: ___s |
| 6 | **Keep / discard / restore without fear**: animator executes Keep (or Discard) and then Restore without asking whether data will be lost. | | | — |
| 7 | **Locked feature explained**: if the animator encounters a disabled control, they read the reason aloud from the panel without hovering a tooltip. | | | — |
| 8 | **No bottom-of-panel dependence**: no step requires the animator to scroll to the bottom of any panel to learn the result of their last action. Log any scroll-to-bottom event during a primary step. | | | — |

---

## Confusion and misclick criteria

### Operational definitions

**Confusion**: the animator pauses for more than 10 seconds with no mouse or keyboard action,
asks any question directed at the operator, or reads a UI label aloud without then taking an
action within 5 seconds. A verbal comment ("OK, so...") followed by immediate action does not
count.

**Misclick**: the animator clicks a control, then immediately reverses or undoes the action
without completing its stated purpose — for example, clicking a button and then pressing Ctrl-Z,
or clicking a control and then clicking Cancel in the same interaction. Accidental mis-selects
in the viewport that are corrected in under 2 seconds without affecting the panel state do not
count.

### Tally table

One row per task step. Increment the tally during review of the recording.

| Step | Step description (short) | Confusion count | Misclick count | Notes |
|---|---|---|---|---|
| 1 | Select character | | | |
| 2 | Find B4ML panel, read character state | | | |
| 3 | Begin whole-body posing | | | |
| 4 | Move viewport targets | | | |
| 5 | Solve and keep two key poses | | | |
| 6 | Find key poses in animation editors | | | |
| 7 | Generate preview | | | |
| 8 | Identify source vs preview | | | |
| 9 | Keep or discard | | | |
| 10 | Restore source | | | |
| **Total** | | | | |

---

## Timing rule

**Pass threshold**: the animator clicks the correct first action (rig check or start posing)
within **30 seconds** of the N-panel opening. Log the actual elapsed seconds regardless of pass
or fail — the raw number informs the next revision.

**How to capture the timestamp**:

1. Mark the recording timestamp at the moment the N-panel becomes visible (either opened by the
   animator or already open when they navigate to the B4Artists ML tab).
2. Mark the recording timestamp at the first qualifying click (a click on the rig-check control
   or the start-posing control in the B4Artists ML panel).
3. Subtract: that difference is the elapsed time for criterion 1.

If screen recording timestamping is not frame-accurate, the note-taker should call out and log
"panel open" and "first click" verbally during the session so the timestamps appear in the audio
track.

---

## Open questions to ask afterward

Ask these after the 10-step task is complete. Do not ask during the task; doing so would
constitute coaching.

1. **Inline vs clustered controls**: "When you were posing — the Solve, Keep Pose, and Cancel
   controls — would you prefer those on each individual target row, or grouped together in one
   place below the target list?"

2. **Generating latency**: "When you clicked to generate the preview, how long did the operation
   feel before you expected some kind of progress indicator? At what point would you have assumed
   it had frozen?"

3. **A/B toggle vs overlay diff**: "When comparing the preview to your original animation — did
   switching between them feel natural, or would you have preferred to see them both at the same
   time somehow?"

4. **Dope Sheet panel visibility**: "Did you find the animation editor view of the key poses
   easily, or did you need to open a panel or change a workspace to see them? What would you
   have expected to see by default?"

5. **Left / right foot independence**: "When posing the feet — did you work them together or
   separately? Was it clear which foot target was left and which was right?"

6. **L/R color convention**: "Looking at the viewport targets during posing — without anyone
   telling you — did the red and blue coloring of left and right feel like something you already
   recognized, or did you have to think about it?"

---

## Pass/fail

**Definition of Done** (from `B4ARTISTS_ML_UI_UX_HANDOFF.md` §Definition of done):

> One independent animator completes the journey unaided.

**Pass**: the animator completes all ten steps without source documentation, without the
operator naming any button label, and without any coaching beyond reading the task script
exactly as written. All eight observations in §Observations to log must be logged; the
first-action time (criterion 1) must be 30 seconds or under.

**Fail**: record exactly which step the animator could not complete, what action they attempted,
and what the UI presented at that moment. Do not record a partial pass. The next revision of
this document must address the specific failure before the session is repeated.

The milestone is not complete until a full pass is recorded. A passing automated test suite
does not substitute for this session.
