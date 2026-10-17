# RC69 — Giao diện gọn, Mascot luôn nổi và ghi nhớ lựa chọn

Ngày 17/10/2026. Giữ luồng chuyển đổi → tạo giọng → tải độc lập hoặc mở bài
để dạy của RC68; không thêm tab và không đổi engine/model.

## Thay đổi

- Vùng tải PowerPoint chuyển thành hàng gọn trên cửa sổ thấp; giảm khoảng
  cách và chiều cao cấu hình. Mẫu riêng, bìa/intro/nội dung/kết thúc chuyển
  vào **Tùy chọn mẫu…**. Nút chuyển đổi và tiếp tục tác vụ vẫn truy cập được.
- Mascot đặt `transientParent: null`, tách cửa sổ công cụ khỏi cửa sổ chính.
  Cờ topmost theo **Luôn nổi trên cùng**, mặc định bật khi tùy chọn cũ chưa
  có giá trị. Escape chỉ thu gọn; Ẩn chủ động vẫn giữ qua minimize/restore.
- Bộ môn trong Cài đặt dùng cùng danh sách môn với Chuyển đổi, có **Khác**.
  Lưu mới áp dụng môn mặc định; bài đang chọn môn thủ công giữ môn riêng.
  Bài mới dùng môn đã lưu. Tên môn chứa dấu phẩy được giữ nguyên một môn.
- Cấp học/Khối lớp lưu ngay lần chọn gần nhất trong thư viện trên máy.
  Mở lại khôi phục đúng cặp; đổi cấp học chọn khối hợp lệ, không dùng khối
  của cấp khác. Cài đặt thiếu/hỏng trở về THPT/10; không tự ghi lúc mở app.
- Giọng đọc gom **Thao tác khác** còn ba mục chính: xem/sửa lời đọc, sửa
  thông tin và nhóm thao tác bài giảng. Bỏ lối chuyển đổi trùng với sidebar.
  Kiểm tra lời đọc chuyển vào menu; tự thống kê theo ngôn ngữ, chỉ hiện nhắc
  và lối xử lý khi có slide thiếu lời. Giữ kiểm tra cấu hình, cache và nội
  dung hiện có trước khi tạo; không tự dịch hoặc tự xác nhận nội dung.
  Nghe thử/Dừng nghe dùng chung nút. Bản giọng sẵn sàng chỉ hiện một khu vực
  tải/mở dạy; tải không giọng vẫn có trong menu. Bản chưa có giọng vẫn tải
  và mở dạy ngay. Giữ ZIP, các bản giọng, chỉnh sửa và bước xác nhận dạy.
- Google Dịch dùng bộ đếm/giới hạn cục bộ riêng theo key, mặc định 500.000
  ký tự/key/tháng UTC. Reserve nguyên lượt trong transaction trước gửi;
  lượt vượt phần còn lại chuyển key khác. Hoàn trả khi Google xác nhận từ
  chối; gửi chưa rõ kết quả vẫn ghi nhận. Tháng mới tự dùng lại các key.
  Đổi tên/xóa/thêm lại không reset. Lịch sử nhóm cũ giữ nguyên, hiển thị
  riêng; không chia đoán cho từng key. Ngay dưới key có Còn/tổng/đã dùng và
  thanh tiến độ. Đồng bộ riêng tư hỗ trợ thêm ledger theo key, đọc được
  định dạng cũ; không gửi key hoặc gọi dịch thật trong lần kiểm thử này.
  Trong tháng nâng cấp, phần lịch sử chung chưa phân bổ được trừ dự phòng
  khỏi hạn mức của từng key cũ. Không gán nó thành số đã dùng riêng; key mới
  thêm sau nâng cấp không chịu dự phòng cũ. Sang tháng mới dự phòng hết áp
  dụng. Kiểm migration cả DB trước RC69, DB ledger cũ bốn cột và đồng bộ.
  Bản candidate đầu đã biên dịch/kiểm ZIP nhưng chưa cài/phát hành; kiểm
  giới hạn lịch sử phát hiện cần dự phòng nên sửa và kiểm lại trước bản cuối.

