"""Stable local voice pairs. Region describes the Vietnamese speaker only."""

ENGLISH_VERSION = 'kokoro-v1_0-sherpa-1.13.8-us-weak-article-v1'
ENGLISH_VOICES = {'kokoro-us:af_heart': ('Heart', 3), 'kokoro-us:af_bella': ('Bella', 2),
                  'kokoro-us:af_nicole': ('Nicole', 6), 'kokoro-us:af_sarah': ('Sarah', 9),
                  'kokoro-us:af_kore': ('Kore', 5), 'kokoro-us:am_michael': ('Michael', 16),
                  'kokoro-us:am_fenrir': ('Fenrir', 14), 'kokoro-us:am_puck': ('Puck', 18)}
PAIRS = tuple(
    {'id': 'pair:' + identity, 'name': f'{vi} + {en} · {gender} {region}–Mỹ',
     'label': f'{vi} – {en}', 'subtitle': f'{gender} {region} – Mỹ',
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
        ('truc-ly', 'Trúc Ly', 'Nữ', 'Bắc', 'Bella', 'af_bella'),
        ('doan-trang', 'Đoan Trang', 'Nữ', 'Bắc', 'Heart', 'af_heart'),
        ('pham-tuyen', 'Phạm Tuyên', 'Nam', 'Bắc', 'Michael', 'am_michael'),
    )
)
CUSTOM_PAIRS = tuple(
    {**row, 'id': row['id'] + ':' + en_id.rsplit(':', 1)[1],
     'name': f"{row['vi'].split(':', 1)[1]} + {en} · Tự ghép",
     'label': f"{row['vi'].split(':', 1)[1]} – {en}",
     'detail': f"Việt: {row['vi'].split(':', 1)[1]} · Anh–Mỹ: {en}",
     'en': en_id}
    for row in PAIRS for en_id, (en, _) in ENGLISH_VOICES.items()
    if row['en'] != en_id
)
ALL_PAIRS = PAIRS + CUSTOM_PAIRS
BY_ID = {row['id']: row for row in ALL_PAIRS}


def compose(vi, en):
    return next((row['id'] for row in ALL_PAIRS if row['vi'] == vi and row['en'] == en), '')


# Suggestions can evolve without changing the speaker behind a saved pair ID.
RECOMMENDED_PAIRS = tuple(BY_ID[compose(row['vi'], 'kokoro-us:' + english)]
                          for row, english in zip(PAIRS, (
                              'af_heart', 'af_sarah', 'af_kore', 'am_michael', 'am_fenrir',
                              'am_puck', 'af_bella', 'af_nicole', 'am_michael'), strict=True))


def voice_for(selection, language):
    """Old recordings keep their exact speaker/cache identity on both routes."""
    return BY_ID[selection][language] if selection in BY_ID else selection


def selection_for(voice):
    return next((row['id'] for row in PAIRS if row['vi'] == voice), voice)
