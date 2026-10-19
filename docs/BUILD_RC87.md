# RC87 — Nhãn lớp trên Trang chủ và thanh trạng thái

Trang chủ dùng “Lớp” thay cho “Khối” ở Bài gần đây và thẻ bài đang chọn.
Không đổi số lớp hoặc dữ liệu bài giảng.

Khi một job kết thúc mà callback không đặt thông báo mới, xóa thông báo
mặc định “Đang xử lý tại máy…”. Không xóa thông báo khi job kế tiếp đã
khởi chạy, thông báo thành công cụ thể hoặc lỗi. Thanh dưới ẩn khi không
có thông báo; tác vụ đang chạy vẫn có chỉ báo và nút Dừng tác vụ.

25 test liên quan đạt. Qt kiểm tra Trang chủ ở ba kích thước, job đang
chạy/hoàn tất và lỗi; kiểm tra footer chuyển đổi ở bốn kích thước. Thử
tệp vượt giới hạn chờ đúng kết quả kiểm tra file bất đồng bộ đã có từ RC84.

Source `5ead8204c09471f262f73822fea89fbfa42eb459` có
[CI đạt](https://github.com/whitelotus-web/BiliClass/actions/runs/39219085814).
[Release RC87](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc87)
đã kiểm hash gói, cài/gỡ trong đường dẫn Unicode riêng, Properties, Qt,
templates, backup, classroom process và tạo giọng Việt–Anh bằng model thật.
Build một lần; ZIP 871.243.653 byte, SHA-256 GitHub khớp
`1141e73754a3193a7b6bee5cdf436460e1f799394a66db5d4ab9d02b19c9bb2c`.
Dữ liệu, model tải về, báo cáo kiểm thử và executable không đưa vào commit.
