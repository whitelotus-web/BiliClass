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
audio; đã bổ sung dependency, kiểm lượt mới sau push. Lint script/test, gói/frozen,
bản cài và commit/hash gói cập nhật sau vòng kiểm tương ứng.
