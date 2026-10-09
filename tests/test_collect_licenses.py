import json
from email.message import Message

from scripts import collect_licenses


def test_collect_notices_from_manifest_without_scanning_package_files(tmp_path, monkeypatch):
    installed = tmp_path / "installed"
    installed.mkdir()
    for name in ("LICENSE,MIT.txt", "NOTICE.txt"):
        (installed / name).write_text("Required attribution", encoding="utf-8")
    metadata = Message()
    metadata["Name"] = "example-dependency"
    metadata["Version"] = "1.0"

    class Distribution:
        version = "1.0"

        @property
        def files(self):
            raise AssertionError("Must not scan every installed package file")

        def read_text(self, name):
            return {
                "RECORD": '"LICENSE,MIT.txt",,\nNOTICE.txt,,\nmissing/LICENSE,,\nunused/model.bin,,\n',
                "METADATA": "Name: example-dependency\nVersion: 1.0\n",
            }.get(name)

        def locate_file(self, path):
            return installed / path

    distribution = Distribution()
    distribution.metadata = metadata
    bundle = tmp_path / "bundle"
    monkeypatch.setattr(collect_licenses.sys, "argv", ["collect_licenses.py", str(bundle)])
    monkeypatch.setattr(collect_licenses.importlib.metadata, "distributions", lambda: [distribution])
    collect_licenses.main()
    notices = json.loads((bundle / "licenses/DEPENDENCIES.json").read_text(encoding="utf-8"))
    assert notices[0]["notices"] == ["LICENSE,MIT.txt", "NOTICE.txt"]
    for name in notices[0]["notices"]:
        assert (bundle / "licenses/example-dependency-1.0" / name).read_text(encoding="utf-8") == "Required attribution"


def test_source_manifest_notices_remain_supported():
    class Distribution:
        def read_text(self, name):
            return {"SOURCES.txt": "package.py\nCOPYING\nlegal/copyright.txt\n"}.get(name)

    assert [path.as_posix() for path in collect_licenses.notice_paths(Distribution())] == [
        "COPYING", "legal/copyright.txt"
    ]
