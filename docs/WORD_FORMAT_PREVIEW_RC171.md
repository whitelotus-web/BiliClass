# RC171 — mẫu định dạng và chọn trọn từ trong Word

Bản nguồn thử tiếp sau tag/bộ cài RC170, nhánh
`codex/word-format-preview-rc171`. Bộ cài RC170 đã phát hành được giữ nguyên.

- Cụm màu/kiểu chữ/font/size/đặt lại được căn giữa nửa bên phải của hàng
  cấu hình, giữ các nút thẳng hàng ở kích thước laptop và desktop.
- Ô **Xem trước song ngữ** bên phải khung tệp, ngoài ô **Dịch toàn bộ**,
  thẳng mép phải bên dưới nút hủy. Chỉ hiện khi đã tải bài Word thành công;
  khi chưa tải hoặc hủy bài, ô ẩn và khung tải dùng toàn bộ chiều ngang.
  Tiêu đề căn giữa, khung cao 108 px. Dùng cặp câu mẫu chung
  “Khám phá ý tưởng mới.” / “Explore new ideas.” và minh họa trực tiếp
  cả bốn kiểu: Anh dưới Việt, hai cột, từ khóa, 100% Anh. Font,
  cỡ, màu, tô sáng, đậm/nghiêng/gạch chân/gạch ngang đổi ngay theo cấu hình.
  Nền giấy trắng thể hiện màu chữ trong tài liệu ở cả giao diện sáng/tối.
  Ô nhỏ có thể cuộn khi chọn cỡ chữ lớn. Không gọi dịch vụ và không thay
  nội dung nguồn, vùng chọn, bản dịch hoặc checkpoint.
- **Dịch toàn bộ** làm mờ và khóa cả hai khung nội dung gốc/vùng chọn,
  kể cả phóng to, cuộn/zoom và bỏ vùng. Popup chọn và cửa sổ nguồn mở
  rộng được đóng khi bật chế độ này. Cấu hình, mẫu song ngữ và nút
  chuyển đổi vẫn hoạt động. Bỏ tích trả lại các vùng đã chọn trước đó.
- Bôi đen hụt ở đầu/cuối từ sẽ nới ra trọn từ trước khi xác nhận, gồm chữ
  Việt tổ hợp và vị trí UTF-16 sau emoji. Không tự thêm cả câu hoặc đoạn;
  muốn lấy trọn câu có thể dùng **Tích chọn → Câu**. Không tự bỏ từ đang
  chọn hụt, tránh mất phần nội dung người dùng định dịch.
- Nút **Vùng 1…** vừa nội dung; nút bỏ vùng là **×**, có tooltip/nhãn hỗ
  trợ tiếp cận. Chỉ bỏ vùng chọn, không xóa file.

Kiểm bằng môi trường dự án: kiểm thử ánh xạ nguồn/vùng chọn, Qt Word với
dịch vụ giả lập, giao diện sáng/tối và nhiều kích thước. File Word nguồn
phải giữ nguyên byte, định dạng xuất chỉ áp dụng cho vùng dịch đã xác nhận.
