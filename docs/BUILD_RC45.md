# Local RC45 build — 2026-10-16

- Source: `324876a3a5383b1821651664b542639f8f86ac78`
- Version: `1.0.0rc45`
- EXE SHA-256: `aee856c72d0760d9e55c70c4d8741a12c25bb845f3b015d9a87adf7e29ce43b3`
- Local candidate: `.runtime/rc45-324876a/BiliClass/BiliClass.exe`
- User shortcut: `BiliClass RC45` on the Windows desktop.

This is a locally verified candidate, not a published installer or a clean Windows
certification. It reuses the installed RC34 base runtime through directory
junctions and adds 120 OCR runtime files plus separate Latin/Vietnamese ONNX model
packs. The 102 application modules are compiled from the source commit above.
Torch and developer training weights are not bundled. Executables, private
libraries, template uploads, reports and model weights are not committed.

Verification completed:

- 106 relevant source tests passed across layout, Google conversion, native design
  preservation, OCR, narration, downloadable audio and preview caching. A final
  16-test template/conversion subset passed after the last presentation changes.
  These sets overlap.
- Qt result/mascot smoke passed at 1080×700 and 1366×850 with a long lesson title;
  actions stayed within the window, narration remained clickable after scrolling,
  and template selection/page-role saving worked. No QML warnings.
- Google workflow Qt smoke passed with one fixture API call. This does not measure
  live Google latency or translation quality.
- Native PowerPoint rendered and measured the new built-in bilingual and English
  samples: zero FAIL findings; visual-review CHECK findings are retained.
- Frozen EXE OCR recognized the Vietnamese diagnostic image using its bundled
  models and child process, with no external Python path or M0 import.
- Frozen EXE native preview successfully exported slide 1 of the teacher's reported
  87-page Bài 6 deck. Its original bytes were not modified.
- Frozen EXE UI smoke passed at both window sizes, including window/EXE icons.
- RC43 was closed gracefully and RC45 opened independently of Codex. Fifteen
  Windows responsiveness checks passed. All 15 stored lesson records and 638 WAV
  files were unchanged across restart.

Private evidence: `reports/rc45`, `reports/rc45-frozen`.
See [the template contract and limitations](CUSTOM_TEMPLATES_RC45.md).
Existing RC42/RC43 drafts keep their prior quality findings; this release does not
silently certify or redesign them. Templates containing flat artwork text or
unrecognised content frames still require a suitable editable template.
