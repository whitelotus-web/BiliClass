"""Generate five local Kokoro samples and record CPU/offline evidence."""

import json
import shutil
import socket
import time
import wave
from pathlib import Path

import psutil

from app import speech


def main():
    if not speech.kokoro_ready():
        raise RuntimeError("Kokoro model is not installed.")
    output = Path(__file__).resolve().parents[1] / "reports" / "app" / "kokoro-samples"
    output.mkdir(parents=True, exist_ok=True)
    sentence = "Welcome to BiliClass. Today we will explore a new idea together."
    process = psutil.Process()
    records = []
    original_socket = socket.socket

    def deny_network(*_args, **_kwargs):
        raise AssertionError("Kokoro synthesis attempted to create a network socket.")

    try:
        socket.socket = deny_network
        for voice in speech.KOKORO_VOICES:
            started = time.perf_counter()
            result = speech.synthesize(sentence, voice["id"], 0, output / "cache")
            elapsed = round(time.perf_counter() - started, 2)
            target = output / (voice["id"].split(":")[1] + ".wav")
            shutil.copy2(result["path"], target)
            with wave.open(str(target), "rb") as audio:
                duration = round(audio.getnframes() / audio.getframerate(), 2)
                sample_rate = audio.getframerate()
            records.append({
                "voice": voice["id"],
                "seconds": elapsed,
                "duration_seconds": duration,
                "sample_rate": sample_rate,
                "wav": str(target),
                "rss_mb": round(process.memory_info().rss / 1024**2, 1),
            })
        started = time.perf_counter()
        repeat = speech.synthesize(sentence, speech.KOKORO_VOICES[0]["id"], 0, output / "cache")
        cache_seconds = round(time.perf_counter() - started, 3)
    finally:
        socket.socket = original_socket
    report = {"model": speech.KOKORO_MODEL, "runtime": speech.KOKORO_VERSION,
              "network_blocked": True, "cache_hit": repeat["cached"], "cache_seconds": cache_seconds,
              "voices": records}
    (output / "benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"voices": len(records), "cache_hit": repeat["cached"], "cache_seconds": cache_seconds}))


if __name__ == "__main__":
    main()
