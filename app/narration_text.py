"""Remove identified source watermarks from speech, without editing slide text."""
import re

SOURCE_STAMP = re.compile(r'\b19(?:wx|lt)568\b', re.I)


def clean_artifacts(text):
    if not SOURCE_STAMP.search(text):
        return text  # Keep every unaffected audio/cache identity unchanged.
    rows = []
    for line in text.splitlines(keepends=True):
        if not SOURCE_STAMP.search(line):
            rows.append(line)
            continue
        ending = '\n' if line.endswith(('\n', '\r', '\v')) else ''
        cleaned = SOURCE_STAMP.sub('', line).strip()
        # This known source credit is decorative only when paired with its stamp.
        if cleaned.casefold() == 'gemini notebook':
            cleaned = ''
        rows.append(cleaned + ending)
    return ''.join(rows)
