"""Prepare the exact VieNeu v3 CPU artifacts for an offline BiliClass build."""

import json
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".runtime" / "vieneu-hf" / "hub"
ARTIFACTS = {
    "pnnbao-ump/VieNeu-TTS-v3-Turbo": {
        "revision": "61b85e3d937fbbacb387714180e8182823512523",
        "files": [
            "config.json", "denoiser.onnx", "onnx_update/config.json",
            "onnx_update/tokenizer.json", "onnx_update/vieneu_prefill.onnx",
            "onnx_update/vieneu_decode_step.onnx", "onnx_update/vieneu_acoustic_cached.onnx",
            "onnx_update/vieneu_backbone_shared.data", "onnx_update/vieneu_v3_heads.npz",
        ],
        "license": "Apache-2.0",
    },
    "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX": {
        "revision": "ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae",
        "files": [
            "codec_browser_onnx_meta.json", "moss_audio_tokenizer_decode_full.onnx",
            "moss_audio_tokenizer_decode_shared.data", "moss_audio_tokenizer_decode_step.onnx",
            "moss_audio_tokenizer_encode.onnx", "moss_audio_tokenizer_encode.data",
        ],
        "license": "Apache-2.0",
    },
}


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    for repo, spec in ARTIFACTS.items():
        for filename in spec["files"]:
            path = hf_hub_download(repo, filename=filename, revision=spec["revision"], cache_dir=CACHE)
            print(f"{repo}/{filename}: {Path(path).stat().st_size} bytes", flush=True)
        ref = CACHE / ("models--" + repo.replace("/", "--")) / "refs" / "main"
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text(spec["revision"], encoding="ascii")
    (CACHE.parent / "PROVENANCE.json").write_text(
        json.dumps(ARTIFACTS, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
