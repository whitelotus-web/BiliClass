# RC55 — mẫu bài giảng, trạng thái dịch và thư viện, 16/10/2026

[GitHub Release RC55](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc55).

- Nguồn: `9a43c4b1f4fd9b106d70eb0aef7f84eb7d802c44`.
- ZIP: `BiliClass-RC55-Windows.zip`, 837247204 byte, 4166 tệp.
- ZIP SHA-256: `2fafff597a0e65bcdf6bde7ffe312684f5037ad4c82fe4cc30534cf5c79defe6`.
- EXE SHA-256: `c689afa87496547466476a9d92cfd5872f7c3affd3460708f9f756ccaba8dd93`.

- Thay hai nút Danh sách/Thẻ lớn bằng một nút biểu tượng 40×40 px cạnh Sắp xếp;
  biểu tượng khớp kiểu xem hiện tại, hỗ trợ tooltip, bàn phím và tên truy cập.
- Giữ cache ảnh bìa trong phiên (tối đa 80 ảnh), làm mới khi bài thay đổi/xóa.
- Bật/tắt mascot từ cùng nút, đồng bộ nhãn khi ẩn bằng menu; bỏ nút tạo bài
  trùng trên Trang chủ, giữ thao tác tạo bài trong Thư viện.
- Trang chủ và Google Dịch có thống kê giới hạn cục bộ theo nhóm, cảnh báo
  80%/95%, số còn lại ước tính và thành phần đã phát hiện. Không đọc số dư
  Google Cloud, không cộng sai bộ đếm chung thành hai hạn mức riêng.
- Key có số thứ tự ổn định, tên đầu vào/tên tùy chỉnh trong ngoặc và hộp đổi tên.
  Giữ thứ tự ưu tiên key, cách chuyển key và lịch sử sử dụng.
- Sửa lỗi dựng mẫu dừng ở 55% khi đoạn văn bị coi là tiêu đề quá dài; giữ đủ
  chữ bằng phân trang. Tách native OMML khỏi văn bản đã dịch, chia công thức
  nhiều đoạn; bỏ liên kết nhảy tới slide gốc gây trùng OPC part trong file mới.

Kiểm chứng nguồn: 78 kiểm thử liên quan; Qt với PowerPoint thật cho ba bài
thử, hai kích thước 1080×700/1366×850, icon, chọn/tải đúng ID, cache qua tab,
cảnh báo giới hạn, đổi tên key và bật/tắt mascot; không QML warning.
Bài lỗi thực được chạy lại bằng cache dịch, cấm mọi yêu cầu Google trong phép
thử: hoàn tất 78 slide, render 78/78, không còn lỗi tràn chữ; ba trang
còn mã ký tự lạ từ nguồn và giữ trạng thái cần kiểm tra. Kiểm tra native bằng PowerPoint không tự chứng nhận ngữ nghĩa, chữ trong
ảnh hoặc hiệu ứng; trạng thái cần rà soát vẫn được giữ, không tự duyệt bài.

Runtime/model giữ nguyên từ mốc đã kiểm tra RC51. Không chạy lại inference
giọng/OCR trong kiểm thử thay đổi này. Thư viện giáo viên, WAV, key, bản dựng,
model và báo cáo riêng không nằm trong commit mã nguồn.

Giới hạn Google được mô tả theo tài liệu chính thức:
[quota theo dự án](https://docs.cloud.google.com/translate/quotas),
[giá và khoản miễn phí](https://cloud.google.com/products/translate/pricing),
[đọc quota cần quyền OAuth](https://docs.cloud.google.com/service-usage/docs/reference/rest/v1beta1/services.consumerQuotaMetrics/list).

Bộ cài đã kiểm SHA-256/CRC mọi tệp trong ZIP, xác minh digest GitHub và
manifest khi cài. EXE đã cài được thử Danh sách, Thẻ lớn, Cài đặt và Trang chủ
ở dữ liệu dùng thử, không có PYTHONPATH nguồn; không QML warning.

Đã mở độc lập qua desktop Explorer, ngoài job launcher; vẫn sống sau khi
đóng launcher và qua 10 kiểm tra phản hồi. Shortcut Desktop/Start menu trỏ
RC55. Bài cũ 16 bản ghi và 992 WAV giữ nguyên; thêm một bản khôi phục 78 slide
của lượt chuyển đổi bị dừng, không gọi lại Google/không đổi bộ đếm dịch.
Bài khôi phục vẫn cần kiểm tra trước khi dạy, không tự tạo lại giọng.
Trình cập nhật công khai từ RC34/RC54 nhận đúng RC55, dung lượng và SHA-256.

Sau phát hành đã rà soát toàn dự án: 869/871 test qua ở lượt đầu; hai fixture
cũ đã cập nhật và 18 test liên quan chạy lại qua. EXE cài thực tổng hợp được
WAV Anh/Việt/trộn, tốc độ/cache, lớp học WebSocket và báo cáo/sao lưu.
Các Qt Google/result/library/voice hiện tại qua. Một Qt browser cũ chưa theo
luồng đang bật, được ghi rõ cùng nợ lint và giới hạn chất lượng trong
[báo cáo rà soát và kế hoạch](AUDIT_OPTIMIZATION_RC55.md). Mã chạy của bộ cài
vẫn đúng commit ghi ở đầu; cập nhật sau đó là test/tài liệu.
