"""Developer-only conversion of official VietOCR weights to a CPU ONNX pack.

The app uses ONNX Runtime; PyTorch/vietocr are needed only for this build step.
Weights and resulting models belong outside Git in a separately packaged pack.
"""

import hashlib
import json
import os
from pathlib import Path

import httpx
import torch
import yaml

WEIGHTS_SHA = "0921503a41375a0584268e23ef3d414ea478a8fe8777865c7745d38f2d0bc5db"


def main():
    from vietocr.tool.translate import build_model

    folder = Path(os.environ["LOCALAPPDATA"]) / "BiliClass/models/ocr-vi-en-v2"
    folder.mkdir(parents=True, exist_ok=True)
    weights = folder / "vgg_seq2seq.pth"
    assert weights.is_file() and hashlib.sha256(weights.read_bytes()).hexdigest() == WEIGHTS_SHA
    root = "https://raw.githubusercontent.com/pbcquoc/vietocr/master/"
    config = yaml.safe_load(httpx.get(root + "config/base.yml").raise_for_status().text)
    config.update(yaml.safe_load(httpx.get(root + "config/vgg-seq2seq.yml").raise_for_status().text))
    config["device"] = "cpu"
    config["cnn"]["pretrained"] = False
    torch.set_num_threads(2)
    model, vocab = build_model(config)
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
    model.eval()

    class Encoder(torch.nn.Module):
        def forward(self, image):
            return model.transformer.forward_encoder(model.cnn(image))

    class Decoder(torch.nn.Module):
        def forward(self, token, hidden, memory):
            prediction, new_hidden, _ = model.transformer.decoder(token, hidden, memory)
            return prediction, new_hidden

    # Register the existing modules so export captures trained weights, not constants.
    encoder = Encoder()
    encoder.add_module("network", model)
    decoder = Decoder()
    decoder.add_module("network", model)
    image = torch.zeros(1, 3, 32, 240)
    with torch.no_grad():
        hidden, memory = encoder(image)
        torch.onnx.export(
            encoder,
            image,
            folder / "encoder.onnx",
            dynamo=False,
            opset_version=17,
            input_names=["image"],
            output_names=["hidden", "memory"],
            dynamic_axes={"image": {3: "width"}, "memory": {0: "sequence"}},
        )
        torch.onnx.export(
            decoder,
            (torch.ones(1, dtype=torch.long), hidden, memory),
            folder / "decoder.onnx",
            dynamo=False,
            opset_version=17,
            input_names=["token", "hidden", "memory"],
            output_names=["prediction", "new_hidden"],
            dynamic_axes={"memory": {0: "sequence"}},
        )
    import onnx

    for name in ("encoder.onnx", "decoder.onnx"):
        graph = onnx.load(folder / name)
        for node in graph.graph.node:
            if node.op_type == "Transpose":
                for attribute in node.attribute:
                    if attribute.name == "perm" and any(value < 0 for value in attribute.ints):
                        rank = len(attribute.ints)
                        values = [value + rank if value < 0 else value for value in attribute.ints]
                        del attribute.ints[:]
                        attribute.ints.extend(values)
        onnx.checker.check_model(graph)
        onnx.save(graph, folder / name)
    files = {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in ("encoder.onnx", "decoder.onnx")
    }
    (folder / "pack.json").write_text(
        json.dumps(
            {
                "version": 1,
                "vocab": config["vocab"],
                "files": files,
                "weights_sha256": WEIGHTS_SHA,
                "source": "https://github.com/pbcquoc/vietocr",
                "modified": "ONNX encoder/decoder split, CPU inference, no PyTorch runtime required",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (folder / "LICENSE.txt").write_text(httpx.get(root + "LICENSE").raise_for_status().text, encoding="utf-8")
    print(json.dumps({"path": str(folder), "files": files}), flush=True)


if __name__ == "__main__":
    main()
