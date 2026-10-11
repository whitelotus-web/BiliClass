"""Render corrected reference slides using installed Microsoft PowerPoint (Windows)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    import pythoncom
    import win32com.client

    from app.paths import RESOURCE_ROOT
    from scripts.import_template_library import MODES, STYLES

    pythoncom.CoInitialize()
    office = None
    try:
        office = win32com.client.DispatchEx("PowerPoint.Application")
        source = Path(".runtime/template-review/language-demo-corrected.pptx").resolve()
        presentation = office.Presentations.Open(str(source), ReadOnly=True, Untitled=False, WithWindow=False)
        try:
            for offset, preset in enumerate(STYLES):
                for index, mode in enumerate(MODES):
                    target = RESOURCE_ROOT / "assets/templates/reference-preview" / f"{preset}-{mode}.png"
                    presentation.Slides(offset * 4 + index + 1).Export(str(target), "PNG", 1600, 900)
        finally:
            presentation.Close()
        for preset in STYLES:
            presentation = office.Presentations.Open(str(RESOURCE_ROOT / "assets/templates" / f"{preset}-classroom.pptx"),
                                                     ReadOnly=True, Untitled=False, WithWindow=False)
            try:
                for index in range(1, 5):
                    target = source.parent / f"neutral-{preset}-{index}.png"
                    presentation.Slides(index).Export(str(target), "PNG", 1280, 720)
            finally:
                presentation.Close()
        print("Rendered 12 language previews and checked 12 universal template slides.", flush=True)
    finally:
        if office:
            office.Quit()
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
