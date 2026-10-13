# Anim Assist 12.6.0 publication preparation

Status: prepared locally; push, merge and publication await owner confirmation.

## Assets

One release tag, `v12.6.0`, contains both downloads:

- `b4_anim_assist_v12.6.0.zip`: 577,101 bytes, SHA256
  `60d4c7f10d9f14adde17e0cd5269bb07d4a4fc8f96810a4cd6e67903e5e73193`.
- `Bforartists_5.2.0_AnimAssist_12.6.0_Windows_x64.zip`: 418,370,656 bytes,
  SHA256 `40eb5bec354cb4296301aa376fc3e513d6620a9ab83ff5a4e2eb89b10cb85503`.
- The application archive's `.sha256` file.

The application and checksum are in
`G:/LapArt/Local-Releases/AnimAssist/12.6.0/`. The add-on is also tracked in
`releases/`. The application archive belongs in GitHub Release assets, not Git.

## Publication order after confirmation

1. Recheck the remote branch and exact asset hashes.
2. Push the prepared work branch and create the release pull request.
3. Create the `v12.6.0` release at the reviewed work-branch commit and upload
   all three assets. Use `GITHUB-RELEASE-NOTES.md` as the exact release body.
4. Verify both public download URLs and the uploaded asset sizes/hashes before
   merging the README links into `main`.
5. Record actual publication URLs and status, merge the reviewed pull request,
   then check the README links again.

The prepared README lists only Anim Assist 12.6.0 as current. Historical builds
remain in the versions ledger. Source/runtime limitations stay documented.

## Attribution policy

Outgoing commits use the existing repository identity. Commit messages, release
notes and pull-request text contain no co-author trailers or generated-by banners.
The outgoing files and both Anim Assist packages were checked for attribution
and watermark patterns. Required upstream licensing remains included.
