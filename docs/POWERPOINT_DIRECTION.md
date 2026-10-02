# Đối chiếu hướng phát triển PowerPoint

Đối chiếu tài liệu người dùng gửi ngày 02/10/2026 với mã nguồn hiện tại. Kết luận: đúng kiến trúc hai luồng và đầu ra PowerPoint, nhưng mới hoàn thành bước nền của luồng giữ thiết kế; chưa đạt toàn bộ trải nghiệm đề xuất.

| Yêu cầu | Hiện trạng | Phần tiếp theo |
|---|---|---|
| PPTX giữ thiết kế là mặc định; tài liệu khác dùng mẫu | Bài PPTX mới có `presentation_style=source`; tài liệu khác dùng `template`. Trong editor có thể đổi. | Cho chọn rõ **Giữ bài giảng của tôi / Tạo bài với BiliClass** ngay sau chọn nguồn. |
| Giữ nguyên nguồn, xuất PPTX sửa được | Nguồn có hash, cấm xuất đè; sửa các phần XML cần thiết, giữ tài nguyên gốc. Biểu đồ bản sao có dữ liệu riêng. | Nghiệm thu bằng bài thật có animation, trigger, SmartArt, nhóm đối tượng, công thức, audio/video và liên kết ngoài. |
| Thêm chữ Anh, ưu tiên không sửa textbox đang có hiệu ứng | Hiện dùng slide Việt và bản Anh kế tiếp; trên bản Anh thay chữ trong ô có sẵn. Chế độ từ khóa có thay chữ trên bản xuất Việt. | Thêm textbox Anh khi có vùng trống và không che đối tượng; slide kế tiếp là phương án dự phòng. |
| Áp L0–L4 đúng mức hỗ trợ | Cùng dùng `presentation_content`; L2 lấy câu Anh dễ đã duyệt khi có. Ngôn ngữ hiển thị vẫn do lựa chọn layout quyết định. | Quy định riêng nội dung cần thêm cho từng level: thuật ngữ, câu lớp học, câu trọng tâm, mức cân bằng và VI Rescue; giữ quyền điều chỉnh của giáo viên. |
| Dự án `.biliclass` và PPTX là hai đầu ra | Gói schema 3 giữ nguồn, đoạn VI/EN, level/layout, trợ giảng, quiz và audio portable; có lưu cách trình bày. Xuất gói và PPTX là hai thao tác riêng. | Bổ sung thuật ngữ riêng của bài, mapping đối tượng bền vững, cấu hình giọng/mascot theo bài và liên kết bản PPTX đã tạo. Không đưa phản hồi học sinh vào gói chia sẻ mặc định. |
| So sánh gốc / song ngữ trước xuất | Xem bản song ngữ bằng PowerPoint; có chặn chữ quá dài theo ước lượng. | Thêm màn so sánh render, cảnh báo chữ tràn/chồng, thay đổi cỡ chữ và duyệt bố cục từng slide. Chưa được tuyên bố không overlap hoặc đạt cỡ chữ tối thiểu cho mọi bài. |
| Mẫu tạo thành bài dạy dùng được | Có ba kiểu dạy và 14 loại khối; dùng nội dung giáo viên đã nhập. | Thiết kế lại bằng nội dung thật theo môn; không coi file tham khảo có chỗ điền là bài đã hoàn thành. |

## Quyết định kỹ thuật

Hiện xuất bằng cách chỉnh trực tiếp gói OOXML, không lưu lại toàn bộ PowerPoint bằng `python-pptx`. `python-pptx` chỉ đọc đối tượng để ánh xạ văn bản. Cách này giữ nguyên các phần không cần sửa và vẫn xuất được khi máy không cài Office. COM đang được dùng để trình chiếu và kiểm chứng đầu ra trên máy có PowerPoint.

Tài liệu gợi ý COM cho các ca cần giữ hiệu ứng phức tạp. Nên bổ sung nhánh xử lý bằng PowerPoint trên Windows khi cần nhân bản/thêm shape và xác nhận hiệu ứng bằng Office thật; không coi COM là bảo đảm tuyệt đối cho mọi file. Cả hai nhánh phải giữ bản nguồn, dùng cùng LevelPolicy và cùng bước giáo viên duyệt.

## Thứ tự làm tiếp

1. Chọn một bài PowerPoint thật của giáo viên. Chuẩn hóa thêm lớp Anh theo L0–L4; ưu tiên chỗ trống, giữ slide kế tiếp khi slide quá kín. Giữ lựa chọn chỉ trợ giảng cạnh bản gốc cho bài đặc biệt phức tạp.
2. Làm so sánh gốc/song ngữ và xác nhận bố cục trước xuất. Kiểm tra cả Office thật và liên kết đoạn khi dùng mascot/giọng/quiz.
3. Hoàn thiện dự án `.biliclass` mở lại/đổi level; sau đó cải thiện luồng template từ nội dung thật.

## Bằng chứng hiện tại

143 bài kiểm thử đạt, kiểm tra mã đạt, Qt smoke xác nhận các điều khiển và số slide nguồn. PowerPoint trên máy phát triển mở/render bộ thử 6 slide có chữ, bảng, biểu đồ; render của 3 slide Việt giống hệt bản nguồn. Các bài kiểm thử xác nhận dữ liệu biểu đồ của bản sao độc lập, pack giữ cách trình bày và cache hỏng được tạo lại. Chưa nghiệm thu mọi hiệu ứng hay mọi tài liệu giáo viên, chưa có màn so sánh gốc/song ngữ trong app. Các tính năng này chưa nằm trong bản phát hành rc12.
