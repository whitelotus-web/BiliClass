# Chuyển đổi một lần và xác nhận toàn bài

Ngày 03/10/2026. Phạm vi: mã nguồn; chưa phát hành bản cài mới thay RC12.

`Bridge.convertLesson` nối ba bước: nhập/đánh giá → bổ sung bản dịch → xuất/xem trước. SQLite chỉ được sử dụng ở luồng UI; công việc đọc tài liệu, dịch, xuất và Office render chạy ở worker. `finishJob` giải phóng tham chiếu của bước cũ trước callback để callback có thể khởi động worker tiếp theo. Hủy tác vụ không áp dụng kết quả chưa hoàn tất; đã lưu nháp từ bước trước vẫn còn.

`plan_batch(limit=None)` chọn toàn bộ phần trống. `translate_batch(whole_document=True)` dùng model một lần cho mỗi hướng, bảo toàn dấu phân bảng/đoạn và chia chuỗi trong giới hạn 2.000 ký tự/350 token. Không đổi ID hoặc vùng nguồn, không ghi đè phần song ngữ đã có. Các trường hợp quá dài không thể chia, bộ nhớ xung đột và thiếu model được báo thay vì tự lấy bản khác.

`quick_conversion.build_preview` xuất từ snapshot riêng có đủ VI/EN; trạng thái duyệt trong thư viện vẫn giữ nguyên. Kết quả ghi lesson ID, revision, SHA-256 PPTX, số slide, slide nguồn hoặc segment map cho mẫu, cùng điểm cần kiểm tra. Slide được render bằng PowerPoint đã cài; không render được vẫn có file PPTX để mở ngoài. File xem trước nằm trong thư mục temp của thư viện, không đưa vào Git.

`verify_preview` kiểm tra artifact, revision và bản nguồn trước khi mở hoặc sử dụng. Nút xác nhận toàn bài gọi `Library.review_lesson`: kiểm tra đủ cặp và nguồn, tạo một phiên bản duyệt và chốt chuẩn bị trong một lần ghi. Không tự duyệt trợ giảng, quiz hoặc dữ liệu kho kiến thức. Sau đó mở phiên trình chiếu; template sử dụng segment map để mascot theo đúng nội dung trên slide.

Đã kiểm tra bằng `.venv`: toàn bộ **178 kiểm thử** và Ruff qua. Qt chạy bằng model dịch và Microsoft PowerPoint thật: một nút nhập PPTX → đánh giá → dịch cả hai hướng → tạo/render slide; mở xác nhận không tự duyệt, xác nhận toàn bài chốt và chuyển giao tới trình chiếu; văn bản → slide mẫu/render và segment map. Bước chuyển giao phiên dạy trong kiểm thử Qt được chặn để không mở slideshow đè lên phiên làm việc của người dùng. Không có lỗi QML trong kiểm thử này.

Chất lượng dịch/OCR và sự phù hợp từng môn vẫn cần giáo viên kiểm tra trên tài liệu thực tế. Không khẳng định tài liệu bất kỳ đều có thể chuyển đổi đúng hoàn toàn hoặc giữ bố cục tuyệt đối. Tệp `.ppt` cũ, PDF không trích xuất được và trường hợp OCR không rõ cần xử lý đầu vào hoặc sửa chi tiết.

Kiểm tra lại luồng Qt trên Windows có model và Office bằng `python scripts/qt_quick_conversion_smoke.py` trong môi trường dự án. Script dùng thư viện tạm riêng dưới `.runtime`, ghi ảnh/báo cáo vào `reports/quick-convert`; không dùng thư viện giáo viên. Chạy qua cache phát triển như `scripts/run.ps1` nếu môi trường cần cache thư viện. Kiểm tra nhanh một màn hình bằng `scripts/run.ps1 --smoke --page new --screenshot reports/quick-convert/new.png`.
