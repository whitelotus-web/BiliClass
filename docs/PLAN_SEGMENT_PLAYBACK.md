# Đề xuất: đọc liên tục hoặc đọc từng đoạn khi dạy

Trạng thái: kế hoạch, chưa thay đổi hành vi phát trong RC97.

## Cách dùng

Giữ hai loa Anh/Việt để đọc liên tục phần đã hiện, theo cơ chế ghi nhớ
phần đã đọc. Bấm lại khi đang phát để tạm dừng, bấm nữa để đọc tiếp.
Thêm khoảng nghỉ mặc định khoảng 700 ms giữa hai đoạn nội dung, khoảng
1.000 ms sau tiêu đề. Không chèn khoảng nghỉ này sau mỗi dấu chấm hoặc
giữa các tệp nhỏ vốn thuộc cùng một đoạn.

Cạnh mỗi loa có nút đọc từng đoạn, hiển thị ví dụ **Đoạn 1/3**. Bấm sẽ
đọc trọn một đoạn rồi tự dừng; nút chuyển sang **Đoạn 2/3**. Số đếm là
nhóm nội dung, không phải số tệp WAV hoặc số câu. Giữ nút đọc lại đoạn
hiện tại và có phím tắt cho thao tác đọc đoạn tiếp. Chưa ấn định bố trí
cuối cùng trước khi thử kích thước bảng Mascot nhỏ/vừa/lớn.

Anh và Việt có tiến độ riêng nhưng cùng ánh xạ nhóm nội dung: Việt 1 →
Anh 1 → Việt 2 → Anh 2. Bắt đầu ngôn ngữ khác dừng nguồn phát trước để
không chồng tiếng. Tạm dừng giữa một đoạn vẫn tiếp tục đúng vị trí;
đọc lại là thao tác riêng. Hai loa trên slide dùng chung trạng thái với
Mascot. Không tạo loa thứ ba cho cả hai ngôn ngữ.

## Xác định một đoạn

- Dựa vào đối tượng PowerPoint, paragraph, cấu trúc gạch đầu dòng, nhóm
  đối tượng, loại tiêu đề/nội dung/chú thích và mốc hiệu ứng.
- Tiêu đề là nhóm riêng; một mục nội dung tự nhiên là một nhóm, dù có
  nhiều câu. Không tách vì xuống dòng khi hết chiều rộng hoặc vì một
  dấu chấm trong số thập phân, viết tắt, công thức.
- Cột Việt và Anh cùng ý được ghép bằng dấu nguồn/locator từ chuyển đổi,
  không ghép theo văn bản gần giống hoặc vị trí thứ n một cách mù quáng.
- Nhãn ngắn, đơn vị và chú thích gắn với đối tượng tương ứng; bảng đọc
  theo hàng hoặc nhóm dữ liệu, không theo thứ tự rời rạc của từng ô.
- Chỉ các nhóm đã hiện mới đủ điều kiện đọc. Hiệu ứng hiện một phần
  nhóm thì chỉ phần đã xác nhận hiện được đưa vào hàng đợi. Không tự
  cho hiện chữ, không làm Trước/Sau thành nút chuyển đoạn âm thanh.
- Mỗi nhóm có ID ổn định; một nhóm dài có thể dùng nhiều WAV kỹ thuật
  nhưng nút đọc đoạn chỉ tự dừng sau toàn bộ nhóm.

Không thể bảo đảm suy luận ý nghĩa hoàn hảo với mọi PPTX tùy ý. Khi thiếu
dấu nguồn, dùng cấu trúc paragraph/shape xác định được; tuyệt đối không
đoán điểm cắt trong WAV theo dấu chấm hay khoảng im lặng. Có thể bổ sung
thao tác gộp/tách nhóm trong bước kiểm tra lời đọc cho trường hợp khó,
không bắt giáo viên cấu hình lại mỗi lần trình chiếu.

## Bản đã tạo

Ưu tiên dùng nguyên WAV cũ và ranh giới segment đã lưu. Với một WAV cũ
chứa nhiều nhóm mà không có thông tin thời gian, chưa thể hứa đọc chính
xác từng nhóm. Giữ phát liên tục cho bản đó; tính năng đoạn chính xác
cần bản tạo mới có chỉ mục hoặc thao tác tạo lại do giáo viên chọn.
Không tự tạo lại âm thanh, đổi người đọc hoặc sửa nguồn bài cá nhân.

## Thứ tự triển khai và kiểm chứng

1. Lập chỉ mục nhóm Việt/Anh ổn định từ slide và metadata, tách khỏi
   speech_chunks dùng cho engine/cache. Kiểm tra mẫu tiêu đề, hai cột,
   bullet nhiều câu, paragraph nhiều dòng, bảng, công thức và nhóm ảnh.
2. Bổ sung hàng đợi có nghỉ giữa nhóm và chế độ tự dừng cuối nhóm.
   Ghi tiến độ theo từng nhóm hoàn tất, từng ngôn ngữ; không đánh dấu
   cả lượt là đã đọc khi mới xong một phần.
3. Thêm điều khiển nhỏ trên Mascot và phím tắt, dùng chung một bộ phát
   với loa trên slide. Khóa chống bấm lặp tạo nhiều lượt phát.
4. Thử đúng kịch bản ba đoạn đã hiện, hiện thêm bằng hiệu ứng, đổi ngôn
   ngữ, dừng giữa đoạn, nghe lại, lùi bước, đổi slide và thoát trình chiếu.
   Kiểm tra cả WAV riêng và media nhúng, thư viện cũ và kích thước Mascot.
