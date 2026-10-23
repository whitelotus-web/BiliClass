# BiliClass 1.0.0rc166

Giữ dòng trạng thái của bảng trợ giảng khi bài đang gắn. Chuyển giữa slide
có giọng và chưa có giọng chỉ đổi nội dung thông báo; không đổi chiều cao
cửa sổ trong suốt, tránh nháy bề mặt khi Windows phải dựng lại cửa sổ.

Thêm “Nghỉ giữa đoạn” ngay trên bảng trợ giảng và trong Cài đặt → Giọng
đọc. Mặc định 0,4 giây thay cho 1,1 giây; có các lựa chọn từ 0 đến 2 giây.
Lựa chọn áp dụng ngay trong phiên, lưu nền và dùng lại khi mở tool.
Không đổi tốc độ hoặc suy luận lại giọng đã tạo. Nếu bài đang gắn chứa
âm thanh với nhịp cũ, lần phát mới bằng Mascot chuyển sang các WAV đã lưu
với nhịp mới. WAV gốc không bị sửa.

File PowerPoint đã xuất cần xuất lại để cập nhật khoảng nghỉ được ghép
trong file. Bộ nhớ đệm và tự lưu nhận diện thay đổi nhịp để không lấy lại
bản cũ; chỉ cập nhật sản phẩm tự lưu còn nguyên, giữ file giáo viên đã
sửa/đang mở. Không thêm khoảng lặng thừa sau đoạn cuối của slide. File
chỉ có âm thanh nhúng mà không có các WAV riêng vẫn phát âm thanh của
chính file đó.

Kiểm chứng nguồn: 91 kiểm thử đọc, cài đặt trợ giảng, phiên dạy, cache,
xuất PowerPoint, tiến độ đọc và tên tải đạt. Kiểm thử bổ sung đổi nhịp
trong phiên chuyển sang WAV cũ đạt. Qt kiểm tra đủ ba kích thước bảng,
chuyển slide có/không có giọng giữ nguyên hình học, đổi khoảng nghỉ và
khôi phục lựa chọn đạt; không cảnh báo QML.

Qt và PowerPoint thật kiểm tra lại cả ba luồng mở từ Thư viện, Chuyển đổi
và Tạo giọng: mascot khôi phục đúng bài, trước/sau giữ nguyên hình học kể
cả slide không có giọng. File nguồn thử giữ nguyên. Ruff toàn bộ app,
scripts, tests và compileall đạt.
