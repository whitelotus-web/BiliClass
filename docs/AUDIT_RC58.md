# Rà soát và tối ưu BiliClass RC58 — 17/10/2026

## Kết quả của đợt này

Rà soát toàn bộ mã Python bằng Ruff và biên dịch; chạy toàn bộ bộ kiểm thử,
kiểm tra Qt thật và một số luồng PowerPoint/máy chủ tại máy. Đợt này tập trung
vào thời gian giao diện phải chờ, tránh kiểm tra/tạo lại dữ liệu, và vòng đời
máy chủ. Chi tiết phiên bản, số kiểm thử và bộ cài ở [BUILD_RC58.md](BUILD_RC58.md).

### Những thay đổi đã thực hiện

- Việc lập danh sách và kiểm tra WAV trước khi tạo giọng chạy trong worker.
  Giao diện hiện trạng thái kiểm tra, đồng hồ vẫn chạy, vẫn dừng được tác vụ.
  Trường hợp mọi đoạn đã có chỉ kiểm tra lại; không khởi tạo model hay tổng hợp lại.
- Khi kiểm tra các bản Anh, Việt và Song ngữ của cùng bài, dùng lại kế hoạch,
  dấu vân tay nội dung và kết quả kiểm tra WAV trong cùng lượt. Lượt sau vẫn
  kiểm tra thay đổi tệp; không giữ trạng thái sẵn sàng sai khi WAV bị mất/hỏng.
- Thay bộ đếm mọi thay đổi SQLite bằng bộ đếm riêng cho bài giảng trên kết nối.
  Đổi mascot, hồ sơ hoặc thuật ngữ không quét lại giọng của cả thư viện. Sửa bài,
  thay giọng mặc định và thay đổi từ kết nối khác vẫn làm mới đúng. Bộ đếm TEMP
  không đổi schema thư viện, định dạng bài hoặc bản sao lưu.
- Tạm đóng máy chủ lớp chạy nền. Đợi yêu cầu đang gửi hoàn tất trước khi dừng;
  khóa thao tác mở lại trong thời gian đóng. Xóa QR và trạng thái cũ khi đóng
  xong; tiết chưa kết thúc vẫn tiếp tục được với câu trả lời đã nhận.
- Sửa kịch bản Qt giọng đọc cũ đang thử luồng Browser đã tạm ẩn, chuyển sang
  kiểm tra đúng luồng hiện tại: bài đã lưu → chủ động tạo giọng → xử lý lỗi.
- Dọn 22 lỗi quy cách mã nguồn: import, import thừa, câu lệnh gộp và callback.
  Ruff không còn báo lỗi trong `app` và `biliclass_m0`. Các script/test cũ còn
  một số lỗi cách trình bày; không đồng nghĩa có lỗi chức năng.
- Sửa cập nhật cho thư mục cài riêng: xác minh marker của bản đang chạy, giữ
  nguyên ổ/thư mục cài khi nâng phiên bản. Nếu ổ dữ liệu thiếu chỗ tải, dùng ổ
  cài đã xác minh còn đủ chỗ; vẫn kiểm checksum và từ chối đường dẫn không thuộc
  bản cài. Kiểm thử có cả marker thiếu/sai và thư mục chứa thư viện.
- Cập nhật hướng dẫn có chỗ còn nhắc RC55 và hướng dẫn Trang chủ đã thay đổi.

### Đo trước và sau

Một lần đo có cProfile trên cùng bài thật 86 slide, 354 đoạn WAV có sẵn. Đây
là đo tại máy này, không phải cam kết thời gian trên mọi máy.

| Công việc | Trước | Sau | Ý nghĩa |
| --- | ---: | ---: | --- |
| Lập ba lựa chọn ngôn ngữ | 63,6 ms | 27,2 ms | Giảm lập kế hoạch lặp |
| Kiểm tra các bản giọng của bài | 360,7 ms | 131,6 ms | Dùng lại kiểm tra WAV giữa các bản |
| Khởi tạo tác vụ giọng trên giao diện | 133,3 ms | 0,24 ms | Chuyển phần kiểm tra sang worker |

Thư viện thử riêng 1.000 bài: tạo 4,01 giây, công bố danh mục kèm kiểm tra giọng
0,97 giây; tìm/lọc 100 lượt có trung vị 4,06 ms, lớn nhất 5,83 ms. Lọc cho đúng
333 kết quả và phân trang 20 bài. Dữ liệu thử đơn giản, không đại diện 1.000
PowerPoint nhiều ảnh hoặc 1.000 bài có hàng trăm WAV mỗi bài.

Các số trên **không phải tốc độ tổng hợp giọng lần đầu**. Phần đó vẫn phụ thuộc
CPU, số chữ, giọng và model. Cơ chế dùng lại WAV, chia đoạn, đổi tốc độ từ bản
gốc và giới hạn worker theo tài nguyên được giữ lại.

## Phạm vi đã kiểm tra

