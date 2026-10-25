"""Bounded, read-only bilingual reference lookup. Never upload a slide or key.

Wikidata labels are reference candidates, not authoritative curriculum approval.
No arbitrary URL, redirect, website instructions, code or generated citation is used.
"""

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request

from .subject_terms import subject_key

ENDPOINT = 'https://www.wikidata.org/w/api.php'
_USER_AGENT = 'BiliClass/1.0 (educational terminology; https://github.com/whitelotus-web/BiliClass)'
DOMAINS = {
    'toan': ('mathemat', 'geometry', 'algebra', 'trigonomet', 'toán', 'hình học'),
    'vat ly': ('physics', 'physical', 'mechanic', 'electr', 'vật lý', 'vật lí'),
    'hoa hoc': ('chem', 'molecul', 'chemical', 'hóa học', 'hoá học'),
    'sinh hoc': ('biolog', 'cell', 'organism', 'ecolog', 'genet', 'sinh học'),
    'tin hoc': ('comput', 'software', 'data', 'program', 'thuật toán', 'tin học'),
    'cong nghe': ('technolog', 'engineer', 'agricultur', 'electr', 'công nghệ'),
    'lich su': ('histor', 'civilization', 'lịch sử'),
    'dia ly': ('geograph', 'climat', 'geolog', 'population', 'địa lý', 'địa lí'),
    'ngu van': ('liter', 'poet', 'narrat', 'rhetor', 'văn học'),
    'tieng viet': ('linguis', 'grammar', 'language', 'liter', 'ngôn ngữ'),
    'tieng anh': ('linguis', 'grammar', 'language', 'ngôn ngữ'),
    'am nhac': ('music', 'âm nhạc'), 'my thuat': ('art', 'paint', 'design', 'mỹ thuật', 'mĩ thuật'),
    'giao duc the chat': ('sport', 'exercise', 'physical', 'thể thao'),
    'giao duc cong dan': ('ethic', 'civic', 'human right', 'societ', 'citizen', 'đạo đức'),
    'giao duc kinh te va phap luat': ('econom', 'law', 'legal', 'financ', 'kinh tế', 'pháp luật'),
    'hoat dong trai nghiem, huong nghiep': ('career', 'occupation', 'education', 'learning', 'skill', 'employment', 'hướng nghiệp'),
    'noi dung giao duc cua dia phuong': ('heritage', 'cultur', 'tradition', 'di sản', 'văn hóa'),
    'giao duc quoc phong va an ninh': ('defen', 'militar', 'security', 'peacekeep', 'maritime', 'quốc phòng', 'an ninh'),
    'khoa hoc': ('scien', 'physics', 'chem', 'biolog', 'experiment', 'measurement', 'khoa học'),
}


def domain_markers(subject):
    """Integrated subjects inherit component evidence, never a guessed domain."""
    direct = DOMAINS.get(subject_key(subject))
    if direct:
        return direct
    from .terminology_seed import GROUPS, SUBJECT_GROUPS

    groups = next((groups for name, groups in SUBJECT_GROUPS.items() if subject_key(name) == subject_key(subject)), ())
    return tuple(dict.fromkeys(marker for group in groups for marker in DOMAINS.get(subject_key(GROUPS[group][0]), ())))


def _domain_match(description, markers):
    # Stems such as "biolog" match biology/biological, but a short complete
    # term such as "art" must not accept "particle" or "article".
    return any(re.search(r'(?<!\w)' + re.escape(marker) + (r'(?!\w)' if marker in {'art', 'law', 'data'} else ''), description)
               for marker in markers)


