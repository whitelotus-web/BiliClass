import io
import wave

from app.presentation_audio import joined_wav


def test_exported_and_embedded_audio_has_an_actual_pause_between_paragraphs(tmp_path):
    folder = tmp_path / 'audio'
    folder.mkdir()
    for key in ('title', 'body'):
        with wave.open(str(folder / (key + '.wav')), 'wb') as wav:
            wav.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
            wav.writeframes(b'\1\0' * 2400)
    data, duration = joined_wav(tmp_path, ['title', 'body'])
    with wave.open(io.BytesIO(data), 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        assert wav.getnframes() == 2 * (2400 + 10800)
        assert frames[2400*2:(2400+10800)*2] == b'\0\0' * 10800
        assert duration == 1100
