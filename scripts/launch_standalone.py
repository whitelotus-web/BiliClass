"""Open BiliClass through desktop Explorer, outside the caller's process tree.

Use this from terminal/agent sessions that kill their child processes on exit.
DETACHED_PROCESS alone does not escape a Windows job. The desktop's actual
ShellFolderView Application is used instead of an in-process Shell.Application
ShellExecute call. Run with the project's Python and an existing BiliClass.exe.
"""

import argparse
import json
import time
from pathlib import Path


def launch(executable, page='new', timeout=25):
    import psutil
    import pythoncom
    import win32com.client
    import win32gui
    import win32process

    executable=Path(executable).resolve(strict=True)
    if executable.name.lower()!='biliclass.exe':
        raise ValueError('Chọn đúng file BiliClass.exe đã build.')

    def matches():
        result=[]
        for process in psutil.process_iter(['name','exe']):
            if (process.info['name'] or '').lower()!='biliclass.exe':
                continue
            if process.info['exe'] and Path(process.info['exe']).resolve()==executable:
                result.append(process)
        return result

    def window(pid):
        handles=[]
        win32gui.EnumWindows(lambda h,_:handles.append(h) if
            win32process.GetWindowThreadProcessId(h)[1]==pid and
            win32gui.IsWindowVisible(h) and 'BiliClass' in win32gui.GetWindowText(h)
            else None,None)
        return handles[0] if handles else None

    existing=matches()
    if existing:
        process=existing[0]
        parent=process.parent()
        if not parent or parent.name().lower()!='explorer.exe':
            raise RuntimeError('BiliClass đang mở từ phiên khác. Đóng cửa sổ tool đó rồi chạy lại; không tự dừng bài đang làm.')
    else:
        pythoncom.CoInitialize()
        try:
            shell=win32com.client.Dispatch('Shell.Application')
            hwnd=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_I4,0)
            desktop=shell.Windows().FindWindowSW(0,0,8,hwnd,1)
            if desktop is None:
                raise RuntimeError('Chưa kết nối được Windows Explorer trên desktop.')
            desktop.Document.Application.ShellExecute(str(executable),'--page '+page,
                                                      str(executable.parent),'open',1)
        finally:
            pythoncom.CoUninitialize()
        end=time.monotonic()+timeout
        process=None
        while time.monotonic()<end:
            found=matches()
            if found and window(found[0].pid):
                process=found[0]
                break
            time.sleep(.2)
        if process is None:
            raise RuntimeError('BiliClass chưa mở được cửa sổ trong khoảng chờ.')

    parent=process.parent()
    if not parent or parent.name().lower()!='explorer.exe':
        raise RuntimeError('Chưa xác nhận được BiliClass do desktop Explorer khởi chạy.')
    handle=window(process.pid)
    if not handle:
        raise RuntimeError('Chưa tìm thấy cửa sổ BiliClass.')
    win32gui.ShowWindow(handle,9)  # SW_RESTORE
    try:
        win32gui.SetForegroundWindow(handle)
    except Exception:
        pass  # Windows may prevent focus stealing; the window is still visible.
    return {'pid':process.pid,'parent_pid':parent.pid,'parent_name':parent.name(),
            'exe':str(executable),'title':win32gui.GetWindowText(handle),
            'window_visible':bool(win32gui.IsWindowVisible(handle)),
            'method':'desktop Explorer ShellExecute'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable',type=Path)
    parser.add_argument('--page',choices=('new','home','library','settings'),default='new')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=launch(args.executable,args.page)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':
    main()
