# RC150 — Chọn nhiều bài đúng công cụ, thu gọn lượt đã hoàn tất

Hai công cụ dùng một hộp chọn PowerPoint, ghi rõ mục đích khi mở.
File nhận cho Tạo giọng đi vào hàng đợi giọng và màn Tạo giọng;
file chuyển đổi đi vào màn Chuyển đổi. Chuyển trang trong lúc chọn
file không đổi mục đích đã ghi. Vùng kéo thả của màn không hoạt động
được khóa. Một bài vẫn dùng workspace một bài; nhiều bài dùng các
bộ xử lý hiện có, mỗi lần một bài, chung cấu hình cho lượt đó.

Danh sách bài trong màn Tạo giọng có checkbox, Chọn tất cả/Bỏ chọn,
số lượng đã chọn và giới hạn 100 bài. Chọn dòng không đóng popup.
Lựa chọn giữ theo ID khi danh sách đổi thứ tự, bỏ ID đã biến mất;
chọn một bài mở workspace cũ, nhiều bài chuẩn bị hàng đợi trên ID
hiện có, bỏ qua bài đã có giọng hoàn tất. Bấm dùng bài chưa tự tạo
âm thanh; cần chọn cấu hình và bấm Tạo giọng như trước.

Khi tất cả mục đều hoàn tất và lượt kết thúc, hàng đợi tự ẩn ở cả
hai công cụ, kể cả khi đọc lại nhật ký sau lần mở ứng dụng. Nhật ký,
PowerPoint và âm thanh được giữ; lượt còn chờ/bị dừng/lỗi vẫn có
Tiếp tục/Thử lại. Không coi lượt có bài lỗi là đã hoàn tất.

Ba tab Thư viện dùng kiểu nhãn kẹp file, có icon và số bài, hỗ trợ
sáng/tối; vẫn là bộ lọc trên cùng một bài. Không đổi các tab Cài đặt.

Kiểm chứng trên dữ liệu riêng: 516 pytest đạt; Ruff/compileall đạt.
Năm Qt smoke về chọn bài/định tuyến, hàng đợi, giao diện sáng/tối,
vòng đời nguồn/sản phẩm và Trang chủ đạt, không cảnh báo QML.
Kiểm một bài qua sự kiện Accepted, chọn nhiều bài bằng con trỏ trong
popup, đổi thứ tự/xóa ID, Chọn tất cả tối đa 100, chưa tự tạo giọng,
Dừng/Tiếp tục/thử lại riêng bài lỗi và giấu lượt thành công sau mở lại.
Hàng đợi giọng xuất PowerPoint thật với WAV mẫu, giữ nguyên các file
nguồn; không phải phép kiểm phát âm trên mọi môn/bài lạ.
Hộp chọn trong Qt smoke dùng giao diện Qt để kiểm nút mở và mục đích;
URL nhiều file được đưa qua đúng receiver của sự kiện nhận file.
Chưa tự động chọn nhiều file trong hộp thoại Windows của người dùng,
nên không kết luận đã tái hiện đầy đủ nguyên nhân báo lỗi trên RC149.

[Trạng thái phát hành RC150: đang kiểm tra.]
