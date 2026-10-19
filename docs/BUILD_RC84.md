# RC84 — Tăng tốc chuyển slide và chọn PowerPoint

## Thay đổi

- Lập chỉ mục loa từ PPTX tại worker; chỉ lấy các đối tượng loa cần thiết
  qua Office một lần khi gắn bài. Trước/Sau không còn quét toàn bộ chữ,
  ảnh, biểu đồ trên slide. Âm lượng cũng chỉ cập nhật các loa đã biết.
  Chỉ đọc XML, không nạp các ảnh/âm thanh nhị phân để lập chỉ mục.
- Giữ bộ đếm theo slide thật, giới hạn đầu/cuối, thứ tự khi bấm liên tục,
  các hiệu ứng của phím mũi tên và player dùng chung với loa trên slide.
  Dò cửa sổ Presenter định kỳ thay vì sau mọi lệnh. Gửi lệnh chuyển trước
  khi xử lý khôi phục focus. Không sửa hiệu ứng hoặc file bài gốc.
- Kiểm tra đường dẫn/dung lượng file ở worker riêng khi chọn hoặc kéo
  thả PowerPoint. Chỉ áp dụng lựa chọn mới nhất; Bỏ tệp loại kết quả đến
  muộn. Chặn chuyển đổi khi tệp chưa kiểm tra xong; vẫn sửa cấu hình được.
  Không phát tín hiệu làm mới toàn Thư viện/Settings khi chọn tệp.
- Gồm hai thay đổi giao diện đã commit sau RC83: bỏ ghi chú hướng dẫn
  chung khi chưa gắn bài, bỏ nút Xem bài đang gắn và Ngắt gắn bài.

## Đo trên máy hiện tại

Bài thử dùng một lần: 51 slide, mỗi slide 120 đối tượng, 29 lần chuyển
tuần tự. Đo từ gửi lệnh đến trạng thái slide được Office xác nhận:

| | Trước | Sau, lượt cuối |
|---|---:|---:|
| Trung bình | 0,693 s | 0,068 s |
| P95 | 0,734 s | 0,094 s |
| Chậm nhất | 0,844 s | 0,094 s |

Khoảng 10 lần nhanh hơn trên cùng cấu trúc bài thử. Thêm chuỗi 8 lệnh
liên tục và thử giới hạn đầu/cuối đạt, nguồn không đổi; tick GUI tối đa
0,016 s. Đây là thời gian phản hồi trạng thái, không phải cam kết thời
gian dựng ảnh cho mọi bài có hiệu ứng/chuyển cảnh của PowerPoint.

Harness chuột/phím Windows thật, bài có hiệu ứng và WAV im lặng: 14 lần
chuyển trung bình 0,032 s, tối đa 0,063 s; 12 lần kéo bảng đạt. F5 từ
editor, khôi phục focus, không bắt phím ứng dụng khác, đọc/tạm dừng/đổi
ngôn ngữ, nút loa theo slide và không làm mới toàn Bridge đều đạt.

Qt màn hình chuyển đổi: giả lập kiểm tra file phải chờ 0,6 s nhưng GUI
vẫn có tick tối đa 0,016 s, không warning QML hoặc làm mới toàn Bridge.
Tên tự đặt được giữ; đổi tệp cập nhật tên mặc định; tệp thiếu và kết quả
đến sau Bỏ tệp không được dùng. Bố cục 4 kích thước màn hình và luồng
mở/gắn bài trước/sau tạo giọng, sau chuyển đổi, trong Thư viện đạt.

Các bài thử dùng thư viện riêng và chỉ đóng bài Office do harness tạo.
Không xác nhận hết mọi nguyên nhân Not Responding hoặc máy chiếu vật lý.
940 test core đạt; sau khi chỉ mục đổi sang đọc XML, 7 kiểm tra chỉ mục/
chọn file và các luồng Office liên quan được chạy lại, đều đạt. Có một warning Starlette/httpx đã tồn tại.
Lint/compile đạt.

## Bản phát hành đã kiểm chứng

- Nguồn `cae909fd71fc90ceaf5ae8e7aec09049ab021a78`;
  [CI đạt](https://github.com/whitelotus-web/BiliClass/actions/runs/39194912870).
- [Release RC84](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc84):
  ZIP 871.227.615 byte, 4.215 mục. GitHub xác nhận digest khớp
  `37a9d6d54d1e1924974e8461f78fdb8a9a7eca999c461cda3d99bb432b4c9e5b`.
  Dựng đúng một lần từ runtime RC83 đã đối chiếu, biên dịch lại mọi module
  ứng dụng. Không đưa EXE/model hoặc dữ liệu cá nhân vào commit.
- Bộ cài trong đường dẫn Unicode đạt: Properties sản phẩm/phiên bản/
  copyright, trang chuyển đổi và Browser AI, template, VieNeu Việt/Anh
  cùng người đọc, process lớp học và backup. Gỡ bản thử giữ thư viện riêng.
  Báo cáo cục bộ: `reports/release/1.0.0rc84-15c4e457/installer.json`.
- Probe desktop nguồn và EXE thực tế đều đạt: hiện Mascot khi mở, giữ khi
  thu nhỏ, đóng ẩn Mascot và thoát mã 0 (lần lượt 0,313 và 0,359 s).
- Cài tại `F:/Applications/BiliClass/1.0.0rc84`, mở trang Chuyển đổi từ
  Explorer, parent `explorer.exe`; xác nhận main window đúng RC84 và có
  phản hồi, độc lập Codex. Tệp key mã hóa đối chiếu không đổi.
