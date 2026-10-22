"""Independent Vietnamese accent check, using the bundled VietOCR ONNX pack."""

import hashlib
import json
import math

import numpy as np


def pack_directory():
    from .paths import model_directory, user_data

    return next(
        (
            root / "ocr-vi-en-v2"
            for root in (model_directory(), user_data() / "models")
            if (root / "ocr-vi-en-v2/pack.json").is_file()
        ),
        None,
    )


class VietnameseReader:
    def __init__(self):
        import onnxruntime as ort

        folder = pack_directory()
        if folder is None:
            raise ValueError("Chưa có gói kiểm tra dấu tiếng Việt trong OCR.")
        config = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
        for name in ("encoder.onnx", "decoder.onnx"):
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != config["files"][name]:
                raise ValueError("Gói OCR tiếng Việt không khớp checksum.")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.encoder = ort.InferenceSession(
            str(folder / "encoder.onnx"), options, providers=["CPUExecutionProvider"]
        )
        self.decoder = ort.InferenceSession(
            str(folder / "decoder.onnx"), options, providers=["CPUExecutionProvider"]
        )
        self.characters = config["vocab"]

    def read(self, image):
        width = max(32, min(512, math.ceil(32 * image.width / image.height / 10) * 10))
        from PIL import Image

        crop = image.convert("RGB").resize((width, 32), Image.Resampling.LANCZOS)
        data = np.asarray(crop, dtype=np.float32).transpose(2, 0, 1)[None] / 255
        hidden, memory = self.encoder.run(None, {"image": data})
        token = np.array([1], dtype=np.int64)
        text = []
        scores = []
        for _ in range(128):
            logits, hidden = self.decoder.run(None, {"token": token, "hidden": hidden, "memory": memory})
            logits = logits[0] - np.max(logits[0])
            probabilities = np.exp(logits) / np.exp(logits).sum()
            index = int(np.argmax(probabilities))
            if index == 2:
                return "".join(text), float(np.mean(scores)) if scores else 0
            if index < 4:
                return "", 0
            text.append(self.characters[index - 4])
            scores.append(float(probabilities[index]))
            token = np.array([index], dtype=np.int64)
        return "", 0

    def read_line(self, image):
        """Split a long line at a real word gap before the 512px encoder cap."""
        if image.width / max(1, image.height) < 14:
            return self.read(image)
        data = np.asarray(image.convert('RGB'))
        ink = (data.min(axis=2) < 130).mean(axis=0)
        gaps, start = [], None
        for index, value in enumerate(ink):
            if value < .02 and start is None:
                start = index
            elif value >= .02 and start is not None:
                if index-start >= image.height*.14 and image.width*.3 < start < image.width*.7:
                    gaps.append((start+index)//2)
                start = None
        if not gaps:
            return self.read(image)
        split = min(gaps, key=lambda x: abs(x-image.width/2))
        pieces = []
        for left, right in ((0, split), (split, image.width)):
            with image.crop((left, 0, right, image.height)) as crop:
                pieces.append(self.read(crop))
        if not all(text for text, _ in pieces):
            return self.read(image)
        return ' '.join(text for text, _ in pieces), min(score for _, score in pieces)
