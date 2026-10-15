# RC34: nhận đúng kết quả và giữ công việc đã hoàn tất

## Các nguyên nhân đã xác định và sửa

- Web có thể hiển thị JSON dưới dạng văn bản kèm nhãn truy cập “ChatGPT said:”. Chỉ đọc vùng câu trả lời và nhận các nhãn vai trò cụ thể; không chấp nhận văn bản tùy ý hoặc nhiều JSON lẫn nhau.
- Số sát chữ như “tr25”, H2O, A0 chưa được khóa đầy đủ. Khóa cả số sát chữ. Checkpoint cũ chỉ được chấp nhận nếu giữ đúng số nguồn và đúng số lần xuất hiện; không bỏ kiểm tra số liệu.
- Lưu bản dịch hợp lệ ngay khi kết thúc câu trả lời, trước khi xử lý lỗi tải của nhóm khác. Kết quả nhóm có checksum có thể phục hồi cache tại máy, không dịch lại khi cache chung bị mất.
- Xác nhận yêu cầu bằng toàn bộ prompt của lượt người dùng mới nhất khi số tin nhắn không tăng do web thu gọn lịch sử. Chỉ mở rộng lượt mới nhất để không kéo trang về các prompt cũ. Vẫn từ chối trường hợp trùng/không rõ yêu cầu.
- Dùng lại tab đúng cuộc trò chuyện đã đăng nhập; không tải lại hoặc đưa tab đang làm bài về trang chủ chỉ để kiểm tra tài khoản.
- Sau hai lần làm mới thụ động, việc một lượt suy luận đang chạy chưa đổi nội dung không bị báo nhầm là mất mạng. Thông báo gián đoạn thật và giới hạn chờ vẫn được xử lý riêng, có giới hạn.
- Lượt sửa tập trung chỉ nhận các lỗi FAIL, gom theo mã lỗi/số slide. Những cảnh báo CHECK đầu bài không còn chiếm hết danh sách và làm mất lỗi thiếu tiếng Anh ở cuối bài. Không yêu cầu render/kiểm kê toàn bộ bài trong lượt sửa này.

## Nhận file khi đường tải thông thường lỗi

Luồng nhóm slide thử đường tải bình thường trước. Nếu việc truyền tệp thất bại, thử một bản xuất dữ liệu XML từ đúng kết quả đã tạo trong cùng cuộc trò chuyện; không tải lại bài gốc hoặc yêu cầu chuyển đổi lại toàn bộ bài.

Bản xuất được nén, mang qua ảnh dữ liệu PNG của giao diện web thông thường, và ghép lại tại máy. Đây là dữ liệu kỹ thuật, không phải hình minh họa hay slide cho học sinh. Không gọi API nội bộ, không lấy cookie/token, không thay đổi cơ chế xác minh của web.

Kiểm tra mã lượt nhận, checksum gói, checksum nguồn và từng XML; chỉ cho phép thay đổi XML. Hình, video, âm thanh và đối tượng nhúng gốc được giữ nguyên bytes. Từ chối sai nguồn, dữ liệu thiếu/hỏng, đổi thành phần nhị phân, đường dẫn không hợp lệ, thực thể XML ngoài hoặc liên kết thực thi mới. Ứng viên còn phải qua kiểm tra số slide/media và kiểm tra bài giảng bình thường. Không tự chứng nhận nội dung hoặc bỏ lỗi chất lượng.

Có checkpoint riêng cho lượt xuất, giới hạn theo dõi 180 giây thực tế; mất xác nhận chỉ kiểm tra đúng lượt đã gửi, không gửi lại mù quáng. File ứng viên đã xác minh được giữ để tiếp tục kiểm tra tại máy. Nếu web không xuất đúng dữ liệu thì vẫn tạm dừng rõ ràng, không giả báo hoàn tất.

## Kết quả và giới hạn thực tế