def key(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _get(parameters, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError()
    parameters = {'format': 'json', 'maxlag': '5', **parameters}
    request = urllib.request.Request(ENDPOINT + '?' + urllib.parse.urlencode(parameters),
                                     headers={'User-Agent': _USER_AGENT, 'Accept': 'application/json'})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=min(1.2, remaining)) as response:
        raw = response.read(192_001)
    if len(raw) > 192_000:
        raise ValueError('Reference response too large')
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get('error'):
        raise ValueError('Reference response unavailable')
    return value


def _label(value, maximum=120):
    if not isinstance(value, str) or not 2 <= len(value.strip()) <= maximum:
        return ''
    if any(ord(c) < 32 for c in value) or re.search(r'[<>{}\[\]\\]|https?://|BCLLOCK|⟦BLC', value, re.I):
        return ''
    return value.strip()


def valid_reference(record, term, subject):
    """Reject malformed cached/network records before they reach any provider."""
    if (not isinstance(record, dict) or record.get('status') != 'online_reference'
            or not all(isinstance(value, str) for value in (term, subject, record.get('subject', '')))):
        return False
    identity = record.get('source_id', '')
    return (isinstance(identity, str) and bool(re.fullmatch(r'Q[1-9]\d{0,11}', identity))
            and record.get('source_url') == 'https://www.wikidata.org/wiki/' + identity
            and bool(_label(record.get('en'))) and bool(_label(record.get('vi'), 90))
            and key(record['vi']) == key(term) and subject_key(record.get('subject', '')) == subject_key(subject))


def lookup(term, subject, cancel, *, deadline=None, fetch=None):
    """Only an exact Vietnamese label/alias plus subject evidence can be a hint."""
    deadline = deadline if deadline is not None else time.monotonic() + 4
    fetch = fetch or _get
    wanted = key(term)
    if cancel.is_set():
        raise InterruptedError('Đã dừng tra cứu thuật ngữ.')
    if not _label(term, 90) or not 2 <= len(term.split()) <= 6 or re.search(r'\d|[@:/]', term):
        return None
    markers = domain_markers(subject)
    if not markers:
        return None  # Unknown custom subjects have no invented expertise.
    result = fetch(dict(action='wbsearchentities', language='vi', uselang='vi', type='item', search=term, limit='3'), deadline)
    search = result.get('search', []) if isinstance(result, dict) else []
    if not isinstance(search, list):
        return None
    ids = list(dict.fromkeys(row['id'] for row in search[:3] if isinstance(row, dict)
           and re.fullmatch(r'Q[1-9]\d{0,11}', str(row.get('id', '')))))
    if not ids or cancel.is_set():
        if cancel.is_set():
            raise InterruptedError('Đã dừng tra cứu thuật ngữ.')
        return None
    result = fetch(dict(action='wbgetentities', ids='|'.join(ids[:3]), languages='vi|en',
                        props='labels|descriptions|aliases'), deadline)
    entities = result.get('entities', {}) if isinstance(result, dict) else {}
    if cancel.is_set():
        raise InterruptedError('Đã dừng tra cứu thuật ngữ.')
    if not isinstance(entities, dict):
        return None
    choices = []
    for identity in ids:
        entity = entities.get(identity, {})
        if not isinstance(entity, dict) or not all(isinstance(entity.get(field, {}), dict) for field in ('labels', 'aliases', 'descriptions')):
            continue
        if not all(isinstance(entity.get('labels', {}).get(lang, {}), dict) for lang in ('vi', 'en')):
            continue
        vi = _label(entity.get('labels', {}).get('vi', {}).get('value', ''))
        en = _label(entity.get('labels', {}).get('en', {}).get('value', ''))
        aliases = entity.get('aliases', {}).get('vi', [])
        aliases = [row.get('value', '') for row in aliases if isinstance(row, dict)] if isinstance(aliases, list) else []
        if wanted not in {key(value) for value in [vi, *aliases] if isinstance(value, str)} or not en:
            continue
        descriptions = ' '.join(str(row.get('value', '')) for row in entity.get('descriptions', {}).values() if isinstance(row, dict)).casefold()
        if not _domain_match(descriptions, markers):
            continue
        choices.append(dict(vi=term, en=en, subject=subject, status='online_reference',
                            source_url='https://www.wikidata.org/wiki/' + identity, source_id=identity,
                            note='Nhãn song ngữ khớp và mô tả phù hợp môn; chưa phải xác nhận chuẩn kiến thức.'))
    # Even equal English labels can denote two different senses. Do not guess.
    return choices[0] if len(choices) == 1 else None
