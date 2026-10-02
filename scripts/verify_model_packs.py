"""Install the two shipped models into an explicitly disposable release-test library."""
import json
import os
from pathlib import Path

from app.model_packs import install_model_pack


def main():
    root = Path(__file__).resolve().parents[1]
    directory = Path(os.environ["BILICLASS_DATA"]).resolve()
    expected = (root / ".runtime/release-validation-data").resolve()
    if directory != expected:
        raise ValueError("Only the isolated release validation library may be used.")
    installed = []
    for name in ("vi-en-1.9", "en-vi-1.9"):
        path = install_model_pack(root / "dist" / (name + ".bclanguage"), directory / "models")
        installed.append(path.name)
    print(json.dumps({"installed_optional_models": installed}))


if __name__ == "__main__":
    main()
