"""Read structural slide labels; leave decimals and English pronouns intact."""
import re

VERSION = 'spoken-labels-v1'
_PREFIX = re.compile(r'^(\s*)(\d+|[IVX]+)[.)/]\s*(?=\S|$)')


def english(text):
    match = _PREFIX.match(text)
    if not match:
        return text
    label = match[2]
    if label.isdigit():
        # A decimal such as 3.5 is a value, not a list item.
        if match.end() < len(text) and text[match.end()].isdigit():
            return text
        number = label
    else:
        valid = re.fullmatch(r'X{0,3}(?:IX|IV|V?I{0,3})', label)
        if not valid or not label:
            return text
        values = {'I': 1, 'V': 5, 'X': 10}
        number = str(sum(-values[v] if i+1 < len(label) and values[v] < values[label[i+1]] else values[v]
                         for i,v in enumerate(label)))
    return match[1] + 'Section ' + number + '. ' + text[match.end():]
