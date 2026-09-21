# Optional live whole-body previews 0.15.0

This development feature adds opt-in Live Solve to the existing current-frame
whole-body posing workflow. The local 0.15.0 package has been built after 238
regression cases passed in 21 suites. Packaged/offline qualification also passes. The full original goal remains active and incomplete.

## Behavior

Start Whole-Body Pose, then Start Live Solve. After target edits settle for
150 ms, the existing cooperative solver fits the newest request. A changed
request cancels the preceding unfinished fit before advancing another step.
Unchanged requests do not launch repeated fits. Target settings remain editable
while live fitting. Stop Live Solve or Escape restores the last successful
preview if a fit was unfinished. Keep rejects unsolved or manually edited poses.
Direct control edits stop live work and preserve the newer control channels.

Save, reload, undo/redo, finishing the preview and unregister stop scheduling.
Each modal operator owns one scheduler session, so a timer left over from an
immediate stop/start cannot operate on a newer session. Undo memfiles can retain
SKIP_SAVE property flags; post-restore handlers explicitly turn live scheduling
off. Restored files never automatically restart it.

## Current evidence

- live-pose-v1-regression.json: eight actual-host scheduler/recovery cases pass,
  including two fits on BoneForge, basic/default generated Rigify and basic/default
  human metarigs. Original source actions, key handles, rig modes and raw control
  channels survive Keep/Cancel. Existing numerical gates remain unchanged.
- live-pose-ui-v1.json: failed keyboard simulation timed out after the initial
  live fit; explicit text and key releases corrected the harness.
- live-pose-ui-v2/v3.json: Undo/Redo diagnostics exposed a stale restored live
  flag. They also showed the Python operator harness needed the undo argument
  enabled to exercise the same undo recording as a normal UI operation.
- live-pose-ui-v4.json: complete automated real-window lifecycle passes.
- live-pose-ui-v5.json: additionally passes real Undo/Redo of snapshots captured
  while live fitting; both restored states have scheduling off. Native keyboard
  target edits, rapid restart, newer-request cancellation, Escape, rejected Keep,
  valid Keep, save/reload, Cancel and unregister recovery all pass.
- live-pose-final-v1-regression.json: all 238 cases in 21 suites pass without
  skips on matching source, including the eight live cases. Package building
  changes only the version literal from 0.14.2 to 0.15.0 afterward, recorded in
  package-test-v0.15.0.json.
- offline-live-composed-v0.15.0.json: 76 executed cases in nine groups pass under
  Python network/process denial. The original stale support-test selector failure
  is retained separately; the corrected six-case support group supplies its proof.
- live-pose-ui-package-v1.json repeats the complete real-window journey from the
  extracted archive, verifies imported module hashes and passes all assertions.
  A screenshot records the disposable native rig fixture; it is not an animator
  quality judgment.

## Measured limits

The first five-rig fixture run takes about 1.1-6.1 seconds for the second complete
fit. Default Rigify fit ticks reach about 139 ms. In the actual-window v5 test,
scheduling p95 is 20.86 ms (maximum 27.78 ms), and fit/completion p95 is 43.00 ms
(maximum 134.54 ms). These are local bounded measurements, not broad performance
acceptance. Automatic updating is implemented; responsiveness remains below the
full goal. Profiling idle validation and the longest cooperative steps is next.

All actual-host runs still terminate with the previously reproduced host shutdown
access violation after their assertions. No clean host lifecycle, independent
animator assessment, learned temporal animation, general production-rig support,
or Cascadeur superiority is claimed. The two pose model files remain unchanged.
Ghost Tool and Anim Assist remain separate and unchanged. No Git publication or
installation has occurred.


## Next measured weakness

The unchanged-request profile (live-idle-profile-v1.json) records four preview
JSON parses per tick. Default Rigify spends 1346.68 ms in 400 reads across 100
ticks, with tick median/p95 of 19.22/21.12 ms. The same BoneForge profile measures
4.04/4.56 ms. Component timings are inclusive. LIVE-REQUEST-PERFORMANCE-PLAN-v1.md
declares the next scoped optimization before implementation.

Builder inspection of live-pose-ui-package-v2.png confirms the selected add-on
sidebar and visible target controls. At its default width, expanded target
controls push solve buttons below the visible area and a long instruction label
is truncated. The animator can collapse targets or scroll; independent usability
acceptance remains unknown. The complete packaged operator/event journey passes
in live-pose-ui-package-v2.json.
