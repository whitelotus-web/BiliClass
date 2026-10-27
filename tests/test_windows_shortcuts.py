import json
import os
from pathlib import Path

import pytest

from app.windows_identity import APP_ID
from app.windows_shortcuts import known_folder, repair_shortcuts, shortcut_target, write_shortcut

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Native Windows Shell links')


def test_unicode_shortcut_roundtrip_and_relaunch_properties(tmp_path):
    from win32com.propsys import propsys, pscon

    executable = tmp_path / 'Ứng dụng mới' / 'BiliClass.exe'
    executable.parent.mkdir()
    executable.write_bytes(b'fixture; never executed')
    link = tmp_path / 'Biểu tượng' / 'BiliClass.lnk'
    write_shortcut(link, executable)
    assert shortcut_target(link).resolve() == executable.resolve()
    store = propsys.SHGetPropertyStoreFromParsingName(str(link))
    assert store.GetValue(pscon.PKEY_AppUserModel_ID).GetValue() == APP_ID
    assert str(executable) in store.GetValue(pscon.PKEY_AppUserModel_RelaunchCommand).GetValue()


def test_upgrade_repoints_owned_pins_but_preserves_unrelated_links_and_old_exe(tmp_path):
    root = tmp_path / 'Bộ cài có dấu'
    old = root / '1.0.0rc155/BiliClass.exe'
    new = root / '1.0.0rc172/BiliClass.exe'
    for path in (old, new):
        path.parent.mkdir(parents=True)
        path.write_bytes(path.parent.name.encode())
    (root / '.biliclass-install.json').write_text(json.dumps(dict(product='BiliClass', root=str(root), version='1.0.0rc172')))
    folders = {name: tmp_path / name for name in ('desktop', 'programs', 'pins')}
    for folder in folders.values():
        folder.mkdir()
    owned = folders['pins'] / 'BiliClass cũ.lnk'
    unrelated = folders['pins'] / 'Ứng dụng khác.lnk'
    other_root = tmp_path / 'Other/1.0.0rc155/BiliClass.exe'
    other_root.parent.mkdir(parents=True)
    other_root.write_bytes(b'other app; preserve')
    write_shortcut(owned, old)
    write_shortcut(unrelated, other_root)
    preserved = unrelated.read_bytes()
    result = repair_shortcuts(root, executable=new, folders=folders)
    assert len(result['updated']) == 3 and not result['pinned_skipped']
    for link in (folders['desktop'] / 'BiliClass.lnk', folders['programs'] / 'BiliClass.lnk', owned):
        assert shortcut_target(link).resolve() == new.resolve()
    assert old.read_bytes() == b'1.0.0rc155' and unrelated.read_bytes() == preserved


def test_shortcut_repair_rejects_unmanaged_root_and_preserves_fixture_folders(tmp_path):
    root = tmp_path / 'Foreign'
    executable = root / '1.0.0rc172/BiliClass.exe'
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b'fixture')
    (root / '.biliclass-install.json').write_text(json.dumps(dict(product='Other', root=str(root), version='1.0.0rc172')))
    with pytest.raises(ValueError):
        repair_shortcuts(root, executable=executable, folders={})
    assert not list(tmp_path.rglob('*.lnk'))


def test_known_folder_uses_current_windows_profile_without_mutating_it():
    desktop = known_folder('b4bfcc3a-db2c-424c-b029-7fe99a87c641')
    assert isinstance(desktop, Path) and desktop.is_absolute() and desktop.is_dir()
