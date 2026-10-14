# Chuyển đổi theo nhóm nội dung — RC32

Yêu cầu mới ở chế độ giữ PowerPoint gốc với ChatGPT tự phân loại slide trước
khi gửi. Bài đang dở từ bản cũ tiếp tục theo bản ghi cũ, không gửi lại để đổi
cơ chế. Giữ model/suy luận cao nhất tài khoản thực sự cho phép; không thêm API
key, không dùng nhiều tài khoản để vượt hạn mức.

- Slide có hộp chữ thông thường và đủ diện tích: gửi văn bản theo ID slide,
  đối tượng và đoạn. Nhận JSON có đủ bản dịch; khóa số liệu, run công thức/
  chỉ số, phát hiện thiếu/lặp ID và kết quả sai. BiliClass dựng bản sao tại máy.
- Slide có chữ phụ thuộc ảnh, sơ đồ, hiệu ứng hoặc hộp chữ chật: dùng luồng
  xử lý PowerPoint trực quan. Không coi văn bản trích được là toàn bộ nội dung.
  Tài khoản Free/chưa xác định gói gửi một nhóm đính kèm để hạn chế số lần
  tải tệp; gói trả phí chia tối đa tám slide mỗi nhóm.
- Chạy tối đa hai nhóm độc lập trong cùng profile, ghép theo vị trí nguồn,
  không theo thứ tự trả kết quả. Nếu ô soạn chưa sẵn sàng trước khi gửi nhóm
  thứ hai, giảm còn một nhóm. Giới hạn lượt sử dụng của web vẫn áp dụng.
- Video/âm thanh lớn được thay bằng media nhẹ hợp lệ trong bản gửi; ảnh kiến
  thức giữ nguyên. File gốc không đổi. Khi nhận kết quả, kiểm tra đối tượng
  media còn tồn tại rồi ghép lại đúng byte video/âm thanh gốc. Nếu AI bỏ media,
  thiếu slide hoặc trả bản chưa đủ nội dung, yêu cầu sửa tối đa một lượt trong
  đúng cuộc trò chuyện. Không tiếp tục lặp cả bài vô hạn.
- Bản dịch đã nhận và nhóm PowerPoint hoàn tất có checksum/checkpoint riêng.
  Tiếp tục tác vụ dùng lại kết quả đó. Lượt gửi chưa xác nhận phải được đối
  chiếu; không tự gửi lại vì chưa thấy câu trả lời. Chỉ sửa JSON lỗi tối đa một
  lượt; hết khoảng chờ giữ lại các phần đã làm.
- Ghép tài nguyên, master, notes và slide bằng quan hệ gốc; ID master/layout
  phải duy nhất. Giữ master ghi chú của bài gốc. Đối tượng phụ nằm ngoài trang
  và không có hiệu ứng được giữ nguyên, không kéo vào nội dung hoặc lời đọc.
- Render và đo tràn chữ bằng PowerPoint tại máy. Cache từng slide chỉ được dùng
  lại khi cả phụ thuộc theme/hình, môi trường Office/font và checksum ảnh khớp.
  Đổi notes vẫn kiểm tra lời đọc/nội dung mới; không dùng cache để tự duyệt bài.
- Lưu bài song ngữ trước. Voice là bước tiếp theo do giáo viên chọn.

Các kiểu mẫu mới/nguồn không phải PPTX dùng prompt rút gọn nhưng vẫn nhận
PowerPoint theo luồng hiện có. Gemini giữ adapter hiện tại; luồng JSON mới
chưa được nối với Gemini. Gemini có thể đảm nhiệm dịch văn bản trong kiến
trúc này mà không cần xuất PPTX, nhưng cần kiểm thử adapter trước khi bật.

Không cam kết mọi bài hoàn thành trong 1–2 phút hoặc giữ bố cục 100%. Nhiều
tab không bảo đảm phía dịch vụ nhanh hơn; bài nhiều ảnh/hiệu ứng vẫn cần
xử lý trực quan. Cloudflare, đăng nhập, hạn mức và dịch vụ không trả file vẫn
có thể cần người dùng xử lý. Không đánh dấu nội dung đạt chỉ vì file mở được.

Tham khảo tài liệu người dùng gửi: lấy ý tưởng tách dịch ngôn ngữ khỏi dựng
file; không dùng nguyên ví dụ ghi đè `paragraph.text`, ký tự Markdown để tạo
chữ nghiêng, model/SDK cũ hoặc dịch vụ API khác cấu hình hiện có.
