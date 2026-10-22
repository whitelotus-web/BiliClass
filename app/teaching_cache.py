"""Verified derivatives only; every Office session receives a separate copy."""

import hashlib
import json
import shutil
from pathlib import Path
from uuid import uuid4

# Bump when managed audio/controls change, independently of cosmetic releases.
FORMAT_VERSION = 2


def cache_key(lesson, source_sha256, directory):
    from .speaker_layout import default_position, position

    record = lesson['narration']
    keys = sorted({key for values in record.get('keys', {}).values() for key in values})
    stamps = []
    for key in keys:
        stat = (Path(directory) / 'audio' / (key + '.wav')).stat()
        stamps.append((key, stat.st_size, stat.st_mtime_ns))
    selected = position(lesson.get('speaker_position', default_position(directory)))
    payload = dict(version=FORMAT_VERSION, lesson=lesson['id'], revision=lesson['revision'],
                   source=source_sha256, record=record, position=selected, audio=stamps)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def _path(directory, key):
    if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
        raise ValueError('Invalid managed cache key')
    return Path(directory) / 'temp/managed-presentations' / (key + '.pptx')


def load(directory, key):
    path = _path(directory, key)
    try:
        metadata = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
        if metadata.get('version') != 1 or metadata.get('key') != key:
            return None
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != metadata.get('sha256'):
                return None
        media = {int(number): list(languages) for number, languages in metadata['media'].items()}
        return dict(path=path, media=media, warning=metadata['warning'], sha256=metadata['sha256'])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def store(directory, key, prepared):
    path = _path(directory, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(uuid4().hex + '.pending')
    description = temporary.with_suffix('.json')
    try:
        shutil.copyfile(prepared['path'], temporary)
        metadata = dict(version=1, key=key, sha256=prepared['sha256'],
                        media=prepared['media'], warning=prepared['warning'])
        description.write_text(json.dumps(metadata), encoding='utf-8')
        temporary.replace(path)
        description.replace(path.with_suffix('.json'))
    finally:
        temporary.unlink(missing_ok=True)
        description.unlink(missing_ok=True)
