# Lớp học, kết quả và mascot — RC57, 17/10/2026

## Cách sắp xếp sau tối ưu

Thanh bên còn Trang chủ, Chuyển đổi bài giảng, Bài giảng, Lớp học, Cài đặt.
Trang chủ là bảng làm việc: bài đang mở/bài gần đây, tác vụ đang xử lý, mở thư
viện, chuyển đổi tài liệu và vào lớp. Không lặp hướng dẫn bốn bước thành một
khối giới thiệu lớn. Thống kê dịch vẫn là số ghi nhận cục bộ, không phải số dư
Google Cloud.

**Kết quả lớp học** nằm ngay trong Lớp học. Giữ chức năng báo cáo vì đây là
đầu ra của tiết tương tác; không cần một mục riêng trên thanh bên.
**Thuật ngữ & kiến thức** chuyển vào Cài đặt → Dữ liệu → Quản lý thuật ngữ &
kiến thức. Không xóa dữ liệu hoặc khả năng dùng thuật ngữ khi dịch.

## Lớp học thực hiện được những gì?

Đây là lớp hỏi đáp nội bộ, không phải hệ thống quản lý trường, danh sách học
sinh theo tên hay nơi phát file PowerPoint cho từng em. Trình chiếu/giọng đọc
vẫn dùng được độc lập, không cần mở lớp tương tác.

| Phần | Cách hoạt động |
| --- | --- |
| Bài giảng | Chọn bài trong thư viện; kiểm tra, duyệt và chốt phiên bản hiện tại. Sửa nội dung hoặc câu hỏi thì cần chốt lại. |
| Câu hỏi | Soạn và duyệt câu trắc nghiệm một đáp án, Đúng/Sai hoặc khảo sát. Bấm Soạn câu hỏi mở đúng tab ngay trong màn Lớp học. |
| Danh tính | Chọn ẩn danh hoặc số chỗ ngồi. Không yêu cầu tài khoản học sinh. Số chỗ không trùng; không tương đương danh sách tên chính thức. |
| Mạng | Giáo viên chọn IPv4 Wi-Fi/LAN để điện thoại cùng mạng truy cập. 127.0.0.1 chỉ thử trên máy giáo viên. |
| Tham gia | Máy giáo viên mở máy chủ cục bộ và QR/link. Học sinh quét QR bằng trình duyệt, nhập số chỗ nếu được yêu cầu. |
| Điều khiển | Giáo viên chọn câu, thời lượng 5–3600 giây và ngôn ngữ Việt, Anh hoặc Việt–Anh. |
| Trả lời | Điện thoại nhận câu hỏi qua WebSocket. Một người có một đáp án hiện hành; được đổi trước khi hết giờ/đóng câu. |
| Công bố | Đóng nhận trả lời trước, rồi Hiện đáp án. Đáp án/giải thích không được gửi sớm cho học sinh. |
| Hỏi lại | Tạo lượt mới của cùng câu; kết quả lần đầu vẫn giữ riêng để đối chiếu. |
| Kết thúc | Ngừng nhận trả lời, chọn sẵn báo cáo của tiết vừa kết thúc; xem/xuất tại Kết quả lớp học. |

Sĩ số cấu hình 1–200 là giới hạn phần mềm, không phải cam kết đã đo 200 thiết
bị thật. Không cần Internet cho hỏi đáp nội bộ; các máy vẫn phải liên lạc được
với nhau. Firewall, mạng khách hoặc Wi-Fi cô lập thiết bị có thể chặn truy cập.
Tool không tự thay cấu hình mạng của trường.

## Một lượt dùng từ đầu đến cuối

1. Mở **Lớp học**, chọn bài → **Dùng bài này**.
2. Bấm **Soạn câu hỏi**, nhập Việt/Anh, lựa chọn, đáp án/giải thích và duyệt.
   Câu hỏi gắn với phần nội dung đang chọn. Muốn gắn phần khác, chọn đoạn
   trong trình biên tập trước. Chưa có cơ chế tự hiểu mọi câu hỏi trong ảnh.
3. Bấm **Kiểm tra và chốt bài**. Nội dung chưa được duyệt không tự được duyệt
   bởi thao tác mở lớp. Giọng đọc không phải điều kiện bắt buộc để hỏi đáp.
