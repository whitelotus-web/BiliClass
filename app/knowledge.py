"""Versioned, source-aware knowledge packs for BiliClass.

Knowledge packs intentionally contain curated metadata and short terminology
records, rather than copied textbooks.  The application can run entirely
offline; a teacher can install a newer pack independently from the Windows
executable and promote individual suggestions into the teacher glossary.
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urlparse

KNOWLEDGE_FORMAT = "biliknowledge"
KNOWLEDGE_SCHEMA_VERSION = 1
_PACK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,79}$")
_MAX_PACK_BYTES = 50 * 1024 * 1024
_MAX_ENTRIES = 50_000


def _text(value, field, *, required=False, maximum=10_000):
    if not isinstance(value, str):
        raise ValueError(f"Trường {field} phải là văn bản.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"Thiếu trường bắt buộc: {field}.")
    if len(value) > maximum:
        raise ValueError(f"Trường {field} quá dài.")
    return value


def _list(value, field, *, maximum=100):
    if not isinstance(value, list) or len(value) > maximum or any(not isinstance(item, str) for item in value):
        raise ValueError(f"Trường {field} phải là danh sách văn bản hợp lệ.")
    return [item.strip() for item in value if item.strip()]


def validate_pack(pack: dict) -> dict:
    """Validate and normalize a pack before it reaches SQLite."""
    if not isinstance(pack, dict):
        raise ValueError("Gói kiến thức không phải JSON hợp lệ.")
    manifest = pack.get("manifest")
    sources = pack.get("sources")
    entries = pack.get("entries")
    if not isinstance(manifest, dict) or not isinstance(sources, list) or not isinstance(entries, list):
        raise ValueError("Gói kiến thức thiếu manifest, sources hoặc entries.")
    if manifest.get("format") != KNOWLEDGE_FORMAT:
        raise ValueError("Định dạng gói kiến thức không được hỗ trợ.")
    try:
        schema_version = int(manifest.get("schema_version", 0))
    except (TypeError, ValueError):
        raise ValueError("Phiên bản schema của gói kiến thức không hợp lệ.") from None
    if schema_version != KNOWLEDGE_SCHEMA_VERSION:
        raise ValueError("Phiên bản schema của gói kiến thức không được hỗ trợ.")
    pack_id = _text(manifest.get("pack_id"), "manifest.pack_id", required=True, maximum=80)
    if not _PACK_ID_RE.fullmatch(pack_id):
        raise ValueError("Mã gói kiến thức không hợp lệ.")
    pack_version = _text(manifest.get("version"), "manifest.version", required=True, maximum=40)
    title = _text(manifest.get("title"), "manifest.title", required=True, maximum=200)
    if len(sources) > 5000 or len(entries) > _MAX_ENTRIES:
        raise ValueError("Gói kiến thức vượt giới hạn kích thước.")

    source_ids = set()
    clean_sources = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Nguồn trong gói kiến thức không hợp lệ.")
        source_id = _text(source.get("id"), "source.id", required=True, maximum=120)
        if source_id in source_ids:
            raise ValueError(f"Trùng mã nguồn: {source_id}.")
        source_ids.add(source_id)
        url = _text(source.get("source_url"), "source.source_url", required=True, maximum=2000)
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"Nguồn phải dùng URL HTTPS: {source_id}.")
        clean_sources.append(
            {
                "id": source_id,
                "title": _text(source.get("title"), "source.title", required=True, maximum=300),
                "publisher": _text(source.get("publisher"), "source.publisher", required=True, maximum=200),
                "document_no": _text(source.get("document_no", ""), "source.document_no", maximum=120),
                "issued_at": _text(source.get("issued_at", ""), "source.issued_at", maximum=40),
                "effective_at": _text(source.get("effective_at", ""), "source.effective_at", maximum=40),
                "source_url": url,
                "official": bool(source.get("official", False)),
                "source_type": _text(source.get("source_type", "reference"), "source.source_type", maximum=80),
                "retrieved_at": _text(source.get("retrieved_at", ""), "source.retrieved_at", maximum=40),
                "status": _text(source.get("status", "active"), "source.status", maximum=40),
                "license": _text(source.get("license", "official_public_reference"), "source.license", maximum=200),
                "notes": _text(source.get("notes", ""), "source.notes", maximum=2000),
            }
        )

    entry_ids = set()
    clean_entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Mục kiến thức không hợp lệ.")
        entry_id = _text(entry.get("id"), "entry.id", required=True, maximum=160)
        if entry_id in entry_ids:
            raise ValueError(f"Trùng mã mục kiến thức: {entry_id}.")
        entry_ids.add(entry_id)
        aliases = _list(entry.get("aliases", []), "entry.aliases")
        source_refs = _list(entry.get("source_ids", []), "entry.source_ids", maximum=30)
        missing = [source_id for source_id in source_refs if source_id not in source_ids]
        if missing:
            raise ValueError(f"Mục {entry_id} trỏ tới nguồn chưa có: {', '.join(missing)}.")
        clean_entries.append(
            {
                "id": entry_id,
                "subject": _text(entry.get("subject", "Chung"), "entry.subject", required=True, maximum=120),
                "grade": _text(entry.get("grade", ""), "entry.grade", maximum=80),
                "kind": _text(entry.get("kind", "term"), "entry.kind", maximum=50),
                "vi": _text(entry.get("vi"), "entry.vi", required=True, maximum=1000),
                "en": _text(entry.get("en"), "entry.en", required=True, maximum=1000),
                "definition_vi": _text(entry.get("definition_vi", ""), "entry.definition_vi", maximum=3000),
                "definition_en": _text(entry.get("definition_en", ""), "entry.definition_en", maximum=3000),
                "aliases": aliases,
                "source_ids": source_refs,
                "status": _text(entry.get("status", "reference_only"), "entry.status", maximum=50),
                "confidence": _text(entry.get("confidence", "curated"), "entry.confidence", maximum=50),
                "updated_at": _text(entry.get("updated_at", manifest.get("updated_at", "")), "entry.updated_at", maximum=40),
            }
        )
    return {
        "manifest": {
            "format": KNOWLEDGE_FORMAT,
            "schema_version": KNOWLEDGE_SCHEMA_VERSION,
            "pack_id": pack_id,
            "version": pack_version,
            "title": title,
            "publisher": _text(manifest.get("publisher", "BiliClass"), "manifest.publisher", maximum=200),
            "updated_at": _text(manifest.get("updated_at", ""), "manifest.updated_at", maximum=40),
            "contains_full_text": bool(manifest.get("contains_full_text", False)),
            "license_note": _text(manifest.get("license_note", ""), "manifest.license_note", maximum=2000),
        },
        "sources": clean_sources,
        "entries": clean_entries,
    }


def load_pack(path: str | Path) -> dict:
    """Load a `.biliknowledge` ZIP using a small, allow-listed file set."""
    source = Path(path)
    if not source.is_file() or source.stat().st_size > _MAX_PACK_BYTES:
        raise ValueError("Gói kiến thức không đọc được hoặc vượt 50 MB.")
    if source.suffix.lower() != ".biliknowledge":
        raise ValueError("Chỉ nhận tệp .biliknowledge.")
    try:
        with zipfile.ZipFile(source) as archive:
            names = set(archive.namelist())
            required = {"manifest.json", "sources.json", "entries.json"}
            if not required.issubset(names) or any(name not in required for name in names):
                raise ValueError("Gói kiến thức có cấu trúc tệp không hợp lệ.")
            if any(info.file_size > _MAX_PACK_BYTES for info in (archive.getinfo(name) for name in required)):
                raise ValueError("Tệp bên trong gói kiến thức quá lớn.")
            pack = {
                "manifest": json.loads(archive.read("manifest.json")),
                "sources": json.loads(archive.read("sources.json")),
                "entries": json.loads(archive.read("entries.json")),
            }
    except zipfile.BadZipFile as exc:
        raise ValueError("Gói kiến thức bị hỏng.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Gói kiến thức chứa JSON không hợp lệ.") from exc
    return validate_pack(pack)


def builtin_pack() -> dict:
    path = Path(__file__).resolve().parent / "assets" / "knowledge" / "vn_education_foundation_2026.json"
    try:
        return validate_pack(json.loads(path.read_text(encoding="utf-8")))
    except FileNotFoundError as exc:
        raise ValueError("Thiếu gói nền tảng kiến thức tích hợp trong ứng dụng.") from exc


def ensure_builtin_foundation(library) -> bool:
    """Install the bundled foundation once; return whether the DB changed."""
    pack = builtin_pack()
    current = library.knowledge_pack(pack["manifest"]["pack_id"])
    if current and current["version"] >= pack["manifest"]["version"]:
        return False
    library.install_knowledge_pack(pack)
    return True


def install_file(library, path: str | Path) -> dict:
    pack = load_pack(path)
    library.install_knowledge_pack(pack)
    return pack["manifest"]
