"""Correct measured solid-fill text contrast on a copy, without rewriting words."""

import copy
import zipfile
from pathlib import Path
from uuid import uuid4

from lxml import etree


def keys(report):
    from .slide_repair import _target

    return {(row['slide'], _target(issue)) for row in report['slides'] for issue in row['issues']
            if issue['code'] == 'low_contrast'}


def repair(path, directory, report):
    from .slide_quality import contrast_ratio
    from .slide_repair import NS, _body, _shape, _write_copy, file_digest
    from .source_deck import source_slide_parts

    if file_digest(path) != report['sha256']:
        raise ValueError('Bài đã thay đổi; giữ nguyên bản trước khi sửa màu chữ.')
    parts = source_slide_parts(path)
    replacements, changes = {}, []
    with zipfile.ZipFile(path) as archive:
        for row in report['slides']:
            root = etree.fromstring(archive.read(parts[row['slide'] - 1]))
            for issue in row['issues']:
                background = issue.get('background_rgb')
                if issue['code'] != 'low_contrast' or type(background) is not int or background < 0:
                    continue
                target = (issue['shape_id'], *issue['cell']) if issue.get('cell') is not None else issue.get('shape_id')
                shape = _shape(root, target)
                body = _body(shape) if shape is not None else None
                if body is None or body.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'):
                    continue
                color = max((0, 0xffffff), key=lambda value: contrast_ratio(value, background))
                if contrast_ratio(color, background) < issue.get('threshold', 4.5):
                    continue
                for paragraph in body.findall('a:p', NS):
                    if not paragraph.xpath('.//a:t/text()', namespaces=NS):
                        continue
                    props = paragraph.find('a:pPr', NS)
                    if props is None:
                        props = etree.Element('{' + NS['a'] + '}pPr')
                        paragraph.insert(0, props)
                    default = props.find('a:defRPr', NS)
                    if default is None:
                        etree.SubElement(props, '{' + NS['a'] + '}defRPr')
                fill = etree.Element('{' + NS['a'] + '}solidFill')
                etree.SubElement(fill, '{' + NS['a'] + '}srgbClr', val='FFFFFF' if color else '000000')
                for props in body.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr', namespaces=NS):
                    for node in list(props):
                        if etree.QName(node).localname in {'solidFill', 'noFill', 'gradFill', 'pattFill', 'grpFill'}:
                            props.remove(node)
                    props.insert(1 if props.find('a:ln', NS) is not None else 0, copy.deepcopy(fill))
                changes.append({'slide': row['slide'], 'shape_id': issue['shape_id'],
                                **({'cell': issue['cell']} if 'cell' in issue else {}), 'operation': 'improve_text_contrast'})
            if changes and changes[-1]['slide'] == row['slide']:
                replacements[parts[row['slide'] - 1]] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    if not changes:
        return {'path': str(path), 'changes': []}
    target = Path(directory) / 'temp/slide-repair' / uuid4().hex / 'contrast.pptx'
    target.parent.mkdir(parents=True)
    _write_copy(path, target, replacements)
    return {'path': str(target), 'changes': changes}


def verified(path, directory, inspection, *, source=None, mode='', style='source', layout_plan=None,
             cancel=None, progress=None):
    from .chatgpt_handoff import inspect_returned_deck
    from .office_tasks import render_quality
    from .slide_repair import failure_keys

    unchanged = {'path': str(path), 'inspection': inspection, 'changes': []}
    if not keys(inspection['slide_quality']) or cancel and cancel.is_set():
        return unchanged
    result = repair(path, directory, inspection['slide_quality'])
    if Path(result['path']) == Path(path):
        return unchanged
    candidate = inspect_returned_deck(result['path'], source, mode, style, layout_plan=layout_plan)
    render_quality(result['path'], directory, candidate['slide_quality'], cancel, progress)
    if (failure_keys(candidate['slide_quality']) <= failure_keys(inspection['slide_quality'])
            and keys(candidate['slide_quality']) < keys(inspection['slide_quality'])
            and all(row['rendered'] for row in candidate['slide_quality']['slides'])):
        return {**result, 'inspection': candidate}
    return unchanged
