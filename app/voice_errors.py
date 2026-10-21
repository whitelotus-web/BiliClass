"""Keep speech-engine diagnostics out of teacher-facing task messages."""

import re

_ENGINE = re.compile(r'vieneu|kokoro|onnxruntime|sherpa[-_]onnx', re.IGNORECASE)


def public_message(value):
    text = str(value or '').strip()
    if _ENGINE.search(text):
        return 'Chưa tạo được âm thanh cho đoạn này.'
    return text
