"""Local DOCX reading preview, with verified rich-text to source selection mapping.

This is a reading surface, not a Word pagination engine. Only embedded raster
images are read; document links and remote relationships are never followed.
"""

import base64
import copy
import io
import re
import zipfile
from collections import Counter
from html import escape
from pathlib import PurePosixPath

from .word_document import NS, parse_xml, tag, utf16_position

ANCHOR = re.compile(r'blc_(p\d+)\Z')


def length(text):
    return len(text.encode('utf-16-le')) // 2


def normalized(text):
    return text.replace('\r\n', '\n').replace('\r', '\n').replace('\u2028', '\n')


def qt_text(text):
    # Qt Quick getText exposes frame boundary characters around table cells;
    # normalize each one to ONE separator, without changing UTF-16 positions.
    return text.translate(str.maketrans({'\u2028': '\n', '\u2029': '\n', '\ufdd0': '\n', '\ufdd1': '\n'}))


class Preview:
    def __init__(self, package):
        self.package = package
        if sum(len(entry[1]) for entry in package.paragraphs.values()) > 30_000:
            raise ValueError('Tài liệu có quá nhiều vùng định dạng để dựng bản xem nhẹ.')
        self.rows = {}
        self.images = {}
        self.image_budget = 2 * 1024**2
        self.markup_budget = 8 * 1024**2
        self.theme_fonts = {'major': 'Cambria', 'minor': 'Calibri'}
        self.font_counts = Counter()
        self.by_element = {entry[0]: identity for identity, entry in package.paragraphs.items()}
        self.width, self.margins = 794, [64, 64, 64, 64]
        section = package.body.find('w:sectPr', NS)
        if section is not None:
            size = section.find('w:pgSz', NS)
            if size is not None:
                self.width = max(500, min(1600, int(size.get(tag('w'), '11906')) / 15))
            margins = section.find('w:pgMar', NS)
            if margins is not None:
                self.margins = [max(12, min(180, int(margins.get(tag(side), '960')) / 15))
                                for side in ('top', 'right', 'bottom', 'left')]
        with zipfile.ZipFile(package.path) as archive:
            if 'word/theme/theme1.xml' in archive.namelist():
                theme = parse_xml(archive.read('word/theme/theme1.xml'))
                for name in ('major', 'minor'):
                    fonts = theme.xpath('//*[local-name()=$kind]/*[local-name()="latin"]/@typeface', kind=name + 'Font')
                    if fonts and fonts[0]:
                        self.theme_fonts[name] = re.sub(r"[^\w .\-]", '', fonts[0])[:120]
            self.relationships = {}
            rel_path = str(PurePosixPath(package.main).parent / '_rels' / (PurePosixPath(package.main).name + '.rels'))
            if rel_path in archive.namelist():
                for rel in parse_xml(archive.read(rel_path)):
                    if rel.get('TargetMode') != 'External' and rel.get('Type', '').endswith('/image'):
                        target = rel.get('Target', '')
                        candidate = PurePosixPath(package.main).parent / target
                        if target.startswith('/'):
                            candidate = PurePosixPath(target.lstrip('/'))
                        if '..' not in candidate.parts and '\\' not in target:
                            self.relationships[rel.get('Id')] = str(candidate)
            body = ''.join(self.block(child, archive) for child in package.body)
        self.html = '<html><body style="font-family:' + self.theme_fonts['minor'] + ';font-size:12pt;color:#202020">' + body + '</body></html>'
        self.fonts = [family for family, _ in self.font_counts.most_common()]
        # Keep the XML tree out of the UI object and release decompressed images.
        del self.package, self.by_element, self.relationships, self.images

    def properties(self, paragraph):
        result = {}
        reference = paragraph.find('w:pPr/w:pStyle', NS)
        identity = reference.get(tag('val')) if reference is not None else 'Normal'
        definitions, seen = [], set()
        if self.package.styles is not None:
            default = self.package.styles.find('w:docDefaults/w:pPrDefault/w:pPr', NS)
            if default is not None:
                definitions.append(default)
            lineage = []
            while identity and identity not in seen:
                seen.add(identity)
                found = self.package.styles.xpath('./w:style[@w:styleId=$identity]', namespaces=NS, identity=identity)
                if not found:
                    break
                lineage.append(found[0].find('w:pPr', NS))
                parent = found[0].find('w:basedOn', NS)
                identity = parent.get(tag('val')) if parent is not None else None
            definitions.extend(reversed(lineage))
        definitions.append(paragraph.find('w:pPr', NS))
        for definition in definitions:
            if definition is not None:
                result.update({child.tag: child for child in definition})
        return result

    def paragraph(self, paragraph, archive):
        identity = self.by_element.get(paragraph)
        if not identity:
            return '<p style="margin:0"><br/></p>'
        _, atoms, row = self.package.paragraphs[identity]
        props = self.properties(paragraph)
        css = ['white-space:pre-wrap', 'margin-top:0px', 'margin-bottom:6px']
        alignment = props.get(tag('jc'))
        if alignment is not None:
            align = {'center': 'center', 'right': 'right', 'end': 'right', 'both': 'justify'}.get(alignment.get(tag('val')), 'left')
            css.append('text-align:' + align)
        spacing = props.get(tag('spacing'))
        if spacing is not None:
            for field, style in (('before', 'margin-top'), ('after', 'margin-bottom')):
                if spacing.get(tag(field)):
                    css.append(f'{style}:{min(120, int(spacing.get(tag(field))) / 15)}px')
            if spacing.get(tag('lineRule'), 'auto') == 'auto' and spacing.get(tag('line')):
                css.append(f'line-height:{max(80, min(300, int(spacing.get(tag("line"))) / 2.4))}%')
        indent = props.get(tag('ind'))
        if indent is not None:
            for field, style in (('left', 'margin-left'), ('right', 'margin-right'), ('firstLine', 'text-indent')):
                if indent.get(tag(field)):
                    css.append(f'{style}:{max(-120, min(240, int(indent.get(tag(field))) / 15))}px')
        # The end position resolves defaults without adopting the first run's style.
        base = self.package.run_style(paragraph, len(row['text']))
        chunks, segments, visible = [], [], ''
        for atom in atoms:
            shown = normalized(atom['text'])
            image = self.image(atom['element'], archive) if atom['kind'] == 'object' else ''
            if image:
                shown, markup = '\ufffc', image
            else:
                style = copy.deepcopy(base)
                run = next((parent for parent in atom['element'].iterancestors() if parent.tag == tag('r')), None)
                override = run.find('w:rPr', NS) if run is not None else None
                if override is not None:
                    for child in override:
                        prior = style.find(child.tag)
                        if prior is not None:
                            style.remove(prior)
                        style.append(copy.deepcopy(child))
                markup = '<span style="' + escape(self.run_css(style, atom['kind'], len(shown)), quote=True) + '">' + escape(shown).replace('\n', '<br/>') + '</span>'
            segments.append((len(visible), len(visible) + len(shown), atom['start'], atom['end'], atom['text'], bool(image)))
            visible += shown
            chunks.append(markup)
        self.rows[identity] = dict(source=row, visible=visible, segments=segments, chunks=chunks, css=';'.join(css))
        return '<p style="' + ';'.join(css) + '"><a name="blc_' + identity + '"></a>' + ''.join(chunks) + '</p>'

    def run_css(self, style, kind, weight=0):
        css = []
        fonts = style.find('w:rFonts', NS)
        family = self.theme_fonts['minor']
        if fonts is not None:
            family = fonts.get(tag('ascii')) or fonts.get(tag('hAnsi'))
            if not family:
                theme = fonts.get(tag('asciiTheme')) or fonts.get(tag('hAnsiTheme')) or ''
                family = self.theme_fonts.get('major' if theme.startswith('major') else 'minor')
            if family:
                # Font names cannot introduce CSS declarations or markup.
                family = re.sub(r"[^\w .\-]", '', family)[:120]
        if family:
            css.append("font-family:'" + family + "'")
            if kind == 'text' and weight:
                self.font_counts[family] += weight
        size = style.find('w:sz', NS)
        if size is not None:
            css.append(f'font-size:{max(6, min(72, int(size.get(tag("val"), "24")) / 2))}pt')
        for prop, name, value in (('b', 'font-weight', 'bold'), ('i', 'font-style', 'italic'), ('strike', 'text-decoration', 'line-through')):
            node = style.find('w:' + prop, NS)
            if node is not None and node.get(tag('val'), '1') not in {'0', 'false', 'off'}:
                css.append(name + ':' + value)
        underline = style.find('w:u', NS)
        if underline is not None and underline.get(tag('val'), 'single') != 'none':
            css.append('text-decoration:underline')
        color = style.find('w:color', NS)
        if color is not None and re.fullmatch('[0-9a-fA-F]{6}', color.get(tag('val'), '')):
            css.append('color:#' + color.get(tag('val')))
        vertical = style.find('w:vertAlign', NS)
        if vertical is not None and vertical.get(tag('val')) in {'superscript', 'subscript'}:
            css.append('vertical-align:' + ('super' if vertical.get(tag('val')) == 'superscript' else 'sub'))
        if kind == 'math':
            css.extend(["font-family:'Cambria Math'", 'font-style:italic'])
        return ';'.join(css)

    def image(self, element, archive):
        links = element.xpath('.//@r:embed | .//@r:id', namespaces={'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
        target = next((self.relationships[link] for link in links if link in self.relationships), '')
        if not target:
            return ''
        if target in self.images:
            result = self.images[target]
            if len(result) > self.markup_budget:
                return ''
            self.markup_budget -= len(result)
            return result
        result = ''
        try:
            from PIL import Image

            info = archive.getinfo(target)
            if info.file_size > 12 * 1024**2 or len(self.images) >= 64 or self.image_budget <= 0:
                return ''
            with Image.open(io.BytesIO(archive.read(target))) as picture:
                if picture.width * picture.height > 25_000_000 or picture.format not in {'PNG', 'JPEG', 'GIF', 'BMP', 'TIFF', 'WEBP'}:
                    return ''
                picture.thumbnail((1000, 1000))
                stream = io.BytesIO()
                picture.convert('RGBA').save(stream, format='PNG')
                raw = stream.getvalue()
                if len(raw) > self.image_budget:
                    return ''
                self.image_budget -= len(raw)
                width, height = picture.size
                extents = element.xpath('.//*[local-name()="extent"]')
                if extents:
                    width, height = int(extents[0].get('cx', '0')) / 9525, int(extents[0].get('cy', '0')) / 9525
                ratio = min(1, (self.width - self.margins[1] - self.margins[3]) / max(1, width), 700 / max(1, height))
                result = f'<img src="data:image/png;base64,{base64.b64encode(raw).decode()}" width="{max(1, int(width * ratio))}" height="{max(1, int(height * ratio))}"/>'
        except (OSError, ValueError, KeyError):
            pass
        self.images[target] = result
        self.markup_budget -= len(result)
        return result

    def excerpt(self, identity, start, end):
        row = self.rows[identity]
        chunks, segments, visible = [], [], ''
        for (_, _, begin, finish, text, image), markup in zip(row['segments'], row['chunks'], strict=True):
            left, right = max(start, begin), min(end, finish)
            if left >= right:
                continue
            if image:
                left, right, shown, part = begin, finish, '\ufffc', text
            else:
                part = text[left - begin:right - begin]
                shown = normalized(part)
                markup = markup[:markup.index('>') + 1] + escape(shown).replace('\n', '<br/>') + '</span>'
            segments.append((len(visible), len(visible) + len(shown), left, right, part, image))
            visible += shown
            chunks.append(markup)
        result = object.__new__(Preview)
        result.rows = {identity: dict(source=row['source'], visible=visible, segments=segments)}
        result.html = '<p style="' + row['css'] + '"><a name="blc_' + identity + '"></a>' + ''.join(chunks) + '</p>'
        return result

    def block(self, element, archive):
        if element.tag == tag('p'):
            return self.paragraph(element, archive)
        if element.tag == tag('tbl'):
            rows = []
            for row in element.findall('w:tr', NS):
                cells = []
                for cell in row.findall('w:tc', NS):
                    grid = cell.find('w:tcPr/w:gridSpan', NS)
                    span = max(1, min(32, int(grid.get(tag('val'), '1')))) if grid is not None else 1
                    cells.append(f'<td colspan="{span}" style="border:1px solid #aeb8c6;padding:5px">' + ''.join(self.block(child, archive) for child in cell) + '</td>')
                rows.append('<tr>' + ''.join(cells) + '</tr>')
            return '<table border="1" cellspacing="0" cellpadding="4" width="100%">' + ''.join(rows) + '</table>'
        if element.tag in {tag('sdt'), tag('sdtContent'), tag('customXml')}:
            return ''.join(self.block(child, archive) for child in element)
        return ''

    def ranges(self, document, start, end):
        if not 0 <= start < end < document.characterCount():
            raise ValueError('Bôi đen lại phần văn bản cần dịch.')
        result, skipped = [], 0
        block = document.findBlock(start)
        while block.isValid() and block.position() < end:
            left, right = max(0, start - block.position()), min(length(block.text()), end - block.position())
            if left < right:
                identity, fragment = '', block.begin()
                while not fragment.atEnd():
                    for name in fragment.fragment().charFormat().anchorNames():
                        match = ANCHOR.fullmatch(name)
                        if match:
                            identity = match[1]
                            break
                    fragment += 1
                row = self.rows.get(identity)
                if not row or normalized(block.text()) != row['visible']:
                    raise ValueError('Bố cục xem trước đã đổi; tải lại tài liệu rồi chọn lại vùng dịch.')
                begin, finish = utf16_position(block.text(), left), utf16_position(block.text(), right)
                if normalized(block.text())[begin:finish].strip():
                    if not row['source']['editable']:
                        skipped += 1
                    else:
                        result.append(dict(paragraph=identity,
                            start=self.source_position(row, begin, False), end=self.source_position(row, finish, True)))
            block = block.next()
        if not result:
            raise ValueError('Vùng bôi đen chưa có phần chữ dịch được. Hình, công thức và đoạn đang khóa được giữ nguyên.')
        return result, skipped

    @staticmethod
    def source_position(row, position, end):
        for left, right, begin, finish, text, image in row['segments']:
            if left <= position <= right:
                if image:
                    return finish if position > left or end and position == right else begin
                # Account for source CRLF and Word's Qt-normalized line breaks.
                boundaries, index = [0], 0
                while index < len(text):
                    index += 2 if text[index:index + 2] == '\r\n' else 1
                    boundaries.append(index)
                return begin + boundaries[position - left]
        return len(row['source']['text'])
