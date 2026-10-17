# Kế hoạch hoàn thiện BiliClass sau rà soát RC72

Ngày 18/10/2026 (bắt đầu rà soát 17/10). Phạm vi: nhập/chuyển đổi, kiểm tra bài, giọng đọc, thư viện,
PowerPoint/mascot, lớp học/báo cáo, dữ liệu, cài đặt, kiểm thử và phát hành.
Đây là kế hoạch triển khai tiếp; không coi các tiêu chí bên dưới là đã đạt.
Giữ các tab Cài đặt Chung, Song ngữ, Giọng đọc, Mascot.

## Kết luận và phần đã xử lý

Lõi ứng dụng đã có luồng nghiệp vụ tương đối đầy đủ. Điểm cần ưu tiên là
**chất lượng bài đầu ra, khả năng khôi phục và tính nhất quán của trạng thái**.
Qua kiểm thử kỹ thuật không có nghĩa mọi bản dịch, bố cục hay phát âm đều đúng.
Không nên tiếp tục thêm nhiều tính năng trước khi khóa các tiêu chí này.

RC71 sửa tách lời đọc VI/EN, lời đọc lưu riêng với slide, trạng thái và hủy
bài đang chọn; thêm điểm tiếp tục sau QA khi thiếu dung lượng ở bước lưu.
RC72 bổ sung:

- Chốt chuyển thư viện dùng lại hash đã kiểm của tệp không đổi; tránh đọc
  lại toàn bộ model, PowerPoint và WAV chỉ để lập manifest. Vẫn xác minh
  thư viện đích trước khi mở; chỉ dọn tệp cũ khớp hash sau khi mở thành công.
- Sao lưu/khôi phục đọc theo khối 1 MiB, lưu tạm trên ổ đích. Cùng giới hạn
  số tệp/dung lượng; không công bố gói mà chức năng khôi phục sẽ từ chối.
  Giữ bản sao lưu tốt cũ khi lỗi; chỉ công bố thư viện khôi phục sau kiểm tra.
- Cập nhật smoke Thư viện/Trang chủ và Lớp học theo giao diện hiện hành.
- Chuẩn hóa lời đọc trước lần ghi đầu tiên của bài mới, tránh sinh lịch sử
  giả; bài cũ được chuẩn hóa trong khóa giao dịch dùng để tìm lại request.
- Loại toàn bộ `output/` khỏi Git để tệp chẩn đoán không bị thêm nhầm.

Một lần đo với tệp thử 24 MiB: bộ nhớ Python đỉnh khi sao lưu giảm từ
24,45 xuống 2,29 MiB. Tổng sao lưu + khôi phục là 0,661 và 0,959 giây.
Đây là cải thiện bộ nhớ; không phải bằng chứng tăng tốc, giảm toàn bộ RAM
của tiến trình, hoặc kết quả trên thư viện giáo viên lớn.

## Đánh giá từng nhóm

| Nhóm | Cơ sở hiện có | Việc còn phải hoàn thiện |
|---|---|---|
| Chuyển đổi | Hash nguồn, cache dịch, khóa tác vụ, giới hạn đầu vào, tiếp tục lưu | Bài dày chữ/công thức còn có cảnh báo tràn và thiếu chữ; cần bộ bài chuẩn và đánh giá hình thật |
| Lời đọc | Tách nhãn VI/EN, sửa riêng, nhiều bản ngôn ngữ/giọng/tốc độ, cache | Phân loại không nhãn vẫn là heuristic; cần điểm tin cậy và danh sách slide chưa chắc |
| Giao diện | Điều hướng theo chuyển đổi → giọng → bài → lớp, trạng thái có sẵn | Giảm dòng trạng thái lặp; làm rõ đủ audio cho lời hiện có khác đủ lời cho mọi slide |
| Thư viện | Tìm không dấu, lọc, phân trang, thẻ/danh sách, chọn nhiều, thùng rác | Phải đo với thư viện lớn và ảnh/WAV thật, không chỉ nhiều bản ghi nhỏ |
| Dạy/mascot | Gắn với phiên trình chiếu, khóa hành động sai ngữ cảnh | Office COM còn có chẩn đoán RPC disconnected; cần cô lập và thử rút màn hình/đóng Office |
| Lớp học | WebSocket, gửi trùng, nối lại, snapshot phiên và xuất CSV | 50 client loopback chưa đại diện Wi-Fi trường hay điện thoại thật |
| Dữ liệu | SQLite, backup/checksum, gói bài, chuyển thư viện có xác minh | Cần trạng thái backup gần nhất trên UI, ngân sách dung lượng, khôi phục có đường dẫn tuyệt đối được đổi đúng |
| Vận hành | Gói tách dữ liệu, version/commit/hash, updater | Nhiều bước phát hành nhanh đang nằm trong helper cục bộ; cần quy trình tái lập đã version hóa |
| Bảo trì | Có bộ test rộng và smoke Qt thật | `app/ui.py` 3.421 dòng, `Main.qml` 1.855 dòng; nợ lint tập trung trong script/test |

