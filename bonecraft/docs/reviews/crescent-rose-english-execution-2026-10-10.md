# Crescent Rose English execution report

**Completed:** 2026-10-11. The English plan is implemented and ready for owner review. The eight FBX preparation steps, 30 Mechanisms steps, both example files and all 52 annotated English images are complete. Owner confirmation and the later translation phase remain open.

## Release and isolation

- Branch: `codex/bonecraft-9.1.2-manual`; previous English interface audit commit: `9fd0374`. This refresh is a separate local work-branch commit. No push or merge.
- Interface baseline: `releases/BoneCraft-BFA-9.1.2.zip`, SHA256 `9901bdb98da47384522b5137df58e8722f7d4f8c6e20cf1d835630c6bbaafa63`.
- Host: `G:/LapArt/.cache/bforartists/5.2.0/portable/Bforartists-5.2.0-Windows/bforartists.exe`, Bforartists 5.2.0, build `0a1ca45552db`. The same binary reports underlying Blender 5.3.0 Alpha.
- Release add-on extracted to `G:/LapArt/output/crescent-rose-work/9.1.2-en/scripts/addons/boneforge`; GUI version 9.1.2 verified, both interfaces English, Show Helpers enabled, Scene Properties visible, default theme and UI scale 1.0.
- Owner sessions under `X:/5.2.0/` were not manipulated. The source FBX and 18 adjacent JPEGs remain untouched. Baseline examples, chapter and image/annotation directory are preserved under the scratch work directory's `baseline/`.

The initial `5.3/config/` staging was not the host's actual preference location. A background resource-path probe identified its executable-adjacent `portable/config/` and `portable/scripts/`. The initial diagnostic preference copy was preserved; after closing that GUI, the scratch preferences were installed into the actual portable directory. A fresh probe and reopened GUI verified the isolated add-on and settings. Evidence: `profile-bootstrap.json`, `portable-profile-probe.json`, `portable-profile-verified.log` and genuine preflight captures. The owner's normal configuration was not written. Preserve this test profile with the review evidence.

The supported desktop launch API timed out. Opening the same designated executable through Explorer reached a Windows security dialog; the owner handled Run. No security setting was changed. Subsequent GUI work used the supported Computer Use API against the identified test window.

## Delivered and corrected

The FBX was prepared manually through the interface, saved and reopened. The parts example is that P8 checkpoint: 37 source islands joined into 15 named meshes, 9,366 vertices, applied rotation/scale, geometry-centred origins, approximately 1.996805 m combined height, and 12 packed maps at 1024 by 1024. Base Color maps use sRGB; data maps use Non-Color and tangent-space Normal Map nodes. The combined height is a geometry measurement, not an individual material object's Dimensions value.

The rig was hand-built from the prepared file, with 14 mechanisms, two Sequences and three Forms. Both supplied examples were replaced only after the candidate passed validation. The saved rig is in Scythe with all controls zero. The prepared-file shortcut starts from the same validated P8 checkpoint; it was reloaded, not independently rebuilt by a second novice tester.

| Discovered gap | Completed correction |
| --- | --- |
| FBX preparation omitted | Eight illustrated preparation steps and explicit 15-part grouping table |
| Blender shortcuts differed from this Bforartists keymap | Visible mode menu, Ctrl+R scale and Ctrl+W move instructions |
| Plate/strut picks obscured | Front/Right views and Frame Selected before starting each guide; explicit pick order |
| RearSpike creation omitted | Both Grip and RearSpike Hinges taught; RearSpike axis corrected to negative X |
| Old fold left blade spread away from receiver | Scythe-to-Rifle targets updated to Blade2 120, BladeTip 70, Blade1 10, PlateL 30, HeadMount 90 and Pole 0.6 |
| Capture Step wording and numbering stale | Both Move Slider to End and Record Step N illustrated; N counts target entries |
| Test and Forms state unclear | Prior-pose restoration, capture arming, Cancel and Go to Scythe behavior explained |
| Old captures and stale index caveat | All 52 final English PNGs replaced/added; index and quick-reference synchronized |
| PDF images exceeded page width | Chapter-only print bounds, step page breaks and visible captions; orphan caption corrected |

