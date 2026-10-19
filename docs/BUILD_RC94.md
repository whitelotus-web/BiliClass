# RC94 — Chọn cặp gợi ý, tự ghép giọng và mẫu nghe dài

Giữ thứ tự Nữ Bắc–Trung–Nam ở hàng đầu, Nam Bắc–Trung–Nam ở hàng dưới
của sáu cặp gợi ý. Nhãn ngắn và bố cục ba cột dùng từ chiều rộng lưới
720 px; cửa sổ hẹp hơn tự giảm cột. Bên dưới là hai cột cân nhau cho
giọng Việt và giọng Mỹ, mỗi bên có bộ chọn, đoạn mẫu sửa được và nút nghe
riêng. Chọn gợi ý cập nhật cả hai bên; đổi một bên giữ bên còn lại.
Nghe cả cặp/dừng/lưu nằm ngoài vùng cuộn để luôn dùng được trên cửa sổ thấp.

Sáu cặp cũ giữ ID. Sáu tổ hợp tự ghép còn lại có ID ổn định; lưu rồi mở
lại, tạo giọng, tên bản và xuất PowerPoint/audio dùng đúng người đọc từng
ngôn ngữ. Bộ chọn tạo giọng thêm cặp tự ghép đã lưu hoặc có trong bài,
không chất thêm toàn bộ tổ hợp vào danh sách mặc định. WAV cũ giữ nguyên
và được dùng lại theo giọng thật. Phát bài vẫn chỉ có hai loa riêng.

Tạo tám mẫu công khai bằng mô hình local đang có: sáu Việt, hai Mỹ,
48 kHz mono PCM 16 bit, khoảng 12–16 giây mỗi ngôn ngữ. Manifest kiểm
checksum, văn bản, engine và người đọc; câu mặc định phát không cần nạp
mô hình. Cặp bất kỳ ghép đúng hai mẫu đã xác minh. Tốc độ khác dùng mẫu
có sẵn; câu riêng vẫn dùng tổng hợp local, nhận tối đa 1.000 ký tự mỗi
yêu cầu nghe thử. Hủy nghe không phát kết quả cũ. Không có cloud TTS.
Các mẫu này chỉ chứa câu mẫu công khai của ứng dụng, không chứa bài cá nhân.

Trang Chuyển đổi dùng lề trên/hai bên 30 px như trang Thư viện và Tạo
giọng. Không giảm còn 16 px khi cửa sổ thấp. Nội dung dài tiếp tục cuộn,
thanh hành động vẫn cố định. Giữ các tab Cài đặt hiện có.

## Kiểm chứng nguồn

- Ruff và compileall đạt; 964 kiểm thử lõi đạt trong 157,60 giây, bỏ sáu
  nhóm trình duyệt cũ như RC92; một cảnh báo Starlette/httpx không liên quan.
- Kiểm thử bao phủ cả 12 tổ hợp × ba chế độ tạo, cache/người đọc đúng,
  lưu/mở lại cặp tự ghép, xuất hai loa và giữ WAV/bản cũ.
- Qt nghe sáu cặp gợi ý và hai ngôn ngữ riêng, lưu cặp Mai Anh + Michael,
  tạo đủ ba sản phẩm và dùng lại WAV Việt cũ: đạt, không cảnh báo QML.
- Kiểm tra giao diện 1366 × 850 và 1080 × 700; đã xem ảnh Settings và
  Chuyển đổi. Lưu/dừng luôn hiện; hai cột cân đối ở cửa sổ đủ rộng.
- Kiểm tra giọng Qt: mẫu phát trong 24–30 ms, lưu khi đang chuẩn bị trong
  21 ms, khoảng ngắt giao diện cao nhất 99,5 ms; hủy không phát muộn,
  không nạp mô hình hoặc gọi Google; không cảnh báo QML.

## Đóng gói

Phiên bản `1.0.0rc94`. Dựng lại toàn bộ mã ứng dụng với runtime/mô hình
RC92 đã kiểm checksum. RC93 là bản nháp trung gian khi yêu cầu được mở rộng.

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc92-voice-pairs --output dist/rc94-voice-settings
```

Kết quả bản cài và phát hành được ghi sau khi xác minh.