## Mốc 1 — Chất lượng và khôi phục (P0, dự kiến 2–4 ngày làm việc)

1. Chọn 8–12 bài chuẩn có quyền sử dụng: văn bản thường, bảng, công thức,
   ảnh/OCR, nhiều hiệu ứng, slide kín chữ và bài song ngữ có sẵn. Ghi phiên
   bản nguồn và kết quả mong đợi; dữ liệu riêng nằm ngoài Git.
2. Tách lỗi đầu vào với lỗi mới do chuyển đổi. Mỗi lỗi có slide, vùng,
   nguyên nhân, ảnh trước/sau và hành động sửa. Không hạ FAIL chỉ để đẹp thống kê.
3. Sửa thứ tự ưu tiên dàn trang: giữ hình/công thức → chia khối hợp lý →
   thêm trang tiếp nối có liên kết → giảm chữ trong giới hạn đọc được.
   So sánh nội dung/quan hệ media sau mỗi lần sửa; không lặp vô hạn.
4. Kiểm lỗi lưu sau QA, đóng app khi đang lưu, hết ổ, tệp nguồn thay đổi,
   tác vụ đã lưu nhưng chưa ghi checkpoint. Luôn tìm lại bằng request ID;
   không dịch lại hay tạo bài trùng khi chỉ còn thiếu bước lưu.
5. Cô lập Office render/fit trong tiến trình con có thời hạn, giữ trạng thái
   từng slide. Hiện lỗi rõ và cho thử lại phần lỗi khi Office ngắt RPC.

**Nghiệm thu:** không mất nguồn/bài/audio; không gửi dịch trùng ở các ca khôi
phục; bộ bài chuẩn không còn lỗi kỹ thuật mới chặn dùng. Giáo viên kiểm tra
đúng nghĩa, thuật ngữ và phát âm riêng; chưa kiểm thì ghi “cần kiểm tra”.

## Mốc 2 — Giao diện và trạng thái (P1, dự kiến 2–3 ngày)

- Dùng một mô hình trạng thái chung cho Trang chủ, thư viện, kết quả và
  giọng đọc: **đã lưu**, **cần kiểm tra nội dung**, **đã có giọng cho X/Y slide**,
  **đã chuẩn bị phiên dạy**. Một dấu xanh không thay thế cả bốn trạng thái.
- Một hành động chính ở mỗi bước; nút quay lại/chọn lại/hủy ở vị trí ổn định.
  Ghi rõ “Bỏ bài đang chọn” với “Dừng tạo giọng”; giữ phần đã tạo và đường tiếp tục.
- Màn giọng: một tóm tắt tiến độ, cảnh báo thiếu lời mở đúng slide; phân biệt
  slide chủ ý không đọc và slide chưa nhận được chữ. Ghi phạm vi của “đã tạo đủ”.
- Với 1080×700, bảo đảm nút chính và Cài đặt tìm thấy dễ dàng; thu gọn chân
  thanh bên và nội dung phụ. Thử 125–150% DPI, phím Tab/Enter/Escape, độ tương
  phản, vùng bấm, thông báo không chỉ dựa vào màu. Giữ phong cách hiện tại.
- Màn dữ liệu có dung lượng còn lại, lần backup thành công, lỗi gần nhất,
  nơi lưu và tiến độ xác minh chuyển. Không để cửa sổ biến mất lâu mà không
  biết ứng dụng đang làm gì.

**Nghiệm thu:** cùng một bài có cùng trạng thái ở mọi màn; chỉnh lời/giọng
chỉ làm hết hiệu lực phần liên quan; người dùng hoàn thành luồng chính bằng
bàn phím; không che nút/nội dung ở ba kích thước và hai mức DPI.

## Mốc 3 — Giọng đọc và hiệu năng (P1, dự kiến 2–4 ngày)

- Thứ tự nhận diện: nhãn rõ → metadata ngôn ngữ của run → cặp câu → nhận diện
  theo dòng. Ghi lý do/độ tin cậy, không ép công thức hoặc mã thành tiếng Anh.
  Nội dung giáo viên đã sửa phải được ưu tiên, không tự ghi đè khi mở lại.
- Bộ nghe thử gồm VI, EN, xen kẽ, viết tắt, tên riêng, đơn vị và công thức.
  Đánh giá 6 giọng trên cùng tập câu, tốc độ và loa; không đổi model ngầm.
- Đo riêng tải model, tiếng đầu tiên, suy luận, ghi WAV, cache, nhúng PPTX.
  Đo nguội/nóng, bài nhỏ/vừa/lớn; sửa một đoạn chỉ tạo lại đoạn cần đổi.
