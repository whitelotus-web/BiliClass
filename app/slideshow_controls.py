"""Native slideshow speaker locations and in-memory pause badges."""

from .paths import RESOURCE_ROOT


def add_pause_badges(presentation):
    """The session discards these overlays on close; the user's file is untouched."""
    badges = {}
    other_media = False
    for slide in presentation.Slides:
        named = {str(shape.Name): shape for shape in slide.Shapes}
        for shape in list(slide.Shapes):
            if str(shape.Name).startswith('BiliClass audio '):
                language = str(shape.Name).split()[-1].lower()
                mini = float(shape.Width) > float(shape.Height) * 1.8
                filename = 'speaker-pause-' + language + ('-mini' if mini else '') + '.png' if language in {'vi', 'en', 'both'} else 'speaker-pause.png'
                icon = str(RESOURCE_ROOT / 'assets/actions' / filename)
                ready = named.get('BiliClass control ' + language.upper(), shape)
                badge = named.get('BiliClass pause ' + language.upper())
                if badge is None:
                    badge = slide.Shapes.AddPicture(icon, False, True, shape.Left, shape.Top, shape.Width, shape.Height)
                    badge.Name = 'BiliClass pause ' + str(shape.Id)
                badge.Visible = False
                ready.Visible = True
                badges[(int(slide.SlideID), int(shape.Id))] = (ready, badge)
            elif int(shape.Type) == 16:  # Source video/audio must keep its native controls.
                other_media = True
    return badges, other_media


def speaker_boxes(slide):
    named = {str(shape.Name): shape for shape in slide.Shapes}
    result = []
    for shape in slide.Shapes:
        if str(shape.Name).startswith('BiliClass audio '):
            language = str(shape.Name).split()[-1].lower()
            control = named.get('BiliClass control ' + language.upper(), shape)
            result.append((language, float(control.Left), float(control.Top), float(control.Width), float(control.Height)))
    return result


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
