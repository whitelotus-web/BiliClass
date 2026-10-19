"""Generate public built-in preview assets, never teacher text or model files."""

import hashlib
import json
import shutil
from pathlib import Path

from app import speech
from app.voice_preview import SAMPLE_ROOT, SAMPLE_TEXT, bundled_sample, pair_preview, pair_preview_key


def main():
    SAMPLE_ROOT.mkdir(parents=True, exist_ok=True)
    cache = Path('reports/voice-preview-assets')
    existing = json.loads((SAMPLE_ROOT / 'manifest.json').read_text(encoding='utf-8')) if (SAMPLE_ROOT / 'manifest.json').exists() else {}
    files = {}
    for voice in speech.VIENEU_VOICES:
        source = bundled_sample(SAMPLE_TEXT, voice['id'])
        if source is None:
            source = Path(speech.synthesize(SAMPLE_TEXT, voice['id'], 0, cache)['path'])
        path = SAMPLE_ROOT / source.name
        if source.resolve() != path.resolve():
            shutil.copy2(source, path)
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(voice['name'], path.stat().st_size, flush=True)
    pairs = {}
    for pair in speech.PAIRS:
        result = pair_preview(SAMPLE_TEXT, pair['id'], 0, cache)
        source = Path(result['path'])
        path = SAMPLE_ROOT / source.name
        if source.resolve() != path.resolve():
            shutil.copy2(source, path)
        assert path.name == pair_preview_key(SAMPLE_TEXT, pair['id'], 0)+'.wav'
        pairs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(pair['name'], path.stat().st_size, flush=True)
    (SAMPLE_ROOT / 'manifest.json').write_text(json.dumps({
        'engine': speech.VIENEU_VERSION, 'text': SAMPLE_TEXT,
        'source': 'Built-in VieNeu voices; locally generated BiliClass preview sentence.',
        'files': files, 'pair_files': pairs, 'english_engine': speech.ENGLISH_VERSION,
        'language_files': existing.get('language_files', {}),
    }, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
