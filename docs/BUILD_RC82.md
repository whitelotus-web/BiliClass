# RC82 — Kéo/thu bảng trợ giảng và đóng Mascot cùng ứng dụng

## Thay đổi

- Kéo tiêu đề, nhãn hoặc vùng trống của bảng để di chuyển cả bảng và
  Mascot. Nhấp một lần không thu bảng; nhấp đúp vùng này thu về Mascot,
  giữ tọa độ nhân vật. Kéo nhân vật vẫn hoạt động như trước.
- Dùng cùng xử lý kéo ở nhân vật/bảng; chỉ lưu vị trí khi thả hoặc hủy
  kéo. Nút kể cả nút bị khóa, dropdown, thanh âm lượng, scrollbar và vùng
  chọn văn bản không biến thành vùng kéo. Cuộn chuột được truyền xuống.
- Đóng cửa sổ chính được chấp nhận thì thoát rõ ràng, ẩn bảng nổi trước
  khi dọn worker. Giữ chặn đóng khi tác vụ chính đang bận; thu nhỏ vẫn
  giữ Mascot, nút “−” chỉ ẩn Mascot. Các đường thoát ứng dụng đều ẩn cửa
  sổ phụ trước khi chờ hoàn tất dọn nền.
- Bỏ ba công tắc Hiện khi dạy/giải thích/quiz, chuẩn hóa các giá trị cũ
  về bật. Khởi động ứng dụng bình thường hiện Mascot; vẫn ẩn được thủ
  công trong phiên. Không buộc một bản BiliClass khác đang chạy phải thoát.
- Ba tùy chọn phụ kiện/chuyển động/nổi trên cùng cùng hàng với “Chọn
  phụ kiện theo môn”. Danh sách có các môn sẵn và môn riêng đang dùng;
  xem trước ngay, bấm Lưu để áp dụng. Lưu riêng môn phụ kiện, không đổi
  môn bài giảng, hồ sơ, liên kết PowerPoint hay lời đọc.

## Kiểm chứng

921 core đạt, một warning dependency Starlette/httpx. Lint/compile đạt.
8 luồng Qt liên quan đạt, không warning QML: bảng, vòng đời đóng/ẩn/thu
nhỏ, điều hướng, Settings, kết quả/giọng, Trang chủ, lớp học và Office
thật. Thử kéo/nhấp đúp tại nền 100%/30%, nút khóa, slider, chọn chữ/cuộn
vẫn đúng. Cấu hình gọn được chụp ở 1080/1366; chọn môn không sửa bài.

GUI giọng/phụ kiện nguồn với 30 môn đạt. Probe riêng chạy desktop nguồn
thực tế với thư viện dùng một lần: khởi động hiện Mascot, thu nhỏ giữ,
gửi Close cho cửa sổ chính thì ẩn Mascot và tiến trình kết thúc mã 0 trong
0,36 s. Probe tắt kiểm cập nhật mạng; không chạm ứng dụng đang dùng.
Office dùng WAV im lặng để kiểm lệnh/đổi bài, không chứng nhận phát âm
hoặc máy chiếu thực tế. Kết quả core không gồm nhóm Browser giữ từ mốc cũ.

RC82 là mốc dựng nội bộ, chưa phát hành; các thay đổi được đưa tiếp vào
RC83 để sửa thêm bàn phím, điều khiển slide và hiệu năng Mascot. Gói nguồn
`9c09611`, SHA256 ZIP `e5c90cf3249a9b27e3990b6a2049874335d5b8cd907c8bcd42b8fd94a1adcb65`.
Kiểm bộ cài/gỡ cô lập, VieNeu Việt/Anh, GUI 30 môn và probe đóng EXE đạt;
đóng ẩn Mascot/thoát trong 0,468 s. Thử bằng thư viện riêng; không đưa thư
viện/key cá nhân vào Git/bộ cài.
