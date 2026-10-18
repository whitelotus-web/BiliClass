# RC77 — Loa trong PowerPoint mở độc lập và vị trí cố định

Người dùng xác nhận đang mở trực tiếp file đã tải xuống. RC77 đưa các
nút điều khiển vào chính PPTX, giữ các phím gán lại thuộc phiên có Mascot.

- Nút loa và nhãn VI/EN/VI+EN có nền trong. Mỗi ngôn ngữ có hai trạng thái
  loa/pause, điều khiển bằng interactive sequence của PowerPoint: đọc hoặc
  đọc tiếp, tạm dừng; chọn ngôn ngữ khác gửi stop cho các player còn lại.
- Nút nhìn thấy là ảnh thông thường. Audio đặt ngoài khung slide, giữ
  player hoạt động; không đặt audio dưới nút bấm để tránh thanh media khi
  rê chuột. Không tắt toolbar của video/audio gốc trong PPTX độc lập.
- Không dùng Selection Pane hidden cho audio: phép thử Office thật bắt
  được trường hợp player không phát. Nút pause cũng dùng animation
  visibility thay vì hard-hide để animation có thể hiện nó.
- Cấu hình tạo giọng thêm Trái dưới / Giữa dưới / Phải dưới. Lần đầu
  Phải dưới; nhớ lựa chọn gần nhất và vị trí riêng của bài đã chọn.
  Đổi vị trí chỉ lưu metadata, không tăng revision hay tạo lại WAV.
- Tính vị trí một lần cho toàn bộ bài, dự trữ các ngôn ngữ có trong bài.
  Slide chỉ có một phần ngôn ngữ vẫn giữ đúng ô của ngôn ngữ ấy. Bài chỉ
  có tiếng Anh được đặt sát lề thực của cụm một loa.
- Loa luôn đặt ở cùng chân trang; nếu trùng nội dung, báo các slide cần
  kiểm tra. Không tự di chuyển loa sang vị trí khác hoặc sửa nội dung gốc.

## Kiểm chứng và giới hạn

47 ca liên quan export, vị trí, preference, phiên dạy và phím đạt.
Harness Office trên fixture 3 slide nhận 6/0/2 interactive sequence,
giữ nguyên toàn bộ lệnh qua SaveCopyAs; không tự phát; native player
phát/tạm dừng/đọc tiếp được khi audio ngoài canvas; nguồn giữ nguyên.
Harness dùng WAV im lặng để kiểm kỹ thuật, không đánh giá phát âm.

Lượt hồi quy: 899 core đạt (`reports/rc77-core.log`); sau chỉnh fill của
interactive sequence, chạy lại 47 ca liên quan và integration đạt.
11 luồng Qt nền Windows, export native, 8 bài corpus/9 slide và helper
parent-exit đạt; không có cảnh báo QML. Kết quả:
`reports/verification/20261018-221242/result.json`. Hai nhóm Browser AI
104 ca và Browser Translation 14 ca giữ kết quả RC76; RC77 không sửa
hai nhóm đó, không tính chúng là lượt chạy mới. Có một warning dependency
Starlette/httpx trong core, không có ca thất bại.

Đã xuất một bản riêng bài thật Hệ điều hành bằng cache, đủ 86 slide/258
loa, cùng vị trí Phải dưới; không ghi lại bài hoặc source trong thư viện.
Kiểm tra hộp bao báo nguy cơ đè chân trang trên cả 86 slide: đây là cảnh
báo giao hình học, chưa phải kết luận chữ bị che. Giáo viên cần xem F5;
không tự xóa cảnh báo hoặc dời loa từng trang để che kết quả.

Đóng gói sau commit nguồn sạch, tái dùng runtime RC76 đã kiểm manifest;
commit/version/hash của gói được ghi trong BUILD_INFO.json và build-result.
Gói EXE/model, báo cáo thử và bài giáo viên không nằm trong commit mã nguồn.

Computer Use đã dừng sau Escape của giáo viên. Không có bằng chứng
thao tác chuột thật trên nút của bản RC77 trong phiên này; kiểm parser
và Player API không thay thế việc bấm trực tiếp/quan sát icon trên F5.
Các file xuất trước RC77 cần tải lại để có bộ nút mới; không ghi đè
file đang mở của giáo viên. Bài đã tạo giọng dùng lại cache khi xuất.

Các kiểm chứng hệ thống của RC76 được ghi ở [AUDIT_RC76](AUDIT_RC76.md).
Phần Wi-Fi trường, máy chiếu, Windows sạch và chất lượng nội dung vẫn
cần nghiệm thu thực tế; không tự duyệt hay bỏ cảnh báo bài cũ.

## Gói cài và phát hành

- Build một lần từ source `5acaea39e9353e53cd723ea8a8080eb779256842`,
  toàn bộ module ứng dụng được biên dịch lại, runtime/model RC76 kiểm
  manifest trước khi tái dùng. GitHub CI của source đạt:
  [run 39139774371](https://github.com/whitelotus-web/BiliClass/actions/runs/39139774371).
- ZIP `BiliClass-RC77-Windows.zip`, 871.069.229 byte; SHA-256
  `79ec4ab2b2e98cc947997a942b2d63f9c78b14593692b7fe45e6a04bad7974e1`.
  GitHub asset đã upload đủ và digest server trùng với hash gói local.
- Cài/gỡ vào vùng Unicode riêng, Qt Windows, VieNeu Anh/Việt ngoại tuyến,
  template, lớp học và backup đạt; gỡ giữ dữ liệu thử. Kết quả:
  `reports/release/1.0.0rc77-ff847d24/installer.json`.
- Đã cài chính tại `F:/Applications/BiliClass/1.0.0rc77`, đổi shortcut,
  kiểm thêm trang Voice EXE ở 1366×850: ảnh lưu được, không cảnh báo QML.
  Đã mở app cửa sổ bình thường, title RC77 và trạng thái Responding.
  Bản RC73 đang ẩn được giữ, không force-kill Office hoặc ứng dụng cũ.
- So snapshot sau mở: 20 bài giữ nguyên revision/nội dung, 1.449 WAV giữ
  nguyên tên và kích thước. Không chạy tổng hợp mới trên thư viện chính.
- [GitHub Release RC77](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc77)
  có ZIP và SHA-256. Updater kiểm từ RC73 đã nhận đúng RC77 và digest trên.

Lượt cài chính đầu có harness đọc nhầm `$LASTEXITCODE` rỗng là thất bại
sau một script PowerShell thuần đã thành công. Không cài đè lần nữa:
kiểm marker/BUILD_INFO, chạy smoke EXE rồi mở app. Đây là lỗi harness
gọi cài cục bộ; bộ cài và verification có báo cáo riêng đều đạt.
