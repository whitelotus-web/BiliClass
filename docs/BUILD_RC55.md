# RC55 — mẫu bài giảng, trạng thái dịch và thư viện, 16/10/2026

Mốc nguồn đã kiểm tra, đang chuẩn bị bộ cài riêng.

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
