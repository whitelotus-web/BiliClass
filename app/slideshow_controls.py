"""Native slideshow speaker locations and in-memory pause badges."""

from .paths import RESOURCE_ROOT


def speaker_index(path):
    """Read only XML metadata, never load the deck's images/audio into memory."""
    import posixpath
    from xml.etree import ElementTree as ET
    from zipfile import ZipFile

    ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
          'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    result, other_media = {}, False
    with ZipFile(path) as archive:
        presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
        relations = {row.attrib['Id']: row.attrib['Target']
                     for row in ET.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))
                     if row.get('TargetMode') != 'External'}
        for row in presentation.findall('p:sldIdLst/p:sldId', ns):
            target = relations[row.attrib['{' + ns['r'] + '}id']]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt', target))
            tree = ET.fromstring(archive.read(target)).find('p:cSld/p:spTree', ns)
            shapes = [shape for shape in tree if shape.tag not in
                      {'{' + ns['p'] + '}' + name for name in ('nvGrpSpPr', 'grpSpPr', 'extLst')}]
            named = {}
            for position, shape in enumerate(shapes, 1):
                props = shape.find('.//p:cNvPr', ns)
                named[props.get('name', '') if props is not None else ''] = position
            audio = []
            for position, shape in enumerate(shapes, 1):
                props = shape.find('.//p:cNvPr', ns)
                name = props.get('name', '') if props is not None else ''
                if name.startswith('BiliClass audio '):
                    language = name.split()[-1].lower()
                    audio.append((position, int(props.attrib['id']), language,
                                  named.get('BiliClass control ' + language.upper(), position),
                                  named.get('BiliClass pause ' + language.upper())))
                elif shape.find('.//a:audioFile', ns) is not None or shape.find('.//a:videoFile', ns) is not None:
                    other_media = True  # Preserve source audio/video controls, including groups.
            result[int(row.attrib['id'])] = audio
    return result, other_media


def prepare_controls(presentation, path, *, add_badges=True, overlay=False, on_warning=None):
    """Resolve only indexed speakers once, on the private Office thread.

    Appending in-memory badges leaves original shape positions intact. The bound
    source is read-only; its identities and geometry stay fixed for this session.
    No source text, chart or picture is traversed over COM during navigation.
    """
    index, other_media = speaker_index(path)
    media, badges = {}, {}
    for identity, records in index.items():
        audio, boxes = [], []
        media[identity] = (audio, boxes)
        if not records:
            continue
        slide = presentation.Slides.FindBySlideID(identity)

        def resolve(name, position, expected_id=None):
            # Office can flatten AlternateContent differently from the XML
            # shape order. Our generated names survive that conversion.
            try:
                found = slide.Shapes.Item(name)
                if expected_id is None or int(found.Id) == expected_id:
                    return found
            except Exception:
                pass
            found = slide.Shapes.Item(position)
            if expected_id is not None and int(found.Id) != expected_id:
                raise ValueError('PowerPoint đã đổi cấu trúc loa; mở lại bài giảng.')
            return found

        for position, shape_id, language, control_position, pause_position in records:
            shape = resolve('BiliClass audio ' + language.upper(), position, shape_id)
            if overlay:
                shape.MediaFormat.Volume = 1  # Unity gain, set before starting the show.
            ready = resolve('BiliClass control ' + language.upper(), control_position)
            boxes.append((language, float(ready.Left), float(ready.Top), float(ready.Width), float(ready.Height)))
            audio.append((shape_id, language, shape))
            if not add_badges:
                continue
            try:
                mini = float(ready.Width) > float(ready.Height) * 1.8
                filename = 'speaker-pause-' + language + ('-mini' if mini else '') + '.png' if language in {'vi', 'en', 'both'} else 'speaker-pause.png'
                badge = resolve('BiliClass pause ' + language.upper(), pause_position) if pause_position else None
                if overlay:
                    # Set once BEFORE the show starts. Live visibility changes
                    # interfere with native animation builds; the owned overlay
                    # supplies both pictures without touching slide content.
                    if badge is not None:
                        badge.Visible = False
                    ready.Visible = False
                    badges[(identity, shape_id)] = (ready, badge)
                    continue
                if badge is None:
                    icon = str(RESOURCE_ROOT / 'assets/actions' / filename)
                    badge = slide.Shapes.AddPicture(icon, False, True, ready.Left, ready.Top, ready.Width, ready.Height)
                    badge.Name = 'BiliClass pause ' + str(shape_id)
                badge.Visible = False
                ready.Visible = True
                badges[(identity, shape_id)] = (ready, badge)
            except Exception:
                # A failed decorative overlay must not discard usable players.
                if on_warning:
                    on_warning()
    return media, badges, other_media


def speaker_regions(boxes, hwnd, slide_width, slide_height):
    import win32gui

    if not hwnd:
        return []
    left, top = win32gui.ClientToScreen(hwnd, (0, 0))
    _, _, width, height = win32gui.GetClientRect(hwnd)
    scale = min(width / slide_width, height / slide_height)
    left += (width - slide_width * scale) / 2
    top += (height - slide_height * scale) / 2
    regions = []
    for language, x, y, w, h in boxes:
        if language in {'vi', 'en', 'both'}:
            x, y = left + x * scale, top + y * scale
            regions.append((language, x, y, x + w * scale, y + h * scale))
    return regions
