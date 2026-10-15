"""Unicode fallback for embedded fonts unavailable for newly translated styles."""

import os
import re
import zipfile
from functools import lru_cache

from lxml import etree

from .source_deck import NS


@lru_cache(maxsize=1)
def installed_families():
    if os.name != 'nt':
        return None
    import winreg

    result = set()
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts') as key:
                for index in range(winreg.QueryInfoKey(key)[1]):
                    name = winreg.EnumValue(key, index)[0]
                    result.update(re.sub(r'\s*\([^)]*\)\s*$', '', part).strip().casefold()
                                  for part in name.split(' & '))
        except OSError:
            pass
    return result or None


def missing_embedded_fonts(source):
    families = installed_families()
    if not families or 'arial' not in families:
        return {}
    with zipfile.ZipFile(source) as archive:
        tree = etree.fromstring(archive.read('ppt/presentation.xml'))
    faces = tree.xpath('.//p:embeddedFontLst//p:font/@typeface', namespaces=NS)
    return {face: 'Arial' for face in faces if face.casefold() not in families
            and not re.search(r'math|symbol|wingdings|webdings', face, re.I)}


def normalize(shape, replacements):
    for font in shape.xpath('.//a:latin|.//a:ea|.//a:cs|.//a:sym', namespaces=NS):
        face = font.get('typeface')
        if face in replacements and not any(
                etree.QName(parent).namespace == 'http://schemas.openxmlformats.org/officeDocument/2006/math'
                for parent in font.iterancestors()):
            font.set('typeface', replacements[face])
