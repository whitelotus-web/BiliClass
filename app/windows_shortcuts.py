"""Unicode Shell links and guarded repair of this installation's pinned links."""

import ctypes
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from .windows_com import Guid, apartment, check, method, release
from .windows_identity import _write_properties, relaunch_properties


@contextmanager
def _link(path=None):
    if os.name != 'nt':
        raise OSError('Windows shortcuts require Windows.')
    link, persist = ctypes.c_void_p(), ctypes.c_void_p()
    with apartment() as ole:
        try:
            clsid = Guid.parse('00021401-0000-0000-c000-000000000046')
            iid = Guid.parse('000214f9-0000-0000-c000-000000000046')  # IShellLinkW.
            ole.CoCreateInstance.argtypes = [ctypes.POINTER(Guid), ctypes.c_void_p, ctypes.c_uint32,
                                            ctypes.POINTER(Guid), ctypes.POINTER(ctypes.c_void_p)]
            ole.CoCreateInstance.restype = ctypes.c_long
            check(ole.CoCreateInstance(ctypes.byref(clsid), None, 1, ctypes.byref(iid), ctypes.byref(link)))
            iid_persist = Guid.parse('0000010b-0000-0000-c000-000000000046')
            check(method(link, 0, ctypes.POINTER(Guid), ctypes.POINTER(ctypes.c_void_p))(
                link, ctypes.byref(iid_persist), ctypes.byref(persist)))
            if path is not None:
                check(method(persist, 5, ctypes.c_wchar_p, ctypes.c_uint32)(persist, str(path), 0))
            yield link, persist
        finally:
            release(persist)
            release(link)


def shortcut_target(path):
    with _link(Path(path).resolve(strict=True)) as (link, _):
        target = ctypes.create_unicode_buffer(32768)
        check(method(link, 3, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)(
            link, target, len(target), None, 4))  # SLGP_RAWPATH; never resolve/search for another EXE.
        return Path(target.value) if target.value else None


def write_shortcut(path, executable, *, preserve_arguments=False):
    path, executable = Path(path), Path(executable).resolve(strict=True)
    if path.suffix.casefold() != '.lnk' or path.is_symlink():
        raise ValueError('Đường dẫn biểu tượng không hợp lệ.')
    path.parent.mkdir(parents=True, exist_ok=True)
    with _link(path if path.is_file() else None) as (link, persist):
        arguments = ctypes.create_unicode_buffer(32768)
        if preserve_arguments and path.is_file():
            check(method(link, 10, ctypes.c_wchar_p, ctypes.c_int)(link, arguments, len(arguments)))
        check(method(link, 20, ctypes.c_wchar_p)(link, str(executable)))
        check(method(link, 9, ctypes.c_wchar_p)(link, str(executable.parent)))
        check(method(link, 7, ctypes.c_wchar_p)(link, 'BiliClass'))
        check(method(link, 11, ctypes.c_wchar_p)(link, arguments.value))
        check(method(link, 17, ctypes.c_wchar_p, ctypes.c_int)(link, str(executable), 0))
        check(method(persist, 6, ctypes.c_wchar_p, ctypes.c_int)(persist, str(path.resolve()), 1))
    properties = relaunch_properties(executable)
    if preserve_arguments and arguments.value:
        properties[0] = (2, properties[0][1] + ' ' + arguments.value)
    _write_properties(path.resolve(), properties, shortcut=True)
    if shortcut_target(path).resolve() != executable:
        raise OSError('Biểu tượng chưa trỏ đúng bản BiliClass mới.')


def known_folder(identity):
    shell = ctypes.WinDLL('shell32')
    function = shell.SHGetKnownFolderPath
    function.argtypes = [ctypes.POINTER(Guid), ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p)]
    function.restype = ctypes.c_long
    path = ctypes.c_wchar_p()
    with apartment() as ole:
        ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        ole.CoTaskMemFree.restype = None
        try:
            check(function(ctypes.byref(Guid.parse(identity)), 0, None, ctypes.byref(path)))
            return Path(path.value)
        finally:
            ole.CoTaskMemFree(ctypes.cast(path, ctypes.c_void_p))


