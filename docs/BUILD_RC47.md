# Local RC47 build — 2026-10-16

- Source commit: `80ad8e403179598df813d12763d0c92e2c9c8efd`
- Version: `1.0.0rc47`
- EXE SHA-256: `46f5c568f8506744b55ac03e57c95e3cc9dd38ccd36a48509f28c0a5fdbac44a`
- Candidate: `.runtime/rc47-80ad8e4/BiliClass/BiliClass.exe`
- Desktop shortcut: **BiliClass RC47**.

The milestone integrates the teacher-supplied Universal 2026 native PPTX packs
and manifest with the new-template flow. Source and all three packs are pushed
to `main`; a second computer can fetch them without files from this machine's
Downloads folder. See [operation, limits and update steps](UNIVERSAL_TEMPLATES_RC47.md).

The local build compiles 105 app modules and copies current QML/assets. It reuses
the verified RC34 native runtime through directory junctions, plus the same 120
OCR runtime files and ONNX packs as RC46. This is a local candidate, not a
portable installer or a published GitHub binary release. No EXE, model, teacher
lesson, private uploaded template, API credential or report is committed.

Verified:

- 126 related source tests passed, covering conversion, the new layout engine,
  private templates, native preservation, input validation and template rules.
- All 69 supplied layout pages were opened/rendered with Microsoft PowerPoint.
  Six short output decks and six output decks with native pictures, equations,
  long tables and a chart were rendered and checked for overflow. There were no
  FAIL issues in those final fixtures; CHECK items for small decorative labels,
  formula reading and visual/semantic review remain explicit.
- Full source Qt check exercised all three presets and two language modes,
  the actual preview button, cache reuse, bookend preference and 1366×850 /
  1080×700 windows, with no QML warnings. Existing result/mascot/custom-template
  Qt checks passed as well.
- Frozen EXE checked its packaged manifest/PPTX files and produced all six
  preset/language combinations offline with `--check-universal-templates`.
  Frozen main UI, settings page and Windows icons passed smoke checks at the
  two window sizes. No source Python path was supplied to the packaged process.
- RC46 closed gracefully; RC47 opened independently of Codex on the creation
  screen and passed 15 Windows responsiveness checks. All 15 lesson records,
  638 WAVs and selected voice/mascot/profile preferences were unchanged.

Private evidence is under `reports/rc47` and `reports/rc47-frozen`. This does not
certify arbitrary source lessons, clean Windows installations, embedded source
animations or all text inside images.
