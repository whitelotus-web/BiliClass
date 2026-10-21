import hashlib
import json

import numpy as np
import pytest

from app import speech
from app.lesson_narration import variant_title
from app.narration_preparation import NarrationPreparation
from app.spoken_vietnamese import vietnamese
from app.voice_errors import public_message


@pytest.mark.parametrize('text, spoken', [('❶', 'Số một.'), ('❷', 'Số hai.'), ('❸', 'Số ba.'),
                                         ('❹', 'Số bốn.'), ('❺', 'Số năm.'), ('⓿', 'Số không.'),
                                         ('⑩', 'Số mười.'), ('⑮', 'Số mười lăm.'),
                                         ('㉑', 'Số hai mươi mốt.'), ('㊿', 'Số năm mươi.'),
                                         ('Chọn đáp án ❷.', 'Chọn đáp án hai.')])
def test_circled_labels_become_spoken_numbers(text, spoken):
    assert vietnamese(text) == spoken


@pytest.mark.parametrize('text', ['Đường thẳng và mặt phẳng trong không gian.', 'C₂H₅OH',
                                 'H2O', '3,5 m/s²', 'x + 2 = 5', 'α và β', '½', 'III. Bài tập'])
def test_scientific_text_and_existing_spoken_content_stay_unchanged(text):
    assert vietnamese(text) == text


def test_real_inference_boundary_receives_speech_but_cache_keeps_raw_label(monkeypatch, tmp_path):
    calls = []

    class Engine:
        def infer(self, text, voice):
            calls.append((text, voice))
            return np.full(4800, .05, dtype=np.float32)

    monkeypatch.setattr(speech, '_vieneu_engine', lambda _: Engine())
    speech._synthesize_vieneu_local('❷', 'vieneu:Mai Anh', 0, tmp_path/'number.wav')
    assert calls == [('Số hai.', 'Mai Anh')]
    assert speech.valid_audio(tmp_path/'number.wav')
    payload = json.dumps({'text': '❷', 'voice': 'vieneu:Mai Anh', 'rate': 0,
                          'provider': speech.VIENEU_VERSION}, sort_keys=True)
    assert speech.audio_key('❷', 'vieneu:Mai Anh', 0) == hashlib.sha256(payload.encode()).hexdigest()


@pytest.mark.parametrize('error', ['VieNeu không tạo được âm thanh cho đoạn này.',
                                  'Kokoro failed to initialize', 'onnxruntime DLL failure'])
def test_voice_failures_offer_resume_without_engine_names(error):
    result = NarrationPreparation._completion_message({'complete': 175, 'total': 180,
                                                       'failed': 5, 'last_error': error})
    assert '175/180' in result and 'Tiếp tục tạo giọng' in result and 'giữ lại' in result
    assert not any(name in result.casefold() for name in ('vieneu', 'kokoro', 'onnxruntime'))


def test_actionable_disk_messages_are_retained_and_unknown_voice_ids_are_not_exposed():
    message = 'Ổ đĩa lưu bài không đủ chỗ trống.'
    assert public_message(message) == message
    assert 'kokoro' not in variant_title({'voice': 'kokoro:af_heart', 'mode': 'en'}).casefold()
