# RC123 — Xem trước nguồn và nội dung theo mẫu

## Thay đổi

Nút Xem trước slide bên Chuyển đổi mở vùng xem ngay trong trang, cùng
cách trình bày với bên Tạo giọng đọc. Có trước/sau, số trang và Ẩn xem
trước; bỏ hộp ảnh đơn có nút Close. Chọn hoặc hủy tệp thu vùng xem lại.
Việc tải trang chạy nền, yêu cầu mới hủy/bỏ kết quả cũ. Dùng lại PNG đã
xác minh theo hash tệp, môi trường Office và ngày render; dựng kèm hai
trang lân cận. Tệp thay đổi trong lúc đọc không được trả ảnh cũ.

Đọc nội dung mẫu theo hàng với dung sai tọa độ nhỏ, tránh đáp án B đứng
trước A do sai số nhập PowerPoint. Khi có hai hộp đáp án chồng khít,
chỉ lấy hộp phía trên có nền đục như PowerPoint hiển thị; giữ cả hai
nếu hộp trên trong suốt. Không suy đoán đáp án đúng. Giữ số mũ từ run
superscript, phần đơn vị/dấu câu bên ngoài XML công thức. Công thức
độc lập cạnh hình được đưa sang trang công thức để tránh co quá nhỏ.
Không thêm trang cảm ơn khi trang cuối nguồn đã có lời cảm ơn.

Google nhận được thuật ngữ, giá trị và đơn vị đọc được trong vùng HTML
không dịch; nhãn định danh nằm trong thuộc tính HTML. Trước đây mã
ẩn thay cả từ và số làm mất ngữ cảnh và đôi lúc đảo trật tự câu.
Giữ kiểm tra đủ/đúng nhãn, phục hồi chính xác nội dung đã khóa và kiểm
số liệu. Công thức XML vẫn dùng mã riêng. Cache phiên bản mới tách khỏi
kết quả cũ; không xóa dữ liệu hay tự dịch lại bài đã lưu.
Tham khảo [Google Basic HTML](https://docs.cloud.google.com/translate/docs/basic/translating-text)
và [quy tắc không dịch](https://cloud.google.com/translate/faq).

## Xác minh

- 120 pytest liên quan đạt bằng `.venv`: chuyển đổi Google, thuật ngữ,
  số liệu/đơn vị, mất/trùng nhãn, cache cũ, nội dung/ảnh/công thức của
  mẫu và hàng đợi xem trước. Sau chỉnh guard cuối, 49 test liên quan đạt.
- Qt thật: nút/thumbnail mở vùng xem, trước/sau, chặn hai đầu, ẩn, hủy
  tệp; ba cỡ 1080/1366/1920, sáng/tối, 100% và 150%, không cảnh báo
  QML. Ảnh fixture dựng bằng Office thật; thư viện thử riêng. Bộ smoke
  bố cục chuyển đổi hiện có cũng đạt.
- Đối chiếu toàn bộ 48 slide nguồn và 67 slide đầu ra của một bài Vật lý
  trên bản sao riêng. Sau sửa dựng 68 slide, render/kiểm bằng PowerPoint,
  không có FAIL kỹ thuật. CHECK vẫn gồm chữ trang trí nhỏ, lời ghi chú,
  hình/công thức cần đối chiếu; không coi đó là chứng nhận kiến thức hay
  bản dịch hoàn hảo. Ảnh có chữ chưa đủ bằng chứng vẫn giữ trạng thái
  cần đối chiếu. Không sửa công thức kiến thức khác với nguồn.
- Bản dựng đối chiếu dùng lại cache; chỉ 10 mục có cách viết số mũ vừa
  phục hồi được dịch thêm (593 ký tự nguồn). Bốn câu kiểm ngữ cảnh đã
  thử qua API thật trước đó. Không dịch lại toàn bộ bài chỉ để thử bố cục.
- Hash tệp nguồn và bài cá nhân sau thử vẫn khớp trước thử. Bài giảng,
  API key, kết quả kiểm/ảnh và dữ liệu giọng cá nhân không vào Git.

## Đóng gói

Nguồn `1.0.0rc123`; dựng một lần sau commit đã kiểm, dùng runtime RC122
có manifest SHA256. Thông tin gói/cài đặt bổ sung sau khi xác minh.
