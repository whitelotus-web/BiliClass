"""Offline recognition with an explicit, separate model preparation step."""

import importlib.util
from pathlib import Path

LATIN_MODEL = "latin_PP-OCRv5_rec_mobile.onnx"
LATIN_SHA256 = "b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a"
LATIN_URL = "https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.9.2/onnx/PP-OCRv5/rec/" + LATIN_MODEL
MODELS = {"Det": "PP-OCRv6_det_small.onnx", "Rec": "PP-OCRv6_rec_small.onnx",
          "Cls": "ch_ppocr_mobile_v2.0_cls_mobile.onnx"}


def model_paths():
    from .paths import user_data
    from .translation import model_directory

    spec = importlib.util.find_spec("rapidocr")
    if spec is None or not spec.origin:
        return {}
    folder = Path(spec.origin).parent / "models"
    paths = {key: folder / filename for key, filename in MODELS.items()}
    latin = next((root / "ocr-vi-en-v1" / LATIN_MODEL for root in (model_directory(), user_data() / "models")
                  if (root / "ocr-vi-en-v1" / LATIN_MODEL).is_file()), None)
    if latin is None:
        return {}
    paths["Rec"] = latin
    return paths if all(path.is_file() for path in paths.values()) else {}


def prepare_models():
    """Explicit setup download of public weights, with no document upload."""
    import hashlib
    import json
    import tempfile

    import httpx

    from .translation import model_directory

    folder = model_directory() / "ocr-vi-en-v1"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / LATIN_MODEL
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == LATIN_SHA256:
        return str(target)
    with tempfile.NamedTemporaryFile(dir=folder, suffix=".download", delete=False) as pending:
        temporary = Path(pending.name)
        try:
            size = 0
            with httpx.stream("GET", LATIN_URL, follow_redirects=True, timeout=60) as response:
                response.raise_for_status()
                for block in response.iter_bytes():
                    size += len(block)
                    if size > 32 * 1024**2:
                        raise ValueError("Gói OCR vượt kích thước cho phép.")
                    pending.write(block)
        except Exception:
            pending.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != LATIN_SHA256:
            raise ValueError("Checksum bộ OCR không khớp; chưa sử dụng gói tải về.")
        temporary.replace(target)
        (folder / "provenance.json").write_text(json.dumps({"url": LATIN_URL, "sha256": LATIN_SHA256,
                                                          "engine": "RapidOCR 3.9.2", "license": "Apache-2.0"}), encoding="utf-8")
    finally:
        temporary.unlink(missing_ok=True)
    return str(target)


def engine(language):
    if language not in {"vi", "en"}:
        raise ValueError("OCR cục bộ hiện hỗ trợ tiếng Việt và tiếng Anh.")
    paths = model_paths()
    if not paths:
        raise ValueError("Chưa có bộ OCR Việt–Anh cục bộ. Bấm Chuẩn bị OCR Việt–Anh ở màn Tạo bài học, rồi nhập lại tài liệu.")
    from rapidocr import ModelType, OCRVersion, RapidOCR

    # Every model path is supplied and checked. RapidOCR's automatic downloader
    # is never used; images, PDFs and extracted text stay on the teacher's PC.
    params = {f"{key}.model_path": str(path) for key, path in paths.items()}
    params.update({"Det.lang_type": language, "Rec.lang_type": "latin", "Rec.ocr_version": OCRVersion.PPOCRV5,
                   "Rec.model_type": ModelType.MOBILE,
                   "Global.log_level": "error", "Global.max_side_len": 2400,
                   "EngineConfig.onnxruntime.intra_op_num_threads": 4,
                   "EngineConfig.onnxruntime.inter_op_num_threads": 1})
    return RapidOCR(params=params)


def image_text(recognizer, path):
    from PIL import Image

    with Image.open(path) as image:
        image.thumbnail((2400, 2400))
        rgb = image.convert("RGB")
        try:
            result = recognizer(rgb)
        finally:
            rgb.close()
    return "\n".join(result.txts or ())
