# RC73 — Khôi phục, giọng đọc và giao diện

Ngày 18/10/2026. Source đang hoàn thiện theo phản hồi thử trực tiếp của
giáo viên. Bộ cài RC72 đang mở không bị dừng khi sửa source RC73.

## Đã kiểm chứng ở mốc source đầu

- 972 ca kiểm thử đạt theo ba tiến trình: 854 core, 104 browser AI, 14
  browser translation. Lượt monolithic bị treo trong Playwright/Chrome sau
  nhiều phiên; ca bị treo chạy riêng đạt, ba nhóm chạy riêng đạt. Lệnh kiểm
  chuẩn đã tách nhóm; chưa kết luận nguyên nhân treo monolithic đã hết.
- Hai lỗi đầu vòng core đã xử lý: thông báo cấu hình có sẵn và fallback
  tên voice trong popup. Nhóm 55 ca liên quan chạy lại đạt trước vòng cuối.
- Qt giọng/diễn giải chuyển đổi, popup tạo lại và bảo toàn nguồn đạt; mặc
  định lần đầu là Tiếng Anh theo yêu cầu mới nhất, nhớ lần chọn gần nhất.
- Sao lưu thư viện thật 8.040.765.784 byte rồi restore 20 bài; restore gói
  cũ 2.231.885.510 byte được 17 bài, integrity SQLite đạt. Tệp giữ tại máy,
  không ở Git. Không bao gồm model, key hoặc phiên đăng nhập trong gói này.
- 8 corpus tự tạo đã render bằng PowerPoint qua worker riêng: 9 slide đầu
  ra, không còn FAIL kỹ thuật; CHECK vẫn giữ cho hình/hiệu ứng/phần cần
  người xem. Group nguồn có 2 vùng overflow, đầu ra không còn overflow.
  Sau kiểm ảnh bảng, sửa lượng có đơn vị như `12 kg` để không nhân đôi
  trong cặp ngôn ngữ; 41 ca và native bảng sau sửa đạt.
- 6 voice có VI/EN/xen kẽ/công thức và bộ WAV để nghe tay. Có mẫu dùng
  cache; không phải chứng nhận phát âm/thuật ngữ bởi giáo viên.

Chi tiết triển khai và phần còn chạy: [IMPLEMENTATION_RC73](IMPLEMENTATION_RC73.md).
Nghiệm thu điện thoại, máy chiếu, Windows sạch và nghe tay:
[ACCEPTANCE_FIELD](ACCEPTANCE_FIELD.md). Kênh nguồn/phát hành:
[RELEASE_CHANNEL](RELEASE_CHANNEL.md).

## Còn cập nhật trước khi chốt gói

## Mốc giọng và PowerPoint

- Vòng core sau sửa: 862 đạt; 104 browser AI và 14 browser translation ở
  mốc source đầu còn áp dụng (không sửa logic browser). Tổng 980 ca theo nhóm.
- Hộp lưu Windows thực có sẵn tên tiếng Việt, mở lại đổi đúng bài; cùng tên
  ngôn ngữ/giọng ở workspace, thư viện và PPTX trong ZIP.
- Bài thật 86 slide, 355/355 đoạn: xuất 258 nút loa trên 86/86 slide, không
  còn trang không đặt được loa; 251 WAV khác nhau nhúng nội bộ. File nguồn và
  bài đã lưu giữ nguyên, không suy luận lại hoặc gửi mạng. Phát VI/EN/chung,
  pause/resume native trên slide 1, 13, 15, 59, 60 đạt; ảnh cửa sổ F5 thấy loa.
- Loa đọc **toàn bộ lời đã lưu của slide khi bấm**, kể cả phần xuất hiện sau;
  không đồng bộ tự động theo hiệu ứng. Mascot chọn riêng đọc theo phần đang
  hiện, chỉ dùng cache và không đọc vùng chưa xác định hiển thị. Không coi
  WAV không rỗng/API playback thành kiểm chứng âm thanh qua loa vật lý/phát âm.
- Qt chuyển đổi, giọng, storage, home, thư viện, lớp học, độ đáp ứng và phiên
  PowerPoint đạt. Giọng kiểm thêm 150% DPI; sửa phép đo ảnh của smoke theo
  devicePixelRatio. Mascot F5 có HWND dự phòng đúng cửa sổ, nút dừng đỏ và
  đổi trạng thái khi native player phát.
