"""Create a small native installer and its complete adjacent ZIP in a new folder."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
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
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if head != commit or result['source_commit'] != commit or not result['zip_verified']:
        raise ValueError('Package only a verified build of the current source commit.')
    asset = Path(result['archive'])
    if not asset.resolve().is_relative_to(release) or digest(asset) != result['sha256']:
        raise ValueError('The complete release ZIP does not match the verified build.')
    csc = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    if not csc.is_file():
        raise ValueError('The Windows .NET Framework compiler is required for the native launcher.')
    output.mkdir(parents=True)
    work = release / '.installer-work'
    work.mkdir()
    metadata = dict(product='BiliClass', version=version, source_commit=commit,
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
        f'[assembly: AssemblyInformationalVersion("{version}")]\n', encoding='utf-8-sig')
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
        '3. Mở BiliClass từ Desktop hoặc Start menu. Bấm F1 để xem hướng dẫn.\n\n'
        'Có sẵn ứng dụng, giọng Việt–Mỹ, OCR, mẫu bài giảng, mascot và giấy phép.\n'
        'Không cần cài Python hoặc tải riêng bộ giọng.\n'
        'Cần Windows 10/11 64-bit và PowerPoint desktop để xem/trình chiếu bài.\n'
        'Chuyển đổi cần Internet và key Google Cloud Translation của người dùng.\n'
        'Thư viện, bài giảng và key cá nhân không nằm trong bộ cài.\n\n'
        'Gỡ cài đặt: mục BiliClass trong Ứng dụng của Windows, hoặc chạy\n'
        'Uninstall-BiliClass.cmd trong thư mục ứng dụng. Thư viện được giữ riêng.\n\n'
        f'Mã nguồn: {commit}\n', encoding='utf-8-sig')
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