4. Điền tên lớp/tiết, chọn chế độ/sĩ số và đúng mạng. Bấm **Mở lớp · Hiện QR**.
5. Cho điện thoại cùng mạng quét QR. Bấm **Thử trên máy** nếu cần tự kiểm tra.
   Con số “đã tham gia” đếm người từng vào tiết, không phải số đang trực tuyến.
6. Chọn câu, thời lượng, ngôn ngữ → **Mở câu hỏi**. Màn giáo viên có đếm ngược
   và số phản hồi theo lựa chọn; học sinh thấy lựa chọn của mình đã được nhận.
7. **Đóng nhận trả lời** → **Hiện đáp án** → câu tiếp theo hoặc Hỏi lại câu này.
8. **Kết thúc và lưu kết quả** → **Kết quả lớp học** → xuất CSV nếu cần.

Không có câu hỏi đã duyệt vẫn mở được tiết, nhưng học sinh chưa có nội dung
để trả lời và báo cáo không có kết quả kiểm tra. Nếu chỉ chiếu slide thì vào
bài giảng → Dùng để dạy là đủ.

## Mất kết nối và mở lại

- Trình duyệt thử kết nối lại; đáp án gửi lại cùng mã không bị tính hai lần.
- **Tạm đóng máy chủ** giữ tiết ở trạng thái có thể mở tiếp. Vào Kết quả lớp
  học, chọn tiết chưa kết thúc và mạng → Mở lại tiết học.
- Mở lại dùng bản câu hỏi đã chụp tại lúc mở tiết. Sửa bài trong thư viện không
  âm thầm đổi câu/đáp án của tiết đang diễn ra.
- Nếu IP/cổng đổi, dùng QR mới; học sinh dùng mã khôi phục cá nhân hiển thị
  trên trang của mình để lấy lại đúng chỗ. Không chia sẻ mã riêng này.
- Tiết đã kết thúc không mở lại để nhận câu trả lời; tạo tiết mới.

## Kết quả lớp học dùng để quyết định điều gì?

Mỗi tiết lưu câu hỏi, lựa chọn, số đã/chưa trả lời, phân bố đáp án và lượt hỏi
lại. Có tìm theo lớp/bài/môn, lọc đang mở/đã kết thúc, mở bài gốc, xuất CSV tổng
hợp hoặc CSV từng phản hồi. CSV không chứa mã bí mật kết nối học sinh.

Ví dụ: 40 người đủ điều kiện, 30 trả lời, 24 đúng thì **tham gia 75%** và
**đúng 80% trong số đã trả lời**. Không nói 80% cả lớp hiểu bài. Khảo sát
không chấm đúng/sai. Hỏi lại cùng câu không được gộp với lần đầu như hai phép
đo độc lập. Nhóm người trả lời thay đổi thì không suy ra tiến bộ cá nhân.

Nhận xét nâng cao được thu gọn. Hệ thống chỉ phân loại chủ đề khi đủ số câu/
người; đối chiếu Việt/Anh cần các cặp tương đương do giáo viên gắn nhãn cùng
điều kiện tham gia. Đây là gợi ý quan sát, không phải điểm học bạ hoặc đánh giá
chính thức. Chuyển đổi/tạo giọng đơn thuần không tạo kết quả học sinh.

## Có cần giữ Thuật ngữ & kiến thức?

Nên **giữ cơ chế và dữ liệu, ẩn màn quản lý khỏi điều hướng chính**.

- Thuật ngữ đã khóa của đúng môn được áp dụng khi chuyển ngữ Google. Cách
  dịch đã chọn và môn nằm trong khóa cache của những câu có dùng thuật ngữ.
- Kiến thức có nguồn dùng tra cứu và chọn từng gợi ý đưa vào kho của giáo viên;
  không tự coi mọi gợi ý là đúng hay tự ghi đè bài giảng.
- Không cần mở màn này mỗi lần chuyển đổi. Chỉ truy cập để sửa cách dùng từ,
  thêm thuật ngữ riêng, kiểm tra nguồn hoặc cập nhật gói dữ liệu.
- “Dùng bên trong” không có nghĩa là một AI khác chạy liên tục ở nền. Thuật
  ngữ được lấy trong lượt dịch; ẩn tab không hứa hẹn tăng tốc tổng hợp giọng.

