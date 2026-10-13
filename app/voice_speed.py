"""Pitch-preserving reading speed, adapted from VieNeuTTSApp core/audio.py.

Source: NguyenSiTrung/VieNeuTTSApp, commit a07bb7db798916852efba15fff7141597f438f22.
Copyright VieNeuTTS App contributors; licensed under Apache-2.0.
Changes: standalone mono validation, bounded settings, no app-specific imports.
See docs/licenses/VieNeuTTSApp-NOTICE.md and Apache-2.0.txt.
"""

import numpy as np

DEFAULT_SAMPLE_RATE = 48000


def _validate_mono(audio):
    if not isinstance(audio, np.ndarray) or audio.ndim != 1 or not np.isfinite(audio).all():
        raise ValueError("Expected finite mono audio.")
    return audio.astype(np.float32, copy=False)


def time_stretch_audio(
    audio: np.ndarray,
    rate: float,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> np.ndarray:
    """Time-stretch 1-D mono float32 audio preserving pitch using WSOLA.

    Uses canonical Waveform Similarity Overlap-Add (WSOLA) in the time domain,
    eliminating STFT phase vocoder artifacts (no 80 Hz frame buzz, no robotic
    phasiness, no sub-bass rumble). Bypasses processing when ``abs(rate - 1.0) < 1e-3``
    to preserve original audio bit-identically with zero overhead.

    The similarity search is an FFT cross-correlation over the same ±15 ms
    window the direct convolution used to scan (Task 5.1): the same
    normalized-correlation maximum, ≥ 3× faster. Search-region spectra and
    candidate energies depend only on the frame index, so they are computed a
    block of frames at a time; only the target's spectrum is per frame.
    """
    mono = _validate_mono(audio)
    if not np.isfinite(rate) or rate <= 0.0:
        raise ValueError(f"rate must be positive, got {rate}")
    if sample_rate <= 0:
        raise ValueError(f"sample_rate must be > 0, got {sample_rate}")
    if abs(rate - 1.0) < 1e-3:
        return mono

    n_in = mono.size
    if n_in == 0:
        return mono
    if n_in < 256:
        target_len = max(1, int(round(n_in / rate)))
        if target_len == n_in:
            return mono
        indices = np.linspace(0, n_in - 1, target_len, endpoint=True)
        return np.interp(indices, np.arange(n_in), mono).astype(np.float32)
    # 25 ms frame is the standard analysis frame for human speech pitch periods (80 - 350 Hz)
    frame_len = int(sample_rate * 0.025)
    if frame_len % 2 != 0:
        frame_len += 1
    if n_in < frame_len * 2:
        frame_len = max(32, (n_in // 3) & ~1)

    s_syn = frame_len // 2
    delta_max = min(frame_len // 2, int(sample_rate * 0.015))

    # Tukey window with 50% flat top retains unaltered speech in the middle
    n_win = np.arange(frame_len, dtype=np.float32)
    taper_len = frame_len // 4
    win = np.ones(frame_len, dtype=np.float32)
    if taper_len > 0:
        left_taper = 0.5 * (1.0 - np.cos(np.pi * n_win[:taper_len] / taper_len))
        win[:taper_len] = left_taper
        win[-taper_len:] = left_taper[::-1]

    target_len = int(round(n_in / rate))
    n_frames = int(np.ceil(target_len / s_syn)) + 2
    out_buf_len = (n_frames + 2) * s_syn + frame_len
    output = np.zeros(out_buf_len, dtype=np.float32)
    output[:frame_len] += mono[:frame_len] * win

    search = _WsolaSearch(mono, frame_len, delta_max, s_syn, rate)
    best_pos = 0
    last_frame = 0
    for frame in range(1, n_frames):
        # WSOLA continues from the segment it chose last: tau + delta == best.
        target_pos = best_pos + s_syn
        if target_pos + frame_len > n_in:
            break
        best_pos = search.best(frame, mono[target_pos : target_pos + frame_len])
        out_start = frame * s_syn
        output[out_start : out_start + frame_len] += mono[best_pos : best_pos + frame_len] * win
        last_frame = frame
        if out_start + s_syn >= target_len:
            break

    # Every frame up to the last one landed the same window one hop apart.
    norm = np.zeros(out_buf_len, dtype=np.float32)
    for frame in range(last_frame + 1):
        norm[frame * s_syn : frame * s_syn + frame_len] += win
    valid_norm = norm > 1e-4
    output[valid_norm] /= norm[valid_norm]
    res = output[:target_len]

    # 2 ms micro-fade at buffer edges prevents boundary clicks during chunk concatenation
    fade_len = min(len(res) // 4, int(sample_rate * 0.002))
    if fade_len > 1:
        fade = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, fade_len, dtype=np.float32)))
        res[:fade_len] *= fade
        res[-fade_len:] *= fade[::-1]

    return np.ascontiguousarray(res, dtype=np.float32)


#: Frames whose search-region spectra :class:`_WsolaSearch` computes per batch
#: (128 × 1201 complex128 ≈ 2.5 MB at 48 kHz — bounded whatever the duration).
_WSOLA_BLOCK_FRAMES = 128


class _WsolaSearch:
    """WSOLA's similarity search: the candidate most like the target segment.

    For frame ``k`` the candidates are the ``frame_len`` windows starting
    within ``±delta_max`` of the nominal analysis position
    ``round(k * s_syn * rate)``; the winner maximizes the correlation with the
    target divided by the candidate's energy. Interior frames read their
    region spectrum and inverse candidate norms from the current block;
    frames whose window is clipped by either end of the input fall back to a
    one-off FFT over the clipped region.
    """

    def __init__(
        self, mono: np.ndarray, frame_len: int, delta_max: int, s_syn: int, rate: float
    ) -> None:
        self._mono = mono
        self._frame_len = frame_len
        self._delta_max = delta_max
        self._s_syn = s_syn
        self._rate = rate
        self._span = frame_len + 2 * delta_max  # a whole region; also the FFT size
        self._count = 2 * delta_max + 1
        self._rows: dict[int, int] = {}
        self._block_start = 0
        self._spectra = np.empty((0, self._span // 2 + 1), dtype=np.complex128)
        self._inv_norms = np.empty(0, dtype=np.float64)

    def _start(self, frame: int) -> int:
        return int(round(frame * self._s_syn * self._rate)) - self._delta_max

    def best(self, frame: int, target: np.ndarray) -> int:
        n_in = self._mono.size
        start = self._start(frame)
        if start >= 0 and start + self._span <= n_in:
            row = self._rows.get(start)
            if row is None:
                self._fill_block(frame)
                row = self._rows[start]
            offset = start - self._block_start
            spectrum = self._spectra[row]
            inv_norm = self._inv_norms[offset : offset + self._count]
            corrs = np.fft.irfft(spectrum * np.fft.rfft(target, self._span).conj(), self._span)
            return start + int(np.argmax(corrs[: self._count] * inv_norm))
        nominal = start + self._delta_max
        low = max(0, start)
        high = min(n_in - self._frame_len, nominal + self._delta_max)
        if low >= high:
            return max(0, min(n_in - self._frame_len, nominal))
        region = self._mono[low : high + self._frame_len].astype(np.float64)
        count = high - low + 1
        corrs = np.fft.irfft(
            np.fft.rfft(region, self._span) * np.fft.rfft(target, self._span).conj(), self._span
        )
        squares = np.cumsum(region * region)
        energies = squares[self._frame_len - 1 :]
        energies[1:] -= squares[: count - 1]
        return low + int(np.argmax(corrs[:count] / np.sqrt(np.maximum(energies, 1e-8))))

    def _fill_block(self, frame: int) -> None:
        n_in = self._mono.size
        starts = [self._start(index) for index in range(frame, frame + _WSOLA_BLOCK_FRAMES)]
        starts = [start for start in starts if start >= 0 and start + self._span <= n_in]
        low = starts[0]
        piece = self._mono[low : starts[-1] + self._span].astype(np.float64)
        offsets = np.asarray(starts, dtype=np.int64) - low
        windows = np.lib.stride_tricks.sliding_window_view(piece, self._span)[offsets]
        self._spectra = np.fft.rfft(windows, axis=1)
        squares = np.zeros(piece.size + 1, dtype=np.float64)
        np.cumsum(piece * piece, out=squares[1:])
        energies = squares[self._frame_len :] - squares[: -self._frame_len]
        self._inv_norms = 1.0 / np.sqrt(np.maximum(energies, 1e-8))
        self._block_start = low
        self._rows = {start: row for row, start in enumerate(starts)}
