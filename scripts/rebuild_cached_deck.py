"""Rebuild a candidate using existing translation cache only; never publish it.

The cache connection is read-only. A cache miss stops before any key, quota or
network access. Source and saved lessons remain unchanged; inspect the output
and layout map before choosing to import a candidate in the application.
"""

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from threading import Event

from app.google_translation import TranslationProblem, Translator
from app.native_bilingual import assemble, extract
from app.slide_refinement import source_media_preserved


class CacheOnly:
    def __init__(self, path):
        self.path = path.resolve(strict=True)

    def cached(self, identity):
        with closing(sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)) as db:
            row = db.execute('SELECT value FROM cache WHERE id=?', (identity,)).fetchone()
            return row[0] if row else None

    def reserve(self, *args, **kwargs):
        raise TranslationProblem('offline_cache_missing',
                                 'Cache chưa đủ để dựng lại. Không gửi mạng hoặc trừ hạn mức; bản cũ được giữ.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('parallel_columns', 'english_only'), default='parallel_columns')
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    if args.output.exists() or args.output.resolve() == source:
        parser.error('Choose a new output directory; do not overwrite a saved candidate.')
    with source.open('rb') as stream:
        original = hashlib.file_digest(stream, 'sha256').hexdigest()
    translator = Translator.__new__(Translator)
    translator.store, translator.budget = CacheOnly(args.data / 'translation_api/usage.db'), 1
    manifest = extract(source, args.mode, preserve_design=True, same_slide=args.mode != 'english_only')
    pending = [unit for unit in manifest['units'] if unit['language'] not in {'en', 'neutral'}]
    translated = translator.translate([unit['text'] for unit in pending], Event())
    values = {unit['id']: {'en': unit['text']} for unit in manifest['units'] if unit['language'] in {'en', 'neutral'}}
    values.update({unit['id']: {'en': value} for unit, value in zip(pending, translated, strict=True)})
    args.output.mkdir(parents=True)
    output = assemble(source, args.output / 'candidate.pptx', manifest, values, args.mode)
    with source.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == original
    assert source_media_preserved(source, output, 'source')
    (args.output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    report = dict(status='candidate_only', source_sha256=original, cached_units=len(pending),
                  output=str(output), network_calls=0, quota_mutations=0,
                  source_unchanged=True, saved_lesson_unchanged=True, media_preserved=True,
                  needs_native_inspection=True, needs_teacher_review=True)
    (args.output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    main()
