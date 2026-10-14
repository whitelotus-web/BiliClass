# Tăng tốc chuyển đổi: đề xuất ngày 14/10/2026

Đây là định hướng tiếp theo, chưa phải các tính năng chạy song song đã triển khai.

## Kết luận về dịch vụ

Ưu tiên nghiệm thu ChatGPT cho luồng nhận PowerPoint hiện tại. Gemini chưa được
nghiệm thu bằng tài khoản thật cho toàn bộ luồng và không nên được giới thiệu như
một lựa chọn tương đương đã ổn định. Đề xuất tạm ẩn khỏi luồng chuyển đổi chính,
giữ dữ liệu profile để có thể dùng lại; chưa xóa hoặc thay đổi lựa chọn của người dùng
chỉ từ câu hỏi xin tư vấn.

Gemini có thể hữu ích ở luồng dịch nội dung có cấu trúc, kiểm tra thuật ngữ hoặc
soạn câu hỏi khi BiliClass tự dựng PPTX. Canvas → Google Slides là một hướng xuất
khác, không bảo đảm giữ nguyên đối tượng, hiệu ứng và bố cục PowerPoint nguồn.
Khả năng trên một gói tài khoản phải được kiểm tra thực tế.

Tài liệu [Gemini Task](https://support.google.com/gemini/answer/17094507?hl=en)
hiện liệt kê `.pptx` trong các file có thể tạo; Task yêu cầu Pro/Ultra và các
điều kiện tài khoản/khu vực khác. Điều này không chứng minh chat thường của
mọi tài khoản Pro trả PPTX. Adapter hiện tại chưa được nghiệm thu luồng Task
thật, vì vậy không kết luận Gemini hoàn toàn không thể tạo PowerPoint.

## Thay đổi đáng ưu tiên

1. **AI xử lý ngôn ngữ, BiliClass xử lý file.** Trích văn bản theo ID slide/shape,
   giữ công thức, media và quan hệ trong PPTX gốc trên máy. Gửi nội dung và ngữ cảnh
   cần thiết, nhận bản dịch theo ID; dựng hoặc ghép bản dịch vào một bản sao. Đây là
   một luồng mới cần kiểm thử, không thay ngay luồng nhận PPTX đang có.
2. **Chia nội dung theo độ phức tạp.** Thử cụm 5–10 slide, kèm thuật ngữ và ngữ cảnh
   chung; chỉ là điểm khởi đầu để đo. Tránh chia cơ học file PPTX rồi ghép các file
   do AI tạo độc lập: có thể đứt master, theme, animation và quan hệ media.
3. **Tối đa hai cụm song song trong thử nghiệm đầu tiên.** Một tab/cuộc trò chuyện
   riêng cho mỗi cụm, đánh dấu ID và lưu checkpoint; ghép theo ID gốc, không theo thứ
   tự hoàn tất. Thử cùng tài khoản trước và chỉ dùng nhiều tài khoản đã được phép nếu
   cần; không dùng đổi tài khoản để vượt giới hạn dịch vụ. Nhiều tab không tạo thêm
   năng lực xử lý của phía dịch vụ và có thể tăng lỗi, nên chưa mặc định bật.
4. **Cache bản dịch theo nội dung + cấu hình + thuật ngữ.** Chỉ làm lại phần thay đổi;
   thiếu bản dịch, sai ID, mất số/công thức hoặc cặp VI/EN phải bị phát hiện. Không coi
   các slide chỉ dịch tiêu đề là hoàn thành. Không suy đoán chữ trong ảnh khi chưa đọc được.
5. **Dựng và kiểm tra tại máy.** Bảo toàn file gốc; áp dụng quy tắc bố cục riêng cho
   bốn kiểu song ngữ. Chỉ gửi lại các phần cần sửa, không lặp cả bài. Việc giữ nguyên
   thiết kế và việc chia hai cột cần được kiểm tra bằng render, không chỉ kiểm tra XML.
6. **Voice là bước tùy chọn sau khi lưu bài.** Tải PPTX dùng được trước; giọng đọc
   tận dụng cache và tài nguyên máy, không chặn thời gian nhận bài song ngữ.

## Điều kiện nghiệm thu

Đo trên cùng tài liệu gốc, cấu hình, tài khoản và máy: tổng thời gian, thời gian tải,
biên soạn, nhận file, kiểm tra và voice riêng; số lần sửa; slide thiếu dịch; tràn/chồng
chữ và sai công thức. So sánh luồng hiện tại, chia cụm tuần tự và hai cụm song song.
Chỉ mặc định bật phương án mới nếu nhanh hơn mà không giảm chất lượng. Chưa có số đo
để hứa nhanh gấp 2–3 lần hay bảo đảm mọi môn học hoàn thành bằng một lượt gửi.

Tham khảo: [Google Canvas](https://support.google.com/gemini/answer/16047321?hl=en),
[tạo file trong Gemini](https://blog.google/innovation-and-ai/products/gemini-app/generate-files-in-gemini/),
[nguyên tắc giảm độ trễ của OpenAI](https://developers.openai.com/api/docs/guides/latency-optimization).
Tài liệu OpenAI này nói về API; các nguyên tắc giảm việc AI phải làm/chạy song song là
tham khảo thiết kế, không phải cam kết về tốc độ hoặc hạn mức ChatGPT web.
