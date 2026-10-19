"""Choose a verified finished recording without generating any new audio."""

from .lesson_narration import MODES, audio_status, records


def available_modes(rows):
    result = dict.fromkeys(MODES, False)
    for row in rows:
        if not row.get('ready') or row.get('mode') not in MODES:
            continue
        for language in MODES[row['mode']]:
            result[language] = True
        if row['mode'] == 'both' and row.get('playback') == 'both_controls':
            result['both'] = True
    return result


def select_final(lesson, directory, cancel=None):
    """Prefer the most complete ready product, then the latest saved product."""
    context, ready = {}, []
    for index, record in enumerate(records(lesson).values()):
        state = audio_status({**lesson, 'narration': record}, directory, cancel=cancel, _context=context)
        if state.get('ready'):
            score = (len(MODES[record['mode']]), record.get('playback') == 'both_controls', index)
            ready.append((score, record))
    selected = max(ready, key=lambda row: row[0])[1] if ready else {'version': 2, 'mode': 'none'}
    return {**lesson, 'narration': selected}
