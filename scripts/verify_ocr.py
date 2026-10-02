import json
import multiprocessing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.importers import parse_document
from app.ocr import languages


def main():
    from PIL import Image, ImageDraw, ImageFont
    root = Path(__file__).resolve().parents[1] / "reports/app"
    image = Image.new("RGB", (1200, 260), "white")
    ImageDraw.Draw(image).text((30, 45), "Discuss the evidence in groups.\nUse 20 kg and 30 cm in your explanation.", font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 38), fill="black")
    png, pdf = root / "ocr-fixture.png", root / "ocr-fixture.pdf"
    image.save(png)
    image.save(pdf, "PDF", resolution=144)
    results = {}
    for path in (png, pdf):
        blocks = parse_document(path, "en")
        assert "Discuss" in blocks[0][1] and "20 kg" in blocks[0][1] and "30 cm" in blocks[0][1], blocks
        results[path.suffix] = blocks
    results["languages"] = languages()
    results["status"] = "passed"
    (root / "ocr.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "passed", "formats": ["PNG", "PDF scan"], "languages": languages()}))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