Các ca dữ liệu, Chrome mô phỏng và Qt/PowerPoint thật đã kiểm tra nhận kết quả, tiếp tục không gửi trùng, checksum, bảo toàn media, từ chối gói hỏng, phục hồi cache, lỗi tin nhắn bị thu gọn và lượt sửa chỉ tập trung vào lỗi thật. Web và đăng nhập trong các phép thử Qt là mô phỏng.

Trên Bài 6 ngày 15/10/2026: xác minh đủ 26 mục dịch và giữ 32 đơn vị nội dung đã xong; không gửi lại bài gốc. Nhận đủ gói XML của nhóm 64 slide, ghép lại được PowerPoint 40.401.075 byte, kiểm tra đúng số slide và media. Kiểm tra ban đầu vẫn có 9 slide FAIL và 55 CHECK, nên đây chưa phải bài đủ điều kiện dùng để dạy.

Sau chẩn đoán, đã chạy lại bằng đúng cơ chế nhận dự phòng mới: tự nhận gói của lượt sửa, xác minh/ghép nhóm 64 slide và tiếp tục ghép bài tại máy, không tải lại nguồn. Lần tiếp tục cuối đi qua bước nhận ở khoảng giây 103 và hoàn tất file ở giây 233. Đây là thời gian tiếp tục từ checkpoint có sẵn; **không phải** thời gian chuyển đổi cả bài từ đầu.

Đối chiếu số slide: nguồn và kết quả đều có **79 slide** (64 slide trực quan, 15 slide đi theo nhánh chữ). 32 là số đơn vị nội dung, không phải số slide. Ứng dụng RC34 đã tự nhập kết quả vào thư viện, ghi lesson_id và tiến độ 100%; thư viện có thêm đúng một bản nháp. Sau render/kiểm tra toàn bài còn **24 slide FAIL, 55 CHECK**, gồm tràn chữ, bố cục/cặp ngôn ngữ và chuỗi kỹ thuật. Voice chưa được bật cho bài lỗi. Bài chưa đạt điều kiện hoàn thiện để dạy ngay.

Phiên web từng không tải được cuộc trò chuyện/lịch sử rồi truy cập được lại. Cửa sổ thật có một khoảng không phản hồi trong bước nhập/mở bài lớn, sau đó khôi phục và hiển thị kết quả; chưa coi toàn bộ quy trình đã mượt. Chưa công bố tốc độ trọn bài, chưa bảo đảm mọi bài chạy hoàn toàn không can thiệp. Không đổi cảnh báo thành PASS để che giới hạn này.

Giữ nguyên bài nguồn, thư viện, phiên tài khoản và cấu hình. Tạo voice vẫn là bước riêng sau khi có PowerPoint, không tự tạo giọng đọc trong bước chuyển đổi.

Kiểm tra bổ sung nhận diện ký hiệu con lắc “Đ” trong hộp English đã được gắn nhãn, giữ nguyên ký hiệu nguồn thay vì bỏ toàn bộ câu tiếng Anh. Tiếng Việt hoặc tên riêng có dấu vẫn không được nhận nhầm là câu English chỉ vì nhãn hộp.

Đã thấy trực tiếp thông báo “Could not load this ChatGPT conversation”, “Unable to load history” và phản hồi 404 từ thao tác tải trang của web. RC34 phân biệt cuộc trò chuyện không mở được với hết đăng nhập; không tự gửi lại bài hoặc xoay tài khoản khi không còn truy cập được lượt đã gửi.

Kiểm chứng milestone: 71 ca dữ liệu/lời đọc, các ca Chrome trong test_browser_translation (nhận file, mất xác nhận, dữ liệu hỏng, tab đang mở, suy luận im lặng), 13 ca xác nhận/phục hồi yêu cầu, 2 ca cuộc trò chuyện không mở được/không nhầm câu trích trong bài, 4 ca nội dung trạng thái; Qt Browser AI với Office thật qua, không warning. Các lần sửa bộ chụp ảnh đã kiểm tra lại riêng ba luồng nhận/tiếp tục/từ chối ảnh hỏng trước khi đóng gói.
