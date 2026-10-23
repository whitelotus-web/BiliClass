"""One adjustable cadence for cached playback and embedded PowerPoint audio."""

PARAGRAPH_GAP_MS = 400
_live = {}


def validated_gap(value):
    return max(0, min(2000, value)) if type(value) is int else PARAGRAPH_GAP_MS


def select_gap(directory, value):
    from pathlib import Path

    _live[str(Path(directory).resolve())] = validated_gap(value)


def reading_gap(directory):
    import json
    import sqlite3
    from contextlib import closing
    from pathlib import Path

    key = str(Path(directory).resolve())
    if key in _live:
        return _live[key]
    database = Path(directory).resolve() / 'library.db'
    if not database.is_file():
        return PARAGRAPH_GAP_MS
    # Read one preference without starting migrations or library backfills.
    with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as connection:
        row = connection.execute('SELECT value FROM settings WHERE key=?', ('paragraph_gap_ms',)).fetchone()
    return validated_gap(json.loads(row[0])) if row else PARAGRAPH_GAP_MS
