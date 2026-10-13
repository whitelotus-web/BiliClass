The pitch-preserving WSOLA transform in `app/voice_speed.py` is adapted from
`src/vienetts_app/core/audio.py` in **VieNeuTTSApp**.

- Source: https://github.com/NguyenSiTrung/VieNeuTTSApp
- Revision: `a07bb7db798916852efba15fff7141597f438f22`
- Copyright: VieNeuTTS App contributors.
- License: Apache License 2.0, included in `Apache-2.0.txt`.
- Modifications: extracted standalone transform, finite mono/rate validation,
  removed application-specific imports. Original transform and FFT search retained.

Speech synthesis uses the separate VieNeu SDK/model by Phạm Nguyễn Ngọc Bảo,
not a copied workstation or cloned personal voice. See `docs/THIRD_PARTY.md`.
