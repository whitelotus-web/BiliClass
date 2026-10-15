"""Conservative local text fitting without moving pictures or source shapes.

These estimates select a native route, not a quality verdict. The resulting
PowerPoint still goes through the normal rendered overflow/coverage checks.
"""

import math
import textwrap
import zipfile
from pathlib import Path

from lxml import etree

from .source_deck import NS, _size

MIN_FONT = 18.0


def text_height(text, width, size, expansion=1.0):
    columns = max(1, int(width / (size * .6 * expansion)))
    lines = sum(max(1, len(textwrap.wrap(line, columns))) for line in text.splitlines() or [''])
    return lines * size * 1.15


def can_fit(shape, mode, *, title_height=None, height=None):
    """A large original font alone is not a reason to upload the whole slide."""
    size = min(_size(shape.text_frame, shape), MIN_FONT)
    width = (shape.width-shape.text_frame.margin_left-shape.text_frame.margin_right)/12700
    height = ((title_height or height or shape.height)-shape.text_frame.margin_top-shape.text_frame.margin_bottom)/12700
    if width <= 0 or height <= 0:
        return False
    if title_height is not None:
        # Keep EN smaller than VI, but never force newly fitted text below 18pt.
        return (text_height(shape.text, width, size / .8)
                + text_height(shape.text, width, size, 1.35)) <= height
    if mode == 'parallel_columns':
        width *= .47
    estimate = text_height(shape.text, width, size, 1.35)
    if mode == 'sentence_pairs':
        estimate += text_height(shape.text, width, size)
    return estimate <= height


