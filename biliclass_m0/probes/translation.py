import csv
import gc
import re
import statistics
import threading
import time

import psutil

from ..benchmark_data import PAIRS
from ..paths import model_root, output_root


def find_package(direction: str):
    for candidate in sorted(model_root().glob(f"{direction}-*"), reverse=True):
        models = list(candidate.rglob("model.bin"))
        tokenizers = list(candidate.rglob("sentencepiece.model"))
        if models and tokenizers and (candidate / "provenance.json").exists():
            return models[0].parent, tokenizers[0]
    return None


def translate_text(text: str, source: str = "vi") -> str:
    import ctranslate2
    import sentencepiece

    package = find_package("vi-en" if source == "vi" else "en-vi")
    if not package:
        raise RuntimeError("Chưa có gói dịch thử nghiệm. Chạy scripts/download_models.py trước.")
    model, tokenizer_path = package
    tokenizer = sentencepiece.SentencePieceProcessor(model_proto=tokenizer_path.read_bytes())
    translator = load_translator(model, ctranslate2)
    try:
        result = translator.translate_batch(
            [tokenizer.encode(text, out_type=str)], beam_size=4, max_decoding_length=256
        )
        return decode_candidate(tokenizer, result[0].hypotheses[0])
    finally:
        translator.unload_model()


def load_translator(model, ctranslate2):
    # Native file loaders can mishandle Vietnamese Windows paths. Python reads
    # Unicode paths correctly; CT2 accepts a named in-memory file mapping.
    files = {path.name: path.read_bytes() for path in model.iterdir() if path.is_file()}
    return ctranslate2.Translator(
        "biliclass-candidate", files=files, device="cpu", compute_type="int8", intra_threads=4
    )


def decode_candidate(tokenizer, pieces):
    # Argos packages can emit a literal SentencePiece separator inside a piece.
    # Preserve regular underscores: they may be meaningful in code/formulas.
    return tokenizer.decode(pieces).replace("▁", " ").strip()


def run() -> dict:
    import ctranslate2
    import sentencepiece

    if any(find_package(direction) is None for direction in ("vi-en", "en-vi")):
        return {
            "status": "needs_setup",
            "message": "Thiếu gói dịch thử nghiệm VI–EN hoặc EN–VI.",
            "command": "python scripts/download_models.py",
        }
    process = psutil.Process()
    stop = threading.Event()
    samples = []

    def sample():
        process.cpu_percent()
        while not stop.wait(0.1):
            samples.append((process.memory_info().rss, process.cpu_percent()))

    monitor = threading.Thread(target=sample, daemon=True)
    monitor.start()
    rows, timings = [], []
    try:
        for source in ("vi", "en"):
            direction = "vi-en" if source == "vi" else "en-vi"
            model, tokenizer_path = find_package(direction)
            tokenizer = sentencepiece.SentencePieceProcessor(model_proto=tokenizer_path.read_bytes())
            start = time.perf_counter()
            translator = load_translator(model, ctranslate2)
            load_ms = (time.perf_counter() - start) * 1000
            latencies = []
            for index, (category, vi, en) in enumerate(PAIRS, 1):
                text, reference = (vi, en) if source == "vi" else (en, vi)
                started = time.perf_counter()
                result = translator.translate_batch(
                    [tokenizer.encode(text, out_type=str)], beam_size=4, max_decoding_length=256
                )
                output = decode_candidate(tokenizer, result[0].hypotheses[0])
                latency = (time.perf_counter() - started) * 1000
                latencies.append(latency)
                missing = [
                    number
                    for number in re.findall(r"\d+(?:\.\d+)?", text)
                    if number not in re.findall(r"\d+(?:\.\d+)?", output)
                ]
                rows.append(
                    {
                        "case": f"{direction}-{index:02}",
                        "category": category,
                        "source": text,
                        "output": output,
                        "reference_for_review": reference,
                        "latency_ms": round(latency, 1),
                        "missing_numbers": "|".join(missing),
                        "human_quality_score": "",
                        "review_notes": "",
                    }
                )
            timings.append(
                {
                    "direction": direction,
                    "cases": len(latencies),
                    "load_ms": round(load_ms, 1),
                    "p50_ms": round(statistics.median(latencies), 1),
                    "p95_ms": round(statistics.quantiles(latencies, n=100)[94], 1),
                    "model_bytes": sum(p.stat().st_size for p in model.rglob("*") if p.is_file()),
                }
            )
            translator.unload_model()
            del translator
            gc.collect()
    finally:
        stop.set()
        monitor.join(timeout=2)
    path = output_root() / "translation-review.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {
        "status": "review_required",
        "candidate": "Argos Translate 1.9 / CTranslate2 INT8 CPU",
        "total_cases": len(rows),
        "timings": timings,
        "peak_rss_mb": round(max((sample[0] for sample in samples), default=0) / 1024**2, 1),
        "peak_cpu_percent": max((sample[1] for sample in samples), default=0),
        "number_surface_flags": sum(bool(row["missing_numbers"]) for row in rows),
        "review_csv": str(path),
        "inference_mode": "local_files_only",
        "notes": [
            "Suy luận chỉ đọc model local; chưa phải kiểm chứng OS chặn Internet.",
            "CPU% có thể >100 vì dùng nhiều core; chất lượng cần giáo viên chấm CSV.",
            "Số đổi thành chữ cũng bị gắn cờ; không tự coi đó là sai nghĩa.",
            "Đây là baseline model thô, chưa có bộ bảo vệ thuật ngữ/công thức của M3.",
        ],
    }
