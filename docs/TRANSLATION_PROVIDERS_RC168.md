# RC168: chọn Google Cloud hoặc Azure Translator

RC168 là nhánh nâng cấp để thử nghiệm. Mốc ổn định tạm được giữ nguyên ở tag
`v1.0.0rc167` (mã nguồn `39b9fd554fcc0ca629b76c2695a9261b4cba2d04`).
Nhánh `main` vẫn ở bản ghi RC167 `29b1a1b`; bộ cài RC167 không bị thay thế.
Chỉ chọn RC168 làm bản nộp sau khi thầy cô kiểm tra và xác nhận.

## Cách dùng

1. Mở **Cài đặt → Google Dịch**.
2. Tích chọn một trong hai dịch vụ: **Google Cloud Translation** hoặc
   **Microsoft Azure Translator**. Chỉ dịch vụ được chọn được dùng cho bài mới.
3. Google dùng các key và bộ đếm đã có. Azure cần key và **Region** lấy từ
   mục **Keys and Endpoint** của tài nguyên Translator. Với tài nguyên Global,
   nhập `global`; với tài nguyên theo vùng, nhập đúng mã, ví dụ `southeastasia`.
4. Bấm **Lưu cấu hình Azure**. Việc lưu mã hóa và kiểm tra khả năng đọc lại
   cấu hình trên máy; không khẳng định kết nối Azure đã được xác thực.
5. Thử chuyển đổi một bài trước, kiểm tra thuật ngữ, công thức và bố cục.

Muốn dùng gói miễn phí Azure, chọn đúng tài nguyên Translator F0 trong Azure.
Hạn mức công bố hiện tại là 2 triệu ký tự/tháng; bộ đếm trong BiliClass chỉ là
giới hạn cục bộ, không xác nhận số dư của tài khoản hay các máy khác.
Thay key, đổi tên, xóa rồi nhập lại cấu hình Azure giữ nguyên lịch sử bộ đếm.

## Cách bảo vệ luồng RC167

- Google tiếp tục là mặc định; không di chuyển hay ghi lại key Google.
- Giữ nguyên định dạng checkpoint, thư viện và cấu trúc dựng PowerPoint.
  Trường nội bộ `provider=google_translate` vẫn định danh luồng dựng cũ;
  trường mới `translation_provider` ghi dịch vụ thực tế `google` hoặc `azure`.
- Checkpoint/hàng đợi RC167 thiếu trường mới luôn tiếp tục bằng Google.
- Bài mới và toàn bộ hàng đợi ghi nhớ dịch vụ đã chọn khi bắt đầu. Đổi lựa chọn
  trong Cài đặt chỉ áp dụng cho lượt mới; lượt đang dở giữ dịch vụ cũ.
- Khóa thay đổi cấu hình dịch trong khi đang xử lý. Không tự chuyển giữa Google
  và Azure khi gặp lỗi. Dừng/tiếp tục dùng lại phần đã dịch hợp lệ.
- Azure dùng chung các lớp kiểm tra thuật ngữ, số liệu, công thức, chữ hoa/thường
  và kết quả của RC167. Chỉ thêm bộ kết nối dịch vụ.
- Azure có thư mục mã hóa, cache và sổ sử dụng riêng `translation_azure/`;
  Google giữ `translation_api/`. Hai thư mục đều ngoài Git và ngoài bản sao lưu
  thư viện. Không gửi key trong URL, không theo chuyển hướng HTTP, không đưa
  thông báo lỗi thô từ dịch vụ vào giao diện.
- Không đổi schema thư viện; RC167 vẫn đọc được các bài đã lưu. Khi quay lại
  RC167, bài mới tiếp tục dùng Google theo hành vi cũ.

## Chạy và kiểm tra

Chạy mã nguồn nhánh RC168 bằng môi trường ảo của dự án:

```powershell
./scripts/run.ps1 --page browser-ai
```

Kiểm tra định tuyến, bí mật, hạn mức, chuyển đổi PPTX và sao lưu:

```powershell
./.venv/Scripts/python.exe -m pytest -q tests/test_translation_provider.py tests/test_google_translation.py tests/test_google_conversion.py
./.venv/Scripts/python.exe -m scripts.qt_translation_provider_smoke reports/rc168-translation
./.venv/Scripts/python.exe -m scripts.qt_google_translation_smoke
```

Kiểm thử dùng tài liệu và phản hồi HTTP giả lập, không dùng key/thư viện cá nhân.
Chúng xác minh chọn đúng dịch vụ, giữ nguồn, hoàn tất và dừng/tiếp tục; không đo
chất lượng hay tốc độ Azure thật. Cần key Azure do thầy cô nhập trên máy để đo
dịch thực tế trước khi chấp nhận thay nguồn dịch mặc định.

Đã kiểm tra trên máy phát triển ngày 24/10/2026:

- 582 kiểm thử đạt trong nhóm dịch, công thức, hình, hàng đợi, sao lưu,
  vị trí thư viện, thứ tự đọc, giọng và điều khiển PowerPoint/Mascot.
- Sau bổ sung xử lý lỗi key Azure, chạy lại 71 kiểm thử dịch/định tuyến: đạt.
- Qt Google: chuyển đổi, dừng/tiếp tục, giữ cấu hình, hoàn tất và chuyển sang
  tạo giọng; không cảnh báo QML.
- Qt Azure: hai PPTX, dừng/tiếp tục khi lựa chọn cho bài mới đã đổi về Google,
  hoàn tất hai bài bằng Azure, không thay nguồn hay key Google; không cảnh báo QML.
- Qt hàng đợi chuyển đổi/tạo giọng, toàn bộ tab Cài đặt và F1: đạt.
- Đã xem giao diện Google/Azure sáng và tối ở 1080/1366 pixel; các kiểm tra
  Cài đặt hiện có còn bao gồm 1920 pixel và bố cục laptop hẹp.
- Ruff và biên dịch Python: đạt. Thêm nhóm kiểm tra dịch vào GitHub Actions.

Kiểm tra bố cục giọng dùng đúng hàng khoảng nghỉ đã có từ RC166 để đo vị trí
các nút; không thay bố cục hoặc hành vi giọng đọc của RC167.

## Tài liệu dịch vụ

- [Azure Translate API](https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/reference/v3/translate)
- [Key và Region Azure](https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/reference/authentication)
- [Gói F0](https://azure.microsoft.com/en-us/pricing/details/translator/)