def fit_body(shape, fallback_size, *, minimum=MIN_FONT):
    """Fit actual translated text, retaining font family, emphasis and geometry.

Apply only to simple, unrotated native text shapes. Never shrink formulas or
superscript XML; those runs keep their original properties. Stop at a readable
floor even if the translation is unexpectedly long; validation reports that.
"""
    body = shape.find('p:txBody', NS)
    transform = shape.find('p:spPr/a:xfrm', NS)
    extent = shape.find('p:spPr/a:xfrm/a:ext', NS)
    if body is None or extent is None:
        return
    if transform is not None and int(transform.get('rot', '0')) % 21600000:
        return
    props = body.find('a:bodyPr', NS)
    if props is None or props.get('vert', 'horz') != 'horz':
        return
    width = (int(extent.get('cx'))-int(props.get('lIns', 91440))-int(props.get('rIns', 91440)))/12700
    height = (int(extent.get('cy'))-int(props.get('tIns', 45720))-int(props.get('bIns', 45720)))/12700
    paragraphs = body.findall('a:p', NS)
    if width <= 0 or height <= 0 or not paragraphs:
        return
    sizes = []
    math_body = bool(body.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'))
    for paragraph in paragraphs:
        values = [int(n) / 100 for n in paragraph.xpath('./a:r/a:rPr/@sz|./a:pPr/a:defRPr/@sz', namespaces=NS)]
        sizes.append(max(values, default=fallback_size / 100))

    def needed(scale):
        total = 0.0
        for paragraph, size in zip(paragraphs, sizes, strict=True):
            text = ''.join(('\n' if etree.QName(n).localname == 'br' else n.text or '')
                           for n in paragraph.iter() if etree.QName(n).localname in {'t', 'br'})
            fitted = max(min(minimum, size), size * scale)
            fractions = bool(paragraph.xpath('.//*[local-name()="f" or local-name()="rad"]'))
            total += text_height(text, width, fitted) * (1.45 if fractions else 1.15 if math_body else 1)
            # Explicit paragraph spacing is scaled with the type. Fixed leading
            # is normalized only when this body actually needs fitting.
            for value in paragraph.xpath('./a:pPr/a:spcBef/a:spcPts/@val|./a:pPr/a:spcAft/a:spcPts/@val', namespaces=NS):
                total += int(value) / 100 * scale
        return total

    if needed(1) <= height:
        return
    scale = 1.0
    while scale > .1 and needed(scale) > height:
        scale -= .025
    if math_body:
        # Scale the entire math/text frame together. Changing only ordinary runs
        # leaves fractions at the old size and can push them across the border.
        for child in list(props):
            if etree.QName(child).localname in {'normAutofit','spAutoFit','noAutofit'}:
                props.remove(child)
        floor = min(1.0, minimum/min(sizes))
        etree.SubElement(props,f'{{{NS["a"]}}}normAutofit',
                         fontScale=str(round(max(floor,scale)*100000)),lnSpcReduction='10000')
        return
    for paragraph, size in zip(paragraphs, sizes, strict=True):
        ppr = paragraph.find('a:pPr', NS)
        if ppr is None:
            ppr = etree.Element(f'{{{NS["a"]}}}pPr')
            paragraph.insert(0, ppr)
        default = ppr.find('a:defRPr', NS)
        if default is None:
            default = etree.SubElement(ppr, f'{{{NS["a"]}}}defRPr')
        for node in [default, *paragraph.findall('a:r/a:rPr', NS), *paragraph.findall('a:endParaRPr', NS)]:
            if node.get('baseline', '0') != '0':
                continue
            old = int(node.get('sz', round(size*100)))
            node.set('sz', str(math.ceil(max(min(minimum*100, old), old*scale))))
        # Runs inheriting source theme size must inherit our new paragraph size.
        for child in ppr:
            tag = etree.QName(child).localname
            if tag == 'lnSpc':
                for node in list(child):
                    child.remove(node)
                etree.SubElement(child, f'{{{NS["a"]}}}spcPct', val='110000')
            elif tag in {'spcBef', 'spcAft'}:
                for node in child.findall('a:spcPts', NS):
                    node.set('val', str(round(int(node.get('val', '0'))*scale)))


def _office_overflows(path, pages, cancel):
    """Measure translated frames read-only; never save an Office rewrite."""
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    office = deck = None
    try:
        office = win32com.client.DispatchEx('PowerPoint.Application')
        deck = office.Presentations.Open(str(path.resolve()), ReadOnly=True, Untitled=False, WithWindow=False)
        result = []
        for page in pages:
            if cancel and cancel.is_set():
                raise InterruptedError('Đã dừng căn chỉnh bài giảng.')
            for shape in deck.Slides(page).Shapes:
                if shape.Type not in {1,14,17} or shape.Rotation or not shape.HasTextFrame or not shape.TextFrame2.HasText:
                    continue
                text = shape.TextFrame2.TextRange
                if text.BoundHeight > shape.Height+1 or text.BoundWidth > shape.Width+1:
                    factor = min((shape.Height-2)/max(1,text.BoundHeight),
                                 (shape.Width-2)/max(1,text.BoundWidth),.95)
                    result.append((page,int(shape.Id),max(.1,factor)))
        return result
    finally:
        if deck is not None:
            deck.Close()
        if office is not None and office.Presentations.Count == 0:
            office.Quit()
        office = deck = None
        pythoncom.CoUninitialize()


def fit_preserved_frames(path, manifest, cancel=None, *, measure=None):
    """At most two measured corrections, touching only new translated text.

    If Office is absent, the portable estimator still supplies the deck. No
    source page, image, math expression or animation is rewritten by this pass.
    """
    from .source_deck import _bytes, _xml, source_slide_parts

    path = Path(path)
    plan = manifest.get('layout_plan', [])
    pages = [index for index,row in enumerate(plan,1) if row['role'] in {'en','bilingual'}]
    if not pages:
        return {'available':None,'changes':[]}
    parts = source_slide_parts(path)
    changed = []
    measure = measure or _office_overflows
    for attempt in range(2):
        try:
            overflows = measure(path,pages,cancel)
        except InterruptedError:
            raise
        except Exception:
            return {'available':False,'changes':changed}
        if not overflows:
            break
        with zipfile.ZipFile(path) as archive:
            entries = {name:archive.read(name) for name in archive.namelist()}
        roots, applied = {}, []
        for page,shape_id,factor in overflows:
            if page not in pages:
                continue
            part = parts[page-1]
            if part not in roots:
                roots[part] = _xml(entries[part])
            nodes = roots[part].xpath('.//p:sp[p:nvSpPr/p:cNvPr[@id=$id]]',namespaces=NS,id=str(shape_id))
            nodes = [node for node in nodes if not any(etree.QName(n).localname=='Fallback' for n in node.iterancestors())] or nodes
            if len(nodes)!=1:
                continue
            body = nodes[0].find('p:txBody',NS)
            props = body.find('a:bodyPr',NS) if body is not None else None
            if props is None:
                continue
            nonempty = [paragraph for paragraph in body.findall('a:p',NS) if
                        paragraph.xpath('.//a:t[normalize-space()]|.//*[local-name()="oMath"]|.//a:fld',namespaces=NS)]
            sizes = [int(value) for paragraph in nonempty for value in
                     paragraph.xpath('.//a:rPr/@sz|.//a:defRPr/@sz',namespaces=NS)]
            # Continuations keep dense multi-paragraph bodies readable. A short,
            # indivisible label/equation can use 14pt rather than overlap artwork.
            floor = min(100000,round((1400 if manifest.get('same_slide') else 1200)/min(sizes,default=2400)*100000))
            spacing_changed = False
            if not body.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'):
                for paragraph in body.findall('a:p',NS):
                    before = etree.tostring(paragraph)
                    ppr = paragraph.find('a:pPr',NS)
                    if ppr is None:
                        ppr = etree.Element(f'{{{NS["a"]}}}pPr')
                        paragraph.insert(0,ppr)
                    if paragraph not in nonempty:
                        default = ppr.find('a:defRPr',NS)
                        if default is None:
                            default = etree.SubElement(ppr,f'{{{NS["a"]}}}defRPr')
                        default.set('sz','100')
                        for node in paragraph.findall('a:endParaRPr',NS)+paragraph.findall('.//a:rPr',NS):
                            node.set('sz','100')
                    for position,tag in enumerate(('lnSpc','spcBef','spcAft')):
                        node = ppr.find('a:'+tag,NS)
                        if node is not None:
                            ppr.remove(node)
                        node = etree.Element(f'{{{NS["a"]}}}{tag}')
                        etree.SubElement(node,f'{{{NS["a"]}}}'+('spcPct' if tag=='lnSpc' else 'spcPts'),
                                         val='110000' if tag=='lnSpc' else '0')
                        ppr.insert(position,node)
                    spacing_changed |= before != etree.tostring(paragraph)
            previous = props.find('a:normAutofit',NS)
            scale = int(previous.get('fontScale','100000')) if previous is not None else 100000
            fitted = min(scale,max(floor,round(scale*factor*.97)))
            if fitted >= scale-100 and not spacing_changed:
                continue
            for child in list(props):
                if etree.QName(child).localname in {'normAutofit','noAutofit','spAutoFit'}:
                    props.remove(child)
            etree.SubElement(props,f'{{{NS["a"]}}}normAutofit',fontScale=str(fitted),lnSpcReduction='10000')
            applied.append({'page':page,'shape_id':shape_id,'font_scale':fitted,'pass':attempt+1})
        if not applied:
            break
        for part,tree in roots.items():
            entries[part] = _bytes(tree)
        pending = path.with_suffix('.fit-pending.pptx')
        try:
            with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
                for name,data in entries.items():
                    archive.writestr(name,data)
            if cancel and cancel.is_set():
                raise InterruptedError('Đã dừng căn chỉnh; bản trước vẫn được giữ.')
            pending.replace(path)
        finally:
            pending.unlink(missing_ok=True)
        changed.extend(applied)
    return {'available':True,'changes':changed}
