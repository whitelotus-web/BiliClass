# RC74 — Phím đọc và điều khiển loa khi trình chiếu

Ngày 18/10/2026. Tiếp tục RC73; giữ các trang Cài đặt và dữ liệu cá nhân.

## Hành vi

- Khi PowerPoint đang trình chiếu bài gắn với Mascot: Cách đọc Anh,
  Enter đọc Việt, Ctrl+Cách đọc hai ngôn ngữ. Bấm cùng phím/loa để
  phát → tạm dừng → tiếp tục. Đổi ngôn ngữ dừng giọng cũ; Dừng đọc ■
  dừng hẳn, Đọc lại bắt đầu lại.
- ←/→ giữ nguyên điều hướng của Office: chạy/lùi hiệu ứng trước khi
  chuyển slide. ↑/↓ điều chỉnh âm lượng lời đọc 5%, giới hạn 0–100%.
- Cài đặt → Mascot có gán phím, lưu và khôi phục mặc định. Anh/Việt
  dùng đúng một phím; hai ngôn ngữ dùng một modifier và một phím.
  Kiểm tra trùng, phím điều hướng, Esc/F5 và tổ hợp cửa sổ Windows.
- Mascot có bảng hướng dẫn cập nhật theo phím đã lưu, slider âm lượng,
  nhãn đọc tiếp/tạm dừng và loa tương ứng với ngôn ngữ thực có trên slide.
- Hook chỉ nhận đầu vào của cửa sổ slideshow/Presenter View đúng bài;
  ngoài phiên đó phím giữ chức năng gốc. Không gọi COM, đọc đĩa hay TTS
  trong callback. Giữ phím không lặp phát; lệnh của slide cũ bị bỏ.
- Nút loa trong phiên gắn đổi sang hình Ⅱ khi phát; bấm trực tiếp để
  tạm dừng. Ẩn thanh media thừa nếu bài không có video/audio nguồn khác;
  giữ thanh gốc nếu cần điều khiển media của giáo viên. Overlay chỉ nằm
  trong bản trình chiếu tạm, không sửa tệp gốc.
- Giọng đã lưu được tái dùng; tăng/giảm âm lượng không đổi volume Windows
  hay WAV gốc. Đổi âm lượng bản WAV riêng giữ vị trí đọc/tạm dừng.

## Kiểm chứng source

- 882 core tests đạt (127 giây); 49 ca liên quan đạt sau các chỉnh cuối,
  gồm ca mới cho bấm lần hai khi Office đang chuẩn bị giọng.
- Ruff toàn app/scripts/tests đạt. Qt Settings thật: gán phím bằng
  QTest, lưu/khôi phục, không có QML warning.
- Qt + Office: mở/F5, bài gắn độc lập với bài đang xem, ngôn ngữ theo
  slide, native pause/resume, không sửa nguồn; smoke RC73 tiếp tục đạt.
- Thao tác bàn phím/chuột thật trên deck tự tạo, WAV im lặng: Cách phát,
  tạm dừng và tiếp tục; Enter/Ctrl+Cách đổi ngôn ngữ; ↑/↓ cập nhật volume
  của Office; phím A gán lại có hiệu lực ngay; slide im lặng báo thiếu
  giọng và không chuyển trang. ←/→ đã xác nhận click index 0→1→0 trên
  cùng slide có hiệu ứng. Ảnh thực xác nhận badge Ⅱ không chồng hình loa.
- Presenter View của đúng deck đã nhận Cách để đọc Anh, giữ click index 0.
- Chứng cứ tại máy: `reports/rc74/shortcuts`, `reports/rc74-core-tests.log`;
  tệp này không thuộc Git. Chưa chứng nhận âm lượng nghe thực, máy chiếu
  thứ hai hoặc mọi phiên bản Office.

## Phạm vi của PowerPoint độc lập

Phím tùy chỉnh, badge động và việc bấm cùng loa để tiếp tục là điều khiển
của phiên có BiliClass/Mascot đang gắn. PPTX tải xuống vẫn có WAV/loa
native như RC73; mở riêng không mang theo hook hoặc macro. Các thử nghiệm
đổi timing native chưa cho hành vi lặp ổn định, nên không đưa vào bản xuất.
Muốn có điều khiển đồng bộ khi mở file đã tải, chọn file qua Mascot.

## Gói cài

- Đã dựng một lần từ commit `9c62e7564d74979a229ab9b8c8edc75b2027ed26`,
  dùng runtime RC73 đã xác minh. CI source commit này đạt.
- Gói `dist/rc74-slideshow-controls/BiliClass-RC74-Windows.zip`: 871.024.546
  byte, 4.197 entry; đã đối chiếu SHA từng file trong ZIP.
- EXE SHA256: `61864ca659586ed1694550bff0ee8e7f3f7b946cd2157a1cdf731707317a1268`.
- ZIP SHA256: `8e5fbeefe99c7f9e56e420aa0ec1009700ee15a535ae490ed40abbf6bb456722`.
- Đã gọi mở EXE với thư viện fixture riêng. Người dùng bấm Escape dừng
  Computer Use trước bước chọn cửa sổ; chưa nghiệm thu UI EXE hoặc cài
  RC74 thay RC73. Không tiếp tục thao tác giao diện trong lượt đó.