Scythe-to-Rifle intervals are 0-0.25 (Blade2/Tip), 0.25-0.5 (Blade1/PlateL), 0.5-0.8 (HeadMount), and 0.8-1 (Pole). Rifle-to-Compact records Grip 90 and RearSpike 90 over 0-0.5, then Magazine 0.04 and Bolt 0.06 over 0.5-1. Every target uses Ease In Out. Individual controls in saved Forms remain zero; Sequence values are Scythe (0,0), Rifle (1,0), Compact (1,1).

## Owner-requested visual instruction revision - 2026-10-11

The owner requested visible directions for every step after the initial English delivery (commit `69c2e60`). The audit found 31 of the 46 images had no annotation marks. This revision supplies 52 annotated screenshots across all eight preparation steps and 30 Mechanisms steps. Each image has numbered red circles or boxes and a matching action key directly below it. Numbers restart per image; captions distinguish interaction targets from expected-result checks.

Six additional command/detail crops show Clear and Keep Transformation, By Loose Parts, Join, Origin to Geometry, Edit Pivot and capture Cancel. They use the genuine 9.1.2 raw captures already retained from the replay. The Join crop comes from the Object-menu capture used for Origin to Geometry; its caption explicitly directs the reader to use the two-piece selection shown separately. The Blade1 preparation caption now correctly describes two source plates selected before joining. Result-form screenshots retain the relevant interface controls and sequence percentages.

English validation and PDF rendering were rerun after the annotation/caption changes. Existing host and rig evidence remains applicable because the examples and add-on are unchanged. The annotations and new crops were produced with the existing deterministic helper; no interface content was synthesized. Translation work still requires direct owner confirmation.

## Genuine capture provenance

Raw JPEG bytes and capture metadata: `G:/LapArt/output/crescent-rose-captures/9.1.2/en/`. The desktop API emits JPEG despite its generic screenshot interface. Format-only PNG copies under `9.1.2/png/en/` feed the unchanged `annotate_manual_images.py`, explicitly scoped to `en`. Cropping, scaling and red annotations use the English entry of `circles.json`; all non-English entries are unchanged.

`capture-manifest-en.json` maps all final stems to raw captures. The committed [evidence manifest](crescent-rose-english-evidence-9.1.2.json) records final/raw image hashes, dimensions, sizes, example and chapter hashes, and review artifact hashes. All 52 final images were visually reviewed in contact sheets, with individual close-up checks of corrected targets; incorrect marks and clipped targets were fixed and reopened. Every image is at most 1400 pixels wide and 300 KiB. The chapter is below 50 KiB and retains attribution/licence.

Step 24's two button-state captures were recaptured with a temporary empty third Sequence in the GUI to show the correct first-group values (Blade2 120, BladeTip 70). The crop contains the recording controls, not the sequence list/count. The scene was reverted to the saved two-Sequence candidate afterward. This temporary demonstration sequence is not in the delivered rig. Other settings screenshots may show a later completed list while illustrating the named control.

The principal replay capture window was 2026-10-11 03:05:25.590 UTC (FBX options) to 06:54:52.985 UTC (Compact): 3 h 49 m 27.395 s, including inspection and capture work. Later button-state/preflight recaptures and publication work are outside that window. This is not a beginner completion-time benchmark; the chapter recommends separate preparation and Mechanisms sessions.

## Validation and rendered review

All scratch scripts/logs below are under `G:/LapArt/output/crescent-rose-work/9.1.2-en/`.

