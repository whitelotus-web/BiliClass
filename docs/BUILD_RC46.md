# Local RC46 build — 2026-10-16

- Source: `b9f84325bfe0f74a74ba49f010761f8270747698`
- Version: `1.0.0rc46`
- EXE SHA-256: `b05035f95073e60b0f6e484015ee1177c63d17c66a32f8f916c8ccf969b5f1d1`
- Candidate: `.runtime/rc46-b9f8432/BiliClass/BiliClass.exe`
- Desktop shortcut: **BiliClass RC46**.

The source milestone contains the settings responsiveness fix, background network
snapshot, independent voice preview/save requests, and subject accessory picker.
The final candidate also fixes the substring collision between Khoa học and Hóa
học. An earlier RC46 candidate was tested but was never opened for the teacher.

The local package compiles 104 app modules and copies their QML/assets. It reuses
the installed RC34 native runtime through directory junctions, plus the same 120
OCR runtime files and local ONNX packs used in RC45. This is a local candidate,
not a published installer or clean-Windows certification. No executable, model,
personal lesson, uploaded template, report or credential is committed.

Verified:

- 87 related source tests passed for voice preferences/preview, speaker and speed,
  cancellation, narration, speech extraction, CPU thread budgets, subject names
  and classroom data. The final subject fix passed its focused four-test subset.
- Full Qt voice check on source and frozen EXE: all six presets reuse valid WAVs;
  no TTS inference is allowed for them, speed adjustment remains model-free,
  Save completes during a pending preview, and Stop suppresses late playback.
- Final frozen measurements: approximately 12–39 ms to the play call, 11 ms to
  saved acknowledgement, maximum observed UI timer gap 95 ms. These measure the
  local application pipeline, not acoustic output or arbitrary custom synthesis.
- All 30 catalogue subjects mapped to a theme. Science and chemistry are checked
  separately; Vật lí/Vật lý and Mĩ/Mỹ thuật aliases agree. Custom preview names
  retain the general fallback, and preview choice does not change the lesson.
- Existing settings, result/mascot and isolated classroom rebind checks passed.
  Frozen main UI checks passed at 1366×850 and 1080×700 with no QML warnings.
- RC45 closed gracefully. RC46 opened in Settings independently of Codex and
  passed 15 Windows response checks. All 15 lesson records, 638 WAVs and selected
  voice/mascot/profile preferences were unchanged across restart.

Private evidence: `reports/rc46`, `reports/rc46-frozen`.
See [measured cause and functional scope](SETTINGS_LATENCY_RC46.md).
