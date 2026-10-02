import importlib.metadata
import platform
import socket

import psutil


def run() -> dict:
    interfaces = []
    for name, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET and not address.address.startswith("127."):
                interfaces.append({"name": name, "address": address.address})
    return {
        "status": "measured",
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu": platform.processor(),
        "logical_cpus": psutil.cpu_count(),
        "ram_gb": round(psutil.virtual_memory().total / 1024**3, 1),
        "interfaces": interfaces,
        "versions": {
            name: importlib.metadata.version(name)
            for name in ("PySide6-Essentials", "ctranslate2", "sentencepiece", "fastapi", "uvicorn")
        },
        "limitation": "Kết quả trên máy phát triển; chưa xác nhận laptop 8 GB hoặc điện thoại thật.",
    }
