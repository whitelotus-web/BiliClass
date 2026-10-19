"""Stable local voice pairs. Region describes the Vietnamese speaker only."""

ENGLISH_VERSION = 'kokoro-v1_0-sherpa-1.13.8-us-weak-article-v1'
ENGLISH_VOICES = {'kokoro-us:af_heart': ('Heart', 3), 'kokoro-us:am_michael': ('Michael', 16)}
PAIRS = tuple(
    {'id': 'pair:' + identity, 'name': f'{vi} + {en} · {gender} {region}–Mỹ',
     'detail': f'Việt: {vi} · Anh–Mỹ: {en}', 'provider': 'local_pair',
     'vi': 'vieneu:' + vi, 'en': 'kokoro-us:' + en_id,
     'region': region, 'gender': gender, 'language': 'multilingual', 'languages': ['vi', 'en']}
    for identity, vi, gender, region, en, en_id in (
        ('north-female', 'Mai Anh', 'Nữ', 'Bắc', 'Heart', 'af_heart'),
        ('central-female', 'Ngọc Trân', 'Nữ', 'Trung', 'Heart', 'af_heart'),
        ('south-female', 'Thùy Dung', 'Nữ', 'Nam', 'Heart', 'af_heart'),
        ('north-male', 'Hải Đăng', 'Nam', 'Bắc', 'Michael', 'am_michael'),
        ('central-male', 'Quang Sơn', 'Nam', 'Trung', 'Michael', 'am_michael'),
        ('south-male', 'Thái Sơn', 'Nam', 'Nam', 'Michael', 'am_michael'),
    )
)
BY_ID = {row['id']: row for row in PAIRS}


def voice_for(selection, language):
    """Old recordings keep their exact speaker/cache identity on both routes."""
    return BY_ID[selection][language] if selection in BY_ID else selection


def selection_for(voice):
    return next((row['id'] for row in PAIRS if row['vi'] == voice), voice)
