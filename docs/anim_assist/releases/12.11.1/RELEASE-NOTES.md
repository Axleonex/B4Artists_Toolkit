# Anim Assist 12.11.1

Find and native menu actions now use one native Undo entry per edit. The shared Timeline dispatcher no longer adds the manual checkpoint intended for canvas actions to these native UI calls. Direct canvas controls retain their checkpoint, and asynchronous slider commit/cancel handling is preserved.

The correction is limited to Timeline action dispatch. Existing animation-editor tools and layouts are retained.

The reproducible archive contains the existing 215-file runtime inventory plus the repository GPL license. Run `package.py` from a Git checkout after staging source changes; the adjacent receipt records all member hashes and the archive hash. A different existing archive is never overwritten.
