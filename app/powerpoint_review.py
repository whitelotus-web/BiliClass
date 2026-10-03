"""Render a source/output pair with the installed PowerPoint, without editing it."""

import hashlib
from pathlib import Path


def render_slide(path, slide, directory):
    """Render one generated slide, including presentations made from documents."""
    import psutil
    import pythoncom
    import win32com.client

    key = hashlib.sha256(Path(path).read_bytes()).hexdigest()[:24]
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
