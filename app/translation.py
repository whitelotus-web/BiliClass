"""Local draft provider. No network access or automatic model installation."""

import os
import sys
from pathlib import Path

from biliclass_m0.probes.translation import decode_candidate, load_translator

from .paths import user_data
from .text_quality import protected_parts


def model_directory():
    configured = os.environ.get("BILICLASS_MODEL_DIR")
    if configured:
        return Path(configured)
    portable = Path(sys.executable).parent / "models"
    if getattr(sys, "frozen", False) and portable.is_dir():
        return portable
    return user_data() / "models"


def find_model(source_language="vi"):
    direction = "vi-en" if source_language == "vi" else "en-vi"
    roots = [user_data() / "models", model_directory()]
    for root in dict.fromkeys(roots):
        for candidate in sorted(root.glob(direction + "-*"), reverse=True):
            models = list(candidate.rglob("model.bin"))
            tokenizers = list(candidate.rglob("sentencepiece.model"))
            if models and tokenizers and (candidate / "provenance.json").exists():
                return models[0].parent, tokenizers[0]
    return None


def draft_resources(source_language):
    import ctranslate2
    import sentencepiece

    package = find_model(source_language)
    if not package:
        raise ValueError("Chưa cài gói dịch trên máy. Bạn vẫn có thể nhập và duyệt bản tiếng Anh.")
    model, tokenizer_path = package
    tokenizer = sentencepiece.SentencePieceProcessor(model_proto=tokenizer_path.read_bytes())
    return tokenizer, load_translator(model, ctranslate2)


def translate_with_resources(text, source_language, terms, tokenizer, translator):
    if source_language not in ("vi", "en") or not text.strip():
        raise ValueError("Chọn hướng dịch hợp lệ và nhập nội dung nguồn.")
    if len(text) > 2000:
        raise ValueError("Dịch thử tối đa 2.000 ký tự mỗi đoạn. Hãy rút gọn hoặc nhập bản tiếng Anh.")
    tokens = tokenizer.encode(text, out_type=str)
    if len(tokens) > 350:
        raise ValueError("Đoạn quá dài cho gói dịch thử. Hãy chia nhỏ để tránh mất nội dung.")
    chunks = protected_parts(text, terms, source_language)
    pending = [(index, chunk["text"]) for index, chunk in enumerate(chunks)
               if not chunk["protected"] and any(character.isalpha() for character in chunk["text"])]
    if pending:
        results = translator.translate_batch(
            [tokenizer.encode(value.strip(), out_type=str) for _, value in pending],
            beam_size=4, max_decoding_length=512,
        )
        for (index, original), result in zip(pending, results, strict=True):
            pieces = result.hypotheses[0]
            if len(pieces) >= 512:
                raise ValueError("Bản dịch chạm giới hạn độ dài và chưa được lưu. Hãy chia nhỏ đoạn.")
            decoded = decode_candidate(tokenizer, pieces).strip()
            if not decoded:
                raise ValueError("Model trả về một phần rỗng; chưa áp dụng bản dịch.")
            chunks[index]["text"] = (" " if original[:1].isspace() else "") + decoded + (" " if original[-1:].isspace() else "")
    return "".join(chunk["text"] for chunk in chunks)


def translate_draft(text, source_language="vi", terms=()):
    if source_language not in ("vi", "en") or not text.strip():
        raise ValueError("Chọn hướng dịch hợp lệ và nhập nội dung nguồn.")
    if len(text) > 2000:
        raise ValueError("Dịch thử tối đa 2.000 ký tự mỗi đoạn. Hãy rút gọn hoặc nhập bản tiếng Anh.")
    tokenizer, translator = draft_resources(source_language)
    try:
        return translate_with_resources(text, source_language, terms, tokenizer, translator)
    finally:
        translator.unload_model()


def translate_document_text(text, source_language, terms, tokenizer, translator, cancelled=None):
    """Translate bounded spans without changing native shape/segment boundaries.

    Keep paragraph and table-cell separators and protected formula spans intact.
    A long indivisible word/formula fails explicitly instead of being truncated.
    """
    import re

    result = []
    for part in re.split(r"(\n|\v|\s*\|\s*)", text):
        if not part or not part.strip() or "|" in part or "\n" in part or "\v" in part:
            result.append(part)
            continue
        atoms = []
        for chunk in protected_parts(part, terms, source_language):
            atoms.extend([chunk.get("original", chunk["text"])] if chunk["protected"]
                         else re.findall(r"\s+|\S+", chunk["text"]))
        spans, pending = [], ""
        for atom in atoms:
            candidate = pending + atom
            if len(candidate) > 2000 or len(tokenizer.encode(candidate, out_type=str)) > 350:
                if not pending.strip():
                    raise ValueError("Một biểu thức hoặc từ quá dài; cần kiểm tra phần này.")
                spans.append(pending)
                pending = atom
                if len(atom) > 2000 or len(tokenizer.encode(atom, out_type=str)) > 350:
                    raise ValueError("Một biểu thức hoặc từ quá dài; cần kiểm tra phần này.")
            else:
                pending = candidate
        if pending:
            spans.append(pending)
        for span in spans:
            if cancelled and cancelled.is_set():
                raise ValueError("Đã dừng chuyển đổi.")
            result.append(translate_with_resources(span, source_language, terms, tokenizer, translator)
                          if span.strip() else span)
    return "".join(result)
