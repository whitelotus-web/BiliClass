# Rà soát cơ chế bốn dịch vụ · 25/10/2026

Phạm vi: Google Cloud Translation, Apps Script LanguageApp, Gemini API và
DeepL API; lớp kiểm tra chung, cấu hình, bộ nhớ dịch, hàng đợi và dừng/tiếp tục.
Giữ mốc RC167, không tạo bộ cài mới trong đợt này.

## Các lỗi đã sửa

- **Hàng đợi nhiều bài:** lỗi hết số dư, model không dùng được hoặc triển khai
  Apps Script sai trước đây bị coi là lỗi riêng từng bài, khiến các bài phía sau
  tiếp tục gọi cùng dịch vụ đang hỏng. Nay hàng đợi tạm dừng ngay, các bài giữ
  trạng thái chờ; sửa cấu hình rồi tiếp tục tại đúng bài. Lỗi nội dung riêng một
  bài vẫn cho phép xử lý bài khác.
- **Hai luồng dịch:** một luồng thất bại sẽ báo dừng cho luồng còn lại, kể cả
  bước chờ/thử sửa lồng bên trong. Yêu cầu đã gửi có thể hoàn tất và được lưu
  nếu hợp lệ; không tiếp tục thử lại hoặc gửi nhóm mới sau khi nhận tín hiệu
  dừng. Giữ nguyên lỗi gốc thay vì biến lỗi dịch vụ thành thông báo hủy.
- **Giới hạn tần suất:** đọc `Retry-After` dạng số giây hoặc ngày HTTP. Tối đa
  hai lần thử lại, chờ ngắn có thể hủy; nếu dịch vụ yêu cầu chờ hơn năm giây thì
  tạm dừng để người dùng tiếp tục sau, không gửi sớm hoặc treo chờ dài. Không
  hoàn lại chi phí của yêu cầu mất mạng chưa biết kết quả.
- **Apps Script dở dang:** gateway v3 trả cả những đoạn đã dịch trước khi lỗi.
  BiliClass chỉ lưu các đoạn qua kiểm tra số liệu/token/ngôn ngữ, rồi tạm dừng;
  tiếp tục chỉ gửi phần còn thiếu. Giữ bộ đếm bảo thủ của nhóm dở dang, không
  hoàn lại toàn bộ rồi vô tình cấp thêm hạn mức.
- **Phản hồi hỏng:** JSON lồng sai cấu trúc của Gemini/LanguageApp hoặc kết nối
  HTTP bị cắt được chuyển thành lỗi có kiểm soát. Không đưa nội dung lỗi thô,
  key hoặc đoạn bài riêng tư ra giao diện. Đóng cả luồng phản hồi lỗi Google.
- **Cấu hình/cache:** kiểm tra lại URL/model ngay trước khi gửi để ngăn một
  cửa sổ khác đổi cấu hình rồi lưu kết quả vào bộ nhớ của cấu hình cũ. Một tùy
  chọn giới hạn Google hỏng khi Google không được chọn không làm tê liệt tab
  dịch vụ khác. Google giữ đúng lỗi key/quota khi không còn key kế tiếp.
- **Ký tự đặc biệt:** chia nhóm LanguageApp theo độ dài UTF-16 của JavaScript,
  tránh nhóm chứa nhiều emoji bị gateway từ chối dù Python đếm còn trong hạn.

## Tương thích Apps Script

Bản triển khai v2 đang dùng vẫn hoạt động với client mới. Lưu cấu hình trong
BiliClass không tự cập nhật mã trên tài khoản Google. Để dùng khả năng giữ
đoạn thành công bên trong một nhóm dở dang, lấy mã mới từ **Hướng dẫn thiết lập**,
giữ đúng mã truy cập hiện có, thay Code.gs rồi **Triển khai → Quản lý bản triển
khai → Chỉnh sửa → Phiên bản mới**. Giữ URL `/exec` để tiếp tục bài đang dở.
Không cần làm bước này để tiếp tục dùng một bản v2 đang dịch thành công.

## Bằng chứng kiểm tra

- Bộ hồi quy 492 ca liên quan đã qua; sau các sửa cuối, chạy lại **170 ca** thuộc
  nhóm bộ dịch, lỗi mạng, hàng đợi và trình bày lỗi (có chồng lặp với bộ 492 ca).
  Ca lỗi mới tái hiện việc hàng đợi chạy
  hết các file khi gặp ba lỗi cấu hình chung trước khi sửa.
- Qt smoke riêng của bốn lựa chọn dịch kiểm tra cấu hình, hướng dẫn lần đầu,
  sáng/tối, hàng đợi hai PPTX, lỗi triển khai chỉ gọi một lần, khôi phục rồi
  dừng/tiếp tục và giữ màn hình hoàn thành. Qt smoke Google cũ kiểm tra luồng
  chuyển đổi, giữ nguồn, bộ nhớ dịch và mở bước tạo giọng. Không có cảnh báo QML.
- Gửi **12 lượt dịch API mới**: ba câu tự biên soạn thuộc Toán, Sinh học và Tin
  học qua từng dịch vụ. Mỗi câu có một lượt gọi thật, không lấy kết quả cache.
  Cả bốn nhận đủ tiếng Anh, giữ ý chính về xác suất có điều kiện, dịch mã RNA
  và xác thực danh tính. Tiêu đề có thể dùng thuật ngữ tại máy. Không gửi bài
  giảng cá nhân. Đây là mẫu nhỏ, không phải chứng nhận mọi môn hoặc đo tải dài.
- Báo cáo máy cục bộ, ngoài Git: `reports/rc168-provider-resilience/` gồm kết quả
  API, Qt và ảnh kiểm tra. Key, thư viện, cache và tệp thực thi không được commit.

Yêu cầu HTTP đang chờ phản hồi vẫn chịu timeout của adapter; nút Dừng ngăn
công việc mới, không hứa hủy ngay yêu cầu đã gửi. Khi nhà cung cấp hết quota,
chặn tài khoản hoặc mất mạng, BiliClass giữ công việc để tiếp tục, không tự đổi
dịch vụ. Các giới hạn tại máy không phải số dư/hạn mức chính thức của tài khoản.
Kiểm tra tự động không chứng minh mọi câu dịch đúng nghĩa, mọi đáp án đúng hoặc
chữ trong ảnh đã được đọc hết.

## Tài liệu API đã đối chiếu

- [Google Translation v2](https://docs.cloud.google.com/translate/docs/reference/rest/v2/translate)
- [LanguageApp HTML](https://developers.google.com/apps-script/reference/language/language-app),
  [ContentService và doPost](https://developers.google.com/apps-script/guides/content)
- [Gemini generateContent](https://ai.google.dev/api/generate-content),
  [xử lý lỗi và thử lại](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [DeepL Translate Text](https://developers.deepl.com/api-reference/translate/request-translation)