- Đo GUI trong khi tổng hợp, đổi slide và dừng. Giới hạn worker theo CPU/RAM;
  tránh tạo cache/ảnh trên luồng UI. Theo dõi RAM/handle sau 60–120 phút.

**Nghiệm thu:** 100% ca có nhãn rõ tách đúng; ca không chắc được hiển thị;
nguồn không đổi; cache sai nội dung/giọng/tốc độ không phát lại. Chỉ công bố
tăng tốc khi có ít nhất 10 lượt đo cùng cấu hình và không giảm chất lượng.

## Mốc 4 — Dữ liệu và vận hành (P1, dự kiến 2–3 ngày)

- Kiểm khôi phục thư viện trên ổ khác, gồm đường dẫn nguồn, thumbnail,
  checkpoint, custom template, lịch sử và phiên lớp. Cho xem trước phạm vi
  backup: model, key và phiên đăng nhập có chính sách riêng, không gọi mọi gói
  là “toàn bộ dữ liệu” nếu chúng không có trong đó.
- Quản lý backup theo dung lượng và tuổi, không chỉ số bản. Cảnh báo trước
  giới hạn hiện có (ZIP 2 GiB, giải nén 4 GiB, 20.000 entry, tệp 200 MiB).
  Thiết kế gói lớn/chia phần hoặc incremental ở mốc riêng có version/migration.
- Resume chuyển thư viện sau mất điện bằng manifest bền; xác minh target
  trước khi đổi selector; dọn chỉ tệp nguồn khớp bản đã chuyển. Không xóa
  bản thay đổi bởi ứng dụng khác.
- Trung tâm chẩn đoán xuất log đã bỏ key/token/nội dung/học sinh; thông báo
  theo nhóm lỗi mạng, quota, dung lượng, Office, lời đọc và chất lượng slide.

**Nghiệm thu:** restore trên ổ khác mở/dạy được, đủ số bài/audio/phiên; lỗi
giữa chừng không để thư viện nửa vời; backup vượt giới hạn không thay bản tốt.

## Mốc 5 — Lớp thật và phát hành (P1, dự kiến 1–2 buổi lớp + 1–2 ngày)

- 30–50 điện thoại Android/iPhone trên Wi-Fi trường: quét QR, khóa màn hình,
  mất mạng, vào lại, gửi trùng, đổi câu, đóng/công bố/recheck, kết thúc/xuất báo cáo.
- Máy chiếu Extend/Duplicate, rút/cắm màn hình, chuyển Presenter View,
  tắt PowerPoint khi đang đọc, mở lại đúng bài. Thử dạy ngoại tuyến với audio có sẵn.
- Windows sạch không Python/Codex: cài, mở model thật, cập nhật từ bản cũ,
  cập nhật gián đoạn, quay lại bản trước, gỡ vẫn giữ thư viện. Thử máy CPU/RAM thấp.

**Nghiệm thu:** không lộ đáp án trước công bố, không nhân phản hồi, báo cáo
giữ mẫu số; phục hồi được sau lỗi. Ghi latency p50/p95 trên mạng thật, thông
số máy và lỗi quan sát; không suy ra thành công từ loopback.

## Mốc 6 — Bảo trì dài hạn (P2, chia từng đợt 2–3 ngày)

- Tách `ui.py` theo chuyển đổi, thư viện, narration, dạy học; tách màn QML theo
  chức năng. Mỗi bước giữ hợp đồng signal/property và có smoke hồi quy.
- Chuẩn hóa lệnh kiểm tra dự án: venv, lint nguồn, unit không cần Office,
  integration Office chạy tuần tự, Qt, kiểm gói. Tránh hai ca Office cùng lúc.
- Gom build/package/install verification vào script có trong Git. Ghi rõ
  runtime/model tái dùng có hash nào, không phụ thuộc helper bị mất ở `.runtime`.
- Xử lý 252 lỗi lint trong scripts/tests theo nhóm nhỏ; không sửa cơ học cả
  kho trong cùng đợt với logic dữ liệu. Thêm CI nguồn và Windows integration.
- Cập nhật README/STATE/changelog theo version thật; giữ một trang trạng thái
  hiện tại, tài liệu RC cũ chỉ dùng làm lịch sử.

**Nghiệm thu:** máy phát triển thứ hai chạy được quy trình kiểm/build bằng
code đã commit; một sửa UI nhỏ có bộ test rõ ràng; không có dữ liệu cá nhân,
model hay EXE trong staged files.

Ước lượng trên dành cho một người thực hiện, chưa gồm thời gian chờ giáo
viên và thiết bị. Chốt mốc 1 trước khi nhận thêm tính năng; sau mỗi mốc chạy
test phù hợp, Qt nếu liên quan, commit/push, rồi build đúng một lần.
