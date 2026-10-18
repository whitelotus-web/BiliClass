"""Windows Explorer Details resource, generated from the package version."""

import re


def version_info(version):
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo,
        StringFileInfo,
        StringStruct,
        StringTable,
        VarFileInfo,
        VarStruct,
        VSVersionInfo,
    )

    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:rc(\d+))?', version)
    if not match:
        raise ValueError('Invalid BiliClass release version')
    numeric = tuple(int(part or 0) for part in match.groups())
    if any(part > 65535 for part in numeric):
        raise ValueError('Windows version components must fit 16 bits')
    values = {
        'CompanyName': 'Nguyễn Diệu Linh',
        'FileDescription': 'BiliClass — Trợ lý dạy học song ngữ',
        'FileVersion': version,
        'InternalName': 'BiliClass',
        'LegalCopyright': 'Copyright © 2026 Nguyễn Diệu Linh. All rights reserved.',
        'OriginalFilename': 'BiliClass.exe',
        'ProductName': 'BiliClass',
        'ProductVersion': version,
    }
    return VSVersionInfo(ffi=FixedFileInfo(filevers=numeric, prodvers=numeric,
                                          flags=2 if match[4] else 0),
                         kids=[StringFileInfo([StringTable('042a04b0',
                                [StringStruct(key, value) for key, value in values.items()])]),
                               VarFileInfo([VarStruct('Translation', [1066, 1200])])])


if __name__ == '__main__':
    import sys
    import tomllib
    from pathlib import Path

    version = tomllib.loads((Path(__file__).resolve().parents[1] / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    Path(sys.argv[1]).write_text(str(version_info(version)), encoding='utf-8')
