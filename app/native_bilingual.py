"""Apply validated translations to native OOXML; keep original package resources."""

import copy
import posixpath
import re
import zipfile
from pathlib import Path

from lxml import etree

from .source_deck import NS, _bytes, _part_relative, _rels_path, _size, _xml, source_slide_parts
from .translation_batches import TOKEN, lock_numbers, restore
from .native_layout import can_fit, fit_body


def leaves(shapes):
    for shape in shapes:
        if hasattr(shape, 'shapes'):
            yield from leaves(shape.shapes)
        else:
            yield shape


def picture_key(shape):
    try:
        return shape.image.sha1
    except (ValueError,KeyError):
        return None


def paragraph_text(paragraph):
    return ''.join(
        node.text or '' for node in paragraph.iter() if etree.QName(node).localname == 't')


def _title_height(shape, shapes, deck):
    size=_size(shape.text_frame,shape)
    required=int(((size+max(18,size*.8))*1.12)*12700+shape.text_frame.margin_top+shape.text_frame.margin_bottom)
    height=max(shape.height,required)
    height=min(height, deck.slide_height-shape.top)
    for other in shapes:
        if other.shape_id==shape.shape_id:
            continue
        if not (other.has_text_frame and other.text.strip()) and other.width*other.height>deck.slide_width*deck.slide_height*.6:
            continue  # A full-slide decorative background remains behind the title.
        if (shape.left<other.left+other.width and shape.left+shape.width>other.left
                and other.top>=shape.top+shape.height-12700 and other.top<shape.top+height):
            height=min(height, other.top-shape.top)
    return height if height >= shape.height and can_fit(shape, '', title_height=height) else None


def _fits_bilingual(shape,mode):
    return can_fit(shape,mode)


