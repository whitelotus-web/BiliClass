# RC159 — xử lý lỗi thực tế và thống nhất tự lưu

Ngày 23/10/2026. Bản nguồn trên F cho giáo viên thử; không tạo bộ cài
hoặc release mới. Kế thừa [RC157](REVIEW_RC157.md) và [RC158](REVIEW_RC158.md).

## Các lỗi thực tế và thay đổi

- Một PowerPoint có ảnh khai báo hơn 3,8 tỷ pixel, khiến Pillow dừng
  ngay khi đọc metadata. Bước OCR chưa bắt loại lỗi đó nên hàng đợi chỉ
  hiện lỗi chung. Nay bỏ qua OCR ảnh đó, giữ hình gốc và đánh dấu slide
  chưa xác minh chữ trong ảnh. Không tắt giới hạn pixel hoặc cố giải
  mã ảnh khổng lồ. Thử đọc lại đúng nguồn lỗi đã đi qua bước này; bộ
  nhận diện trong phép thử thay bằng fixture, không phải chứng nhận OCR.
  Cùng kiểu header quá lớn được bắt ở bước nhận diện khung nền, kiểm
  tra mặt nạ logo và đọc cache ảnh bìa. Cache bìa hỏng được dựng lại từ
  ảnh slide hợp lệ; không bỏ giới hạn pixel. 15 kiểm tra bị ảnh hưởng
  đạt, gồm ba trường hợp PNG có header giả kích thước lớn, không cấp
  phát bitmap khổng lồ.
- Hai bài dừng khi phản hồi dịch làm mất các dấu giữ công thức. Sau
  lần thử lại bằng khóa ẩn đã có, thêm một bước cuối: dịch riêng phần
  chữ, ghép khóa tại máy, kiểm tra lại số/ký hiệu/hóa học rồi mới cache.
  Không gửi lại toàn bộ bài, không bỏ kiểm tra để báo xong. Các lần gọi
  đều tính hạn mức, có giới hạn lần thử và nhận Dừng. Nếu vẫn lỗi, chẩn
  đoán trỏ về đoạn gốc thay vì một mảnh chữ thường xuất hiện nhiều nơi.
- Log lỗi hàng đợi được ghi vào log cục bộ của app cả khi không có
  console. Giữ loại lỗi/vị trí stack; không chép nguyên thông báo có
  thể chứa lời bài hoặc key. Lỗi chưa phân loại có mã `unexpected`.
- Bổ sung lời dịch chính xác cho lệnh giải phương trình/hệ phương trình
  và hai câu ghi nhớ lượng giác đã thấy trong mẫu thật. Chỉ áp dụng cho
  câu khớp chính xác, ưu tiên thuật ngữ giáo viên; không sửa công thức.

## Một kết quả tự lưu từ B đến C

Khi đã tự lưu B, tạo giọng cập nhật cùng file đó thành C. Tạo lại giọng
hoặc đổi chính sách nối đoạn cũng cập nhật file được quản lý, thay vì
thêm một bản ở mỗi lần. Lặp lại bước tự lưu chuyển đổi không hạ bản đã
có giọng thành bản không giọng. Tên tự lưu ổn định theo kiểu bài, không
phụ thuộc giọng. Tải thủ công vẫn gợi ý rõ ngôn ngữ/giọng và lưu riêng.

Chỉ cập nhật khi có bản ghi đúng bài/nơi lưu và hash file vẫn khớp.
Kiểm tra lại ngay trước công bố vì ghép giọng có thể mất thời gian;
file đã sửa, đang khóa/mở, không ghi được thì giữ bản cũ và chọn tên
mới hoặc thư mục dự phòng. File gốc không được chọn làm đích cập nhật.
Ghép giọng thất bại giữ B. Khi mở B do tool tự lưu để tạo giọng, giữ
liên kết về A cả ở một bài và hàng đợi. Không dò tên giống nhau rồi
tự xóa các bản B/C cũ không xác minh được.

## Giao diện và bằng chứng

Nút Dừng của hàng đợi chuyển về thanh cố định cạnh Đang xử lý, giống
luồng một bài ở cả Chuyển đổi/Tạo giọng. Không có nút Dừng trùng ở
thanh trạng thái khi đang ở đúng công cụ; sang trang khác vẫn có Dừng
tác vụ. Dừng/tiếp tục giữ checkpoint và các bài đã xong.

Kiểm tra cấu trúc 34 PowerPoint trong Downloads, gồm 8 tên file kết
quả và 4 gói có audio; 26 file có ảnh vector, 23 có Office Math, 34 có
hiệu ứng và 23 có nhóm đối tượng. Không file nào vượt 200 MiB. Đọc số
slide theo thứ tự quan hệ trong presentation, kể cả các trang tiếp
nối có tên part khác `slideN.xml`. Không đồng nhất số part tên truyền
thống với số trang thực tế của file đã chuyển đổi.

Render mẫu ba kết quả gần đây, so sánh nguồn và dựng một ứng viên
riêng bằng cache dịch chỉ đọc. Không gọi Google, dùng key thật hay
công bố ứng viên vào thư viện. Hash các file được render giữ nguyên.
Mẫu vẫn có đoạn dịch diễn đạt chưa tự nhiên và khung dày chữ/công
thức có thể chồng nhau ở trang tiếp nối. Kết quả này không chứng nhận
mọi nội dung/slide đều đạt. Không tự thay đáp án hoặc sửa hàng loạt
PowerPoint cá nhân để che những giới hạn đó.

Các báo cáo/ảnh ở `reports/rc159`, ngoài Git. Kiểm thử dùng thư viện
riêng; không đổi bộ model, tab Cài đặt hoặc bài/giọng của giáo viên.
**1.619 pytest nguồn lõi đạt**, một cảnh báo deprecation như RC158.
133 kiểm thử liên quan đạt trước lượt nguồn lõi. Năm nhóm Qt đạt:
hàng đợi, tự lưu, chuyển đổi một bài, giọng một bài và F1; không cảnh
báo QML. Thử nút Dừng ở footer, dừng từ trang khác, khôi phục lượt,
không nhân đôi sản phẩm và vị trí giữa cụm chuyển slide. Ruff,
compileall và diff-check đạt. Hai nhóm Browser AI cũ tiếp tục nằm
ngoài phạm vi luồng đang dùng; đây không phải phép đo máy cấu hình thấp.

Việc xóa ZIP build cũ vẫn bị hệ thống thực thi chặn (`blocked by policy`),
nên chưa ghi nhận là đã dọn dung lượng các ZIP đó. Đã dọn riêng các
bản sao PPTX trung gian trong `temp` của báo cáo kiểm thử cũ, sau khi
kiểm tra từng đường dẫn và giữ nguồn, dữ liệu thật, candidate ngoài
temp, ảnh và log. Không đụng các ZIP bị chặn. Chờ giáo viên thử
bản nguồn và yêu cầu riêng trước khi tạo bộ cài.
