# Local RC48 build — 2026-10-16

- Source commit: `db598fecc2feda23df9002b84fe01d864493632a`
- Version: `1.0.0rc48`
- EXE SHA-256: `a8d5115e2cd79c185569394aa80caab59f1b5ecae1265a6d3fb5fb9f1b3dfaf4`
- Candidate: `.runtime/rc48-db598fe/BiliClass/BiliClass.exe`
- Desktop shortcut: **BiliClass RC48**.

See [voice progress, bounded parallelism and measured limits](VOICE_PROGRESS_RC48.md).
Verified source was committed/pushed before building once. The build compiles
105 app modules and copies current QML/assets. It reuses the verified RC34
native runtime/model directories through junctions, plus the 120 OCR runtime
files and existing local ONNX packs. This is a local candidate, not a portable
installer or published GitHub binary release. Executables, model packs,
personal lesson records, keys and reports stay out of normal commits.

Checks completed:

- 99 relevant source tests and the source Qt result/mascot/template check passed.
  Qt checks cover 1080×700 / 1366×850, status/actions alignment, centered slide
  controls and the live clock while synthesis is blocked, then frozen on stop.
- Two actual model instances produced eight new valid 48 kHz WAVs through the
  production worker, with no failed chunks. Ready cache avoids further work.
  The gate is forced for this short isolated fixture; ordinary short lessons
  continue using one model.
- Frozen main/settings UI and EXE/window icons passed at both window sizes,
  without a source Python path. Frozen voice settings exercised all six bundled
  samples, saving during playback, cancellation and subject themes without
  QML warnings. This settings check does not run model inference.
- Packaged Universal 2026 templates still generate all three presets in both
  language modes through the frozen offline diagnostic.
- RC47 closed gracefully after its current 274-chunk narration completed.
  RC48 opened the saved lesson on the result screen without starting narration
  again. The completed voice checkpoint still reports 274/274, failed zero.
- Explorer launches RC48 independently. A disposable helper was assigned to an
  explicit Windows kill-on-close job; the app was outside that job and stayed
  visible/responsive after the helper was killed. Ten subsequent Windows
  responsiveness probes passed. The retained library has 16 lessons / 912 WAVs;
  their content/metadata and selected preferences were unchanged during the
  final standalone verification.

The first immediate responsiveness probe while reopening the real lesson
exceeded two seconds; later probes passed after startup settled. These checks
do not certify instant startup or every lesson's rendering/voice quality.
The extra model was tested on source with the actual local SDK/runtime; frozen
UI checks use bundled samples. No clean-machine installation is certified here.

Private evidence: `reports/rc48` and `reports/rc48-frozen`.

The standalone launcher can reopen an existing saved lesson using `--page
result --lesson-id ID`. It passes the arguments through the desktop Explorer
instance and never regenerates that lesson. Opening an already-running matching
app only restores/focuses its existing window.
