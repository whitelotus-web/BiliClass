"""Measure only the optional reference layer, with synthetic public terms."""

import argparse
import json
import tempfile
import time
import tracemalloc
from contextlib import closing
from pathlib import Path
from threading import Event

from app.library import Library
from app.terminology_seed import ensure_seed, seed_pack, statistics, terms_for
from app.translation_knowledge import prepare, prompt_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default='reports/rc168-knowledge-benchmark.json')
    parser.add_argument('--live', action='store_true', help='One public reference query, no teacher data or API key')
    args = parser.parse_args()
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-reference-', dir=report.parent) as temporary:
        root = Path(temporary)
        with closing(Library(root)):
            pass
        empty_bytes = (root / 'library.db').stat().st_size
        tracemalloc.start()
        started = time.perf_counter()
        with closing(Library(root)) as library:
            ensure_seed(library)
        install_ms = (time.perf_counter() - started) * 1000
        install_peak = tracemalloc.get_traced_memory()[1]
        seed_database_bytes = (root / 'library.db').stat().st_size - empty_bytes
        rows = [dict(slide=i+1, text='; '.join(row['vi'] for row in terms_for('Toán'))) for i in range(100)]
        config = dict(translation_knowledge_version=1, translation_knowledge_online=False, subject='Toán',
                      grade='11', title='Các khái niệm cơ bản', source_sha256='synthetic-benchmark')
        tracemalloc.reset_peak()
        started = time.perf_counter()
        value = prepare(root, root, config, rows, Event())
        cold_ms = (time.perf_counter() - started) * 1000
        selection_peak = tracemalloc.get_traced_memory()[1]
        started = time.perf_counter()
        assert prepare(root, root, config, rows, Event()) == value
        resume_ms = (time.perf_counter() - started) * 1000
        tracemalloc.stop()
        result = dict(seed=statistics(), serialized_pack_bytes=len(json.dumps(seed_pack(), ensure_ascii=False).encode()),
                      added_library_bytes=seed_database_bytes, install_ms=round(install_ms, 1),
                      install_python_peak_bytes=install_peak, synthetic_slides=len(rows),
                      selection_ms=round(cold_ms, 1), resume_ms=round(resume_ms, 1),
                      selection_python_peak_bytes=selection_peak,
                      job_context_bytes=(root / 'terminology-context.json').stat().st_size,
                      provider_context_chars=len(prompt_context(value)),
                      reference_cache_bytes=(root / 'translation_knowledge/references.db').stat().st_size,
                      scope='Synthetic offline layer only; Python allocations, not whole-app RAM or translation service latency.')
        if args.live:
            from app.terminology_lookup import lookup

            started = time.perf_counter()
            try:
                hint = lookup('không gian vectơ', 'Toán', Event(), deadline=time.monotonic()+5)
                result['live_public_reference'] = dict(status='matched' if hint else 'no_exact_match',
                    source_url=hint['source_url'] if hint else '')
            except Exception as exc:
                result['live_public_reference'] = dict(status='unavailable', exception=type(exc).__name__)
            result['live_public_reference']['elapsed_ms'] = round((time.perf_counter()-started)*1000, 1)
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
