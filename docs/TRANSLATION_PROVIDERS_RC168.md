# RC168: Dịch thuật với bốn lựa chọn

Nhánh thử nghiệm: `codex/translation-providers-rc168`. RC167 vẫn là mốc ổn định
tạm: tag `v1.0.0rc167` tại `39b9fd554fcc0ca629b76c2695a9261b4cba2d04`.
Không thay main, tag hoặc bộ cài RC167; chưa đóng gói bản mới.

## Cách chọn

Mở **Cài đặt → Dịch thuật** (tên cũ: Google Dịch). Chọn một dịch vụ rồi lưu
cấu hình phía dưới. Chỉ dịch vụ đã chọn được dùng cho bài/hàng đợi mới.

| Thứ tự | Dịch vụ | Cần chuẩn bị | Giới hạn cần hiểu đúng |
| --- | --- | --- | --- |
| 1 | Google Cloud Translation | Key Google Cloud đã dùng trước đây | Giữ cách đếm/key/cache gốc; bộ đếm trên máy không phải số dư tài khoản |
| 2 | Google Apps Script LanguageApp | Triển khai Apps Script một lần bằng Google; URL /exec và mã truy cập riêng | Google công bố 5.000 lượt translate/ngày cho tài khoản cá nhân; các máy chung URL chia sẻ hạn mức chủ |
| 3 | Gemini API | Key Google AI Studio, dự án Free và model có quyền sử dụng | Miễn phí theo model/tài khoản; không cam kết ký tự cố định. Gói Free có thể dùng nội dung để cải thiện sản phẩm Google |
| 4 | DeepL API Developer | Tài khoản Developer, API key | Hiện công bố không cần thẻ; 1 triệu ký tự tổng cộng, không làm mới theo tháng; cần kiểm tra quyền ngôn ngữ của tài khoản |

LanguageApp không cần key Google Cloud hoặc thẻ, nhưng chưa có dịch vụ triển
khai sẵn. Gemini/DeepL vẫn cần key riêng. Tool không tự đăng ký, bật thanh toán
hay nâng gói. Điều kiện dịch vụ có thể thay đổi.

Azure đã bỏ khỏi lựa chọn cho bài mới. Lựa chọn Azure lưu từ RC168 cũ được
hiển thị về Google cho lượt mới; không xóa key Azure. Checkpoint/hàng đợi đã
ghim Azure vẫn tiếp tục bằng bộ kết nối cũ, không tự đổi dịch vụ.

## Thiết lập LanguageApp

Chọn phương án 2 → **Hướng dẫn thiết lập**:

1. Bấm **Sao chép mã**, mở Apps Script và dán thay nội dung `Code.gs`.
2. Cài đặt dự án → Thuộc tính tập lệnh: thêm `BILICLASS_ACCESS_CODE` với mã
   riêng 16–200 ký tự chữ/số/`_`/`-`. Không dùng API key Google làm mã này.
3. Triển khai → Bản triển khai mới → Ứng dụng web. Thực thi bằng **Tôi**;
   ai có quyền truy cập: **Mọi người**. Cấp quyền cho chính dự án đã tạo.
4. Dán URL kết thúc `/exec` và mã riêng vào BiliClass rồi Lưu cấu hình.
5. Thử một bài ngắn. Nếu sửa mã, cập nhật phiên bản của bản triển khai.

Tài khoản trường có thể bị quản trị viên hạn chế triển khai công khai.
Không dùng URL chỉnh sửa hoặc `/dev`. Mã mẫu ở `app/resources/languageapp.gs`
không chứa tài khoản/key/URL cá nhân. Giữ kín mã truy cập và URL; không nhúng
dịch vụ cá nhân vào bộ cài công khai.

Chặn tại máy: 4.500 đoạn/ngày UTC. Mã Apps Script có khóa đồng thời và sổ dùng
chung tối đa 4.500 lượt trong ít nhất 24 giờ (bucket giữ 24–25 giờ để không xóa
sớm). Đây là chặn phòng ngừa, không phải lịch reset/số dư chính thức của Google.

## Gemini và DeepL

Gemini: **Mở Google AI Studio** → tạo key ở dự án Free → dán và lưu. Model
mặc định `gemini-3.5-flash-lite`, có thể nhập model Gemini khác mà tài khoản
được phép gọi. Không bật thanh toán nếu chỉ muốn dùng Free; tool không thể
biến một key dự án trả phí thành key miễn phí. Chặn tại máy: 200.000 ký tự
đầu vào/ngày UTC, gồm HTML bảo vệ; không phải quota token của Google.

