# RC160 — mở bài không tự chạy sửa, đồng bộ chữ hoa bản dịch

Mở một bài đã lưu, chuyển sang trang tạo giọng hoặc cập nhật danh sách
giọng trước đây có thể kích hoạt bước sửa bố cục hoặc tạo bù âm thanh.
Việc này khiến người dùng thấy công cụ tự xử lý ngoài thao tác vừa chọn.
Đã bỏ các điểm kích hoạt đó. Mở bài chỉ nạp dữ liệu/ảnh; sửa bố cục và
tạo giọng chỉ chạy khi người dùng bấm nút. Quy trình chuyển đổi đang
được yêu cầu vẫn kiểm tra/căn bố cục trước khi công bố kết quả.

Báo cáo cũ dùng tiêu đề “Bố cục cần xem lại” và nút “Thử căn lại”, để
phân biệt kết quả kiểm tra đã lưu với một tác vụ đang chạy. Bước sửa
vẫn có giới hạn số lượt và giữ nguyên báo cáo nếu chưa sửa hết lỗi.

Quy tắc chữ hoa áp dụng cho bản dịch mới, kết quả lấy từ cache và bước
dựng PowerPoint: đầu câu/tiêu đề viết hoa đầu tương ứng với tiếng Việt;
tiêu đề HOA chuyển phần chữ Anh thành HOA. Không dùng title/capitalize
để tránh hạ chữ trong Newton, DNA, pH; khóa công thức, trường dữ liệu
và liên kết vẫn được giữ nguyên. Không dịch lại hoặc tiêu thêm hạn mức
chỉ để đổi chữ hoa.

Với bản song ngữ đã tạo trước đây, thao tác “Thử căn lại” chỉnh chữ hoa
ở các cặp Việt–Anh được xác minh bằng hash. Cặp đã bị sửa khác với
bản ghi không được tự ghi đè; giữ nguyên run, công thức và ID đối tượng.
Cập nhật hash cặp trong bản kế hoạch riêng trước khi kiểm tra lại.

Đã dựng ứng viên riêng từ đúng bài trong phản ánh: 82 cặp ở 45 trang
được chỉnh cách viết hoa. Trang 2 hiển thị “Trigonometric function” và
“Basic trigonometric equation” đúng. Ảnh được render bằng PowerPoint;
file cá nhân đầu vào không đổi, các ZIP part ngoài trang thay đổi giữ
nguyên byte. Đây là kiểm tra chữ hoa, không chứng nhận toàn bộ bản dịch
hoặc bố cục đã hết lỗi.

Bằng chứng và ảnh nằm trong `reports/rc160`, ngoài Git. Không đóng gói
bộ cài trong mốc này; giữ các tab Cài đặt hiện tại.

Kiểm chứng: 1.642 pytest nguồn lõi đạt, một cảnh báo deprecation như
RC159; hai nhóm Browser AI cũ tiếp tục ngoài luồng dùng hiện tại. Ba
nhóm Qt đạt: mở thụ động/sửa thủ công bằng Office (không tự tạo giọng),
báo cáo ở cả hai công cụ với giao diện sáng/tối, và F1. Không có cảnh
báo QML. Ruff, compileall và diff-check đạt. Kiểm thử giữ công thức XML,
hash cặp, cache cũ, tên riêng và phần nội dung giáo viên đã sửa.
