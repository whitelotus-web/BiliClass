# Tiến trình và tốc độ chuyển đổi

Thanh % cho biết các mốc của quy trình, không phải dự đoán thời gian hay số slide ChatGPT đã tạo. Nó bắt đầu khi chuẩn bị tài liệu, cập nhật khi mở phiên/chọn model/tải tài liệu/nhận PPTX, rồi theo số slide kiểm tra và số đoạn giọng đọc đã xử lý. Chỉ đạt 100% sau khi lưu bài vào thư viện. Bài vẫn là bản nháp cần giáo viên kiểm tra; 100% không chứng nhận bản dịch/bố cục đúng hoàn toàn.

Khi chờ ChatGPT tạo hoặc sửa bài, thanh giữ nguyên ở mốc chờ và ghi rõ web không cung cấp %. Có thể đứng ở 25% hoặc 75% khá lâu. Lỗi/thử lại không làm thanh lùi. Checkpoint tiến trình được lưu riêng với gói yêu cầu trên máy; tiếp tục dùng mốc đã lưu, không gửi lại yêu cầu gốc chỉ để có tiến trình mới.

Ảnh render và phép đo tràn chữ/tương phản được dùng lại giữa bước kiểm tra browser, nhập thư viện và xem slide. Cache chỉ hợp lệ khi khớp SHA-256 đầy đủ của PPTX, phiên bản bộ render và SHA-256 từng PNG. Tệp/ảnh thay đổi, cache cũ hoặc slide chưa hoàn tất thì render lại phần cần thiết. Phân tích chữ/lời đọc/công thức theo cấu hình vẫn thực hiện lại; kết quả ngữ nghĩa không lấy từ cache render. Office thiếu/lỗi không được lưu thành kiểm tra thành công.

Chuẩn bị voice bỏ các tác vụ trùng chữ/giọng/tốc độ và dùng WAV đã kiểm tra sẵn. Đổi giọng/tốc độ/nội dung tạo khóa audio mới. Một giọng lỗi không làm mất PowerPoint hay âm thanh khác đã hoàn tất; tool báo số đoạn chưa tạo được. Không tự phát hay tự duyệt lời đọc.

Lỗi mạng/browser/download tạm thời có tối đa hai lượt thử lại (2 và 5 giây), dùng lại đúng tài khoản/cuộc trò chuyện sau khi gửi. Trước khi gửi, tài khoản không dùng được có thể chuyển sang tài khoản còn kết nối theo ưu tiên hiện có. Nếu chưa rõ đã gửi hay chưa, tool giữ yêu cầu và dừng thay vì gửi trùng. ChatGPT không đưa tệp thì yêu cầu xuất PPTX thêm tối đa một lần; slide có lỗi thì yêu cầu sửa thêm tối đa một lượt. Không hứa tự xử lý mọi lỗi: đăng nhập, xác minh người dùng, hạn mức, web đổi giao diện hoặc nội dung không có căn cứ vẫn có thể cần can thiệp.

Đây là tối ưu xử lý trên máy, không làm ChatGPT suy luận nhanh hơn. Giữ lựa chọn model/suy luận cao nhất mà tài khoản thực sự cho phép. Kiểm chứng cache bằng `python -m scripts.verify_render_cache`; Qt workflow bằng `python scripts/qt_chatgpt_handoff_smoke.py`. Bằng chứng/tệp thử nằm ngoài Git.
