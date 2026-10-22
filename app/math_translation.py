"""Exact classroom geometry clauses; no inferred answers or formula rewriting."""

import re

NUMBER = r'(?:⟦BLC\d+⟧|\d+)'


def exact(text):
    source = ' '.join(text.split())
    token = r'⟦BLC\d+⟧'
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
