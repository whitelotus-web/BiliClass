"""Prepare a private, ready-to-paste Apps Script without changing saved settings."""

import re
from pathlib import Path

_MARKER = "const BILICLASS_SETUP_CODE = '';"


def prepared_script(access_code):
    if not re.fullmatch(r'[A-Za-z0-9_-]{16,200}', access_code):
        raise ValueError('Mã truy cập Apps Script chưa hợp lệ.')
    script = (Path(__file__).parent / 'resources/languageapp.gs').read_text(encoding='utf-8')
    if script.count(_MARKER) != 1:
        raise ValueError('Chưa chuẩn bị được mã Apps Script. Hãy mở lại BiliClass và thử lại.')
    return script.replace(_MARKER, "const BILICLASS_SETUP_CODE = '" + access_code + "';")
