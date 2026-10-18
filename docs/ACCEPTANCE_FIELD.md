# Nghiệm thu trên thiết bị thật

Chỉ ghi đạt khi có người thực hiện và bằng chứng trên đúng thiết bị. Các
kiểm tra loopback, ảnh Qt và WAV fixture là kiểm tra kỹ thuật riêng. Không
đưa tên học sinh, câu trả lời, key, báo cáo lớp hoặc bài giáo viên vào Git.

## Chuẩn bị

Ghi phiên bản/commit trong `BUILD_INFO.json`, cấu hình máy, Windows/Office,
DPI, màn hình, Wi-Fi và số thiết bị vào một báo cáo ở `reports/field/`.
Dùng lớp thử và nội dung có quyền sử dụng. Xuất bản sao lưu trước buổi thử;
xác minh mở bản khôi phục ở thư mục khác và đủ bài/audio/phiên.

## 30–50 điện thoại trên Wi-Fi trường

1. Có cả Android/iPhone; quét QR vào lớp, giữ nguyên câu hỏi chưa công bố.
   Kiểm tra không thấy đáp án/giải thích trước bước công bố.
2. Gửi cùng mã nộp hai lần, đóng tab và vào lại; mỗi học sinh chỉ có một
   phản hồi hiệu lực. Đổi câu khi vài máy đang gửi và kiểm tra đúng vòng.
3. Khóa màn hình 2 phút, tắt Wi-Fi 30 giây rồi bật, nối lại; giữ lựa chọn và
   trạng thái câu. Thử một máy rời lớp hẳn.
4. Đóng câu, công bố, chấm lại, kết thúc và xuất CSV. So số phản hồi, mẫu số
   và phần trăm với danh sách thử. Mở lại phiên sau khi khởi động ứng dụng.
5. Đo thời gian nhấn Gửi đến xác nhận bằng ghi hình hoặc đồng hồ trình duyệt;
   ghi ít nhất 50 mẫu, p50/p95/max cùng số lần mất kết nối. Không dùng số
   loopback thay cho độ trễ Wi-Fi thật.

Kiểm tra tải tự động tại máy: `.venv/Scripts/python.exe -m scripts.verify_classroom_load`.
Kết quả này được ghi rõ là loopback, không là nghiệm thu điện thoại.

## Máy chiếu, PowerPoint và ngoại tuyến

1. Extend: cửa sổ giáo viên ở màn chính, câu hỏi ở máy chiếu. Duplicate:
   kiểm tra không vô tình lộ bảng điều khiển/đáp án. Thử Presenter View.
2. Rút/cắm màn hình khi đang chiếu và khi thu gọn mascot. Cửa sổ phải còn
   tìm thấy được; bật lại đúng màn, không tự mở một bài khác.
3. Tắt PowerPoint khi đang đọc, mở lại đúng bài. Một PowerPoint giáo viên
   mở riêng phải còn nguyên khi BiliClass hết thời hạn hoặc dừng kiểm tra.
4. Ngắt mạng và dạy bài đã tạo giọng: thử loa Việt, Anh, Việt–Anh chung,
   đổi slide, quay lại và dừng. Không lấy âm thanh sai ngôn ngữ/tốc độ.

Kiểm tra màn hình thứ hai: `.venv/Scripts/python.exe -m scripts.verify_displays`.
Script yêu cầu màn phụ thật; không giả lập để ghi đạt.

## Windows sạch và cập nhật

Thử trên máy/VM Windows không Python/Codex. Cài gói, tạo giọng thật bằng
model đi kèm, mở bài và lớp học. Cập nhật từ bản trước, ngắt mạng khi tải,
thử gói sai hash; bản cũ vẫn mở được. Cài bản mới không ghi đè thư viện.
Gỡ ứng dụng và kiểm thư viện/bản sao lưu còn nguyên. Ghi RAM/CPU và thời
gian ở máy ít RAM; chạy 60–120 phút trước khi kết luận ổn định phiên dài.

## Nghe và xem bài

Mở `reports/app/multilingual-voice/listening-review.html`: chấm VI, EN,
xen kẽ, công thức của 6 giọng, tên riêng/đơn vị/từ viết tắt và tốc độ.
Giáo viên ghi từ sai và tên WAV; tạo được WAV không xác nhận phát âm đúng.
Với corpus, đối chiếu PNG trước/sau cùng `source-inspection.json` và
`after-repair.json`. Lỗi đầu vào và cảnh báo còn lại phải ghi riêng; không
hạ FAIL vì đã giữ được tệp hoặc PowerPoint mở được.
