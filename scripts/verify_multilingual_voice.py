"""Generate real offline VI/EN/mixed samples for each shipped male/female voice."""
import json
import time
import wave
from pathlib import Path

import numpy as np

from app import speech


def main():
    root = Path(__file__).resolve().parents[1] / "reports/app/multilingual-voice"
    root.mkdir(parents=True, exist_ok=True)
    samples = {
        "vi": "Chào các em. Hôm nay chúng ta tìm hiểu về năng lượng.",
        "en": "Good morning, class. Today we will explore energy.",
        "mixed": "Động năng là kinetic energy. Energy is measured in joules.",
        "formula": "Động năng bằng một phần hai khối lượng nhân bình phương vận tốc. A force of twenty newtons acts on the object.",
    }
    voices = speech.list_voices()
    assert len(voices) == 9
    rows = []
    for voice in voices:
        for language, text in samples.items():
            started = time.monotonic()
            audio = speech.synthesize(text, voice["id"], 0, root)
            assert speech.synthesize(text, voice["id"], 0, root)["cached"]
            with wave.open(audio["path"]) as wav:
                assert wav.getframerate() == 48000 and wav.getnchannels() == 1
                duration = wav.getnframes() / wav.getframerate()
                pcm = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2")
            assert 1 < duration < 20 and np.sqrt(np.mean(pcm.astype(float)**2)) > 100
            row = {"voice": voice["id"], "language": language, "duration": round(duration, 3),
                   "elapsed": round(time.monotonic() - started, 3), **audio}
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    text, voice = samples["mixed"], voices[0]["id"]
    for rate in (-3, 0, 3):
        audio = speech.synthesize(text, voice, rate, root)
        with wave.open(audio["path"]) as wav:
            duration = wav.getnframes() / wav.getframerate()
        rows.append({"voice": voice, "language": "mixed", "rate": rate, "duration": duration, **audio})
    speeds = rows[-3:]
    assert speeds[0]["duration"] > speeds[1]["duration"] > speeds[2]["duration"]
    result = {"status": "passed", "engine": speech.VIENEU_VERSION, "samples": rows,
              "scope": "Actual waveform, cache, duration, speed; teacher pronunciation review still required."}
    (root / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    import html

    items = ''.join('<p>' + html.escape(row['voice'] + ' · ' + row['language']) +
                    '</p><audio controls preload="none" src="' + Path(row['path']).name + '"></audio>'
                    for row in rows)
    (root / 'listening-review.html').write_text('<!doctype html><meta charset="utf-8">'
        '<title>BiliClass · Nghe nghiệm thu giọng</title><h1>Bộ nghe thử 6 giọng</h1>'
        '<p>Kiểm tra nghĩa, tên riêng, đơn vị và phát âm; kiểm WAV thành công chưa thay thế việc nghe.</p>'
        + items, encoding='utf-8')


if __name__ == "__main__":
    main()
