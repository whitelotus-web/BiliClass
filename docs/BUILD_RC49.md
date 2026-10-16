# Local RC49 build — 2026-10-16

- Source commit: `5319dfe148a097f758417e7fa265cb64a3c3a900`
- Version: `1.0.0rc49`
- EXE SHA-256: `bcf29c3779eeac35a28d7b05e58bbeb18d771f9607d7f871fdb15f7a137c28a6`
- Candidate: `.runtime/rc49-5319dfe/BiliClass/BiliClass.exe`
- Desktop shortcut: **BiliClass RC49**.

See [operation and limits](VOICE_LIBRARY_MASCOT_RC49.md). Verified source was
committed/pushed before building once. The candidate compiles 106 app modules,
including the new in-memory library filter. It copies current QML/assets and
reuses the verified RC34 native runtime/model directories through junctions,
with the same 120 OCR runtime files and existing ONNX packs. It is a local
candidate, not a portable installer or a published GitHub binary release.

Source checks: 131 relevant tests, Qt result/voice variant/mascot flow at
1080×700 and 1366×850, Qt library/edit/trash/download with Office preview,
and floating mascot navigation/drag/menu placement passed. Actual PowerPoint
opened/rendered the three-speaker fixture and recognized EN/VI/BOTH as audio
media with click action 12 and the expected joined recording duration.

Frozen checks, with no source Python path supplied to the EXE:

- Creation and Settings pages at 1366×850 / 1080×700, EXE/window icons and the
  selected subtitle **Trợ lý dạy học song ngữ** passed without QML warnings.
- Six bundled voice samples, save during preview, cancellation and all subject
  themes passed. This Settings diagnostic does not run model inference.
- The bundled Universal 2026 packs still produced all six preset/language
  combinations through the offline template diagnostic.

RC48 was closed gracefully after its narration checkpoint reported complete
354/354, failed zero. Before registering products, the personal SQLite database
was backed up under the user's private BiliClass backups directory. All WAVs
for English, Vietnamese and both plans were validated before saving their
metadata. No synthesis was run: the current lesson received English-only,
Vietnamese-only and the new bilingual three-control plans using existing WAVs.
Its old two-speaker plan remains available as well.

Lesson text, source references, approval flags, revisions, other lessons,
selected profile/voice/mascot preferences and metadata of all 992 WAVs were
unchanged. Only narration metadata was registered for the current lesson. The
library retains 16 lessons. RC49 reopened that lesson on the result screen
without automatically starting another narration job.

Explorer launched the app independently. A disposable launcher was put in an
explicit Windows kill-on-close job; BiliClass was outside that job and remained
visible after the launcher was killed. Ten subsequent responsiveness probes
passed. The Desktop shortcut points directly to RC49; the verified RC48
shortcut was replaced.

Private evidence is under `reports/rc49`, `reports/rc49-frozen`, and
`reports/lesson-management`. No teacher data, generated WAV, API key, EXE,
runtime junction or model is committed. These checks do not certify all pages
of the real lesson, all animation-dependent narration, or a clean Windows
installation.
