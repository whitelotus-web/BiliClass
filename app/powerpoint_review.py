"""Render a source/output pair with the installed PowerPoint, without editing it."""

import hashlib
import json
from pathlib import Path
from threading import RLock

_preview_lock = RLock()


def render_preview_pages(path,pages,directory,sha256):
    # Library covers and the open lesson share an atomic cache and one Office
    # renderer. A fast view switch must not start multiple Office instances.
    with _preview_lock:
        return _render_preview_pages(path, pages, directory, sha256)


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
    index={'version':2,'sha256':sha256,'slides':{}}
    try:
        cached=json.loads((folder/'preview-cache.json').read_text(encoding='utf-8'))
        if cached.get('sha256')==sha256 and cached.get('version')==2:
            index=cached
    except (OSError,ValueError):
        pass
    office=deck=None
    existing=any((p.info['name'] or '').lower()=='powerpnt.exe' for p in psutil.process_iter(['name']))
    pythoncom.CoInitialize()
    try:
        office=win32com.client.DispatchEx('PowerPoint.Application')
        deck=office.Presentations.Open(str(Path(path).resolve()),ReadOnly=True,Untitled=False,WithWindow=False)
        for page in pages:
            if not 1<=page<=deck.Slides.Count:
                raise ValueError('Slide xem trước không hợp lệ.')
            image=folder/f'slide-{page}.png'
            pending=image.with_suffix('.pending.png')
            deck.Slides(page).Export(str(pending),'PNG',1600,round(1600*deck.PageSetup.SlideHeight/deck.PageSetup.SlideWidth))
            pending.replace(image)
            index['slides'][str(page)]={'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
                                       'environment':environment_key()}
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
    import psutil
    import pythoncom
    import win32com.client

    key = sha256[:24]
    folder = Path(directory) / "temp/lesson-preview-images" / key
    folder.mkdir(parents=True, exist_ok=True)
    image = folder / f"slide-{slide}.png"
    if image.is_file():
        return str(image)
    pythoncom.CoInitialize()
    existing = any((p.info["name"] or "").lower() == "powerpnt.exe" for p in psutil.process_iter(["name"]))
    office = deck = None
    try:
        office = win32com.client.DispatchEx("PowerPoint.Application")
        deck = office.Presentations.Open(str(Path(path).resolve()), ReadOnly=True, Untitled=False, WithWindow=False)
        if not 1 <= slide <= deck.Slides.Count:
            raise ValueError("Slide xem trước không hợp lệ.")
        height = round(1600 * deck.PageSetup.SlideHeight / deck.PageSetup.SlideWidth)
        deck.Slides(slide).Export(str(image.resolve()), "PNG", 1600, height)
        return str(image)
    finally:
        if deck is not None:
            deck.Close()
        if office is not None and not existing and office.Presentations.Count == 0:
            office.Quit()
        office = deck = None
        pythoncom.CoUninitialize()


def render_pair(source, converted, output_slide, directory):
    import psutil
    import pythoncom
    import win32com.client

    mapping = converted["slide_map"]
    if type(output_slide) is not int or not 1 <= output_slide <= len(mapping):
        raise ValueError("Slide đối chiếu không hợp lệ.")
    source_slide = mapping[output_slide - 1]
    key = hashlib.sha256(Path(converted["path"]).read_bytes()).hexdigest()[:24]
    folder = Path(directory) / "temp/powerpoint-review" / key
    folder.mkdir(parents=True, exist_ok=True)
    original_png, result_png = folder / f"source-{source_slide}.png", folder / f"result-{output_slide}.png"
    pythoncom.CoInitialize()
    existing = any((p.info["name"] or "").lower() == "powerpnt.exe" for p in psutil.process_iter(["name"]))
    office = None
    opened = []
    try:
        office = win32com.client.DispatchEx("PowerPoint.Application")
        for path, index, image in ((source, source_slide, original_png), (converted["path"], output_slide, result_png)):
            if image.is_file():
                continue
            deck = office.Presentations.Open(str(Path(path).resolve()), ReadOnly=True, Untitled=False, WithWindow=False)
            opened.append(deck)
            height = round(1600 * deck.PageSetup.SlideHeight / deck.PageSetup.SlideWidth)
            deck.Slides(index).Export(str(image.resolve()), "PNG", 1600, height)
            deck.Close()
            opened.remove(deck)
    except Exception as exc:
        raise ValueError("Chưa đối chiếu được bằng PowerPoint trên máy này. Có thể dùng Mở trong PowerPoint để kiểm tra: " + str(exc)) from exc
    finally:
        for deck in opened:
            deck.Close()
        if office is not None and not existing and office.Presentations.Count == 0:
            office.Quit()
        office = None
        pythoncom.CoUninitialize()
    return {"source_image": str(original_png), "result_image": str(result_png), "source_slide": source_slide,
            "output_slide": output_slide, "total": len(mapping), "report": converted.get("report", [])}
