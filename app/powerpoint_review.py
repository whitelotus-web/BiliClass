"""Render a source/output pair with the installed PowerPoint, without editing it."""

import hashlib
import json
from datetime import date
from pathlib import Path
from threading import RLock

_preview_lock = RLock()


def render_preview_pages(path,pages,directory,sha256):
    # Library covers and the open lesson share an atomic cache and one Office
    # renderer. A fast view switch must not start multiple Office instances.
    with _preview_lock:
        from .office_tasks import run_task

        folder, index = run_task('preview', directory,
                                 dict(path=str(Path(path).resolve()), pages=pages,
                                      directory=str(Path(directory).resolve()), sha256=sha256), timeout=180)
        return Path(folder), index


def _render_preview_pages(path,pages,directory,sha256):
    """One Office open for a requested page and its immediate neighbours.

    Caller has verified the deck hash and file stamp. This is a preview cache,
    not evidence that native measurements or content checks have passed.
    """
    import psutil
    import pythoncom
    import win32com.client

    from .slide_fingerprint import environment_key

    folder=(Path(directory)/'temp/lesson-preview-images'/sha256[:24]).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    index={'version':3,'sha256':sha256,'slides':{}}
    try:
        cached=json.loads((folder/'preview-cache.json').read_text(encoding='utf-8'))
        if cached.get('sha256')==sha256 and cached.get('version')==3:
            index=cached
    except (OSError,ValueError):
        pass
    office=deck=None
    existing=any((p.info['name'] or '').lower()=='powerpnt.exe' for p in psutil.process_iter(['name']))
    pythoncom.CoInitialize()
    try:
        office=win32com.client.DispatchEx('PowerPoint.Application')
        from .office_tasks import native_progress, register_office

        register_office(office)
        deck=office.Presentations.Open(str(Path(path).resolve()),ReadOnly=True,Untitled=False,WithWindow=False)
        for page in pages:
            native_progress(f'Đang dựng ảnh xem trước slide {page}…')
            if not 1<=page<=deck.Slides.Count:
                raise ValueError('Slide xem trước không hợp lệ.')
            image=folder/f'slide-{page}.png'
            pending=image.with_suffix('.pending.png')
            deck.Slides(page).Export(str(pending),'PNG',1600,round(1600*deck.PageSetup.SlideHeight/deck.PageSetup.SlideWidth))
            pending.replace(image)
            try:
                sensitive = bool(deck.Slides(page).HeadersFooters.DateAndTime.Visible)
            except Exception:
                sensitive = True
            index['slides'][str(page)]={'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
                                       'environment':environment_key(), 'date_sensitive': sensitive,
                                       'rendered_date': date.today().isoformat()}
        pending=folder/'preview-cache.tmp'
        pending.write_text(json.dumps(index),encoding='utf-8')
        pending.replace(folder/'preview-cache.json')
        return folder,index
    finally:
        if deck is not None:
            deck.Close()
        if office is not None and not existing and office.Presentations.Count==0:
            office.Quit()
        office=deck=None
        pythoncom.CoUninitialize()


def render_slide(path, slide, directory):
    """Render one generated slide, including presentations made from documents."""
    from .slide_render_cache import RenderCache, digest

    sha256 = digest(path)
    cache = RenderCache(path, directory, {"sha256": sha256})
    row = {"slide": slide, "issues": []}
    if cache.reuse(row):
        return str(cache.image(slide))
    folder, _ = render_preview_pages(path, [slide], directory, sha256)
    return str(folder / f'slide-{slide}.png')


def render_pair(source, converted, output_slide, directory):
    mapping = converted['slide_map']
    if type(output_slide) is not int or not 1 <= output_slide <= len(mapping):
        raise ValueError('Slide đối chiếu không hợp lệ.')
    source_slide = mapping[output_slide - 1]
    original = render_slide(source, source_slide, directory)
    result = render_slide(converted['path'], output_slide, directory)
    return dict(source_image=original, result_image=result, source_slide=source_slide,
                output_slide=output_slide, total=len(mapping), report=converted.get('report', []))
