# RC46 — voice settings latency and mascot subjects

## Measured cause

On this Windows machine, profiling **Lưu giọng và tốc độ** with a saved 87-page
lesson open took 6.906 seconds. Most time was spent in repeated global Qt change
notifications, which rebuilt unrelated hidden UI. The classroom network getter
alone called `psutil.net_if_stats()` 144 times during that one save. The installed
bundled WAVs were valid; a separate native playback/stop probe returned quickly.
This evidence corrected the initial suspicion of a blocked audio driver.

## Changes

- Voice preference and playback notifications are separate from the global
  lesson/settings signal. Model availability is the loaded voice catalogue rather
  than repeated filesystem scans in QML property getters.
- Preferences commit atomically on a dedicated SQLite worker. The green saved
  message appears after the commit succeeds. A busy/failed library reports failure
  and permits retry; it never reports a successful save early.
- Sample preparation has its own bounded worker queue and latest-request token.
  It does not set the whole app busy, so Save and Stop remain available during a
  custom preview. Cancelled results cannot start playing later.
- All six preset samples reuse the engine-versioned WAVs. Rate variants use
  pitch-preserving processing without loading TTS. A first custom sentence still
  needs local synthesis; its speed is not represented by the preset benchmark.
- Network interfaces are a cached snapshot with a separate notification. Opening
  the classroom page or pressing **Làm mới mạng** scans once in a worker thread.
  Unrelated voice/settings changes do not enumerate Windows adapters.
- Mascot preview uses the existing 30-subject catalogue plus **Khác**. Its subject
  is only a preview choice. During teaching the companion still uses the lesson's
  own subject.
- Native vector accessories distinguish subject groups: ruler, atom, flask, leaf,
  computer, globe, book, scroll, notes, palette, ball, scale, compass, shield and
  location marker. Accent/spelling variants such as Vật lí/Vật lý and Mĩ/Mỹ thuật
  map consistently. Milo and Lumi keep their selected character art and motion;
  this is an accessory/colour theme, not a full costume replacement.

## Verification

Source Qt checks use a disposable library, the full production QML, real bundled
WAVs, one Windows playback call and a forbidden-TTS guard for presets. Local
measurements were approximately 11–14 ms to the play call and 11–13 ms for a saved
preference acknowledgement. This is application pipeline latency, not measured
speaker/acoustic delay or a universal hardware promise.

Regression coverage includes saving while a custom preview waits, late-result
suppression after Stop, a locked database remaining responsive and preserving
the old preference until successful retry, one background interface scan, all
catalogue subjects, and unknown-subject fallback. Existing settings/result/mascot
Qt checks and isolated classroom rebind checks also pass. Private reports live
under `reports/rc46`; [packaged verification and build provenance](BUILD_RC46.md)
record the final independent executable.
