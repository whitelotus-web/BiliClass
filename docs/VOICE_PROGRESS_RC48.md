# Giọng đọc và màn hình kết quả — RC48

Ngày 16/10/2026. Màn hình kết quả hiển thị thời gian tạo giọng thực tế dạng
`HH:MM:SS`, cùng số đoạn đã sẵn sàng và phần trăm. Đồng hồ vẫn chạy khi model
đang nạp hoặc đang xử lý một đoạn dài; dừng khi worker kết thúc, kể cả sau yêu
cầu Dừng. Đây là thời gian đã dùng, không phải dự báo thời gian còn lại.

Đồng hồ dùng tín hiệu Qt riêng, không quét thư viện/WAV hoặc làm mới toàn
giao diện mỗi giây. Thời gian được lưu cùng checkpoint của lượt tạo giọng.
Các nút Dùng để dạy / Tải PowerPoint nằm cạnh trạng thái bài đã lưu khi đủ
rộng; cửa sổ hẹp tự xuống hàng. Bộ điều hướng Slide nằm giữa khung xem.

## Tạo giọng nhanh hơn có giới hạn

- Đoạn đã có WAV hợp lệ được dùng lại. Lượt tiếp tục chỉ tạo phần còn thiếu;
  giữ nguyên định danh cache để dùng lại giọng từ các bản trước.
- Lượt còn ít nhất 48 đoạn và 3.000 ký tự có thể dùng hai bộ xử lý, nếu máy
  có ít nhất sáu nhân CPU vật lý và 6 GiB RAM đang trống. Máy khác hoặc bài
  ngắn dùng một bộ. Có thể ép một bộ bằng `BILICLASS_NARRATION_WORKERS=1`.
- Model chính dùng bốn luồng ONNX, model phụ hai luồng. Cả hai giữ model
  VieNeu FP32, giọng đã chọn và WAV mono PCM16 48 kHz; không rút bớt lời đọc.
  Giới hạn BLAS dùng chung tránh nhiều nhóm CPU tranh tài nguyên.
- Chỉ có tối đa hai đoạn đang xử lý. Model phụ được nạp sau đoạn đầu thành
  công và giải phóng khi lượt tạo giọng kết thúc. Nếu model phụ lỗi, đoạn đó
  được thử lại bằng model chính và phần còn lại chạy tuần tự.
- Khóa theo WAV tránh hai bộ tạo trùng cùng đoạn. Nghe thử/đọc chủ động được
  ưu tiên ở model chính; tạm dừng ngăn nhận thêm việc. Dừng giữ các WAV đã
  hoàn thành, chờ lệnh CPU đang chạy kết thúc an toàn.

Hai model dùng thêm RAM và có chi phí nạp lần đầu. Điều kiện trên là lựa chọn
thận trọng, không bảo đảm mọi máy hoặc mọi bài đều nhanh hơn cùng một tỷ lệ.

## Kiểm chứng

- 99 kiểm thử liên quan qua: điều khiển giọng, nghe thử, đa ngôn ngữ, cache,
  tốc độ, lời đọc bài giảng, xử lý song song/hủy/lỗi phụ, ngân sách CPU,
  lớp học và nhúng audio PowerPoint.
- Qt source: 1080×700 và 1366×850 không cảnh báo; kiểm tra nút không bị che,
  cùng hàng với trạng thái, điều hướng căn giữa; đồng hồ tăng khi chưa có
  đoạn mới hoàn thành và ngừng sau khi worker dừng.
- Máy đo: Intel i7-8700, sáu nhân / 12 luồng. Sau khi nạp model, tám đoạn
  mẫu chạy tuần tự 24,898 giây; hai model 21,367 giây, giảm khoảng 14,2%.
  Đây là phép đo mẫu, không phải thời gian hoàn thành toàn bộ bài giảng.
- Chạy pipeline thực với hai model và tám nội dung mới: 8/8 WAV hợp lệ,
  không lỗi; 27,306 giây gồm nạp model. Kiểm tra lại đủ tám cache trong
  0,001 giây và không còn việc phải tạo. Fixture ngắn này ép hai bộ để
  kiểm tra; điều kiện tự chọn trong sản phẩm vẫn yêu cầu bài dài như trên.

Bằng chứng riêng trong `reports/rc48` không đưa lên Git. Xem
[bản đóng gói, kiểm tra EXE và cách mở độc lập](BUILD_RC48.md).
