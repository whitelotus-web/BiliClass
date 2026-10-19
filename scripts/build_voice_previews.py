"""Generate public built-in preview assets, never teacher text or model files."""

import hashlib
import json
from pathlib import Path

from app import speech
from app.voice_preview import SAMPLE_ROOT, SAMPLE_TEXT, pair_preview, pair_preview_key


def main():
    SAMPLE_ROOT.mkdir(parents=True, exist_ok=True)
    files = {}
    for voice in speech.VIENEU_VOICES:
        result = speech.synthesize(SAMPLE_TEXT, voice['id'], 0, SAMPLE_ROOT)
        path = Path(result['path'])
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(voice['name'], path.stat().st_size, flush=True)
    pairs = {}
    for pair in speech.PAIRS:
        result = pair_preview(SAMPLE_TEXT, pair['id'], 0, SAMPLE_ROOT)
        path = Path(result['path'])
        assert path.name == pair_preview_key(SAMPLE_TEXT, pair['id'], 0)+'.wav'
        pairs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(pair['name'], path.stat().st_size, flush=True)
    (SAMPLE_ROOT / 'manifest.json').write_text(json.dumps({
        'engine': speech.VIENEU_VERSION, 'text': SAMPLE_TEXT,
        'source': 'Built-in VieNeu voices; locally generated BiliClass preview sentence.',
        'files': files, 'pair_files': pairs, 'english_engine': speech.ENGLISH_VERSION,
    }, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
