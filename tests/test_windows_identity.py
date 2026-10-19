import os
import subprocess

import pytest

from app.windows_identity import APP_ID, register_shortcut, relaunch_properties


def test_relaunch_properties_quote_unicode_paths_and_set_id_last(tmp_path):
    executable = tmp_path / 'Thư mục có dấu' / 'BiliClass.exe'
    properties = relaunch_properties(executable)
    assert properties[-1] == (5, APP_ID)
    assert properties[0] == (2, subprocess.list2cmdline([str(executable.resolve())]))
    assert properties[2] == (3, str(executable.resolve()) + ',0')
    source = relaunch_properties(executable, frozen=False)
    assert source[0][1].endswith(' -m app')
    assert source[2][1].endswith('biliclass.ico,0')


def test_shortcut_registration_rejects_missing_or_unrelated_links(tmp_path):
    with pytest.raises(FileNotFoundError):
        register_shortcut(tmp_path / 'BiliClass.lnk')
    other = tmp_path / 'Other.lnk'
    other.touch()
    with pytest.raises(ValueError):
        register_shortcut(other)


@pytest.mark.skipif(os.name != 'nt', reason='Windows property store')
def test_native_shortcut_persists_app_identity(tmp_path):
    import win32com.client
    from win32com.propsys import propsys, pscon

    path = tmp_path / 'BiliClass.lnk'
    shortcut = win32com.client.Dispatch('WScript.Shell').CreateShortcut(str(path))
    shortcut.TargetPath = str(tmp_path / 'BiliClass.exe')
    shortcut.Save()
    register_shortcut(path)
    store = propsys.SHGetPropertyStoreFromParsingName(str(path))
    assert store.GetValue(pscon.PKEY_AppUserModel_ID).GetValue() == APP_ID
