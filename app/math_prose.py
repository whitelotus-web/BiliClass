"""Expose Vietnamese prose typed in normal OMML runs, retaining native math."""

import copy
import re

MATH = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
DRAWING = 'http://schemas.openxmlformats.org/drawingml/2006/main'
_VI = re.compile(r'[ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]', re.I)


def fragments(element):
    """Split only top-level normal text, never fraction/matrix/delimiter internals.

    Word processors often split one word across many differently styled runs.
    Reassemble adjacent normal runs before classifying them as prose.
    """
    container = element
    if len(element) == 1 and element[0].tag == '{' + MATH + '}oMathPara':
        container = element[0]
        if any(child.tag not in {'{' + MATH + '}oMathParaPr', '{' + MATH + '}oMath'} for child in container):
            return None
    maths = container.findall('{' + MATH + '}oMath')
    if len(maths) != 1 or container is element and len(element) != 1:
        return None
    math = maths[0]
    groups = []
    for child in math:
        normal = child.tag == '{' + MATH + '}r' and child.find('{' + MATH + '}rPr/{' + MATH + '}nor') is not None
        if groups and groups[-1][0] == normal:
            groups[-1][1].append(child)
        else:
            groups.append((normal, [child]))
    if not any(normal and _VI.search(''.join(node.text or '' for child in children for node in child.iter('{' + MATH + '}t')))
               for normal, children in groups):
        return None
    result = []
    for normal, children in groups:
        text = ''.join(node.text or '' for child in children for node in child.iter('{' + MATH + '}t'))
        if normal and (not text.strip() or _VI.search(text)):
            # Do not expose deliberately invisible source text.
            if any(node.tag == '{' + DRAWING + '}alpha' and node.get('val') == '0'
                   or node.tag == '{' + DRAWING + '}noFill' for child in children for node in child.iter()):
                normal = False
            else:
                result.append(('text', text))
                continue
        wrapper = copy.deepcopy(element)
        # Split prose becomes an ordinary inline paragraph. Retain mathematical
        # subtrees, but not display-math paragraph wrappers around each fragment.
        for child in list(wrapper):
            wrapper.remove(child)
        formula = copy.deepcopy(math)
        wrapper.append(formula)
        for child in list(formula):
            formula.remove(child)
        formula.extend(copy.deepcopy(child) for child in children)
        result.append(('xml', wrapper))
    return result if any(kind == 'text' and _VI.search(value) for kind, value in result) else None