- Mẫu nghe thử ở cấu hình dùng câu VI–EN đã đóng gói cho từng giọng, không
  tải model/suy luận lại chỉ vì radio đang chọn Anh hoặc Việt.

## Phạm vi chưa nghiệm thu

Phiên dài ghi được 49 phút/5.877 lần điều hướng rồi bị gián đoạn; không có
kết quả hoàn tất 60 phút. Trong mẫu đã ghi, handles khoảng 7.369, RSS từ
493 MB xuống khoảng 198 MB; gap UI lớn nhất 1,063 giây. Catalog gọi refresh
theo revision, không thực hiện quét lại toàn bộ mỗi lần. Không chứng nhận
không rò bộ nhớ hoặc nhanh hơn từ lượt đo này.

Ứng viên bài khôi phục cũ dựng bằng 246 đơn vị cache đã kiểm 70 trang bằng
Office, giữ media/nguồn nhưng vẫn 44 FAIL/26 CHECK sau 179 thay đổi; không
thay bài đã lưu hoặc đánh dấu chất lượng đạt. Bài đang thử voice còn cảnh
báo tràn chữ slide 15; giọng hoàn tất không đồng nghĩa bố cục đã được duyệt.

GitHub CI hai lượt đầu thiếu pywin32 cho fixture COM rồi numpy cho nhúng
audio; bổ sung dependency, lượt `5d650cc` đạt. Lint app/script/test sạch;
161 ca và ba Qt liên quan đạt sau dọn lint. Bước format 16 file giữ nguyên
AST, sau đó sửa import và biến giữ vòng đời Qt trong commit riêng.

Kiểm ảnh xuất thật bổ sung: thứ tự loa VI → EN → VI+EN được giữ ở cả cụm
thường và cụm nhỏ; mở rộng nhãn nhỏ để VI+EN không xuống dòng. Thêm ca
vùng header hẹp, 27 ca export/phiên dạy/thư viện đạt. Gói/frozen, bản cài và
commit/hash gói cập nhật sau vòng kiểm tương ứng.

Giữ chiều cao cụm loa nhỏ ở 20 pt để vừa header 26 pt có lề 6 pt; tăng độ
rộng nhãn thay vì tăng chiều cao. Fixture vùng hẹp và 18 ca audio/phiên dạy
đạt; xuất lại bài thật có đủ 258 loa/86 slide, không thiếu vùng đặt hoặc lời.

## Gói đã cài và kiểm chứng

- Source gói: `58ab0d28103ebcc9426a28bd6a3de40e5f0bce9f`, version `1.0.0rc73`.
  CI source của commit này đạt. Tất cả module app biên dịch từ source đã
  commit; dependency/model dùng runtime baseline có manifest/hash kiểm đủ.
- EXE SHA-256: `ee16bd11ab281bc67db0d1335eb486052d80b4d066a49e37c3b7d48e4710bac2`.
- ZIP 871.000.738 byte, 4.194 mục; hash
  `08441097b8f10cb98f94fa39f0e9a8c569de9a67074a47b1217a9546d203c119`.
  Mỗi nội dung ZIP đối chiếu manifest và CRC, không chứa dữ liệu giáo viên.
- 8 trang EXE cuối đạt, không QML warning: Home, New, Voice, Library,
  Settings, Classroom, Reports, Editor. Cài thử ở đường dẫn Unicode, kiểm
  hai trang từ bản cài; self-test model VieNeu thật VI/EN/xen kẽ/tốc độ/cache,
  template, lớp học spawn/WebSocket, backup và gỡ cài giữ thư viện đều đạt.
  Bằng chứng máy: `reports/release/1.0.0rc73-826fb2e8/installer.json`.
- Cài tại `F:/Applications/BiliClass/1.0.0rc73`; Desktop/Start menu trỏ RC73.
  Thư viện `F:/BiliClassData` giữ nguyên, không chuyển hoặc phục hồi đè. RC72
  được đóng bình thường khi không còn tác vụ, cả cửa sổ Mascot còn mở; không
  cưỡng bức dừng và không mở đồng thời hai bản ghi chung thư viện.
- Bản xuất kiểm cuối có đủ 3 loa ở từng trang trong 86 trang; native phát
  VI/EN/chung, pause/resume trên 1, 3, 4, 13, 15, 59, 60 đạt. Giữ bản nguồn,
  bài đã lưu và cache cũ. Đợt này chưa tạo GitHub Release công khai.
