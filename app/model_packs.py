"""Explicit, integrity-checked installation of offline model data, never executable code."""
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


def build_model_pack(source, destination):
    source, destination = Path(source), Path(destination)
    files = {}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if path.is_file() and not path.is_symlink():
                name = path.relative_to(source).as_posix()
                data = path.read_bytes()
                files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
                archive.writestr(name, data)
        archive.writestr("manifest.json", json.dumps({"version": 1, "kind": "biliclass-model", "name": source.name, "files": files}))
    return destination


def install_model_pack(path, directory):
    path, root = Path(path), Path(directory)
    if path.stat().st_size > 1024**3:
        raise ValueError("Gói ngôn ngữ vượt 1 GB.")
    root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if len(entries) > 2000 or len(set(names)) != len(names) or sum(e.file_size for e in entries) > 2*1024**3:
            raise ValueError("Gói ngôn ngữ quá lớn hoặc có entry trùng.")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("kind") != "biliclass-model" or manifest.get("version") != 1 or not re.fullmatch(r"(?:vi-en|en-vi)-[\w.-]{1,40}", manifest.get("name", "")):
            raise ValueError("Gói ngôn ngữ không hợp lệ.")
        if set(names) != {"manifest.json", *manifest.get("files", {})}:
            raise ValueError("Danh sách tệp không khớp manifest.")
        destination = root / manifest["name"]
        if destination.exists():
            raise ValueError("Gói này đã có trên máy. Chọn gói có phiên bản mới hơn để giữ khả năng quay lại.")
        with tempfile.TemporaryDirectory(dir=root, prefix=".install-") as staging:
            folder = Path(staging) / manifest["name"]
            folder.mkdir()
            for entry in entries:
                name = entry.filename
                if name == "manifest.json":
                    continue
                parts = PurePosixPath(name)
                if (parts.is_absolute() or ".." in parts.parts or ":" in name or "\\" in name or
                        ((entry.external_attr >> 16) & 0o170000) == 0o120000 or
                        parts.suffix.lower() not in {".bin", ".json", ".model", ".txt", ".md", ".pt"}):
                    raise ValueError("Tệp trong gói không phải dữ liệu model được hỗ trợ.")
                data = archive.read(name)
                record = manifest["files"][name]
                if len(data) != record["size"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                    raise ValueError("Checksum gói ngôn ngữ không khớp.")
                target = folder / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            if not (folder / "provenance.json").is_file() or not list(folder.rglob("model.bin")) or not list(folder.rglob("sentencepiece.model")):
                raise ValueError("Gói ngôn ngữ thiếu trọng số, tokenizer hoặc nguồn gốc.")
            shutil.move(str(folder), str(destination))
    return destination
