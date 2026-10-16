"""Render language examples from the same local builder used by the product."""

import sys
from pathlib import Path
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    import pythoncom
    import win32com.client

    from app.google_conversion import _template
    from app.paths import RESOURCE_ROOT

    folder = Path(".runtime/conversion-examples").resolve()
    folder.mkdir(parents=True, exist_ok=True)
    pythoncom.CoInitialize()
    office = deck = None
    try:
        office = win32com.client.DispatchEx("PowerPoint.Application")
        for preset in ("standard", "visual", "practice"):
            for mode in ("parallel_columns", "english_only"):
                path = folder / (preset + "-" + mode + ".pptx")
                config = {
                    "title": "Vận tốc trong dao động điều hòa",
                    "english_title": "Velocity in simple harmonic motion",
                    "preset": preset,
                    "conversion_format": mode,
                }
                pairs = [
                    (
                        "Ví dụ bố cục",
                        "Vận tốc của vật biến thiên tuần hoàn theo thời gian.\nỞ vị trí cân bằng, độ lớn vận tốc đạt giá trị lớn nhất.",
                        "The velocity varies periodically with time.\nAt equilibrium, the speed reaches its maximum value.",
                    )
                ]
                _template(path, config, pairs, Event())
                deck = office.Presentations.Open(str(path), ReadOnly=True, WithWindow=False)
                target = RESOURCE_ROOT / "assets/templates/reference-preview" / (preset + "-" + mode + ".png")
                deck.Slides(1).Export(str(target.resolve()), "PNG", 1600, 900)
                deck.Close()
                deck = None
        print("Rendered six previews with native bilingual/English-only headings.", flush=True)
    finally:
        if deck is not None:
            deck.Close()
        if office is not None and office.Presentations.Count == 0:
            office.Quit()
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
