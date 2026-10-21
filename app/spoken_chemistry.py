"""Speak explicit chemical notation, without guessing names from formulas.

The slide text remains unchanged. Shared by synthesis and cache identity so
exports and the classroom reader cannot silently reuse an older pronunciation.
"""
import re

from .chemical_notation import formula_spans

VERSION = 'spoken-chemistry-v1'
_LETTERS = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', (
    'ay bee see dee ee ef gee aitch eye jay kay el em en oh pee cue ar ess tee '
    'you vee double-you ex why zee').split()))
_SUBSCRIPTS = str.maketrans('₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹', '01234567890123456789')
_ATOM = re.compile(r'[A-Z][a-z]?|\d+|[()+−⁺⁻–=≡#-]')
_INVERSE_CM = re.compile(r'(?<!\w)cm\s*(?:\^\s*\{?\s*[-−]\s*1\s*\}?|[-−]\s*1|⁻¹)(?!\w)')
_RANGE = re.compile(r'(\d+(?:\.\d+)?)\s*[–—−-]\s*(\d+(?:\.\d+)?)\s+(?=inverse centimeters)')
_WORDS = {'He', 'Be', 'In', 'As', 'At', 'No'}
_BARE = {'CO', 'HCN', 'COOH'}
_OXIDATION = re.compile(r'\b(iron|copper|chromium|manganese|cobalt|nickel|tin|lead|mercury|gold|silver|vanadium)\s*\((VIII|VII|VI|IV|V|III|II|I)\)',re.I)
_ROMAN = {value:str(index) for index,value in enumerate(('I','II','III','IV','V','VI','VII','VIII'),1)}
_ELEMENT_NAMES = dict(zip(
    'H O N C S P Cl F Br I Na K Ca Mg Al Fe Cu Zn Ag Au'.split(),
    'hydrogen oxygen nitrogen carbon sulfur phosphorus chlorine fluorine bromine iodine sodium potassium calcium magnesium aluminium iron copper zinc silver gold'.split()))
_ELEMENT = re.compile(r'(?<!\w)(?:'+ '|'.join(sorted(_ELEMENT_NAMES,key=len,reverse=True)) + r')(?!\w)')
_BOND_CONTEXT = re.compile(r'\b(?:bonds?|functional|groups?|molecules?|molecular|chemical|aldehyde|ketone|alcohol|infrared)\b',re.I)


def _formula(value, chemical=False):
    words = []
    tokens = _ATOM.findall(value.translate(_SUBSCRIPTS))
    for index,token in enumerate(tokens):
        if token[0].isalpha():
            words.extend(_LETTERS[letter] for letter in token.upper())
        else:
            if token in {'-','–','−'} and 0 < index < len(tokens)-1 and tokens[index+1][0].isalpha():
                words.append('single bond' if chemical else 'minus')
                continue
            words.append({'(':'open parenthesis', ')':'close parenthesis', '=':'double bond' if chemical else 'equals',
                '≡':'triple bond', '#':'triple bond',
                '+':'plus', '⁺':'plus', '-':'minus', '−':'minus', '⁻':'minus'}.get(token, token))
    return ' '.join(words)


def english(text):
    text = _OXIDATION.sub(lambda match: match[1]+' '+_ROMAN[match[2].upper()],text)
    text = _INVERSE_CM.sub('inverse centimeters', text)
    text = _RANGE.sub(r'\1 to \2 ', text)
    chemical = bool(_BOND_CONTEXT.search(text))
    for match in reversed(formula_spans(text)):
        value, start, end = match.group(), match.start(), match.end()
        # The shared recognizer accepts spaced symbols from PowerPoint runs.
        # English "In CO2" starts with a preposition, not an indium atom.
        while True:
            prefix = re.match(r'([A-Z][a-z])\s+', value)
            if not prefix or prefix[1] not in _WORDS:
                break
            value = value[prefix.end():]
            start += prefix.end()
        while True:
            suffix = re.search(r'\s+([A-Z][a-z])$', value)
            if not suffix or suffix[1] not in _WORDS:
                break
            value = value[:suffix.start()]
            end = start + len(value)
        compact = re.sub(r'\s+', '', value)
        if not compact or '⟦' in compact:
            continue  # Native XML tokens must be resolved before narration.
        if not re.search(r'[\d₀-₉⁺⁻+−–=≡#-]', compact) and compact not in _BARE and not (chemical and compact in {'OH','CH','NH','CN'}):
            # Mixed-case multi-element formulas (NaCl) are unambiguous;
            # bare English words such as NO, ON and IN are not.
            if len(re.findall(r'[A-Z][a-z]?', compact)) < 2 or not re.search('[a-z]',compact):
                continue
        text = text[:start] + _formula(value,chemical) + text[end:]
    def element(match):
        before,after = text[max(0,match.start()-80):match.start()],text[match.end():match.end()+30]
        explicit = re.search(r'\b(?:element|atom|symbol)\s*$',before,re.I)
        # Keep pronoun I and physics variables in sentences about atoms.
        if match[0] == 'I' and not explicit:
            return match[0]
        context = explicit or re.search(r'^\s+(?:atoms?|elements?)\b',after,re.I) or re.search(
            r'\belements?\s*(?::|are|include)?[^.!?;]*$|\breact\w*\s+with\s*$',before,re.I)
        return _ELEMENT_NAMES[match[0]] if context else match[0]
    text = _ELEMENT.sub(element,text)
    return text
