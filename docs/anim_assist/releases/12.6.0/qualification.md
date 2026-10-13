# Native Timeline qualification — 12.6.0

Status: implementation and local packaging in progress; native compilation and
manual usability observations pending. No runtime pass is claimed.

## Source evidence

- Add-on commits: 8f1fc5c, 810de59, 3b581a2, 21d7822.
- Native source baseline: Bforartists v5.2.0,
  0a1ca45552dba1006ae0fb5c4dd36657622a4e66.
- Windows libraries: 60d6e96b917568278d400a4024c98da0fb777338.
- Add-on syntax inventory: 201 Python files; archive inventory: 203 files.
- Catalogue: 89 presets; 70 prior mappings, 13 defaults and 17 quick presets
  preserved; valid operator IDs and parameter names checked from source.
- Separate spec review found migration retries and search-ID mismatch;
  both corrected in 3b581a2. Follow-up static spec review passed.
- Independent add-on quality review found restricted startup-data access and
  multi-window disable failures; corrected in 21d7822, re-review passed.
- Native static spec review passed after fixing ordinary-header visibility
  restoration and bounded impossible-size reporting. Native quality review passed for f63e549b after inactive-space ownership and warning-cache lifecycle fixes.
- CMake Release/Ninja configuration succeeded with MSVC 19.44.35228.0 and
  pinned libraries in the C: build cache. This confirms configuration only;
  the application has not yet compiled or launched.
- Native compilation now running from a byte-verified C: source mirror at
  f63e549b; exact local source diff and build record are in native_patches.
- Isolated CONFIG/SCRIPTS/DATAFILES directories are precreated. The exact
  12.6.0 ZIP is staged; startup helper asserts isolation before enabling it.

## Required native observations

Fresh visible two rows; border/window resizing at 100% and 150%; unchanged
area count; direct buttons/search/pins/options; modal commit/Esc; disabled
prerequisites; native playback/scrub/keying; save/reopen and user hiding;
workspace/multiple-window behavior; one-time legacy migration; stable behavior
when geometry cannot grow. Unobserved cases must remain marked pending.

The exact compiled application, portable artifact hashes and recorded
observations will be added after actual build and use. No Blender stand-in
qualifies this native application. No formal test suite was added or run.

Additional cached-space fixes: nativef5f5501 and addon1c76f9c. Both passed static independent quality re-review. Latest local ZIP:576442bytes,SHA256221afae332a3b2217d3e33c6075bac24c22def82cdd7bbf909a2e14f5de72a1b. Exact staged-profile package matches. The C: build source was updated while compiling; a final incremental install build is required before launch to ensure all changed sources/build metadata are current.
