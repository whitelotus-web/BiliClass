"""Choose a verified finished recording without generating any new audio."""

from .lesson_narration import MODES, audio_status, records


def available_modes(rows):
    result = dict.fromkeys(MODES, False)
    for row in rows:
        if not row.get('ready') or row.get('mode') not in MODES:
            continue
        for language in MODES[row['mode']]:
            result[language] = True
        if row['mode'] == 'both':
            result['both'] = True
    return result


def preferred_ready(rows):
    """One selection policy for verified audio and its cached download label."""
    ready = [(index, row) for index, row in enumerate(rows) if row.get('ready') and row.get('mode') in MODES]
    return max(ready, key=lambda item: (len(MODES[item[1]['mode']]),
               item[1].get('playback') == 'both_controls', item[0]))[1] if ready else {}


def select_final(lesson, directory, cancel=None):
    """Prefer the most complete ready product, then the latest saved product."""
    context, ready = {}, []
    for record in records(lesson).values():
        state = audio_status({**lesson, 'narration': record}, directory, cancel=cancel, _context=context)
        if state.get('ready'):
            ready.append({**state, 'record': record})
    choice = preferred_ready(ready)
    selected = choice['record'] if choice else {'version': 2, 'mode': 'none'}
    return {**lesson, 'narration': selected}
