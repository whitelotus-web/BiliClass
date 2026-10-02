"""Measure offline VieNeu synthesis on this Windows machine."""

import json
import os
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
MODEL_CACHE = ROOT / ".runtime" / "vieneu-hf"
MODEL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ["HF_HOME"] = str(MODEL_CACHE)
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from vieneu import Vieneu  # noqa: E402


def main():
    process = psutil.Process()
    started = time.monotonic()
    engine = Vieneu(backend="onnx", precision="fp32", threads=4)
    load_seconds = time.monotonic() - started
    load_memory = process.memory_info().rss
    output = ROOT / "reports" / "app" / "vieneu-samples"
    output.mkdir(parents=True, exist_ok=True)
    voices = ["Mai Anh", "Thùy Dung", "Hải Đăng", "Thái Sơn"]
    sentence = "Chào các em. Hôm nay chúng ta sẽ cùng khám phá một ý tưởng mới."
    trials = []
    for name in voices:
        started = time.monotonic()
        samples = engine.infer(sentence, voice=name)
        elapsed = time.monotonic() - started
        path = output / (name.replace(" ", "-") + ".wav")
        engine.save(samples, str(path))
        trials.append({"voice": name, "seconds": round(elapsed, 2), "audio_seconds": round(len(samples) / 48000, 2), "rss_mb": round(process.memory_info().rss / 1024**2), "path": str(path)})
        print(json.dumps(trials[-1], ensure_ascii=False), flush=True)
    report = {"runtime": "vieneu", "load_seconds": round(load_seconds, 2), "load_rss_mb": round(load_memory / 1024**2), "trials": trials}
    (output / "benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
