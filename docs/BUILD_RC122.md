# RC122 — Phím Mascot, cấu hình giọng và thêm giọng Anh

## Giao diện

- Đổi tên vùng phím thành **Phím tắt Mascot**. Hai nhóm Giọng đọc và
  Di chuyển/âm lượng chia đều chiều rộng, cùng hàng tiêu đề. Màn hẹp
  xếp dọc. Hướng dẫn nằm dưới từng nhóm; nút khôi phục/lưu đặt cạnh
  nhau bên phải. Giữ nguyên cách gán và lưu phím.
- Hướng dẫn khi rê dấu hỏi ở bảng trợ giảng dùng cửa sổ tooltip riêng,
  ưu tiên phía trên bảng. Nếu sát mép trên không đủ chỗ, đặt bên cạnh
  trong vùng màn hình khả dụng. Không tăng kích thước bảng hay che nút.
- Bỏ “· chọn một” ở Kiểu chuyển đổi. Hai nút chỉ ghi **Xem mẫu**, căn
  phải trong từng lựa chọn; giữ nút ở hàng tiêu đề khi dùng bố cục gọn.
- Thêm tiêu đề **Cấu hình tạo giọng đọc**, giữ dòng Giọng đọc và ngôn
  ngữ phía dưới. Nhóm chọn ngôn ngữ/vị trí loa được căn giữa với khoảng
  cách vừa đủ; màn hẹp xuống hàng, không dãn hai nhóm về hai mép.
- Nút nghe riêng tiếng Việt/Anh và Nghe cả cặp chuyển thành biểu tượng
  pause + **Dừng** trong lúc chuẩn bị/phát. Bấm sẽ hủy/dừng và trở lại
  nhãn nghe thử; hết âm thanh cũng trở lại. Chỉ nút của yêu cầu hiện tại
  đổi trạng thái, đổi ngôn ngữ sẽ dừng yêu cầu cũ. Bỏ nút Dừng nghe riêng.
  Nút đang phát vẫn dừng được nếu nội dung ô mẫu vừa bị xóa.
- Thư viện chỉ dùng Chưa có giọng/Có giọng Anh/Có giọng Việt/Có giọng
  Việt + Anh sau khi kiểm tra. Bản chưa đủ được gộp vào Chưa có giọng,
  màu xám; bản đủ màu xanh lá. Kiểm tra nền vẫn có nhãn tạm riêng.
  Bộ lọc cùng quy tắc hợp các ngôn ngữ đủ, bỏ lựa chọn chưa hoàn tất.

## Giọng và giữ dữ liệu cũ

Thêm Nicole, Sarah, Kore, Fenrir, Puck, nâng danh sách lên 8 giọng Mỹ.
Dùng model/voices.bin hiện có, không tải thêm model. SID đối chiếu với
[tài liệu chính thức sherpa-onnx](https://k2-fsa.github.io/sherpa/onnx/tts/all/Chinese-English/kokoro-multi-lang-v1_0.html).
Chọn các giọng bổ sung dựa trên loại giọng và thông tin chất lượng của
[tác giả Kokoro](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md);
ghép cặp là gợi ý để giáo viên nghe/chọn, không phải xếp hạng khách quan.

9 gợi ý đa dạng hơn; mọi ID cặp cũ, ánh xạ người đọc và phiên bản cache
giữ nguyên. Có thể tự ghép 9 giọng Việt với 8 giọng Anh. Năm WAV nghe thử
mới là câu mẫu công khai cố định, được tạo tại máy và kiểm SHA256 trong
manifest; không chứa bài, giọng hay nội dung cá nhân của giáo viên.

Khi vào cấu hình, nếu kiểm tra nền phát hiện mất WAV ở bản đã hoàn tất
trước đó, tool tạo tiếp đúng cấu hình đã lưu, dùng lại WAV còn hợp lệ.
Không tự chạy lại tác vụ đã bị hủy/thất bại hoặc nội dung đã đổi; các
trường hợp đó vẫn tạo tiếp bằng nút tạo giọng. Chưa báo có giọng cho
ngôn ngữ khi mới tạo một phần. Giữ cơ chế phục hồi dấu nguồn cũ.

## Kiểm tra

280 pytest liên quan đạt bằng `.venv`: mọi cặp/ngôn ngữ, định tuyến/cache
cũ, nghe mẫu không tải model, hủy yêu cầu chậm, lưu cấu hình, phục hồi
WAV mất, bộ lọc trạng thái, phiên dạy và bộ nhớ đệm đã có.
Qt thật kiểm bố cục sáng/tối 1080/1366/1920, phóng/thu cửa sổ, cỡ hiển
thị 100%/150%, click lưu/khôi phục phím, nhóm giọng căn giữa và 48 bố
cục chuyển đổi. Mẫu 8 giọng/9 gợi ý phát qua điều khiển thật với playback
được chặn trong thư viện thử; play/stop/hết âm thanh và lưu cặp đạt.
Tooltip được đo bằng tọa độ cửa sổ native, gồm vị trí dưới và sát mép
trên màn hình. Các phép kiểm không mở/đóng bài riêng của giáo viên.
Không có cảnh báo QML ở các lần kiểm đạt.

## Gói

Nguồn `1.0.0rc122`; dựng một lần sau commit đã kiểm, dùng runtime/model
RC121 có manifest SHA256. Gói, model và báo cáo không đưa vào Git.
Commit nguồn `98217240533cab351a1e505b013f0e5d0dc47006`.
Gói `dist/rc122-shortcut-layout/BiliClass-RC122-Windows.zip`,
1.255.953.933 byte, SHA256
`5a571fc623afa8dbeec2f50b273d727a22de2a8794fde0d943c36efdfecc8893`.
Manifest xác minh 4.667 file; 54 file QML/qmldir khớp commit nguồn.
Smoke bản đóng gói 1920×1080 đạt, không có cảnh báo QML.

Cài vào `F:/Applications/BiliClass/1.0.0rc122`, mở từ Explorer, có cửa sổ
chính và Mascot hoạt động độc lập với Codex. Kiểm sau cài xác nhận giữ
nguyên bài/nguồn, 1.066 WAV cá nhân, logo, API key mã hóa và lựa chọn
giọng; không đóng PowerPoint hay phiên BiliClass cũ độc lập.
