import hashlib
import json

import pytest

from app import speech
from app.spoken_labels import english
from app.voice_pairs import ENGLISH_VERSION


@pytest.mark.parametrize('text,expected', [('1. Introduction','Section 1. Introduction'),
    ('I/ Energy','Section 1. Energy'), ('II. Speed','Section 2. Speed'), ('IV/','Section 4. '),
    ('3.5 m/s','3.5 m/s'), ('I am here.','I am here.'), ('A. Force','A. Force'),
    ('Lesson 4:','Lesson 4:'), ('The value is 50%.','The value is 50%.'),
    ('III . Functional groups','Section 3. Functional groups'), ('2 . Bond','Section 2. Bond')])
def test_spoken_section_labels_preserve_values_and_english(text, expected):
    assert english(text) == expected


def test_only_changed_english_labels_need_new_audio_cache_keys():
    def old(text):
        return hashlib.sha256(json.dumps({'text':text,'voice':'kokoro-us:af_bella','rate':0,
            'provider':ENGLISH_VERSION}, sort_keys=True).encode()).hexdigest()
    assert speech.audio_key('Lesson 4:', 'kokoro-us:af_bella', 0) == old('Lesson 4:')
    assert speech.audio_key('I/ Introduction', 'kokoro-us:af_bella', 0) != old('I/ Introduction')
