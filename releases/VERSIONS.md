# Releases index

The current build of each add-on. **Install these.**

| Tool | Version | File | Bytes | sha256 (first 12) |
|---|---|---|---|---|
| Anim Assist | **12.1.0** | `b4_anim_assist_v12.1.0.zip` | 557,834 | `ee4ea5f1f517` |
| Ghost Tool | **3.4.0** | `b4_ghost_tool_v3.4.0.zip` | 154,640 | `69adf612e996` |
| BoneCraft BFA (optional) | **8.9.9** | `BoneCraft-BFA-8.9.9.zip` | 791,160 | `2bcb76b9fe82` |

Each zip is byte-identical to the matching source folder in this repository
(`anim_assist/`, `ghost_tool/`) — the zip is only the packaged form.
BoneCraft BFA ships as a packaged zip only; the add-on folder inside it is `boneforge/`.

## How to tell which build you have

Read the version from **inside** the add-on, never from the filename:

```bash
python -c "import zipfile,re,sys; z=zipfile.ZipFile(sys.argv[1]); print([re.search(r'\"version\"\s*:\s*\(([^)]*)\)', z.read(n).decode('utf-8','ignore')).group(1) for n in z.namelist() if n.endswith('__init__.py') and n.count('/')==1])" b4_ghost_tool_v3.4.0.zip
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
- **Releases page** — every release, with its notes and zip, is on the repository's
  [Releases page](../../../releases); each is also tagged.

All future releases are named with their real version.
