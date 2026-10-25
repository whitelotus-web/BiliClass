"""Exact classroom geometry clauses; no inferred answers or formula rewriting."""

import re

NUMBER = r'(?:⟦BLC\d+⟧|\d+)'


def grammatical_terms(terms, excluded):
    """Lock complete noun phrases so a singular glossary cannot erase plurality."""
    plurals = {'góc lượng giác': 'trigonometric angles', 'góc hình học': 'geometric angles',
               'giá trị lượng giác': 'trigonometric values', 'hàm số': 'functions',
               'tia đầu': 'initial rays', 'tia cuối': 'terminal rays'}
    prefixes = {'các': '', 'những': '', 'hai': 'two ', 'ba': 'three ', 'bốn': 'four ',
                'năm': 'five ', 'sáu': 'six ', 'bảy': 'seven ', 'tám': 'eight ',
                'chín': 'nine ', 'mười': 'ten '}
    result = {}
    for vi, en in plurals.items():
        for prefix, english in prefixes.items():
            phrase = prefix + ' ' + vi
            if vi in terms and not any(term in phrase for term in excluded):
                result[phrase] = english + en
    return result


def exact(text):
    source = ' '.join(text.split())
    token = r'⟦BLC\d+⟧'
    # A bare hour/minute label may be a clock reading or a duration. Retain both
    # units without guessing which interpretation the slide author intended.
    match = re.fullmatch('(' + NUMBER + r')\s*giờ\s*(' + NUMBER + r')\s*phút', source, re.I)
    if match:
        return f'{match[1]} h {match[2]} min'
    # This source template sometimes omits "dài". The arc-length formula makes
    # the intended quantity explicit; never turn length into an angle in degrees.
    variable = r'(?:⟦BLC\d+⟧|[A-Za-zΑ-ω])'
    match = re.fullmatch(r'Một cung của đường tròn bán kính (' + variable + r') và có số đo (' + variable
                        + r') thì có độ(?: dài)? là (⟦BLC\d+⟧|l\s*=\s*R\s*[.·×*]?\s*α)([.]?)', source, re.I)
    if match:
        return f'An arc of a circle with radius {match[1]} and measure {match[2]} has length {match[3]}' + match[4]
    match = re.fullmatch(r'Số đo của các góc lượng giác tia đầu (' + token + r'),\s*tia cuối (' + token + r') là[:.]?', source, re.I)
    if match:
        return f'The measures of trigonometric angles with initial ray {match[1]} and terminal ray {match[2]} are'
    # A formula can mix immutable OOXML tokens with ordinary runs for sđ,+,=.
    # Translate the connective locally; sending those runs as prose let DeepL
    # turn an equality into a list with commas and "and" while retaining digits.
    match = re.fullmatch(r'(Do đó|Suy ra|Ta có)\s*:?\s+(.+)', source, re.I)
    if match:
        tail = match[2]
        residue = re.sub(token + r'|sđ', '', tail, flags=re.I)
        if re.search(token, tail) and re.fullmatch(r'[\s=+−*/^.,;:()°-]*', residue):
            label = {'do đó':'Therefore, ', 'suy ra':'Hence, ', 'ta có':'We have '}
            return label[match[1].casefold()] + tail
    match = re.fullmatch(r'Mặt khác, đường tròn có số đo bằng (' + token + r') nên ta có (.+)', source, re.I)
    if match and not re.search(r'[a-zA-ZÀ-ỹ]', re.sub(token + r'|rad', '', match[2])):
        return f'On the other hand, a full turn measures {match[1]}, so {match[2]}'
    match = re.fullmatch(r'Do đường tròn có độ dài là (' + token + r') nên nó có số đo (' + token + r')(\s*rad)?([.]?)', source, re.I)
    if match:
        return f'Since the circumference of the circle is {match[1]}, a full turn measures {match[2]}' + (match[3] or '') + match[4]
    match = re.fullmatch(r'Giải (phương trình|hệ phương trình)\s*:?\s*(' + token + r')([.]?)', source, re.I)
    if match:
        command = 'Solve the equation' if match[1].casefold() == 'phương trình' else 'Solve the system of equations'
        return command + ' ' + match[2] + match[3]
    match = re.fullmatch(r'Phải quay kim phút mấy phần của một vòng tròn theo '
        r'(chiều quay ngược chiều kim đồng hồ|chiều quay của kim đồng hồ) để nó chỉ đúng số (' + NUMBER + r')\?', source, re.I)
    if match:
        direction = 'counterclockwise' if 'ngược' in match[1].casefold() else 'clockwise'
        return f'Through what fraction of a full turn must the minute hand rotate {direction} to point to {match[2]}?'
    match = re.fullmatch('(' + token + r') với (' + token + r') là (tâm hình bình hành|trung điểm) (' + token + r')(' + token + r'|[.])?', source, re.I)
    if match:
        role = 'center of the parallelogram' if match[3].casefold() == 'tâm hình bình hành' else 'midpoint of'
        return f'{match[1]}, where {match[2]} is the {role} {match[4]}' + (match[5] or '')
    match = re.fullmatch(r'([+•-]\s*)?Một mặt đáy là tứ giác (' + token + r'|[A-Z]{4})([.]?)', source, re.I)
    if match:
        return (match[1] or '') + f'The base is the quadrilateral {match[2]}' + match[3]
    match = re.fullmatch(r'Ta có (' + NUMBER + r') vị trí tương đối giữa đường(?: thẳng)? và mặt(?: phẳng)?\s*:', source, re.I)
    if match:
        return f'There are {match[1]} possible relative positions of a line and a plane:'
    match = re.fullmatch(r'([+•-]\s*)?Qua (' + NUMBER + r') điểm phân biệt không thẳng hàng[.]?', source, re.I)
    if match:
        return (match[1] or '') + f'Through {match[2]} distinct, noncollinear points.'
    clauses = {
        'sin thì sin cos cos sin': 'Sine: sine–cosine, cosine–sine',
        'cos thì cos cos sin sin nhớ trừ': 'Cosine: cosine–cosine, sine–sine; remember to subtract',
        'các mặt đều là hình tam giác': 'All the faces are triangles',
        'đường nằm trong mặt (vô số điểm chung)': 'The line lies in the plane (infinitely many common points)',
        'đường cắt mặt tại một điểm (một điểm chung)': 'The line intersects the plane at one point (one common point)',
        'đường song song với mặt ( không có điểm chung)': 'The line is parallel to the plane (no common points)',
        'đường song song với mặt (không có điểm chung)': 'The line is parallel to the plane (no common points)',
        'vô số': 'Infinitely many',
    }
    match = re.fullmatch(r'([+•-]\s*)?(.*?)([.]?)', source)
    if match and match[2].casefold() in clauses:
        return (match[1] or '') + clauses[match[2].casefold()] + match[3]
    return None


