# RC39 — sửa dừng trước bước dịch PowerPoint

Ngày 15/10/2026. Khóa đã được lưu/mở lại đúng bằng DPAPI và gọi thử Google
Cloud Translation thành công. Lượt chuyển đổi đang dở dừng ở bước đọc nguồn,
chưa gửi cụm chữ nào tới API.

## Nguyên nhân

Khi placeholder không đặt cỡ chữ trực tiếp, `_size` tìm cỡ chữ từ layout và
master. Mã cũ đọc `Slide.slide_master`, một thuộc tính không tồn tại trong
python-pptx. Cần đi qua `Slide.slide_layout.slide_master`. Vì dùng phần tử
tuple, truy cập sai xảy ra trước cả khi duyệt được layout có cỡ chữ hợp lệ.

Ngoại lệ `AttributeError` không có mã lỗi API nên UI hiển thị thông báo kết
nối chung, khiến lỗi đọc tài liệu dễ bị hiểu là thiếu key hoặc lỗi Google.

## Thay đổi

- Đọc đúng quan hệ slide → layout → master; giữ ưu tiên cỡ chữ trực tiếp.
- Kiểm thử placeholder không có cỡ chữ riêng, kế thừa cả layout/master.
- Lỗi parser có mã `source_document`; lỗi dựng file có mã `api_conversion`.
  Lỗi key/quota vẫn giữ mã riêng. Chẩn đoán chỉ lưu loại lỗi và vị trí mã
  trong thư mục job cục bộ, không lưu key/nội dung ngoại lệ vào log kỹ thuật.
- Nạp lại trạng thái key trước khi chuyển đổi, không chỉ dùng snapshot cũ.
  Lỗi đọc key đã lưu được báo đúng thay vì luôn yêu cầu thêm key mới.
- Chỉ xác nhận lưu key khi đọc lại được; khi đọc lại thất bại, giữ ô nhập
  để người dùng thử lại. Bộ đếm ký tự hiển thị số nguyên.

## Kiểm chứng

- Các nhóm kiểm thử nguồn/native, Google, lỗi parser và lưu key đều qua;
  không cộng gộp số ca chạy lặp thành số kiểm thử độc lập.
- API thật đã trả kết quả kiểm tra ngắn bằng key được lưu, không ghi key
  vào command line, log, source hoặc báo cáo.
- Đã chạy lại nguồn thực tế qua luồng Google → dựng PowerPoint → kiểm tra
  → lưu thư viện. Đây là một ca thực tế, không phải bảo đảm tốc độ/độ đúng
  cho mọi tệp. Báo cáo chi tiết nằm ngoài Git cùng dữ liệu giáo viên.
- Bản kết quả vẫn còn cảnh báo/lỗi nội dung cần rà soát. Không tự duyệt,
  không đổi FAIL/CHECK thành PASS hoặc chứng nhận toàn bài dùng để dạy.

Key, cache, nguồn, bài giảng, báo cáo và EXE vẫn ở ngoài Git. RC39 là bản
thử độc lập tại máy; mã nguồn và bộ cài cập nhật là hai mốc riêng.

## Mốc bản chạy độc lập

- Phiên bản: `1.0.0rc39`; mã nguồn: `e1deda1c1b88d5466c3ecda4cdeb036d6ebdadf1`.
- SHA-256 EXE: `5755472191ff42183a8b51b26a53eee5ff116263b560910a7c19bf0f0856c4d9`.
- Biên dịch lại toàn bộ 90 module ứng dụng, dùng lại runtime/model RC34
  không thay đổi. Đây là bản thử tại máy, chưa phát hành bộ cài tự cập nhật.
- Kiểm tra EXE độc lập: màn tạo bài 1366×850 và cài đặt Google Dịch
  1080×700 đều mở/thoát đúng, có icon Windows, đúng số phiên bản và không
  có cảnh báo QML. Kiểm tra này không thay thế thử cài trên Windows sạch.
