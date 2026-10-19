# RC92 — Sáu cặp Việt–Mỹ, ba cách tạo và hai loa riêng

Giữ các sửa lỗi RC91. Tạo giọng có ba lựa chọn: chỉ Anh, chỉ Việt, cả
Anh và Việt. Cả hai tạo hai loa độc lập, không tạo loa đọc nối hai ngôn ngữ.
PowerPoint, Mascot, nghe bản đã tạo và ZIP audio chỉ phát từng ngôn ngữ.
Loại nút/phím đọc chung; giữ phím đọc Anh, Việt và bốn phím điều hướng/
âm lượng có thể gán lại. Cài đặt và hướng dẫn phím cùng dữ liệu đã lưu.

| Cặp | Giọng Việt | Giọng Anh–Mỹ |
| --- | --- | --- |
| Nữ Bắc | Mai Anh | Heart |
| Nam Bắc | Hải Đăng | Michael |
| Nữ Trung | Ngọc Trân | Heart |
| Nam Trung | Quang Sơn | Michael |
| Nữ Nam | Thùy Dung | Heart |
| Nam Nam | Thái Sơn | Michael |

VieNeu 3.8.3/fp32 dùng cho Việt; Kokoro 82M v1.0 qua sherpa-onnx 1.13.8
CPU dùng cho Anh. Không có API/cloud TTS. Có sáu mẫu nghe thử công khai,
được kiểm SHA-256 để phát ngay mà không nạp mô hình. Các thư mục model,
âm thanh và nguồn bài cá nhân không vào Git.

Khóa WAV cũ giữ nguyên. Cặp mới tách khóa theo người đọc thật của từng
ngôn ngữ; giọng Anh mới có phiên bản engine/cache riêng. Mở bản cũ dùng
đúng WAV cũ. Đổi cấu hình tạo bản mới; không xóa hoặc ghi lại bài đã có.
Các bản metadata `both_controls` cũ vẫn đọc được, khi xuất lại chỉ có hai
loa riêng. Tệp PPTX nguồn giữ nguyên. Mẫu thử giọng từ slide cá nhân chỉ
ở thư mục báo cáo được bỏ qua bởi Git.

Hai nút Mascot luôn giữ vị trí, nút thiếu giọng xám. Icon đơn giản, không
có chữ EN/VI nhỏ. Khả năng đọc của bước hiện tại không nhấp nháy trong
hiệu ứng; bấm lúc hiệu ứng chưa xong chờ đúng bước rồi đọc. Bấm lần nữa
hủy yêu cầu chờ; đổi bước/slide, đổi chế độ hoặc dừng đều hủy yêu cầu cũ.
Tiếp tục giữ cơ chế đọc phần đang hiện chưa đọc, rồi phát lại khi đã đọc hết.

Chuẩn hóa HWND về 32 bit có nghĩa khi so sánh PyWin32 với ctypes. Sửa
trường hợp loa trên màn hình phụ bị bỏ qua do một phía có dấu, phía kia
không dấu. Managed PPTX dùng trigger trung tính để hiện con trỏ bấm, không
điều khiển âm thanh hoặc ẩn ảnh loa; trạng thái phát vẫn do phiên dạy quản lý.

## Kiểm chứng nguồn

- Ruff và compileall đạt. 944 kiểm thử lõi đạt; bỏ sáu nhóm trình duyệt cũ
  như RC91. Một cảnh báo Starlette/httpx không liên quan.
- 22 kiểm thử cặp giọng: sáu cặp × ba lựa chọn, đúng cache/ngôn ngữ,
  hai loa/tệp audio, bản cũ còn dùng được, thiếu model và định dạng PCM.
- Qt kiểm tra sáu mẫu, lưu cặp, tạo ba sản phẩm khi đã có bản cũ, không
  có nút đọc chung. Ba cỡ bảng Mascot giữ vị trí hai nút qua đổi ngôn ngữ/
  slide trống. Không cảnh báo QML.
- Qt → helper thực tạo đủ một đoạn Việt và một đoạn Anh bằng hai engine:
  12,14 giây; 554 nhịp giao diện; khoảng ngắt lớn nhất 265 ms. Không gọi
  API/phát tiếng; nguồn nguyên vẹn, watchdog bật.
