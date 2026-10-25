"""Selective DOCX edits: preserve the package and edit only mapped source ranges."""

import copy
import hashlib
import re
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W, 'm': M}
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
MODES = ('below', 'columns', 'keywords', 'english')
TOKEN = re.compile(r'⟦BLC(\d+)⟧')
UNSAFE = {'ins', 'del', 'moveFrom', 'moveTo', 'bookmarkStart', 'bookmarkEnd', 'commentRangeStart',
          'commentRangeEnd', 'fldChar', 'instrText', 'fldSimple', 'sdt', 'altChunk'}


def tag(name):
    return '{' + W + '}' + name


def node(name, **attrs):
    value = etree.Element(tag(name))
    for key, item in attrs.items():
        value.set(tag(key), str(item))
    return value


def parse_xml(raw):
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('Tệp Word có cấu trúc XML không hỗ trợ. Hãy lưu lại thành .docx bằng Word.')
    return etree.fromstring(raw, etree.XMLParser(resolve_entities=False, no_network=True))


class Package:
    def __init__(self, path):
        self.path = Path(path)
        from .document_limits import check_document_size

        check_document_size(self.path)
        if self.path.suffix.lower() != '.docx':
            raise ValueError('Chọn tệp .docx. Với .doc cũ, mở Word và Lưu thành .docx trước.')
        try:
            with zipfile.ZipFile(self.path) as archive:
                entries = archive.infolist()
                names = [entry.filename for entry in entries]
                if (len(entries) > 10000 or len(set(names)) != len(names)
                        or sum(entry.file_size for entry in entries) > 200 * 1024**2
                        or any('..' in PurePosixPath(name).parts or name.startswith('/') or '\\' in name for name in names)):
                    raise ValueError('Gói Word vượt giới hạn cấu trúc an toàn.')
                if any(name.startswith('_xmlsignatures/') or name.endswith('vbaProject.bin') for name in names):
                    raise ValueError('Tài liệu có chữ ký hoặc macro. Dùng một bản .docx không ký, không macro để chuyển đổi.')
                rels = parse_xml(archive.read('_rels/.rels'))
                main = [row.get('Target', '') for row in rels if row.get('Type', '').endswith('/officeDocument') and row.get('TargetMode') != 'External']
                if len(main) != 1:
                    raise ValueError('Không xác định được nội dung Word.')
                self.main = main[0].lstrip('/')
                if self.main not in names:
                    raise ValueError('Tệp Word thiếu phần nội dung chính.')
                if archive.getinfo(self.main).file_size > 32 * 1024**2 or ('word/styles.xml' in names and archive.getinfo('word/styles.xml').file_size > 8 * 1024**2):
                    raise ValueError('Phần văn bản/định dạng Word quá lớn; chia thành bài nhỏ hơn trước khi chuyển đổi.')
                self.tree = parse_xml(archive.read(self.main))
                self.styles = parse_xml(archive.read('word/styles.xml')) if 'word/styles.xml' in names else None
        except (zipfile.BadZipFile, KeyError, etree.XMLSyntaxError):
            raise ValueError('Chưa đọc được .docx. Tệp có thể hỏng hoặc được mã hóa; mở và lưu một bản mới bằng Word.') from None
        self.body = self.tree.find('w:body', NS)
        if self.body is None:
            raise ValueError('Tệp Word chưa có phần thân văn bản.')
        self.rows, self.paragraphs = [], {}
        characters = 0
        for paragraph in self.body.iter(tag('p')):
            if any(parent.tag == tag('txbxContent') for parent in paragraph.iterancestors()):
                continue
            atoms = self.atoms(paragraph)
            text = ''.join(atom['text'] for atom in atoms)
            if not text.strip():
                continue
            identifier = 'p' + str(len(self.rows))
            blocked = any(etree.QName(child).localname in UNSAFE for child in paragraph.iter()) or any(
                parent.tag == tag('sdt') for parent in paragraph.iterancestors())
            prose = any(atom['kind'] == 'text' and any(char.isalpha() for char in atom['text']) for atom in atoms)
            in_table = any(parent.tag == tag('tc') for parent in paragraph.iterancestors())
            row = dict(id=identifier, text=text, editable=not blocked and prose,
                       location=('Ô bảng' if in_table else 'Đoạn') + ' ' + str(len(self.rows) + 1),
                       reason='Đoạn có trường tự động, đánh dấu hoặc lịch sử sửa; giữ nguyên đoạn này.' if blocked else '' if prose else 'Chỉ có hình/công thức; giữ nguyên đối tượng này.',
                       sentences=sentence_ranges(text, atoms))
            self.rows.append(row)
            self.paragraphs[identifier] = (paragraph, atoms, row)
            characters += len(text)
            if len(self.rows) > 5000 or characters > 1_000_000:
                raise ValueError('Bản dùng thử hỗ trợ tối đa 5.000 đoạn và 1.000.000 ký tự mỗi tài liệu.')

    @staticmethod
    def atoms(paragraph):
        result, position = [], 0

        def walk(element):
            nonlocal position
            if element.tag in {tag('pPr'), tag('rPr')}:
                return
            if element.tag in {'{' + M + '}oMath', '{' + M + '}oMathPara', tag('drawing'), tag('pict'), tag('object')}:
                math = element.tag.startswith('{' + M + '}')
                text = ''.join(element.xpath('.//m:t/text()', namespaces=NS)) if math else '[Hình minh họa]'
                text = text.strip() or '[Công thức]'
                kind = 'math' if math else 'object'
            elif element.tag == tag('t'):
                text, kind = element.text or '', 'text'
            elif element.tag in {tag('tab'), tag('br'), tag('cr')}:
                text, kind = ('\t' if element.tag == tag('tab') else '\n'), 'break'
            else:
                for child in element:
                    walk(child)
                return
            result.append(dict(element=element, text=text, kind=kind, start=position, end=position + len(text)))
            position += len(text)

        for child in paragraph:
            walk(child)
        return result

    def selection(self, rows):
        if not isinstance(rows, list) or len(rows) > 2000:
            raise ValueError('Chọn tối đa 2.000 vùng trong một lượt.')
        groups = {}
        for selected in rows:
            identifier = selected.get('paragraph')
            if identifier not in self.paragraphs:
                raise ValueError('Vùng chọn không thuộc tài liệu hiện tại.')
            _, atoms, paragraph = self.paragraphs[identifier]
            if not paragraph['editable']:
                raise ValueError(paragraph['reason'])
            start, end = selected.get('start'), selected.get('end')
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(paragraph['text']):
                raise ValueError('Vị trí vùng chọn chưa hợp lệ.')
            # Never split an equation, image, or a Vietnamese combining cluster.
            for atom in atoms:
                if atom['kind'] in {'math', 'object'} and atom['start'] < end and start < atom['end']:
                    start, end = min(start, atom['start']), max(end, atom['end'])
            while start and start < len(paragraph['text']) and unicodedata.combining(paragraph['text'][start]):
                start -= 1
            while end < len(paragraph['text']) and unicodedata.combining(paragraph['text'][end]):
                end += 1
            groups.setdefault(identifier, []).append((start, end))
        result = []
        for identifier in self.paragraphs:
            merged = []
            for start, end in sorted(groups.get(identifier, [])):
                if merged and start <= merged[-1][1]:
                    merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
                else:
                    merged.append((start, end))
            paragraph, atoms, row = self.paragraphs[identifier]
            for start, end in merged:
                wire, locks, cursor = '', [], start
                for atom in atoms:
                    if atom['kind'] in {'math', 'object'} and start <= atom['start'] and atom['end'] <= end:
                        wire += row['text'][cursor:atom['start']] + f'⟦BLC{len(locks)}⟧'
                        locks.append(dict(text=atom['text'], kind=atom['kind']))
                        cursor = atom['end']
                wire += row['text'][cursor:end]
                if not any(char.isalpha() for char in TOKEN.sub('', wire)):
                    continue
                result.append(dict(id=f'{identifier}:{start}:{end}', paragraph=identifier, start=start, end=end,
                                   vi=row['text'][start:end], wire=wire, locks=locks))
        return result

    def slice(self, paragraph, start, end):
        cloned = copy.deepcopy(paragraph)
        pairs = dict(zip(paragraph.iter(), cloned.iter(), strict=True))
        for atom in self.atoms(paragraph):
            child = pairs[atom['element']]
            left, right = max(start, atom['start']), min(end, atom['end'])
            if right <= left:
                child.getparent().remove(child)
            elif atom['kind'] == 'text':
                child.text = atom['text'][left - atom['start']:right - atom['start']]
                child.set(XML_SPACE, 'preserve')
        section = cloned.find('w:pPr/w:sectPr', NS)
        if section is not None:
            section.getparent().remove(section)
        return cloned

    def english(self, original, region, value, options, *, objects=False):
        paragraph = etree.Element(tag('p'), nsmap=original.nsmap)
        properties = original.find('w:pPr', NS)
        if properties is not None:
            paragraph.append(copy.deepcopy(properties))
        props = paragraph.find('w:pPr', NS)
        if props is None:
            props = node('pPr')
            paragraph.insert(0, props)
        for child in list(props):
            if child.tag in {tag('numPr'), tag('sectPr'), tag('pageBreakBefore')}:
                props.remove(child)
        numbering = node('numPr')
        numbering.append(node('numId', val=0))
        props.append(numbering)
        style = self.run_style(original, region['start'])
        for name, val in [('color', options.get('color', '1667B1')), ('i', '1' if options.get('italic', True) else '0')]:
            existing = style.find('w:' + name, NS)
            if existing is not None:
                style.remove(existing)
            style.append(node(name, val=val))
        size = style.find('w:sz', NS)
        if size is not None:
            size.set(tag('val'), str(max(18, min(144, int(size.get(tag('val'), '22')) - 2))))
        else:
            style.append(node('sz', val=20))
        atoms = self.atoms(original)
        protected = [atom for atom in atoms if atom['kind'] in {'math', 'object'} and region['start'] <= atom['start'] and atom['end'] <= region['end']]
        for part in re.split(r'(⟦BLC\d+⟧)', value):
            match = TOKEN.fullmatch(part)
            if match:
                atom = protected[int(match[1])]
                if atom['kind'] == 'math' or objects:
                    child = copy.deepcopy(atom['element'])
                    if child.tag in {tag('drawing'), tag('pict'), tag('object')}:
                        run = node('r')
                        run.append(child)
                        paragraph.append(run)
                    else:
                        paragraph.append(child)
            elif part:
                run = node('r')
                run.append(copy.deepcopy(style))
                for text in re.split(r'([\n\t])', part):
                    if text in {'\n', '\t'}:
                        run.append(node('br' if text == '\n' else 'tab'))
                    elif text:
                        leaf = node('t')
                        leaf.text = text
                        leaf.set(XML_SPACE, 'preserve')
                        run.append(leaf)
                paragraph.append(run)
        return paragraph

    def run_style(self, paragraph, position):
        style = node('rPr')

        def merge(properties):
            if properties is not None:
                for child in properties:
                    prior = style.find(child.tag)
                    if prior is not None:
                        style.remove(prior)
                    style.append(copy.deepcopy(child))

        if self.styles is not None:
            merge(self.styles.find('w:docDefaults/w:rPrDefault/w:rPr', NS))
            reference = paragraph.find('w:pPr/w:pStyle', NS)
            identity = reference.get(tag('val')) if reference is not None else 'Normal'
            lineage, seen = [], set()
            while identity and identity not in seen:
                seen.add(identity)
                candidates = self.styles.xpath('./w:style[@w:styleId=$identity]', namespaces=NS, identity=identity)
                if not candidates:
                    break
                definition = candidates[0]
                lineage.append(definition.find('w:rPr', NS))
                parent = definition.find('w:basedOn', NS)
                identity = parent.get(tag('val')) if parent is not None else None
            for properties in reversed(lineage):
                merge(properties)
        merge(paragraph.find('w:pPr/w:rPr', NS))
        for atom in self.atoms(paragraph):
            if atom['start'] <= position < atom['end']:
                run = next((parent for parent in atom['element'].iterancestors() if parent.tag == tag('r')), None)
                if run is not None:
                    merge(run.find('w:rPr', NS))
                break
        return style

    def render(self, regions, options):
        mode = options.get('mode', 'below')
        if mode not in MODES or options.get('color', '1667B1') not in {'1667B1', '666666', '000000'}:
            raise ValueError('Chọn kiểu trình bày Word hợp lệ.')
        checked = self.selection(regions)
        incoming = {row['id']: row for row in regions}
        if {row['id'] for row in checked} != set(incoming):
            raise ValueError('Vùng chọn đã thay đổi. Tạo lại bản dịch trước khi lưu.')
        grouped = {}
        for region in checked:
            region.update(en=incoming[region['id']].get('en', ''))
            validate_translation(region, region['en'], keywords=mode == 'keywords')
            grouped.setdefault(region['paragraph'], []).append(region)
        for identifier, chosen in grouped.items():
            paragraph, atoms, row = self.paragraphs[identifier]
            section = paragraph.find('w:pPr/w:sectPr', NS)
            if mode == 'columns':
                table = node('tbl')
                properties = node('tblPr')
                properties.append(node('tblW', w=0, type='auto'))
                properties.append(node('tblLayout', type='fixed'))
                borders = node('tblBorders')
                for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
                    borders.append(node(side, val='nil'))
                properties.append(borders)
                margins = node('tblCellMar')
                for side in ('top', 'left', 'bottom', 'right'):
                    margins.append(node(side, w=100, type='dxa'))
                properties.append(margins)
                table.append(properties)
                width = 9000
                cell = next((parent for parent in paragraph.iterancestors() if parent.tag == tag('tc')), None)
                size = cell.find('w:tcPr/w:tcW', NS) if cell is not None else None
                if size is not None and size.get(tag('type')) == 'dxa':
                    width = max(1800, int(size.get(tag('w'), '9000')) - 200)
                else:
                    section_props = self.body.find('w:sectPr', NS)
                    if section_props is not None:
                        page, margin = section_props.find('w:pgSz', NS), section_props.find('w:pgMar', NS)
                        if page is not None and margin is not None:
                            width = max(1800, int(page.get(tag('w'), '11906')) - int(margin.get(tag('left'), '1440')) - int(margin.get(tag('right'), '1440')))
                grid = node('tblGrid')
                grid.extend([node('gridCol', w=width // 2), node('gridCol', w=width // 2)])
                table.append(grid)
                table_row = node('tr')
                table.append(table_row)
                for english in (False, True):
                    cell = node('tc')
                    cell_props = node('tcPr')
                    cell_props.append(node('tcW', w=width // 2, type='dxa'))
                    cell.append(cell_props)
                    if english:
                        for region in chosen:
                            cell.append(self.english(paragraph, region, region['en'], options))
                    else:
                        cell.append(self.slice(paragraph, 0, len(row['text'])))
                    table_row.append(cell)
                replacement = [table]
                # A Word cell must end in a paragraph, including nested tables.
                separator = node('p')
                separator_props = node('pPr')
                separator_props.append(node('spacing', before=0, after=0, line=20, lineRule='exact'))
                separator.append(separator_props)
                replacement.append(separator)
            else:
                merged = etree.Element(tag('p'), nsmap=paragraph.nsmap)
                if paragraph.find('w:pPr', NS) is not None:
                    merged.append(copy.deepcopy(paragraph.find('w:pPr', NS)))

                def append_contents(part):
                    for child in list(part):
                        if child.tag != tag('pPr'):
                            merged.append(child)

                cursor = 0
                for region in chosen:
                    append_contents(self.slice(paragraph, cursor, region['start']))
                    if mode == 'english':
                        append_contents(self.english(paragraph, region, region['en'], {**options, 'italic': False}, objects=True))
                    elif mode == 'keywords':
                        # Build annotations by source positions, retaining all original runs.
                        position = region['start']
                        for annotation in region.get('annotations', incoming[region['id']].get('annotations', [])):
                            if (not isinstance(annotation, dict) or type(annotation.get('start')) is not int
                                    or type(annotation.get('end')) is not int
                                    or not 0 <= annotation['start'] < annotation['end'] <= len(region['vi'])
                                    or region['start'] + annotation['start'] < position
                                    or not isinstance(annotation.get('en'), str) or not annotation['en'].strip()
                                    or len(annotation['en']) > 160):
                                raise ValueError('Vị trí từ khóa đã thay đổi; tạo lại bản xem trước.')
                            end = region['start'] + annotation['end']
                            append_contents(self.slice(paragraph, position, end))
                            append_contents(self.english(paragraph, {**region, 'start': end, 'end': end}, ' (' + annotation['en'] + ')', options))
                            position = end
                        append_contents(self.slice(paragraph, position, region['end']))
                    else:
                        append_contents(self.slice(paragraph, region['start'], region['end']))
                        for value in ('\n', region['en'], '\n' if region['end'] < len(row['text']) else ''):
                            if value:
                                append_contents(self.english(paragraph, region, value, options))
                    cursor = region['end']
                append_contents(self.slice(paragraph, cursor, len(row['text'])))
                replacement = [merged]
            if section is not None and mode == 'columns':
                props = node('pPr')
                props.append(copy.deepcopy(section))
                replacement[-1].append(props)
            parent, index = paragraph.getparent(), paragraph.getparent().index(paragraph)
            parent.remove(paragraph)
            for child in reversed(replacement):
                parent.insert(index, child)
        return etree.tostring(self.tree, xml_declaration=True, encoding='UTF-8', standalone=True)

    def save(self, output, regions, options):
        raw = self.render(regions, options)
        target = Path(output)
        pending = target.with_suffix('.pending')
        try:
            with zipfile.ZipFile(self.path) as source, zipfile.ZipFile(pending, 'w') as result:
                for item in source.infolist():
                    result.writestr(item, raw if item.filename == self.main else source.read(item.filename))
            with zipfile.ZipFile(pending) as verified:
                if verified.testzip() is not None:
                    raise ValueError('Tệp Word xuất chưa hợp lệ; bản trước được giữ lại.')
                parse_xml(verified.read(self.main))
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)


def sentence_ranges(text, atoms=()):
    starts, cursor = [], 0
    for match in re.finditer(r'[.!?…]+(?=\s|$)|\n+', text):
        if any(atom['kind'] in {'math', 'object'} and atom['start'] <= match.start() < atom['end'] for atom in atoms):
            continue
        prefix = text[cursor:match.end()]
        if re.search(r'(?:\b(?:TS|ThS|PGS|GS|TP|Mr|Mrs|Dr|Prof)|^\s*\d+|\bv\.v|\be\.g|\bi\.e)\.$', prefix, re.I):
            continue
        if prefix.strip():
            starts.append(dict(start=cursor, end=match.end(), text=prefix))
        cursor = match.end()
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
    if text[cursor:].strip():
        starts.append(dict(start=cursor, end=len(text), text=text[cursor:]))
    return starts


def utf16_position(text, offset):
    if type(offset) is not int or offset < 0:
        raise ValueError('Vị trí bôi đen chưa hợp lệ.')
    count = 0
    for position, char in enumerate(text):
        if count == offset:
            return position
        count += 1 + (ord(char) > 0xffff)
        if count > offset:
            raise ValueError('Vùng chọn cắt giữa một ký tự; hãy chọn lại.')
    if count == offset:
        return len(text)
    raise ValueError('Vùng chọn nằm ngoài đoạn.')


def display_translation(region):
    return TOKEN.sub(lambda match: '〔' + region['locks'][int(match[1])]['text'] + '〕', region.get('en', ''))


def validate_translation(region, value, *, keywords=False):
    from .translation_batches import NUMBERS

    if not isinstance(value, str) or not value.strip() or len(value) > 30000:
        raise ValueError('Bản dịch đang trống hoặc quá dài.')
    if keywords:
        return
    if Counter(TOKEN.findall(value)) != Counter(TOKEN.findall(region['wire'])):
        raise ValueError('Giữ nguyên các công thức/hình minh họa trong bản dịch.')
    if Counter(NUMBERS.findall(value)) != Counter(NUMBERS.findall(region['wire'])):
        raise ValueError('Bản dịch làm thay đổi số liệu; kiểm tra lại trước khi lưu.')


def keyword_annotations(region, terms, density='normal'):
    limit = {'few': 2, 'normal': 4, 'deep': 8}.get(density, 4)
    text = region['vi']
    normalized, boundaries = '', []
    for match in re.finditer(r'[^\W\d_][\u0300-\u036f]*|.', text, re.S):
        value = unicodedata.normalize('NFC', match[0])
        normalized += value
        boundaries.extend([(match.start(), match.end())] * len(value))
    candidates = []
    for vi, en in sorted(terms.items(), key=lambda row: (-len(row[0]), row[0])):
        if not vi or vi.casefold() == en.casefold() or not any(char.isalpha() for char in en):
            continue
        for match in re.finditer(r'(?<!\w)' + re.escape(unicodedata.normalize('NFC', vi)) + r'(?!\w)', normalized, re.I):
            start, end = boundaries[match.start()][0], boundaries[match.end() - 1][1]
            if text[end:].lstrip().startswith('(') or any(a['start'] < end and start < a['end'] for a in candidates):
                continue
            if any(a['en'].casefold() == en.casefold() for a in candidates):
                continue
            candidates.append(dict(start=start, end=end, vi=text[start:end], en=en))
            if len(candidates) == limit:
                return sorted(candidates, key=lambda row: row['start'])
    return sorted(candidates, key=lambda row: row['start'])


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while part := stream.read(1024**2):
            result.update(part)
    return result.hexdigest()