## Mascot đang làm gì, và gắn bài thế nào?

Mascot là bảng điều khiển nổi cho bài đang trình chiếu. **Không cần khóa bài
vĩnh viễn**: mở bài → Dùng để dạy → xác nhận mở PowerPoint; mascot đi cùng
phiên đó và hiện tên bài/slide. Đóng phiên hoặc đổi sang bài không khớp thì
khóa các thao tác dạy. Đổi môn xem trước chỉ đổi phụ kiện, không chọn bài.

| Chức năng | Điều kiện và giới hạn |
| --- | --- |
| Mở/ẩn/di chuyển | Cùng nút thanh bên bật/tắt; kéo thả, nhớ vị trí, Về góc, Escape thu gọn/ẩn. |
| Nhân vật | Milo/Lumi, kích thước, góc, giảm chuyển động và phụ kiện theo môn/tự theo bài hoặc môn cố định. |
| Điều khiển slide | Trước/Sau/Theo slide của đúng phiên PowerPoint; không tự đổi nội dung bài khác. |
| Đọc Anh | Đọc các đoạn tiếng Anh đã xác minh và đang hiện; bỏ vùng ẩn/hiệu ứng chưa xác định. |
| Đọc Việt | Đọc phần Việt có cặp Anh đang hiện đã xác minh; không đọc ghi chú của đáp án còn ẩn. |
| Đọc chung | Việt rồi Anh theo phần nội dung phù hợp; chỉ khi bản giọng có cả hai ngôn ngữ. |
| Điều khiển giọng | Dừng, tạm dừng/tiếp tục, đọc lại; đổi/đóng slide dừng lời cũ. |
| Giải thích/ví dụ/gợi mở/Việt | Hiển thị nội dung trợ giảng đã chuẩn bị, duyệt và gắn với đoạn đang chiếu; không phải chatbot tự tạo đáp án tức thời. |

Các nút trợ giảng và chuyển slide nay cũng khóa khi chưa có trình chiếu đúng
bài. Trang trống/không gắn nội dung không được dùng câu trả lời của đoạn cũ.
Hình mascot có trạng thái/chuyển động nhẹ; không phải hoạt hình khẩu hình
theo âm thanh. Độ đẹp của bộ phụ kiện hiện tại chưa được thay bằng bộ vẽ mới
trong mốc này.

## Đã kiểm chứng và giới hạn bằng chứng

- 59 test liên quan qua: lớp học, lời đọc, điều kiện chuẩn bị, kiến thức,
  thuật ngữ và quy trình; có một cảnh báo deprecation của thư viện thử HTTP.
- Qt thật: tạo lớp qua nút UI → máy chủ riêng → học sinh trả lời bằng WebSocket
  → đóng/công bố → ngắt/mở lại giữ đáp án → kết thúc/xuất hai CSV; giữ câu đang
  chọn qua các lượt cập nhật; lỗi mở mạng được báo và có thể thử lại.
- Qt Trang chủ có/không có bài ở 1080×700/1366×850; quản lý thư viện, kho nâng
  cao và thao tác mascot. Không QML warning trong các lượt đã kiểm.
- 50 kết nối học sinh mô phỏng loopback trên máy này: 50 phản hồi, 35 đúng,
  kết quả 70%; gửi trùng/kết nối lại và khởi động lại giữ dữ liệu. ACK p95
  khoảng 195 ms, tối đa 202 ms trong lần đo; không phải cam kết tốc độ Wi-Fi.
- PowerPoint thật với bài thử 3 slide: mở từ Dùng để dạy, mascot nổi/kéo/đọc
  giọng Anh đã lưu, theo slide, dừng khi đổi/đóng, trang trống không đọc lại
  lời cũ, mở lại phiên được. Hai bản nguồn không bị thay đổi.
- Chưa thử một lớp điện thoại thật qua Wi-Fi trường, 200 thiết bị hoặc Windows
  sạch. Kiểm tra hiển thị/trạng thái không chứng nhận mọi phát âm/ngữ nghĩa.

Thư viện giáo viên, kết quả học sinh, WAV, key và báo cáo thử riêng không đưa
vào kho mã nguồn. Dữ liệu lớp học lưu tại máy giáo viên; ứng dụng không tự gửi
báo cáo cho người khác.
