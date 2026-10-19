"""Generate only public, fixed language samples; never teacher content."""

import hashlib
import json
import shutil
from pathlib import Path

from app import speech
from app.voice_preview import EN_SAMPLE_TEXT, SAMPLE_ROOT, VI_SAMPLE_TEXT


def main():
    cache = Path('reports/language-preview-assets')
    manifest_path = SAMPLE_ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    files = {}
    for voice, text in ([(row['id'], VI_SAMPLE_TEXT) for row in speech.VIENEU_VOICES]
                        + [(identity, EN_SAMPLE_TEXT) for identity in speech.ENGLISH_VOICES]):
        result = speech.synthesize(text, voice, 0, cache)
        source = Path(result['path'])
        destination = SAMPLE_ROOT / source.name
        shutil.copy2(source, destination)
        files[destination.name] = {'voice': voice, 'text': text,
            'engine': speech.ENGLISH_VERSION if voice in speech.ENGLISH_VOICES else speech.VIENEU_VERSION,
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}
        print(voice, destination.stat().st_size, flush=True)
    manifest['language_files'] = files
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
