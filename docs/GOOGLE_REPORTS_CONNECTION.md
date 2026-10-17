# Kết nối báo cáo Google — hướng triển khai

RC69 chưa tích hợp đăng nhập Google hoặc tự đọc Cloud Billing. Số ký tự
trong ứng dụng là **bộ đếm cục bộ của BiliClass**, không phải báo cáo Google.

## Dùng một Gmail chính

Không cần một lần đăng nhập báo cáo cho mỗi key. Có thể cấp cho một Gmail
chính quyền xem các tài khoản thanh toán liên quan. Với quyền phù hợp,
Gmail đó xem được nhiều dự án. Google tổng hợp chi phí theo tài khoản thanh
toán/dự án; không nên hiểu báo cáo này là bộ đếm riêng từng API key.

Để xem báo cáo trên web, chủ tài khoản thanh toán thực hiện một lần:

1. Mở Google Cloud → **Billing**, chọn tài khoản thanh toán.
2. Mở **Account management → Show info panel → Add principal**, thêm Gmail chính.
3. Gán **Billing Account Viewer** và lưu.
4. Đăng nhập Gmail chính, vào **Billing → Reports**.

Lặp lại việc cấp quyền cho các tài khoản thanh toán khác cần xem. Không
cần cấp quyền quản trị cho Gmail chỉ dùng xem báo cáo. Dữ liệu có độ trễ;
không dùng báo cáo cũ để kết luận ngay rằng một key còn đủ hạn mức.

Nguồn: [Cấp quyền xem Billing](https://docs.cloud.google.com/billing/docs/how-to/grant-access-to-billing),
[Cloud Billing Reports](https://docs.cloud.google.com/billing/docs/how-to/reports).

## Tích hợp vào BiliClass sau này

Luồng mong muốn: **Kết nối Google → chọn Gmail chính → đồng ý quyền đọc**.
Ứng dụng hiển thị nguồn số liệu và thời điểm cập nhật; bộ đếm cục bộ tiếp
tục giữ phần sử dụng mới chưa có trong báo cáo.

API key dịch hiện dùng không có danh tính IAM để chỉ tích thêm quyền đọc
báo cáo. Phía phát triển phải chuẩn bị ứng dụng OAuth và chọn nguồn dữ liệu
thực sự truy vấn được; việc cấp Billing Account Viewer để xem web chưa tự
tạo kết nối trong BiliClass.

Nguồn: [Xác thực bằng API key](https://docs.cloud.google.com/docs/authentication/api-keys).

Xuất Billing sang BigQuery là một lựa chọn cần đánh giá riêng: phải cấu
hình xuất, quyền đọc dữ liệu và chi phí liên quan. Không tự bật xuất, tạo
tài nguyên tính phí hoặc mở rộng IAM trong bản nâng cấp này.

Nguồn: [Thiết lập Billing export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-setup).