- Office thật trên bản sao tạm và WAV im lặng: mở/F5, phát native,
  tạm dừng/đọc tiếp, điều khiển từng ngôn ngữ, đổi slide loại cập nhật cũ,
  xem bài khác không đổi liên kết, mở trước/sau tạo giọng đạt.
- Bắt chuột/phím trên hai cửa sổ tạm với HWND bí danh có dấu đạt, gồm
  giữ nguyên thao tác ở cửa sổ không thuộc phiên dạy.

## Đóng gói

Phiên bản `1.0.0rc92`. Dựng lại mọi module ứng dụng từ commit đã kiểm thử;
kiểm checksum runtime RC91. Cờ `--english-model` bổ sung tường minh Python/
native sherpa-onnx đã ghim và model Kokoro đã đối chiếu SHA-256. Ghi danh
sách checksum phần bổ sung trong `BUILD_INFO.json`, đưa model vào manifest/
installer/ZIP. Các thay đổi native khác vẫn dùng build đầy đủ.

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc91-window-identity --output dist/rc92-voice-pairs --english-model .runtime/kokoro/kokoro-multi-lang-v1_0
```

## Kết quả đóng gói và bản cài

- Commit ứng dụng: `05e21ffd063bea9629b7d9ebb2dedf82f8d4f44a`.
- CI Source checks đạt:
  https://github.com/whitelotus-web/BiliClass/actions/runs/39263362486
- Dựng một lần; Python 3.12.7, PyInstaller 6.22.3, Qt/PySide6 6.11.2.
- `BiliClass-RC92-Windows.zip`: 1.232.983.961 byte; 4.613 tệp ứng dụng.
- SHA256: `39bcca1591586495a4fd1613de116a7574253a0fbedbb1f32ca7c178a994bba7`.
- ZIP khớp manifest và checksum; digest asset trên GitHub khớp SHA256.
- Phát hành: https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc92

Bộ kiểm tra bản cài hoàn tất cả luồng, bằng chứng
`reports/release/1.0.0rc92-5ce367a9/installer.json`: cài vào đường dẫn
Unicode, Windows Details, CLI shortcut tạm, trang Qt, template, hai engine
thật không dùng cache phát triển, tiến trình lớp học, sao lưu và gỡ bản cài
tạm vẫn giữ thư viện riêng. Đây là kiểm tra trên máy hiện tại, chưa phải
chứng nhận trên Windows mới hoàn toàn.

Qt của bản đóng gói tạo hai đoạn bằng đúng VieNeu cho Việt và Kokoro cho
Anh trong 18,42 giây; 803 nhịp giao diện, khoảng ngắt lớn nhất 703 ms.
Không cảnh báo QML, watchdog bật, nguồn giữ nguyên. Sáu mẫu nghe thử
trong bản đóng gói bắt đầu trong 12–27 ms mà không nạp mô hình; lưu cặp
trong khi nghe thử đạt, hủy không phát muộn; khoảng ngắt giao diện lớn
nhất 97,8 ms. Các phép thử dùng thư viện tạm.

Đã cài tại `F:/Applications/BiliClass/1.0.0rc92`. Đóng RC91 bình thường,
không buộc dừng. Explorer mở RC92 độc lập với Codex vào bài đang chọn;
cửa sổ chính và Mascot hiện và đáp ứng. Icon native, AppUserModelID và
hai shortcut đều đúng. Bằng chứng `reports/rc92/installed-verification.json`.
Nguồn, revision, môn đã chọn, khóa API và toàn bộ 134 WAV của bài đang
thử giữ nguyên. Không tự đổi môn hoặc tạo lại giọng của bài cũ.

Lượt kiểm tra chuột/phím trực tiếp trong PowerPoint đã đạt sau khi Windows
cho truy cập input desktop trở lại, bằng chứng
`reports/rc92/native-input-final/result.json`. Dùng bản sao tạm và WAV im
lặng; nguồn giữ nguyên. Loa trên slide có con trỏ bàn tay, đọc/tạm dừng/
đọc tiếp đồng bộ với Mascot ở cả đường native và cache; đổi ngôn ngữ,
F5 từ cửa sổ soạn thảo, tiến/lùi hiệu ứng rồi slide, phím WASD gán lại
và 12 lần kéo bảng đều đạt. Không bắt phím ở cửa sổ khác, không đổi âm
lượng máy thật. 16 lần điều hướng trung bình 24 ms, cao nhất 47 ms;
khoảng ngắt giao diện lớn nhất 47 ms, không cảnh báo QML.