Cửa sổ QML lồng có thể tự gắn transient owner; xem [Qt Window](https://doc.qt.io/qt-6/qml-qtquick-window.html).

## Kiểm chứng nguồn

145 tình huống kiểm thử đạt bằng `.venv`: suite tổng hợp 144 ca và một ca
migration bổ sung cho ledger bốn cột. Phạm vi: đóng gói, cấu hình chuyển đổi, phiên dạy,
narration workspace, bản giọng, PowerPoint, giới hạn/đổi key/đổi tháng,
lịch sử cũ, đồng bộ riêng tư và dịch Google bằng transport giả lập.

- `qt_conversion_layout_smoke.py`: 32 tình huống ở 1080×700, 1366×768,
  1366×850 và 1920×1080; trước/sau chọn tệp, giữ gốc/mẫu mới, môn thường/Khác.
  Nội dung cấu hình chính vừa viewport; trường hợp chật nhất 484/499 px.
- `qt_conversion_defaults_smoke.py`: Save hồ sơ, môn mặc định/môn riêng,
  tên môn chứa dấu phẩy, môn Khác, ba cấp học, chặn cặp cấp/khối sai và mở
  lại cả thư viện/QML khôi phục môn riêng cùng THCS/8.
- `qt_mascot_window_smoke.py`: kiểm Win32 `IsWindowVisible`, `IsIconic`,
  topmost và z-order; thu nhỏ/khôi phục ba lần; trên cửa sổ toàn màn hình
  thông thường; Ẩn chủ động; lưu bật/tắt topmost; thu nhỏ khi topmost tắt.
- Qt Home, kết quả/preview/bản giọng và phiên dạy Office đã kiểm lại trong
  mốc này. Phiên dạy kiểm native visibility/topmost khi PowerPoint đang
  trình chiếu và BiliClass thu nhỏ. WAV thử im lặng; không đánh giá giọng.
- `qt_narration_workspace_smoke.py` kiểm menu mới, cảnh báo thiếu lời, sửa
  script, tạo/dừng/tiếp tục, cache, các nút sau tạo, đường tải không giọng,
  ZIP/PowerPoint nhúng loa và giữ nguyên nguồn.
- `qt_review_usage_smoke.py` kiểm bộ đếm độc lập bên dưới hai key, lịch sử
  chung riêng, chỉnh giới hạn không reset và bố cục 1080/1366.
- Qt Google chuyển đổi bằng transport giả lập qua: một lượt API, tiến độ/
  đồng hồ, xuất PowerPoint và màn Settings ở hai kích thước. Không có cảnh
  báo QML. Bộ unit có chẩn đoán RPC disconnected từ Office trong kiểm tra
  repair; luồng xử lý fallback hoàn thành và suite vẫn đạt. Không dùng kết
  quả đó để chứng nhận chất lượng dàn trang của mọi tệp PowerPoint.

Không có cảnh báo QML ở các kiểm tra đạt. Chưa chứng nhận máy vật lý thứ
hai, màn hình phụ hoặc fullscreen GPU độc quyền/secure desktop. Báo cáo,
thư viện cá nhân, model và EXE không vào Git.

Kết nối đọc báo cáo Google chưa tích hợp trong RC69. Đã ghi lại cách cấp
quyền cho một Gmail chính và các điều kiện tích hợp trong
[GOOGLE_REPORTS_CONNECTION.md](GOOGLE_REPORTS_CONNECTION.md); không thay
đổi IAM hoặc bật tài nguyên Google Cloud trên máy người dùng.

## Đóng gói

Thông tin commit, checksum, bản cài và xác minh phát hành sẽ ghi sau khi
đóng gói và kiểm tra bản RC69.