DeepL: **Mở DeepL API** → đăng ký Developer → lấy key → dán và lưu.
Chặn tại máy: 1 triệu ký tự tổng cộng, không reset tháng/đổi/xóa/nhập lại key.
Chọn host DeepL chuẩn theo hậu tố key `:fx`, không nhận máy chủ tùy ý.
Gói API Free cũ có chính sách khác với Developer. Lỗi ngôn ngữ/quyền sử dụng
cần xử lý ở tài khoản, không tự nâng gói hoặc đổi dịch vụ.

Lưu cấu hình chỉ xác nhận mã hóa và đọc lại tại máy, **chưa xác nhận kết nối,
hạn mức hoặc chất lượng dịch thật**. Giao diện hiển thị rõ trạng thái này.

## Bảo vệ luồng cũ và dữ liệu

- Google mặc định số 1, không di chuyển/ghi lại key và cache gốc.
- Checkpoint RC167 thiếu trường mới luôn dùng Google dù lựa chọn hiện tại khác.
- Hàng đợi ghim dịch vụ và cấu hình URL/model lúc bắt đầu. Đổi lựa chọn chỉ
  áp dụng lượt mới; bài cũ cần khôi phục URL/model cũ nếu muốn tiếp tục.
- Chặn đổi cấu hình khi đang xử lý; không tự chuyển dịch vụ khi lỗi/hết quota.
- Dùng lại kiểm tra thuật ngữ, chữ hoa/thường, số, đơn vị, công thức. Gemini trả
  JSON có chỉ số; bản thiếu, sai thứ tự, bị chặn hoặc cắt đều bị từ chối.
- HTTP HTTPS cố định, giới hạn thời gian/dung lượng; không trả lỗi thô chứa
  key/nội dung bài. LanguageApp chỉ theo redirect kết quả đến đúng host
  `script.googleusercontent.com` bằng GET không mang body/mã truy cập.
- DPAPI theo tài khoản Windows. Các thư mục `translation_languageapp/`,
  `translation_gemini/`, `translation_deepl/` tách key/cache/sổ sử dụng;
  chúng cùng key Google/Azure đều ngoài Git và sao lưu thư viện.
- Không đổi schema thư viện hoặc thay PPTX nguồn. Nhánh Git chỉ tách mã nguồn;
  chạy bình thường vẫn dùng thư viện đang chọn (hiện `F:\BiliClassData`).
  Không coi nhánh là bản sao dữ liệu. Kiểm tra tự động dùng thư viện tạm.
- Không thêm phụ thuộc Python/mô hình mới. Các đường build kèm mã Apps Script;
  không tạo bộ cài ở lần thay đổi này.

## Kiểm tra

Chạy bằng môi trường `.venv` của dự án, nạp môi trường nguồn nếu dùng runtime cache:

```powershell
./scripts/run.ps1 --page browser-ai
./.venv/Scripts/python.exe -m pytest -q tests/test_alternative_translation.py tests/test_translation_provider.py tests/test_google_translation.py tests/test_google_conversion.py
./.venv/Scripts/python.exe -m scripts.qt_translation_provider_smoke reports/rc168-alternatives
./.venv/Scripts/python.exe -m scripts.qt_google_translation_smoke
```

Kiểm tra dùng HTTP giả lập, PPTX và thư viện dùng một lần, gồm Google cũ,
các dịch vụ mới, mã hóa, giới hạn, file gốc, dừng/tiếp tục, sao lưu, giao diện
sáng/tối và hướng dẫn. Không dùng key/thư viện cá nhân để chạy kiểm tra.
**Không đo chất lượng/tốc độ dịch thật**: cần triển khai/nhập key rồi thử bài
ngắn trước khi chọn dịch vụ sử dụng thường xuyên hoặc đóng gói.

## Tài liệu chính thức đã đối chiếu (24/10/2026)

- [LanguageApp](https://developers.google.com/apps-script/reference/language/language-app), [hạn mức](https://developers.google.com/apps-script/guides/services/quotas)
- [Web app](https://developers.google.com/apps-script/guides/web), [ContentService](https://developers.google.com/apps-script/guides/content)
- [Gemini models](https://ai.google.dev/gemini-api/docs/models), [giá](https://ai.google.dev/gemini-api/docs/pricing), [JSON](https://ai.google.dev/gemini-api/docs/structured-output)
- [DeepL Developer](https://www.deepl.com/en/developers), [chính sách gói](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans)
- [DeepL auth](https://developers.deepl.com/docs/getting-started/auth), [dịch HTML](https://developers.deepl.com/api-reference/translate/request-translation)
