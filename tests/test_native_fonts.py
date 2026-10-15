import zipfile

from lxml import etree
from pptx import Presentation

from app import native_fonts
from app.source_deck import NS


def test_only_unavailable_embedded_prose_fonts_receive_fallback(tmp_path, monkeypatch):
    path = tmp_path/'fonts.pptx'
    Presentation().save(path)
    with zipfile.ZipFile(path) as archive:
        entries = {n: archive.read(n) for n in archive.namelist()}
    root = etree.fromstring(entries['ppt/presentation.xml'])
    font_list = etree.SubElement(root, '{'+NS['p']+'}embeddedFontLst')
    for face in ['Cabin', 'Arial', 'Cambria Math', 'Wingdings']:
        entry = etree.SubElement(font_list, '{'+NS['p']+'}embeddedFont')
        etree.SubElement(entry, '{'+NS['p']+'}font', typeface=face)
    entries['ppt/presentation.xml'] = etree.tostring(root)
    with zipfile.ZipFile(path, 'w') as archive:
        for n, data in entries.items():
            archive.writestr(n, data)
    monkeypatch.setattr(native_fonts, 'installed_families', lambda: {'arial', 'cambria math'})
    assert native_fonts.missing_embedded_fonts(path) == {'Cabin': 'Arial'}
    shape = etree.fromstring(('<p:sp xmlns:p="'+NS['p']+'" xmlns:a="'+NS['a']+'">'
                              '<a:r><a:rPr><a:latin typeface="Cabin"/></a:rPr><a:t>Năng lượng</a:t></a:r>'
                              '<a:r><a:rPr><a:latin typeface="Cambria Math"/></a:rPr><a:t>π</a:t></a:r></p:sp>').encode())
    native_fonts.normalize(shape, {'Cabin': 'Arial'})
    assert shape.xpath('.//a:latin/@typeface', namespaces=NS) == ['Arial', 'Cambria Math']
    assert shape.xpath('.//a:t/text()', namespaces=NS) == ['Năng lượng', 'π']
