# Rà soát giọng đọc RC100

Phạm vi: lựa chọn, nghe thử, lưu mặc định, tạo bản giọng, dùng lại WAV,
tải PowerPoint/audio và phát khi dạy. Tách xác minh kỹ thuật khỏi đánh
giá độ tự nhiên bằng nghe thực tế.

| Luồng | Kết quả kiểm chứng |
| --- | --- |
| Chọn cặp gợi ý/tự ghép | 9 cặp gợi ý; 9 Việt × 3 Mỹ = 27 cặp. Thứ tự vùng/giới và cặp bổ sung giữ đúng. |
| Nghe thử | Mẫu dài riêng Việt/Anh; nghe cặp theo hai người đọc. Nghe thử không tự lưu. Hủy không phát kết quả muộn. |
| Lưu mặc định | Lưu giọng/tốc độ cho lần tạo mới; không thay WAV hay bản giọng của bài đã tạo. |
| Ba lựa chọn tạo | Anh, Việt, cả hai. Cả hai tạo hai loa độc lập, không thêm nút phát cả hai. Kiểm thử đủ 27 × 3 lựa chọn. |
| Phiên bản giọng | Cache gắn nội dung, người đọc, engine và tốc độ. Bản cũ còn dùng được; giọng thiếu/sai chữ không được báo hoàn tất. |
| Mở/tải bài | Mở không tự tạo giọng. Chọn bản đã lưu, xác minh WAV khi xuất; nguồn không bị ghi đè. |
| Mascot/PowerPoint | Kiểm tra phát, tạm dừng, tiếp tục, đổi slide, ngôn ngữ có/không có giọng, từ chối phát trễ sau đổi slide. |
| Xem trước | Worker Office còn gắn nhưng không trình chiếu không chặn xem trước. Đang trình chiếu/đang khởi động vẫn được bảo vệ. |

RC100 sửa việc quét lại toàn bộ PowerPoint khi lần kiểm tra trước
không có nhãn OCR. Kết quả âm tính cũng được ghi nhớ; không đổi
người đọc, model, tốc độ hay khóa WAV của bài hiện có.

Tên tải từ thư viện dùng cùng chính sách chọn bản giọng đã sẵn sàng
với tệp xuất thực tế. Một lựa chọn hiện tại chưa đủ giọng không làm
tên tải mất nhãn Voice khi bài vẫn có bản hoàn chỉnh đã lưu khác.

Bằng chứng local (không đưa vào Git): kiểm thử pytest, Qt cặp giọng,
Qt phiên dạy với PowerPoint thật và kiểm tra gói cài. Fixture âm thanh
im lặng xác minh vận hành; tự kiểm tra trong gói dùng engine thật.
Việc mô hình phát âm tự nhiên với mọi thuật ngữ, công thức và câu
chưa được xác nhận. Chưa chứng nhận thao tác click loa vật lý trên
mọi máy/PowerPoint; các kiểm tra tự động dùng control Qt và API Office.

Đọc từng đoạn theo cấu trúc là chức năng riêng trong
`PLAN_SEGMENT_PLAYBACK.md`, chưa triển khai trong RC100. Đoạn trong
ảnh chưa được OCR đầy đủ cũng chưa trở thành lời đọc đầy đủ chỉ nhờ
đổi giọng; phải giải quyết mức bao phủ nội dung trước.
