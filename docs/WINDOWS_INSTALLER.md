# Bộ cài Windows đầy đủ

`BiliClass-Setup.exe` là cửa sổ cài đặt tiếng Việt, được biên dịch bằng
C#/.NET Framework có sẵn trên Windows. File ZIP cạnh nó chứa ứng dụng
độc lập, Python/Qt, model giọng Việt–Mỹ và OCR, mẫu bài giảng, ảnh và các
giấy phép. Không cần Python hoặc tải model riêng trên máy nhận.

Người dùng giữ cả thư mục bộ cài, mở EXE và chọn thư mục cài. Không cần
giải nén ZIP. Thư viện, key dịch và bài cá nhân được lưu riêng. Chuyển đổi
cần Internet và key Google Cloud Translation; PowerPoint desktop vẫn
là phần mềm cần có trên máy để xem và trình chiếu PowerPoint.

Launcher chứa phiên bản, commit nguồn và SHA-256 của payload. Nó kiểm
tra toàn bộ ZIP trước khi cài. PowerShell giải nén trực tiếp vào thư mục
staging duy nhất trên ổ đích, kiểm tra từng file theo manifest rồi đổi
tên nguyên tử thành thư mục phiên bản. Không tạo thêm bản giải nén đầy
đủ trong Temp trên ổ C. File tạm của launcher chỉ là script cài nhỏ.

Chặn đường dẫn thoát thư mục, tên trùng khác hoa/thường, sai phiên bản,
file thiếu hoặc sai hash, đè thư mục có dữ liệu khác và cài vào thư viện.
Lỗi giải nén hủy staging riêng, giữ bản cài cũ. Mỗi lần cài kiểm tra đủ
dung lượng cho toàn bộ file và 64 MB dự phòng. Chỉ tạo shortcut/đăng ký
Ứng dụng Windows khi không dùng chế độ kiểm thử `-NoShortcuts`.

Gỡ từ Ứng dụng của Windows hoặc `Uninstall-BiliClass.cmd` trong thư mục
ứng dụng. Chỉ thư mục có marker BiliClass khớp đường dẫn mới được gỡ;
thư viện và sao lưu ở ngoài thư mục này không bị xóa.

Để tái tạo một mốc đã kiểm tra và commit:

```powershell
.venv/Scripts/python.exe scripts/build_from_runtime.py --baseline dist/rc155-input-consistency --output dist/rc164-full
.venv/Scripts/python.exe scripts/package_installer.py --release dist/rc164-full --output F:/BiliClass-BoCai-RC164
```

Script build xác minh runtime nền, biên dịch lại toàn bộ mã app hiện tại,
thay QML/tài nguyên bằng nguồn hiện tại, ghi commit vào BUILD_INFO, tạo
và kiểm tra ZIP. Script bàn giao yêu cầu build khớp HEAD và ZIP đã xác minh,
không ghi đè thư mục bàn giao có sẵn. EXE, ZIP, model và báo cáo không vào Git.