def _body_height(shape, shapes, deck, mode):
    """Use only genuinely empty space below a text box; never move a picture."""
    height = min(deck.slide_height-shape.top, shape.height+max(shape.height//2, 48*12700))
    for other in shapes:
        if other.shape_id == shape.shape_id:
            continue
        if not (other.has_text_frame and other.text.strip()) and other.width*other.height > deck.slide_width*deck.slide_height*.6:
            continue
        if (shape.left < other.left+other.width and shape.left+shape.width > other.left
                and other.top+other.height > shape.top+shape.height
                and other.top < shape.top+height):
            # An already overlapping decoration/figure forbids expansion too.
            height = min(height, max(shape.height, other.top-shape.top-12700))
    return height if height > shape.height and can_fit(shape, mode, height=height) else None


def extract(source, mode):
    """Preflight before any send. Image/diagram-heavy decks retain the visual route."""
    from pptx import Presentation

    from .importers import inspect_zip
    from .input_analysis import language_of

    inspect_zip(source)
    deck = Presentation(source)
    original_parts = source_slide_parts(source)
    units, unsupported, english = [], [], 0
    picture_slides = {}
    for index, slide in enumerate(deck.slides,1):
        for shape in leaves(slide.shapes):
            if int(shape.shape_type) == 13:
                picture_slides.setdefault(picture_key(shape),set()).add(index)
    for index, slide in enumerate(deck.slides, 1):
        shapes = list(leaves(slide.shapes))
        motion={int(value) for value in slide._element.xpath('.//p:spTgt/@spid') if value.isdigit()}
        if mode != 'english_only' and any(hasattr(shape,'shapes') and any(s.has_text_frame and s.text.strip() for s in leaves(shape.shapes)) for shape in slide.shapes):
            unsupported.append(f'Slide {index}: giữ bố cục nhóm đối tượng gốc')
        text_ids={shape.shape_id for shape in shapes if shape.has_text_frame and shape.text.strip()}
        if (mode in {'parallel_columns','sentence_pairs'} and slide._element.find('p:timing',NS) is not None
                and (not motion or motion & text_ids)):
            unsupported.append(f'Slide {index}: giữ đồng bộ hiệu ứng với bản song ngữ')
        if slide._element.xpath('.//*[local-name()="AlternateContent"]//*[local-name()="txBody" or local-name()="oMath"]'):
            unsupported.append(f'Slide {index}: đối tượng chữ/công thức có nhánh tương thích cần kiểm tra trực quan')
        text_count = sum(len(shape.text.strip()) for shape in shapes if shape.has_text_frame)
        pictures = [s for s in shapes if int(s.shape_type) == 13]
        if any(p.width*p.height > deck.slide_width*deck.slide_height*.08
               and (text_count < 60 or picture_key(p) is None or len(picture_slides[picture_key(p)]) <= max(2,len(deck.slides)*.15)) for p in pictures):
            unsupported.append(f'Slide {index}: nội dung phụ thuộc ảnh')
        for shape in shapes:
            fully_outside=(shape.left+shape.width<=0 or shape.top+shape.height<=0
                or shape.left>=deck.slide_width or shape.top>=deck.slide_height)
            if fully_outside and shape.shape_id not in motion:
                continue  # Keep unused source workspace objects byte-for-byte.
            transform = shape._element.find('p:spPr/a:xfrm',NS)
            if mode == 'parallel_columns' and shape.has_text_frame and (
                    transform is None or transform.get('rot') not in {None,'0'}):
                unsupported.append(f'Slide {index}: hộp chữ xoay hoặc thiếu tọa độ riêng')
            title_height=layout_height=None
            shape_title=(shape.has_text_frame and (shape.is_placeholder and int(shape.placeholder_format.type) in {1,3}
                or 0<=shape.top<deck.slide_height*.18 and shape.width>deck.slide_width*.22 and len(shape.text)<180))
            if shape.has_text_frame and shape.text.strip():
                if (shape.left<0 or shape.top<0 or shape.left+shape.width>deck.slide_width
                        or shape.top+shape.height>deck.slide_height) and shape.shape_id not in motion:
                    unsupported.append(f'Slide {index}: dàn lại vùng chữ tràn khung có sẵn')
                if shape_title and mode!='english_only':
                    title_height=_title_height(shape,shapes,deck)
                    if title_height is None:
                        unsupported.append(f'Slide {index}: cần dành vùng cho tiêu đề song ngữ')
                elif len(shape.text)>12 and not _fits_bilingual(shape,mode):
                    layout_height=_body_height(shape,shapes,deck,mode)
                    if layout_height is None:
                        unsupported.append(f'Slide {index}: cần dàn lại vùng chữ chật')
            if shape._element.xpath('.//a:graphicData[not(a:tbl)]'):
                unsupported.append(f'Slide {index}: sơ đồ cần xử lý trực quan')
            if shape.has_chart:
                unsupported.append(f'Slide {index}: biểu đồ có nhãn riêng')
            if shape.has_table and mode == 'parallel_columns':
                unsupported.append(f'Slide {index}: bảng cần dàn hai cột trực quan')
            bodies = ([shape._element.find('p:txBody', NS)] if shape.has_text_frame else
                      shape._element.findall('.//a:tc/a:txBody', NS) if shape.has_table else [])
            for body_index, body in enumerate(bodies):
                if body is None:
                    continue
                for paragraph_index, paragraph in enumerate(body.findall('a:p', NS)):
                    raw = paragraph_text(paragraph).strip()
                    if not raw:
                        continue
                    if TOKEN.search(raw):
                        unsupported.append(f'Slide {index}: nhãn nguồn trùng định dạng chuyển đổi')
                        continue
                    parts, numbers, xml_locks = [], [], {}
                    for child in paragraph:
                        tag = etree.QName(child).localname
                        if tag in {'pPr','endParaRPr'}:
                            continue
                        if tag == 'br':
                            parts.append('\n')
                            continue
                        special = tag != 'r' or child.find('a:rPr', NS) is not None and (
                            child.find('a:rPr', NS).get('baseline', '0') != '0')
                        if special:
                            token = len(numbers)
                            numbers.append(paragraph_text(child))
                            xml_locks[str(token)] = _bytes(child).decode('utf-8')
                            parts.append(f'⟦BLC{token}⟧')
                        else:
                            value = paragraph_text(child)
                            protected, locked = lock_numbers(value)
                            protected = TOKEN.sub(lambda m: f'⟦BLC{int(m.group()[4:-1])+len(numbers)}⟧', protected)
                            numbers.extend(locked)
                            parts.append(protected)
                    text = ''.join(parts).strip()
                    if not text:
                        continue
                    if len(text)>14000:
                        unsupported.append(f'Slide {index}: vùng nội dung cần xử lý trực quan')
                    language = language_of(raw)
                    if re.fullmatch(r'[A-Za-zα-ωΑ-Ω]',raw) or len(raw)<=8 and re.search(r'[\d₀-₉/*^=]',raw) and re.fullmatch(r'[A-Za-zα-ωΑ-Ω\d₀-₉/*^=+().−-]+',raw):
                        language='neutral'
                    english += language == 'en'
                    units.append({'id':f's{index}o{shape.shape_id}b{body_index}p{paragraph_index}',
                        'slide':index,'shape_id':shape.shape_id,'body':body_index,'paragraph':paragraph_index,
                        'text':text,'numbers':numbers,'xml_locks':xml_locks,'language':language,
                        'raw':raw,'title':bool(shape_title),'title_height':title_height,'part':original_parts[index-1],
                        'layout_height':layout_height,
                        'font_size':round(_size(shape.text_frame,shape)*100) if shape.has_text_frame else 1800})
    if mode != 'english_only' and english > max(5, len(units)*.35):
        unsupported.append('Nguồn có nhiều vùng English/song ngữ cần ghép cặp trực quan')
    if not units:
        unsupported.append('Nguồn chưa có văn bản chỉnh sửa được')
    visual = {int(match[1]) for reason in unsupported if (match:=re.match(r'Slide (\d+):',reason))}
    if any(not reason.startswith('Slide ') for reason in unsupported):
        visual = set(range(1,len(deck.slides)+1))
    native = [unit for unit in units if unit['slide'] not in visual]
    return {'version':2,'eligible':bool(units or visual),'reasons':list(dict.fromkeys(unsupported)),
            'slides':len(deck.slides),'units':native,'visual_slides':sorted(visual),
            'text_characters':sum(len(u['text']) for u in native)}


def _element(parent, prefix, tag, **attributes):
    return etree.SubElement(parent, f'{{{NS[prefix]}}}{tag}', **{k:str(v) for k,v in attributes.items()})


def translated_paragraph(original, text, unit, *, english=False, smaller=False):
    """Translate natural text while keeping fields/equations/superscripts as XML."""
    restore(text, unit['numbers'])
    result = copy.deepcopy(original)
    for child in list(result):
        if etree.QName(child).localname != 'pPr':
            result.remove(child)
    template = next((props for run in original.findall('a:r', NS)
                     if (props := run.find('a:rPr', NS)) is not None
                     and props.get('baseline', '0') == '0'), None)
    if template is None:
        template=original.find('a:pPr/a:defRPr',NS)
    template = copy.deepcopy(template) if template is not None else etree.Element(f'{{{NS["a"]}}}rPr')
    template.tag=f'{{{NS["a"]}}}rPr'
    template.attrib.pop('baseline', None)
    if template.get('sz') is None and unit.get('font_size'):
        template.set('sz',str(unit['font_size']))
    if english:
        template.set('lang','en-US')
    if smaller:
        template.set('i','1')
        size = int(template.get('sz', '2400'))
        template.set('sz',str(max(min(1400, size), round(size*.8))))
    for piece in re.split(r'(⟦BLC\d+⟧)', text):
        if not piece:
            continue
        if TOKEN.fullmatch(piece):
            key = piece[4:-1]
            if key in unit['xml_locks']:
                result.append(_xml(unit['xml_locks'][key].encode('utf-8')))
                continue
            piece = unit['numbers'][int(key)]
        for number, line in enumerate(piece.split('\n')):
            if number:
                _element(result,'a','br')
            if line:
                run = _element(result,'a','r')
                run.append(copy.deepcopy(template))
                _element(run,'a','t').text = line
    return result


def _fit_body(body):
    properties = body.find('a:bodyPr', NS)
    if properties is None:
        return
    properties.set('wrap','square')
    for child in list(properties):
        if etree.QName(child).localname in {'normAutofit','spAutoFit','noAutofit'}:
            properties.remove(child)
    _element(properties,'a','noAutofit')


def _pair_columns(tree, shape, english):
    """Static text uses sibling columns; animated/grouped slides use the visual lane."""
    properties = shape.find('p:spPr/a:xfrm', NS)
    if properties is None or properties.get('rot') not in {None,'0'}:
        raise ValueError('Đối tượng này cần dàn cột bằng luồng trực quan.')
    off, ext = properties.find('a:off', NS), properties.find('a:ext', NS)
    if off is None or ext is None:
        raise ValueError('Thiếu tọa độ hộp chữ để giữ PowerPoint gốc.')
    x,w = int(off.get('x')),int(ext.get('cx'))
    ids = [int(value) for value in tree.xpath('.//p:cNvPr/@id',namespaces=NS)]
    clone_id = english.find('p:nvSpPr/p:cNvPr', NS)
    clone_id.set('id',str(max(ids)+1))
    clone_id.set('name',clone_id.get('name','')+' English')
    gap = min(127000, int(w*.035))
    column = (w-gap)//2
    properties.find('a:ext', NS).set('cx',str(column))
    en_transform = english.find('p:spPr/a:xfrm', NS)
    en_transform.find('a:off', NS).set('x',str(x+column+gap))
    en_transform.find('a:ext', NS).set('cx',str(column))
    owner = shape.getparent()
    position = owner.index(shape)
    owner.insert(position+1,english)


def assemble(source, destination, manifest, translations, mode):
    """Only the changed slide/notes XML is serialized; media and timing survive."""
    from pptx import Presentation

    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Không ghi đè PowerPoint nguồn.')
    if set(translations) != {u['id'] for u in manifest['units']}:
        raise ValueError('Chưa đủ bản dịch để dựng bài giảng.')
    with zipfile.ZipFile(source) as archive:
        entries = {item.filename:archive.read(item) for item in archive.infolist()}
    grouped = {}
    for unit in manifest['units']:
        grouped.setdefault(unit['part'],{}).setdefault(unit['shape_id'],[]).append(unit)
    notes = {}
    for part, shapes in grouped.items():
        tree = _xml(entries[part])
        for shape_id, units in shapes.items():
            nodes = tree.xpath('.//p:cNvPr[@id=$id]',namespaces=NS,id=str(shape_id))
            if len(nodes) != 1:
                raise ValueError('Đối tượng PowerPoint không còn khớp nguồn.')
            shape = nodes[0].getparent().getparent()
            if all(u['language'] == 'neutral' or u['language'] == 'en'
                   and translations[u['id']]['en'] == u['text'] for u in units):
                continue  # Keep exact XML only when the validated response agrees.
            bodies = ([shape.find('p:txBody', NS)] if shape.tag == f'{{{NS["p"]}}}sp' else
                      shape.findall('.//a:tc/a:txBody', NS))
            if manifest.get('version', 1) >= 2:
                height=max((u.get('layout_height') or 0 for u in units),default=0)
                extent=shape.find('p:spPr/a:xfrm/a:ext',NS)
                if extent is not None and height:
                    extent.set('cy',str(height))
            clone = copy.deepcopy(shape)
            clone_bodies = ([clone.find('p:txBody', NS)] if shape.tag == f'{{{NS["p"]}}}sp' else
                            clone.findall('.//a:tc/a:txBody', NS))
            title = any(u['title'] for u in units)
            if title and mode!='english_only':
                height=max((u.get('title_height') or 0 for u in units),default=0)
                extent=shape.find('p:spPr/a:xfrm/a:ext',NS)
                if extent is not None and height:
                    extent.set('cy',str(height))
            for body_index, body in enumerate(bodies):
                if body is None:
                    continue
                originals = list(body.findall('a:p', NS))
                selected = {u['paragraph']:u for u in units if u['body'] == body_index}
                for paragraph in originals:
                    body.remove(paragraph)
                en_body = clone_bodies[body_index]
                for paragraph in list(en_body.findall('a:p', NS)):
                    en_body.remove(paragraph)
                for paragraph_index, original in enumerate(originals):
                    unit = selected.get(paragraph_index)
                    if unit is None:
                        body.append(copy.deepcopy(original))
                        en_body.append(copy.deepcopy(original))
                        continue
                    value = translations[unit['id']]
                    english = translated_paragraph(original,value['en'],unit,english=True,
                        smaller=mode=='sentence_pairs' or title)
                    if mode == 'english_only':
                        body.append(english)
                    elif mode == 'sentence_pairs' or title:
                        body.append(copy.deepcopy(original))
                        body.append(english)
                    elif mode == 'integrated_keywords':
                        body.append(translated_paragraph(original,value['mixed'],unit))
                    else:
                        body.append(copy.deepcopy(original))
                        en_body.append(english)
                    pair = notes.setdefault(unit['slide'],{'vi':[],'en':[]})
                    pair['vi'].append(unit['raw'])
                    pair['en'].append(restore(value['en'],unit['numbers']))
                _fit_body(body)
                _fit_body(en_body)
            if mode == 'parallel_columns' and not title:
                if shape.tag != f'{{{NS["p"]}}}sp':
                    raise ValueError('Bảng này cần dàn hai cột bằng luồng trực quan.')
                _pair_columns(tree,shape,clone)
                if manifest.get('version', 1) >= 2:
                    fit_body(clone, max(u['font_size'] for u in units))
            if manifest.get('version', 1) >= 2:
                fit_body(shape, max(u['font_size'] for u in units))
        entries[part] = _bytes(tree)
    # python-pptx creates only the notes plumbing in a temporary copy. Keep its
    # slide XML out of the output so unsupported source extensions stay intact.
    deck = Presentation(source)
    original_parts = source_slide_parts(source)
    normalized = {str(slide.part.partname)[1:]:part for slide,part in zip(deck.slides,original_parts,strict=True)}
    for index,pair in notes.items():
        frame = deck.slides[index-1].notes_slide.notes_text_frame
        original = frame.text.split('BILICLASS_NOTES:')[0].rstrip()
        frame.text = original + '\nBILICLASS_NOTES:\nVI: ' + '\n'.join(pair['vi']) + '\nEN: ' + '\n'.join(pair['en'])
    notes_copy = destination.with_suffix('.notes.pptx')
    pending = destination.with_suffix('.pending.pptx')
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        deck.save(notes_copy)
        with zipfile.ZipFile(notes_copy) as archive:
            incoming = {name:archive.read(name) for name in archive.namelist()}
        for name,data in incoming.items():
            if name.startswith(('ppt/notesSlides/','ppt/notesMasters/')):
                if name.endswith('.rels'):
                    owner=posixpath.join(posixpath.dirname(posixpath.dirname(name)),posixpath.basename(name)[:-5])
                    tree=_xml(data)
                    for relation in tree:
                        if relation.get('Type','').endswith('/slide'):
                            target=_part_relative(owner,relation.get('Target',''))
                            if target in normalized:
                                relation.set('Target',posixpath.relpath(normalized[target],posixpath.dirname(owner)))
                    data=_bytes(tree)
                entries[name] = data
            elif name.startswith('ppt/slides/_rels/') or name == 'ppt/_rels/presentation.xml.rels':
                destination_name=name
                if name.startswith('ppt/slides/_rels/'):
                    owner='ppt/slides/'+posixpath.basename(name)[:-5]
                    destination_name=_rels_path(normalized.get(owner,owner))
                tree = _xml(entries[destination_name]) if destination_name in entries else etree.Element(f'{{{NS["rel"]}}}Relationships')
                by_id = {node.get('Id'):node for node in tree}
                for node in _xml(data):
                    if not node.get('Type','').endswith(('/notesSlide','/notesMaster')):
                        continue
                    if node.get('Id') in by_id:
                        if by_id[node.get('Id')].get('Type') != node.get('Type'):
                            raise ValueError('Liên kết ghi chú trùng với tài nguyên nguồn.')
                    else:
                        tree.append(copy.deepcopy(node))
                entries[destination_name] = _bytes(tree)
        types = _xml(entries['[Content_Types].xml'])
        known = {(node.tag,node.get('PartName') or node.get('Extension')) for node in types}
        for node in _xml(incoming['[Content_Types].xml']):
            key = (node.tag,node.get('PartName') or node.get('Extension'))
            if key not in known and (node.tag.endswith('Default') or node.get('PartName','').startswith(('/ppt/notesSlides/','/ppt/notesMasters/'))):
                types.append(copy.deepcopy(node))
                known.add(key)
        entries['[Content_Types].xml'] = _bytes(types)
        presentation = _xml(entries['ppt/presentation.xml'])
        masters = _xml(incoming['ppt/presentation.xml']).find('p:notesMasterIdLst',NS)
        if masters is not None and presentation.find('p:notesMasterIdLst',NS) is None:
            following = presentation.find('p:sldIdLst',NS)
            presentation.insert(presentation.index(following) if following is not None else 0,copy.deepcopy(masters))
            entries['ppt/presentation.xml'] = _bytes(presentation)
        with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
            for name,data in entries.items():
                archive.writestr(name,data)
        with zipfile.ZipFile(pending) as archive:
            if archive.testzip() is not None:
                raise ValueError('Tệp PowerPoint xuất chưa hoàn chỉnh.')
        pending.replace(destination)
    finally:
        notes_copy.unlink(missing_ok=True)
        pending.unlink(missing_ok=True)
    return destination
