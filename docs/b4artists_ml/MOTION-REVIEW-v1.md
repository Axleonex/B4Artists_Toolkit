# Motion review v1

Open `motion-review-v1/index.html` manually to inspect 96 fixed validation examples. Each shows the recorded reference, the strongest procedural control for that validation cohort, and learned candidates v19 and v20. The viewer embeds its motion data, so it needs no server, account or network resources.

Every exposed validation cohort contributes its first deterministically sampled interval; no examples were chosen for their appearance. The strongest procedural control was selected using the already exposed cohort reports, not an inference-time oracle. Comparisons use the same camera, scale, frame and reference basis. Endpoint markers and root trails can help expose priority drift and root-motion changes. Optional endpoint holds are labeled and can be disabled. Displayed metrics summarize the whole cohort, not just the selected example.

The 96 examples contain 1,888 displayed frames, four methods and 17 joint centers. The embedded payload is 4,345,915 bytes. Build assertions verified full priority poses and true skeletal edge preservation before display conversion; serialized priority points match exactly across methods. Static verification confirmed matching embedded/standalone data, unique controls and syntactically valid JavaScript without executing the page.

Browser URL security policy blocked local-file navigation. No alternate browser surface or indirect rendering was attempted. Browser interaction, visual layout and independent animator assessment remain unverified. No reviewer ratings were entered or exported by the agent. The optional feedback fields begin unrated and only download a local JSON file when a reviewer explicitly chooses Export.

Joint-center skeletons do not display mesh deformation, axial twist or collisions. These validation partitions have already been used for development. This artifact is neither a held-out qualification nor an equivalent Cascadeur comparison. Six new confirmation clips remain sealed. Neither temporal candidate qualifies for inclusion in the addon.

Evidence: `training/b4artists_ml/results/motion-review-build-v1.json`, `motion-review-static-verification-v1.json`, and the fixed sampling plan `training/b4artists_ml/motion_review_plan_v1.json`.
