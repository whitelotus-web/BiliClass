"""Conservative evidence of untranslated prose, not a semantic quality score."""

import re
import unicodedata

_FUNCTION_WORDS = set('của và có các một những được trong trên dưới khi thì để bằng với giúp là nếu sẽ từ vào đã đang chưa không nào tại sao nhiều'.split())
_ACCENTS = re.compile('[ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]')
VERSION = 'english-prose-check-v1'


def untranslated_prose(text):
    """Require several accented words and grammar markers; names alone pass.

    Call on provider prose with protected math/teacher terminology replaced by
    their IDs. This intentionally does not certify every short heading or phrase.
    """
    words = re.findall(r'[^\W\d_]+', unicodedata.normalize('NFC', text).casefold())
    return len(set(words) & _FUNCTION_WORDS) >= 2 and sum(bool(_ACCENTS.search(word)) for word in words) >= 3
