"""Explicit, checksum-pinned download of the offline Kokoro model for builds."""

import hashlib
import tarfile
import urllib.request
from pathlib import Path

SOURCE = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2"
SHA256 = "c5f7e2d2caf082bc1d20fb70334a61d99d20b484500aad32e7cf84c128ea3298"
NAME = "kokoro-multi-lang-v1_0"
MAX_ARCHIVE = 400 * 1024**2
MAX_EXPANDED = 500 * 1024**2


def main():
    root = Path(__file__).resolve().parents[1] / ".runtime" / "kokoro"
    root.mkdir(parents=True, exist_ok=True)
    archive = root / (NAME + ".tar.bz2")
    model = root / NAME
    if (model / "model.onnx").is_file() and (model / "voices.bin").is_file():
        print("Kokoro model already present.")
        return
    if archive.is_file():
        with archive.open("rb") as existing:
            archive_valid = hashlib.file_digest(existing, "sha256").hexdigest() == SHA256
    else:
        archive_valid = False
    if not archive_valid:
        temporary = archive.with_suffix(".partial")
        digest = hashlib.sha256()
        size = 0
        try:
            with urllib.request.urlopen(SOURCE, timeout=60) as response, temporary.open("wb") as output:
                while chunk := response.read(1024**2):
                    size += len(chunk)
                    if size > MAX_ARCHIVE:
                        raise ValueError("Kokoro download exceeded expected size.")
                    digest.update(chunk)
                    output.write(chunk)
            if digest.hexdigest() != SHA256:
                raise ValueError("Kokoro archive checksum mismatch.")
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
    with tarfile.open(archive, "r:bz2") as source:
        members = source.getmembers()
        if not all(
            (member.name == NAME or member.name.startswith(NAME + "/"))
            and (member.isfile() or member.isdir())
            for member in members
        ):
            raise ValueError("Kokoro archive contains an unexpected path or file type.")
        if sum(member.size for member in members) > MAX_EXPANDED:
            raise ValueError("Kokoro archive expands beyond its expected size.")
        source.extractall(root, filter="data")
    if not (model / "model.onnx").is_file() or not (model / "voices.bin").is_file():
        raise ValueError("Kokoro model files are missing after extraction.")
    print("Kokoro model verified and extracted.")


if __name__ == "__main__":
    main()
