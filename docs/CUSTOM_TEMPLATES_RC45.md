# RC45 — local PowerPoint templates and desktop fixes

The Google Translation API still translates text only. Layout, template assembly,
OCR checks, PowerPoint preview and optional narration run locally. No browser chat
is used by this workflow.

## Teacher templates

Choose **Tạo theo mẫu mới → Chọn mẫu PowerPoint riêng…**. BiliClass copies the
template into the private library, identifies editable title/body frames, and shows
the page numbers for cover, intro, content and ending. Zero omits an optional page.
Save the page roles before previewing/converting. The content page repeats when
the supplied text needs more space; the optional intro receives the first source
unit, rather than an invented AI summary.

For reliable matching, name the editable text boxes **BCL_TITLE** and
**BCL_CONTENT** in PowerPoint's Selection Pane. Otherwise title placeholders,
known neutral markers and the largest suitable text box are used. Tables, text in
grouped shapes and text baked into template artwork are not template insertion
frames. A template without usable frames is rejected before translation.

The selected template's background, native artwork, themes and page transitions
are retained. Text goes into its frames; wide bodies use two columns, narrow ones
use stacked pairs. English follows Vietnamese titles with a smaller italic style.
Template page cloning gives charts/notes their own relationships. Source images
are placed on separate visual pages in the content frame. Source animation and
embedded objects are not recreated by the new-template route. Use the original
design route when preserving these is the priority.

Uploaded templates are documents, not instructions. Their metadata and SHA-256
are stored privately; each conversion snapshots the exact template and verifies
its hash on resume. Private templates, lessons and models stay outside Git.

The three built-in local styles now use actual editable template pages in the
same builder used for preview and conversion. They provide structured, restrained
classroom layouts. This is deterministic layout, not arbitrary graphic design;
there is no claim that every external template or lesson will look perfect.
Existing drafts are not automatically redesigned.

## Desktop fixes

- OCR model paths no longer import the retired M0 translation provider. The
  RC44 candidate's frozen OCR diagnostic exposed this missing-module failure;
  source-only checks did not catch it. RC45 must pass frozen OCR and Qt checks.
- Result width follows the scroll viewport. Long lesson titles wrap, primary
  actions have their own wrapping row, and narration controls wrap as needed.
- Preview errors save a private diagnostic in `temp/preview-errors` instead of
  discarding the underlying exception. A hidden native-preview diagnostic tests
  the packaged Office integration without starting the teacher's classroom.
- Cached previews use NTFS change-journal sequence numbers where available,
  with an exact hash fallback. A file rewritten in the same clock tick with its
  timestamp restored cannot silently reuse the old verified image.

## Verification scope

Tests cover complete VI/EN text through pagination, independent notes links,
preserved template image bytes, embedded source visuals, invalid frames/roles,
template tampering, and importing OCR without M0. Qt smoke exercises custom
template selection/roles and long result titles at 1080×700 and 1366×850.
Native PowerPoint rendering checks the generated bilingual and English decks.
These are local checks and fixture translations, not a live Google speed or
translation-quality benchmark. Native visual review flags remain meaningful;
they are not hidden to make a draft appear certified.
