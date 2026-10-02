"""Offline OCR using recognizers installed in Windows; explicit language, no upload."""
import asyncio
import multiprocessing
import queue
import tempfile
import time
from pathlib import Path


def languages():
    try:
        from winrt.windows.media.ocr import OcrEngine
        return [item.language_tag for item in OcrEngine.available_recognizer_languages]
    except (ImportError, OSError, RuntimeError):
        return []


async def _image(path, language):
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapAlphaMode, BitmapDecoder, BitmapPixelFormat
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage import FileAccessMode, StorageFile
    available = [item.language_tag for item in OcrEngine.available_recognizer_languages]
    match = next((tag for tag in available if tag.lower().split("-")[0] == language.lower().split("-")[0]), None)
    if match is None:
        raise ValueError(f"Windows chưa có OCR {language}. Chọn đúng ngôn ngữ nguồn hoặc cài thêm gói nhận dạng trong Windows.")
    engine = OcrEngine.try_create_from_language(Language(match))
    if engine is None:
        raise ValueError(f"Windows chưa có OCR ngôn ngữ {language}. Cài gói OCR trong Windows Settings hoặc nhập văn bản đã trích xuất. Không tự dùng tiếng Anh thay tiếng Việt.")
    file = await StorageFile.get_file_from_path_async(str(Path(path).resolve()))
    stream = await file.open_async(FileAccessMode.READ)
    bitmap = None
    try:
        decoder = await BitmapDecoder.create_async(stream)
        if max(decoder.pixel_width, decoder.pixel_height) > OcrEngine.max_image_dimension:
            raise ValueError(f"Ảnh OCR vượt {OcrEngine.max_image_dimension}px mỗi chiều; hãy xuất ảnh nhỏ hơn.")
        bitmap = await decoder.get_software_bitmap_converted_async(BitmapPixelFormat.BGRA8, BitmapAlphaMode.IGNORE)
        result = await engine.recognize_async(bitmap)
        return "\n".join(line.text for line in result.lines)
    finally:
        if bitmap is not None:
            bitmap.close()
        stream.close()


def _recognize(path, language="vi", pages=None, cancelled=None):
    import winrt.runtime
    winrt.runtime.init_apartment(winrt.runtime.MTA)
    try:
        path = Path(path)
        if path.suffix.lower() != ".pdf":
            from PIL import Image
            try:
                with Image.open(path) as image:
                    image.verify()
            except (OSError, ValueError) as exc:
                raise ValueError("Tệp ảnh OCR không hợp lệ; hãy xuất lại PNG/JPG.") from exc
            return [("Ảnh 1 · OCR cần kiểm tra", asyncio.run(_image(path, language)))]
        import pypdfium2 as pdfium
        blocks = []
        with pdfium.PdfDocument(str(path)) as pdf, tempfile.TemporaryDirectory(prefix="biliclass-ocr-") as work:
            indices = list(pages) if pages is not None else list(range(len(pdf)))
            if len(indices) > 50:
                raise ValueError("Mỗi lần OCR tối đa 50 trang scan. Hãy chia nhỏ PDF.")
            for index in indices:
                if cancelled and cancelled.is_set():
                    raise ValueError("Đã dừng OCR; chưa tạo bài.")
                page = pdf[index]
                width, height = page.get_size()
                scale = min(2.0, 2400/max(width, height))
                bitmap = page.render(scale=scale)
                image = bitmap.to_pil()
                target = Path(work) / f"page-{index}.png"
                image.save(target)
                image.close()
                bitmap.close()
                page.close()
                text = asyncio.run(_image(target, language))
                blocks.append((f"Trang {index + 1} · OCR cần kiểm tra", text))
        return blocks
    finally:
        winrt.runtime.uninit_apartment()


def _worker(path, language, pages, events):
    try:
        events.put({"blocks": _recognize(path, language, pages)})
    except Exception as exc:
        events.put({"error": str(exc)})


def recognize(path, language="vi", pages=None, cancelled=None):
    """Native recognition runs separately so a decoder failure cannot lose unsaved work."""
    context = multiprocessing.get_context("spawn")
    events = context.Queue()
    process = context.Process(target=_worker, args=(str(path), language, pages, events), daemon=True)
    process.start()
    start = time.monotonic()
    try:
        while True:
            if cancelled and cancelled.is_set():
                raise ValueError("Đã dừng OCR; chưa tạo bài.")
            try:
                result = events.get(timeout=.2)
                if "error" in result:
                    raise ValueError(result["error"])
                return result["blocks"]
            except queue.Empty:
                if not process.is_alive():
                    raise ValueError("OCR Windows không hoàn tất. Kiểm tra gói ngôn ngữ hoặc dùng tài liệu có văn bản.")
                if time.monotonic()-start > 600:
                    raise ValueError("OCR quá thời gian 10 phút; hãy chia nhỏ tài liệu.")
    finally:
        process.join(timeout=1)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
        events.close()
