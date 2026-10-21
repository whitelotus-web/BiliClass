"""Deck-wide speaker placement; changing this never invalidates narration WAVs."""

POSITIONS = {'top_left': 'Trái trên', 'top_center': 'Giữa trên', 'top_right': 'Phải trên',
             'bottom_left': 'Trái dưới', 'bottom_center': 'Giữa dưới', 'bottom_right': 'Phải dưới'}
DEFAULT_POSITION = 'bottom_right'


def position(value):
    return value if isinstance(value, str) and value in POSITIONS else DEFAULT_POSITION


def default_position(directory):
    import json
    import sqlite3
    from contextlib import closing
    from pathlib import Path

    path = Path(directory).resolve() / 'library.db'
    if not path.is_file():
        return DEFAULT_POSITION
    try:
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=2)) as db:
            row = db.execute('SELECT value FROM settings WHERE key=?', ('narration_speaker_position',)).fetchone()
            return position(json.loads(row[0])) if row else DEFAULT_POSITION
    except (sqlite3.Error, ValueError):
        return DEFAULT_POSITION


def fixed_slots(bounds, selected=DEFAULT_POSITION, *, mini=False, languages=('vi', 'en', 'both')):
    width, height = bounds
    cell_width, cell_height = (50, 20) if mini else (36, 34)
    total = cell_width * len(languages)
    row, column = position(selected).split('_')
    left = {'left': 12, 'center': (width - total) / 2, 'right': width - total - 12}[column]
    top = 12 if row == 'top' else height - cell_height - 12
    return {language: (left + index * cell_width, top, 'mini' if mini else False)
            for index, language in enumerate(languages)}
