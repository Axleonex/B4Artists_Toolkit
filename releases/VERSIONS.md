# Releases index

The current build of each add-on. **Install these.**

| Tool | Version | File | Bytes | sha256 (first 12) |
|---|---|---|---|---|
| Anim Assist | **12.0.3** | `b4_anim_assist_v12.0.3.zip` | 540,599 | `a1f3bb73de90` |
| Ghost Tool | **3.3.4** | `b4_ghost_tool_v3.3.4.zip` | 151,529 | `4d946e71d15b` |

Each zip is byte-identical to the matching source folder in this repository
(`anim_assist/`, `ghost_tool/`) — the zip is only the packaged form.

## How to tell which build you have

Read the version from **inside** the add-on, never from the filename:

```bash
python -c "import zipfile,re,sys; z=zipfile.ZipFile(sys.argv[1]); print([re.search(r'\"version\"\s*:\s*\(([^)]*)\)', z.read(n).decode('utf-8','ignore')).group(1) for n in z.namelist() if n.endswith('__init__.py') and n.count('/')==1])" b4_ghost_tool_v3.3.4.zip
```

In Bforartists: **Edit → Preferences → Add-ons**, expand the add-on, read the
version shown there.

## Why older zips are not in this folder

Earlier Ghost Tool builds were published with a **build counter** in the
filename rather than the real version, so filename order contradicted release
order. For example the file once published as `b4_ghost_tool_v7.zip` actually
contained version **3.3.0**, and sorted *after* `b4_ghost_tool_v3.3.3.zip` in a
directory listing — so the newest-looking file was the oldest code.

To remove that trap, superseded zips are no longer kept in this folder. They
remain available two ways:

- **Git history** — every removed zip is still retrievable:
  `git log --diff-filter=D --name-only -- releases/`
- **Tags** — each release is tagged (see below).

All future releases are named with their real version.

## Tags

| Tag | Contents |
|---|---|
| `v12.0.3` | Anim Assist 12.0.3 + Ghost Tool 3.3.4 (this release) |
| `ghost-v3.3.4` | Ghost Tool 3.3.4 |
| `v12.0.2` | Anim Assist 12.0.2 (+ Ghost Tool 3.3.1 as shipped at that commit) |
| `ghost-v3.3.3` | Ghost Tool 3.3.3 |

## Version history

### Ghost Tool

| Version | Notes |
|---|---|
| **3.3.4** | Easing presets refuse zero-width ranges (keyframe ghosts no longer get their handles collapsed); handle recalculation refuses non-Bezier segments and rolls back on non-convergence instead of reporting success; the Initialize repair button catches the ValueError Blender actually raises; ballistic preview guards a zero frame rate; bone ghost drags convert through the bone's channel space so rest-rotated bones follow the cursor. |
| **3.3.3** | Correctness + performance. Ghost generation ~7.4× faster; frame evaluations reduced from 761 to 20 in the measured pass. Fixes playhead loss, point-store data loss on failed evaluation, and stale range/key caches. |
| 3.3.2 | Intermediate optimization pass. |
| 3.3.1 | Shipped alongside Anim Assist 12.0.2. |
| 3.3.0 | Published as `b4_ghost_tool_v7.zip` — see the naming note above. |

### Anim Assist

| Version | Notes |
|---|---|
| **12.0.3** | Blender 5.x compatibility and correctness: PoseBone selection API, persistent app handlers, undo on mutating operators, pose-bone matching and rotation-mode-aware mirroring/layers/matching, range compensation that persists, slotted layer actions, ripple/bake/breakdown/curve-tool correctness, custom-property curves in bone operations, escaped bone names. See `anim_assist/CHANGELOG.md`. |
| **12.0.2** | Onboarding reliability: fixes First Run Setup under the string-based enum API, surfaces the setup action when the shelf is empty, makes the invalid-audio prompt version-independent, completes native hover descriptions. |
| 12.0.1 | Low-jitter trajectory overlay defaults. |
| 12.0.0 | Phase 12 lipsync layer. |

See [`../anim_assist/CHANGELOG.md`](../anim_assist/CHANGELOG.md) for the full
Anim Assist changelog and the versioning policy.