def terminology(source, translated):
    # A ray in geometry is not a pulse; keep this repair scoped to mathematical prose.
    if re.search(r'\btia\b', source, re.I):
        translated = re.sub(r'\bpulses\b', 'rays', translated, flags=re.I)
        translated = re.sub(r'\bpulse\b', 'ray', translated, flags=re.I)
    if re.search(r'quay kim phút một khoảng bằng', source, re.I):
        translated = re.sub(r'rotating the minute hand by a distance equal to',
                            'rotating the minute hand through', translated, flags=re.I)
    if re.search(r'\blớp\s+⟦BLC\d+⟧', source, re.I):
        translated = re.sub(r'(⟦BLC\d+⟧) grade\b', r'Grade \1', translated, flags=re.I)
    if re.search(r'\bnằm trên\b', source, re.I) and not re.search(r'\bphía trên\b', source, re.I):
        translated = re.sub(r'\bis above\b', 'lies on', translated, flags=re.I)
    # The Vietnamese classroom term does not specify that the puzzle is a cube.
    # Do not invent a six-faced solid where the source describes four faces.
    if re.search(r'\bkhối\s+rubik\b', source, re.I):
        translated = re.sub(r"Rubik[’']s Cube", "Rubik's puzzle", translated, flags=re.I)
    if re.search(r'\btiết\s*\)', source, re.I):
        translated = re.sub(r'\bSections?\b(?=\s*\))', 'lessons', translated, flags=re.I)
    return translated
