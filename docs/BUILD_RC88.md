# RC88 — Xem bài giảng và tự căn bố cục

Trang chủ: ba mục chuyển ngữ/thiết kế/giọng đọc & mascot có chiều rộng
bằng nhau; mỗi cụm biểu tượng và chữ được căn giữa trong phần của mình.
Các nút chọn mẫu dùng chung component vòng tròn xanh 18 px với lựa chọn
chuyển ngữ/thiết kế, giữ vùng bấm và điều khiển bằng bàn phím.
Theo lựa chọn mới nhất, bỏ viền và nền chọn của các thẻ chuyển ngữ,
thiết kế và mẫu; trạng thái chọn thể hiện bằng nút radio xanh.

Màn Xem bài giảng có thông tin môn/lớp, kiểu chuyển ngữ, thiết kế, số slide
và từng bản giọng đã lưu (ngôn ngữ, người đọc, tốc độ, trạng thái). Ba nút
Mở PowerPoint, Tải PowerPoint và Tạo giọng đọc nằm cạnh nhau. Không đưa
form cấu hình tạo giọng hoặc nút tạo lại vào màn xem. Tab giọng đọc giữ
cấu hình, lời đọc riêng và tiến độ. Lưu lời đọc không làm đổi tab.

Mở bài dùng luồng gắn Mascot. Mở/tải thông thường chọn bản giọng đã kiểm
tra đủ, ưu tiên bản có nhiều ngôn ngữ rồi bản lưu mới hơn; không có giọng
đủ thì dùng bản không giọng. Bản hỏng WAV hoặc khác nội dung không được
nhúng. Các lựa chọn tạo ngôn ngữ đã hoàn tất được ẩn; bản Việt–Anh có loa
riêng và chung được tính là đã có cả ba. Tạo tiếp dùng lại WAV đúng nội
dung/người đọc/tốc độ. Các lựa chọn tải riêng tại tab giọng vẫn dùng đúng
bản đang chọn.

Định dạng số và đơn vị bằng khoảng trắng không ngắt dòng, kể cả khi nằm
ở hai run hoặc bị ngắt dòng mềm. Giữ kiểu chữ, số, công thức và field.
Các đoạn đọc chuẩn hóa khoảng trắng để dùng lại cache âm thanh. Cỡ chữ
mới trong khung song ngữ có sàn 18 pt trước bước đo/căn chữ của Office.
Địa chỉ web/mạng xã hội độc lập được giữ một bản.

Khi có tràn chữ đã đo, thử nới khung vào khoảng trống, xử lý cả nhóm không
xoay. Chú thích dưới hàng ảnh có thể được dành thêm chỗ: co ảnh theo đúng
tỷ lệ và giữ các đối tượng ảnh chồng tương đối; không di chuyển motion
path/trigger. Tách hàng chữ giao nhau trong khu vực này. Chỉ nhận bản sửa
được PowerPoint render và giảm tập lỗi đo được; giữ bản trước khi có lỗi
mới. Tối đa ba lượt, dừng khi không tiến triển. Mở/tải bài cũ có FAIL tự
chạy hoàn thiện ở worker; dấu phiên bản/hash ngăn lặp sửa vô ích. Giữ lịch
sử nguồn và chỉ giữ chữ ký âm thanh khi toàn bộ tác vụ đọc vẫn giống nhau.

Kiểm chứng cục bộ: bài 30 slide được thử trên bản sao, 8 lỗi tràn chữ ban
đầu giảm về 0. Thử chuyển đổi lại cùng nguồn bằng cache dịch đã có cũng
30 slide/0 FAIL, không gọi API. Đo từng ký tự bằng PowerPoint xác nhận
108 km, 10 s, 10s, 108 km/h nằm cùng dòng trong khung thử hẹp. Đây là bằng
chứng cho các ca đã chạy, không phải chứng nhận mọi file PowerPoint.
CHECK về nội dung, công thức, hiệu ứng hoặc chữ nguồn nhỏ vẫn được giữ;
tool không tự xác nhận thay giáo viên về độ đúng của bản dịch/cách đọc.

Qt thử màn xem ở 1080/1366/1680, luồng không giọng/Anh/Việt–Anh, tab tạo
giọng, các lựa chọn còn thiếu và nút mở gắn Mascot. Audio của smoke là WAV
fixture; kiểm tra model thật được thực hiện riêng khi kiểm gói phát hành.
Dữ liệu cá nhân, báo cáo, file thử, model và executable không đưa vào Git.

Kiểm thử nguồn: 891 test lõi đạt (không chạy sáu nhóm browser/Chrome cũ
không liên quan thay đổi). Sau khi bổ sung giữ WAV khi chỉ đổi thứ tự đọc,
63 test giọng/hoàn thiện/nhúng/trợ giảng đạt. Qt màn xem, workspace giọng,
Trang chủ và cấu hình chuyển đổi đều đạt, không có cảnh báo QML. Cấu hình
chuyển đổi được thử bốn cỡ cửa sổ, đủ trạng thái có/chưa file và gốc/mẫu.
Đã áp dụng bản sửa vào bài đang kiểm tra sau khi thử trước trên thư viện
riêng: 30 slide, 0 FAIL, đủ 134/134 đoạn Anh; nguồn cũ và lịch sử còn nguyên,
không gọi API hoặc tạo lại giọng.
