"""Recognize chemical notation without naming a compound or changing its atoms.

Element symbols follow the IUPAC periodic table: https://iupac.org/what-we-do/periodic-table-of-elements/
Native OOXML index tokens stay opaque so assembly can restore the original runs.
"""
import re

VERSION = 'chemical-notation-v5'
ELEMENTS = frozenset('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn '
    'Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm '
    'Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu '
    'Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split())
_SYMBOL = '(?:' + '|'.join(sorted(ELEMENTS, key=lambda value: (-len(value), value))) + ')'
_SPACE = r'[ \t\u00a0]*'
_INDEX = r'(?:\d+|[₀-₉]+|⟦BLC\d+⟧)'
_ATOM = _SYMBOL + '(?:' + _SPACE + _INDEX + ')?'
_GROUP = r'\(' + _ATOM + '(?:' + _SPACE + _ATOM + r')*\)(?:' + _SPACE + _INDEX + ')?'
_PART = '(?:' + _GROUP + '|' + _ATOM + ')'
# Do not swallow a following English word (e.g. "C2 CUP") into the formula.
# Spaced individual symbols/indices remain accepted, as exported by PowerPoint.
_JOIN = r'(?:' + _SPACE + r'[-–−=≡#]' + _SPACE + r'|[ \t\u00a0]+(?![A-Z]{2,}(?!\w))|)'
FORMULA = re.compile(r'(?<![\w⟦])' + _PART + '(?:' + _JOIN + _PART + r')*(?:[⁰¹²³⁴⁵⁶⁷⁸⁹]*[⁺⁻]|[+−-])?(?![\w⟧])')
_SYMBOLS = re.compile(_SYMBOL)
_SHORT_GROUPS = {'COOH'}


def formula_spans(text):
    """Require more evidence than one element or an arbitrary uppercase word."""
    result = []
    for match in FORMULA.finditer(text):
        value = match.group()
        plain = re.sub(r'⟦BLC\d+⟧', '', value)
        atoms = _SYMBOLS.findall(plain)
        indexed = bool(re.search(_INDEX, value))
        charged = bool(re.search(r'[⁺⁻+−-]$', value))
        if not indexed and not charged and len(atoms) < 2:
            continue
        if not indexed and len(atoms) > 3 and not any(len(atom) > 1 for atom in atoms) and plain not in _SHORT_GROUPS:
            continue  # For example, the unaccented Vietnamese heading CHINH.
        result.append(match)
    return result


def only_notation(text):
    value = re.sub(r'^\s*[A-D][.)]\s*', '', text)
    spans = formula_spans(value)
    if not spans:
        return False
    for match in reversed(spans):
        value = value[:match.start()] + value[match.end():]
    return not value.strip(' \t\r\n,;.:()[]+−-=→⇌…')


def signature(text):
    """Count unambiguous formulas, excluding English IN/ON/NO and Roman labels."""
    from collections import Counter

    values = []
    for match in formula_spans(text):
        value = re.sub(r'\s+', '', match.group())
        if value.startswith('(') and value.endswith(')'):
            value = value[1:-1]  # Sentence parentheses are not part of the formula.
        if re.search(r'\d|[₀-₉⁺⁻+−=≡#-]|[a-z]',value) or value in {'CO','HCN','COOH'}:
            values.append(value.translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉','0123456789')))
    return Counter(values)