| Check | Result and evidence |
| --- | --- |
| Prepared geometry/materials | PASS; `gui-P8-check.json/log`, 37-island reference comparison `gui-P4-geometry-map.json` |
| Unchanged shipped host test | Exit 0, both example passes, `RESULT OK`, no traceback; `candidate-host-test.log` |
| Individual controls/reload | Exit 0; 24 half/full-travel samples across 12 controls, finite motion, linked plates/strut, restoration tolerance 1e-4, Forms round trip; `candidate-handle-checks.json/log` |
| Rig Validator | No non-pass findings, including no root warning; `candidate-rig-records.json` |
| Automatic script execution | Disabled before reload; file opened with `use_scripts=False` |
| English manual | PASS test_manual (en); all English assertions retained, no `--partial`; `english-validation-build.log` |
| Annotation coverage | PASS; 38 steps, 52 images, 121 numbered marks; every caption key matches its image badges; `visual-instructions/coverage.json` |
| Joined HTML | Internal links resolve; linked to reviewed repository images |
| Final English PDF | 107 pages; chapter 12 starts on page 58; zero image overflow; all pages rendered and visually reviewed |
| Printed page numbering | PASS; centered Page X of 107 footer on all 107 pages, no overlap; body text, image positions and link counts unchanged; `page-number-check.json` beside the PDF |
| Scope and whitespace | Non-English annotation entries unchanged; scoped `git diff --check` passes; no source, helper, test, version or release ZIP changes |

Reproduction commands ([PowerShell], with the same scratch setup):

```powershell
$testHost = 'G:/LapArt/.cache/bforartists/5.2.0/portable/Bforartists-5.2.0-Windows/bforartists.exe'
$work = 'G:/LapArt/output/crescent-rose-work/9.1.2-en'
& $testHost --background --factory-startup --python-exit-code 1 --python "$work/test-in-addon-context.py"
& $testHost --background --factory-startup --disable-autoexec --python-exit-code 1 --python "$work/check-candidate-handles.py"
python -W error "$work/validate-build-english.py"
python "$work/review-pdf.py"
```

The first wrapper creates the missing `boneforge` preference entry before invoking the unchanged `tests/run_one_host.py -- test_crescent_rose_host`. It suppresses no assertion. The original raw harness had printed PASS alongside a preferences traceback; that run was not accepted as final evidence. Informational duplicate-panel notices remain harmless in the passing log.

The manual wrapper uses the prior audit's temporary packaged source/dependencies and sets both checker language lists to `('en',)`. It retains completeness, labels, structure, link, image and size checks, and invokes the unchanged PDF builder with explicit `en`. It is not a translated-edition pass. No shipped helper changed, so a new helper-code test suite was not needed.

A possible shared PDF helper edit was routed through the canonical evaluator; it returned `DESKTOP_HOST_ADAPTER_QUALIFICATION_FAILED` because this workspace resolves to UNC, with no `actual_lane`. That coding route was not used. The final solution is chapter-local Markdown image attributes and scoped print CSS supported by the existing renderer. No routing-success claim or shared-helper change is made.

Review artifacts are `G:/LapArt/output/bonecraft-manual/9.1.2-en-review/BoneCraft_Manual_en.html` and `BoneCraft_Manual_en.pdf`; page renders/contact sheets and `pdf-layout-check.json` are beside them. Every final image and tutorial page was reviewed; the final index, quick-reference, piston caption and last pages were checked again after corrections.

## Page-numbering correction - 2026-10-11

The owner identified missing printed page numbers. The English index now supplies a print-only bottom-center page counter, retained by future English builds. The rebuilt 107-page PDF passed English validation and footer checks on every page; the first, dense preparation and last pages were visually inspected. Body text, image placements, page count and per-page link counts match the prior PDF. The shared renderer and translated sources are unchanged. Verification script and before/after renders are under the scratch work directory's `page-numbering/`.

## Endpoint and remaining owner gate

English implementation and verification are complete. Updated chapter, examples, screenshots, plan/design, README files, interface audit and this report constitute the review package. Original planning documents are preserved as `*-original.md`.

These are teaching poses for a fan-made mesh, not a collision-certified physical mechanism or exact fictional transformation. Visual replay and finite/restoring transforms do not establish collision-free engineering. There has been no independent novice usability study. The broader manual's other tools retain their source-audit status; this GUI replay covers the Crescent Rose tutorial.

Await direct owner confirmation of English before activating ja, zh, ko, fr, es or pt translation work. No translated chapters/captures/PDFs, localization tables, release archive, or version number were changed. Unrelated Anim Assist and Ghost Tool work remains outside the commit.
