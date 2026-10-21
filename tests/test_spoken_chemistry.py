import hashlib
import json

import pytest

from app import speech
from app.english_speech import spoken_text
from app.spoken_chemistry import english
from app.voice_pairs import ENGLISH_VERSION


@pytest.mark.parametrize('text,expected', [
    ('HCN', 'aitch see en'), ('CO₂', 'see oh 2'), ('CH3COOH', 'see aitch 3 see oh oh aitch'),
    ('CH 3 Cl', 'see aitch 3 see el'), ('NaCl', 'en ay see el'),
    ('Ca(OH)2', 'see ay open parenthesis oh aitch close parenthesis 2'),
    ('NH₄⁺', 'en aitch 4 plus'), ('CN⁻', 'see en minus'),
    ('In CO2, the ratio is 1:2.', 'In see oh 2, the ratio is 1:2.'),
    ('NaCl In this example', 'en ay see el In this example'),
    ('C-H and C=O bonds', 'see single bond aitch and see double bond oh bonds'),
    ('C-H and C=O', 'see minus aitch and see equals oh'),
    ('The OH group', 'The oh aitch group'),
    ('3500 – 3200 cm -1', '3500 to 3200 inverse centimeters'),
    ('at 3337 cm⁻¹.', 'at 3337 inverse centimeters.'),
    ('cm^{-1}', 'inverse centimeters'),
    ('Iron(III) oxide; Copper(II) hydroxide', 'Iron 3 oxide; Copper 2 hydroxide'),
    ('The element H is present in H2O.', 'The element hydrogen is present in aitch 2 oh.'),
    ('Contains only two elements: C and H.', 'Contains only two elements: carbon and hydrogen.'),
    ('Does not react with Na.', 'Does not react with sodium.'),
    ('I identify the element I.', 'I identify the element iodine.'),
])
def test_spoken_formulas_keep_every_atom_index_and_charge(text, expected):
    assert english(text) == expected


@pytest.mark.parametrize('text', ['I am here. He is in class.', 'NO, IN, ON, CHINH',
    'COOL colors', 'The value is -1 cm.', 'Section 2. Structure', '2500 – 1800 Hz',
    '⟦BLC0⟧', 'An Alcohol group', 'F = ma', 'H is the height.', 'C is the speed of light.',
    'An atom moves under force F.'])
def test_ordinary_english_and_unresolved_native_tokens_are_unchanged(text):
    assert english(text) == text


def test_chemical_names_are_spoken_as_english_words_not_spelled_symbols():
    assert spoken_text('Oxygen, hydrogen, sulfuric acid, iron, aluminium and alcohol.') == 'Oxygen, hydrogen, sulfuric acid, iron, aluminium and alcohol.'


def test_cache_migration_matches_actual_rendering_and_keeps_unaffected_audio():
    def legacy(text,voice='kokoro-us:af_heart',provider=ENGLISH_VERSION):
        return hashlib.sha256(json.dumps({'text':text,'voice':voice,'rate':0,'provider':provider},sort_keys=True).encode()).hexdigest()
    assert spoken_text('II. CO2') == 'Section 2. see oh 2'
    for text in ['HCN','3500–3200 cm-1','CH3COOH']:
        assert speech.audio_key(text,'kokoro-us:af_heart',0) != legacy(text)
    assert speech.audio_key('Alcohol','kokoro-us:af_heart',0) == legacy('Alcohol')
    assert speech.audio_key('HCN','sapi:legacy',0) == legacy('HCN','sapi:legacy','sapi-v1')