| Khu vực | Bằng chứng | Giới hạn |
| --- | --- | --- |
| Chuyển đổi | Test Google, giữ thiết kế, công thức, OCR, mẫu, dịch theo lô, tiếp tục sau lỗi; Qt nguồn → API fixture → PPTX chỉnh sửa được | Không gửi bài/tiêu quota Google thật trong đợt thử |
| Mẫu bài giảng | Qt dựng và xem 3 phong cách × 2 chế độ; cache mẫu và trang mở/kết bài | Độ đẹp và chất lượng nội dung vẫn cần giáo viên duyệt từng bài |
| Giọng đọc | Test cache, sáu giọng, tốc độ, bản ngôn ngữ, xuất âm thanh; Qt vẫn có nhịp khi cố tình giữ kiểm tra WAV và tổng hợp 250 ms mỗi giai đoạn | Không biến thời gian kiểm tra tệp thành lời hứa tăng tốc model |
| Thư viện | Tìm không dấu, lọc, phân trang, chọn nhiều, tải/xóa, thùng rác, khôi phục, hình bìa 16:9; Qt đổi danh sách/thẻ và chuyển tab giữ cache | Bài lớn thực tế có chi phí đọc/render riêng |
| Lớp học | Qt mở → học sinh trả lời WebSocket → đóng/công bố → tạm đóng/mở lại → kết thúc → CSV; kiểm tra đóng không chặn GUI | Cần cùng mạng phù hợp và cấu hình firewall đúng |
| Tải lớp học | 50 kết nối loopback, nhận đủ 50 phản hồi, 35 đúng; gửi trùng/kết nối lại không nhân đáp án; khởi động lại giữ dữ liệu | Không phải 50 điện thoại thật trên Wi-Fi trường |
| PowerPoint/mascot | PowerPoint thật chuyển đủ 3 slide, file gốc không đổi; Qt phụ kiện/môn đã lưu, bật/ẩn, khóa đọc khi chưa có trình chiếu đúng bài | Hiệu ứng đặc biệt và máy chiếu chưa được chứng nhận chung |
| Dữ liệu/cập nhật | Test giao dịch, lịch sử, gói bài, sao lưu/khôi phục, kiểm tệp/path/checksum, key sync và updater | Chuyển key là snapshot qua repo riêng, không đồng bộ trực tiếp quota |

Lượt tải lớp hiện tại có ACK p95 331,7 ms, lớn nhất 339,1 ms; CPU cùng lúc chạy
kiểm thử khác. Kết quả 70% đúng đã được tính đúng sau khi khởi động lại. Không
so sánh con số này như một cải tiến độ trễ so với lần đo RC57 ở tải máy khác.

Lượt toàn bộ trước sửa qua 886 test; lượt sau tối ưu qua 890 test trong
493,19 giây. Sau điều chỉnh cuối về thư mục cập nhật/giọng mặc định, nhóm 20
test updater, package và catalog cũng qua. Có một cảnh báo tương thích từ
FastAPI/Starlette test client với httpx trong runtime hiện có; không nâng thư
viện nhị phân giữa đợt đóng gói chỉ để ẩn cảnh báo.

## Những điều vẫn phải hiểu đúng

- Hạn mức trên Trang chủ là lượng dùng BiliClass ghi nhận theo nhóm dự án,
  không phải số dư Google Cloud đã xác minh. Hai Gmail khác nhau không tự chứng
  minh hai project. Muốn chặn chi phí thật cần cấu hình quota ở Google Cloud.
- Mascot đọc và điều khiển bài trình chiếu đã gắn đúng, không tự đọc bài đang
  lưu khi chưa mở trình chiếu. Giải thích/quiz dùng nội dung đã chuẩn bị, duyệt;
  không tự động có một hệ AI trả lời mọi câu hỏi.
- Thuật ngữ vẫn hữu ích cho dịch theo môn. Đã đưa vào Cài đặt → Dữ liệu,
  không cần chiếm mục thanh bên. Kết quả lớp học nằm trong Lớp học.
- Nội dung giáo viên, phản hồi học sinh, báo cáo riêng, key, model và EXE không
  đưa vào commit nguồn. Bộ cài là tài sản riêng trong GitHub Releases.

## Kế hoạch tối ưu tiếp, theo mức ưu tiên

1. **Thử lớp tại môi trường thật.** 30–50 điện thoại cùng Wi-Fi trường; mất mạng,
   đổi mạng, khóa màn hình, kết nối lại và mở tiếp tiết. Tiêu chí: không nhân
   phản hồi, giữ câu đã gửi, giáo viên thấy rõ lỗi truy cập.
2. **Đánh giá chất lượng mẫu bằng bài chuẩn.** Bộ bài nhiều công thức, bảng,
   ảnh và lựa chọn trắc nghiệm từ 5 môn. Duyệt ảnh render; ưu tiên chữ dễ đọc,
   công thức giữ nguyên, số trang hợp lý. Không coi test không tràn chữ là đủ đẹp.
3. **Đo giọng nguội và nóng.** Tách thời gian tải model, suy luận, ghi WAV và
   phát; báo riêng từng giai đoạn. Chỉ đổi model/worker nếu đo được thời gian
   giảm mà giữ chất lượng phát âm và khả năng dùng giao diện.
4. **Kiểm tra cài đặt trên Windows sạch.** Chưa có Python, Codex, model hay
   runtime từ máy phát triển; thử nâng RC34 và khôi phục bản cũ khi cập nhật lỗi.
5. **Tách dần cầu nối giao diện theo chức năng.** `app/ui.py` còn lớn. Tách theo
   thư viện/chuyển đổi/dạy học từng phần sau khi có test hồi quy, tránh sửa đồng
   loạt khiến thay đổi UI nhỏ ảnh hưởng luồng khác.

Đây là phạm vi và giới hạn kiểm chứng của đợt này, không phải cam kết tool
không còn bất kỳ lỗi nào trên mọi dữ liệu và mọi máy.
