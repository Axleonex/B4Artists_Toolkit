# Contextual fallback prior experiment v10

Status: REJECTED. All 36 prespecified variants completed. The incumbent V9
research pair is retained, with identical validation and previously observed
confirmation reports. No temporal model is promoted into the add-on.

The experiment uses the same 31 training clips, four catalog-group-excluded
base predictions, 480 validation windows, frozen comparison gates and old
validation protection as V9. Four binary root/body context priors are each
crossed with three kernel widths and three regularizations. The prior is present
only when surrounding observations exist; learned kernel residuals modify that
prior before convex projection. No new files are downloaded. Prior confirmation
remains observed diagnostic data and is not used for selection.

Six focused tests pass in desktop Python and actual Bforartists. All nine
zero-prior model fits reproduce V9's compact candidate metrics exactly, and
all four cross-fit prediction hashes match V9. The best nonzero-prior variant
still loses to V9's frozen validation objective. This rejects the proposed
context-prior change under this protocol; it does not show that surrounding
motion is generally unhelpful, nor identify a unique cause of the failures.

Evidence: training/b4artists_ml/results/context_prior_v10/report.json,
folds.json, selection.json and protocol.json; the host tests are recorded in
results/context-prior-host-v10-regression.json. Host shutdown remains the known
3221225477 failure after passing assertions. A second complete training run was
not performed for this rejected change; exact controls and stored source/protocol
make the experiment repeatable, but only the performed checks are claimed.

Next product work addresses continuous whole-body preview interaction. Accepted
learned motion, physical refinement, broader rigs, independent animator testing
and equivalent Cascadeur comparison remain required. None is replaced by the
research results or the proposed live posing interface.