def repair_shortcuts(install_root, *, executable=None, folders=None):
    from .updater import VERSION_PATTERN

    if executable is None and not getattr(sys, 'frozen', False):
        raise ValueError('Chỉ bản đã đóng gói mới được sửa biểu tượng cài đặt.')
    root = Path(install_root).resolve(strict=True)
    executable = Path(executable or sys.executable).resolve(strict=True)
    marker_path = root / '.biliclass-install.json'
    if marker_path.stat().st_size > 8192:
        raise ValueError('Thông tin bản cài chưa hợp lệ.')
    marker = json.loads(marker_path.read_text(encoding='utf-8-sig'))
    if (not isinstance(marker, dict) or root == Path(root.anchor)
            or marker.get('product') != 'BiliClass' or Path(marker.get('root', '')).resolve() != root
            or executable.name.casefold() != 'biliclass.exe' or executable.parent.parent != root
            or executable.parent.name != marker.get('version') or not VERSION_PATTERN.fullmatch(marker['version'])
            or (root / 'library.db').exists()):
        raise ValueError('Chưa xác nhận được bản cài BiliClass để sửa biểu tượng.')
    if folders is None:
        folders = dict(desktop=known_folder('b4bfcc3a-db2c-424c-b029-7fe99a87c641'),
            programs=known_folder('a77f5d77-2e2b-44c3-a6a2-aba601054a51'),
            pins=known_folder('3eb685db-65f9-4cf6-a03a-e3ef65729f3d') /
                 'Microsoft/Internet Explorer/Quick Launch/User Pinned/TaskBar')
    result = dict(updated=[], pinned_skipped=[])
    for name in ('desktop', 'programs'):
        path = Path(folders[name]) / 'BiliClass.lnk'
        write_shortcut(path, executable)
        result['updated'].append(str(path))
    for path in sorted(Path(folders['pins']).glob('*.lnk')):
        try:
            target = shortcut_target(path)
            if (target is None or target.name.casefold() != 'biliclass.exe'
                    or not VERSION_PATTERN.fullmatch(target.parent.name) or target.parent.parent.resolve() != root):
                continue
            write_shortcut(path, executable, preserve_arguments=True)
            result['updated'].append(str(path))
        except (OSError, ValueError):
            result['pinned_skipped'].append(path.name)
    return result


def diagnose_shortcuts(report):
    """Exercise packaged Unicode/pin repair only in disposable fixture folders."""
    import tempfile
    import traceback

    from . import __version__

    report = Path(report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='bcl-shortcuts-', dir=report.parent) as temporary:
            folder = Path(temporary)
            root = folder / 'BiliClass có dấu'
            old = root / '1.0.0rc155/BiliClass.exe'
            new = root / __version__ / 'BiliClass.exe'
            for executable in (old, new):
                executable.parent.mkdir(parents=True, exist_ok=True)
                executable.write_bytes(executable.parent.name.encode())
            (root / '.biliclass-install.json').write_text(json.dumps(dict(
                product='BiliClass', root=str(root), version=__version__)), encoding='utf-8')
            folders = {name: folder / name for name in ('desktop', 'programs', 'pins')}
            for path in folders.values():
                path.mkdir()
            pinned = folders['pins'] / 'BiliClass cũ.lnk'
            write_shortcut(pinned, old)
            other = folder / 'Other.exe'
            other.write_bytes(b'preserved fixture')
            foreign_link = folders['pins'] / 'Other.lnk'
            write_shortcut(foreign_link, other)
            preserved = foreign_link.read_bytes()
            result = repair_shortcuts(root, executable=new, folders=folders)
            assert len(result['updated']) == 3 and not result['pinned_skipped']
            for path in (folders['desktop'] / 'BiliClass.lnk', folders['programs'] / 'BiliClass.lnk', pinned):
                assert shortcut_target(path).resolve() == new.resolve()
            assert old.read_bytes() == b'1.0.0rc155' and foreign_link.read_bytes() == preserved
        report.write_text(json.dumps(dict(status='passed', version=__version__,
            checks=['Unicode Shell links', 'Desktop and Start targets', 'owned RC155 taskbar pin',
                    'unrelated pin preserved', 'previous executable preserved'],
            scope='isolated fixture folders; no real user shortcuts changed'), indent=2), encoding='utf-8')
        return 0
    except Exception:
        report.write_text(json.dumps(dict(status='failed', error=traceback.format_exc()), indent=2), encoding='utf-8')
        return 1
