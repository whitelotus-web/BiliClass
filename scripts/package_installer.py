"""Create a small native installer and its complete adjacent ZIP in a new folder."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

INSTALLER_REVISION = 2


def verify_source(root, application_commit, *, reuse_application=False):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip():
        raise ValueError('Commit verified source changes before packaging the installer.')
    if head != application_commit:
        if not reuse_application:
            raise ValueError('Package only a verified build of the current source commit, or explicitly reuse unchanged application source.')
        changed = subprocess.check_output(
            ['git', 'diff', '--name-only', application_commit, head, '--',
             'app', 'pyproject.toml', 'requirements*.txt', 'scripts/build_runtime.spec'], cwd=root, text=True)
        if changed.strip():
            raise ValueError('Rebuild the application before packaging: application/runtime source changed: ' + changed.strip())
    return head


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-application', action='store_true',
                        help='Update only the setup launcher when the verified application/runtime source is unchanged')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    release = args.release.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Choose a new delivery folder; never overwrite an existing installer.')
    result = json.loads((release / 'build-result.json').read_text(encoding='utf-8-sig'))
    build = json.loads((release / 'BiliClass/BUILD_INFO.json').read_text(encoding='utf-8-sig'))
    version = build['version']
    commit = build['source_commit']
    if result['source_commit'] != commit or not result['zip_verified']:
        raise ValueError('Package only a verified application build.')
    installer_commit = verify_source(root, commit, reuse_application=args.reuse_application)
    asset = Path(result['archive'])
    if not asset.resolve().is_relative_to(release) or digest(asset) != result['sha256']:
        raise ValueError('The complete release ZIP does not match the verified build.')
    csc = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    if not csc.is_file():
        raise ValueError('The Windows .NET Framework compiler is required for the native launcher.')
    output.mkdir(parents=True)
    work_root = release / '.installer-work'
    work_root.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f'setup-{INSTALLER_REVISION}-', dir=work_root))
    metadata = dict(product='BiliClass', version=version, source_commit=commit,
                    installer_source_commit=installer_commit, installer_revision=INSTALLER_REVISION,
                    payload=asset.name, sha256=result['sha256'], payload_bytes=asset.stat().st_size)
    metadata_path = work / 'release.json'
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    parts = version.split('rc')
    windows_version = parts[0] + '.' + (parts[1] if len(parts) == 2 else '0')
    assembly = work / 'AssemblyInfo.cs'
    assembly.write_text(
        'using System.Reflection;\n'
        '[assembly: AssemblyTitle("BiliClass Setup")]\n'
        '[assembly: AssemblyProduct("BiliClass") ]\n'
        '[assembly: AssemblyCopyright("Copyright © 2026 Nguyễn Diệu Linh")]\n'
        f'[assembly: AssemblyFileVersion("{windows_version}")]\n'
        f'[assembly: AssemblyInformationalVersion("{version}+setup.{INSTALLER_REVISION}")]\n', encoding='utf-8-sig')
    executable = output / 'BiliClass-Setup.exe'
    subprocess.run([
        str(csc), '/nologo', '/target:winexe', '/platform:anycpu', '/optimize+', '/codepage:65001',
        '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll', '/reference:System.Web.Extensions.dll',
        '/win32icon:' + str(root / 'app/assets/brand/biliclass.ico'), '/out:' + str(executable),
        '/resource:' + str(metadata_path) + ',release.json',
        '/resource:' + str(root / 'scripts/Install-BiliClass.ps1') + ',Install-BiliClass.ps1',
        str(root / 'scripts/SetupLauncher.cs'), str(assembly),
    ], check=True)
    # A hardlink saves disk space on this drive; copying this folder to USB or
    # another computer still transfers the complete file, with no outside links.
    try:
        os.link(asset, output / asset.name)
    except OSError:
        shutil.copy2(asset, output / asset.name)
    shutil.copy2(root / 'docs/USER_GUIDE.md', output / 'HUONG_DAN.md')
    (output / 'BAT_DAU_O_DAY.txt').write_text(
        f'BILICLASS {version} — BỘ CÀI ĐẦY ĐỦ\n\n'
        '1. Để các file trong thư mục này cạnh nhau. Không cần giải nén file ZIP.\n'
        '2. Bấm đúp BiliClass-Setup.exe, chọn thư mục cài rồi bấm Cài đặt.\n'
        '   Chọn thư mục mới/trống, ví dụ D:\\BiliClass-App. Không chọn thư mục đang chứa bộ cài.\n'
        '3. Mở BiliClass từ Desktop hoặc Start menu. Bấm F1 để xem hướng dẫn.\n\n'
        'Có sẵn ứng dụng, giọng Việt–Mỹ, OCR, mẫu bài giảng, mascot và giấy phép.\n'
        'Không cần cài Python hoặc tải riêng bộ giọng.\n'
        'Cần Windows 10/11 64-bit và PowerPoint desktop để xem/trình chiếu bài.\n'
        'Chuyển đổi cần Internet và key Google Cloud Translation của người dùng.\n'
        'Thư viện, bài giảng và key cá nhân không nằm trong bộ cài.\n\n'
        'Gỡ cài đặt: mục BiliClass trong Ứng dụng của Windows, hoặc chạy\n'
        'Uninstall-BiliClass.cmd trong thư mục ứng dụng. Thư viện được giữ riêng.\n\n'
        f'Mã nguồn ứng dụng: {commit}\n'
        f'Mã nguồn bộ cài {INSTALLER_REVISION}: {installer_commit}\n', encoding='utf-8-sig')
    update_note = (
        'Chỉ sửa bộ cài, ứng dụng/ZIP không đổi. Có thể chỉ gửi lại BiliClass-Setup.exe.\n'
        f'Người nhận giữ nguyên {asset.name} cạnh EXE mới. Không cần gửi/tải lại ZIP.\n'
        if args.reuse_application else
        f'Đây là bản ứng dụng {version}. Gửi cả BiliClass-Setup.exe và {asset.name}.\n'
        'Không ghép Setup mới với ZIP khác phiên bản. Giữ hai file cạnh nhau.\n')
    (output / 'CAP_NHAT_BO_CAI.txt').write_text(
        f'BILICLASS {version} — BỘ CÀI {INSTALLER_REVISION}\n\n' + update_note
        + 'Không giải nén ZIP. Chọn thư mục mới/trống để cài.\n'
        'Không xóa dữ liệu trong thư mục đã chọn nhầm.\n', encoding='utf-8-sig')
    metadata['installer_sha256'] = digest(executable)
    metadata['installer_bytes'] = executable.stat().st_size
    (output / 'BUILD_INFO.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    (output / 'SHA256.txt').write_text(
        metadata['installer_sha256'] + '  ' + executable.name + '\n'
        + metadata['sha256'] + '  ' + asset.name + '\n', encoding='ascii')
    subprocess.run([str(executable), '--verify'], check=True, timeout=180)
    print(json.dumps(dict(metadata, folder=str(output), payload_verified=True), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
