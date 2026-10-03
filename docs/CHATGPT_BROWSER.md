# Gửi và nhận PowerPoint thủ công trong browser

Mã nguồn ngày 03/10/2026. Chưa đóng vào release rc12.

Đây là cách gửi thủ công dự phòng. Luồng tự gửi/chờ/tải thử nghiệm và quản lý tài khoản nằm trong [Browser AI](BROWSER_AI.md). Trong Cài đặt → Browser AI, tắt **Tự gửi tài liệu, chờ và tải PowerPoint qua web ChatGPT**, rồi lưu để hiện các bước bên dưới.

## Sử dụng

1. Nhập tài liệu, điền tên bài/môn/khối, chọn level 0–4 và sắp xếp song ngữ.
2. PPTX: chọn giữ thiết kế gốc hoặc mẫu BiliClass. DOCX/PDF/TXT/ảnh: dùng mẫu BiliClass. Mở **Xem slide mẫu** để xem thiết kế bằng ví dụ và hình minh họa.
3. Chọn **Browser AI · ChatGPT**, bấm **Chuẩn bị & mở ChatGPT**. Browser mặc định của Windows mở `chatgpt.com`; đăng nhập tài khoản của giáo viên nếu chưa có phiên đăng nhập.
4. Bấm **Sao chép prompt**, dán vào ChatGPT. Bấm **Mở thư mục tài liệu**, đính kèm `tai-lieu-goc.*` và `mau-biliclass.pptx` nếu có. Bấm Gửi tại ChatGPT. Gói ZIP chỉ để lưu/chia sẻ; có thể giải nén rồi đính kèm từng tệp.
5. Tải `.pptx` kết quả về máy. Chọn **Nhận PowerPoint từ ChatGPT**, xem các slide hoặc mở toàn bộ bài.
6. Kiểm tra nghĩa, thuật ngữ, số liệu/công thức, hình, hiệu ứng. Bấm **Dùng để dạy** và xác nhận. PowerPoint đã nhận mở nguyên trạng, cùng mascot khi cần.

Ở chế độ thủ công này, giáo viên thực hiện thao tác gửi/tải trong browser; app chỉ chuẩn bị và nhận tệp. App không gọi API hoặc thu thập mật khẩu. Browser AI tự động dùng hồ sơ đăng nhập riêng và bấm Gửi khi giáo viên chọn Chuyển đổi; không xuất cookie/token. Việc tạo PowerPoint và số lượt dùng phụ thuộc tính năng/hạn mức tài khoản. Có thể yêu cầu ChatGPT xuất tệp nếu chỉ nhận được dàn ý. [Hướng dẫn tạo slide của OpenAI](https://learn.chatgpt.com/use-cases/generate-slide-decks).

Giữ thiết kế là yêu cầu đưa vào prompt, không phải đảm bảo ChatGPT giữ được mọi hiệu ứng/đối tượng. Nội dung hình nhúng trong PowerPoint có thể không được đọc qua cách trích xuất văn bản; khi cần đối chiếu, giáo viên đính kèm thêm ảnh slide quan trọng. [File Uploads FAQ](https://help.openai.com/en/articles/8555545-file-uploads-faq).

## Trợ giảng và dữ liệu

Prompt yêu cầu ghi chú `VI:` và `EN:` trên từng slide. BiliClass đọc chữ/ghi chú có sẵn bằng parser nhẹ, không OCR hoặc dịch lại file nhận về. Cặp nhận diện vẫn là nháp cho đến khi giáo viên xác nhận. Nếu không đủ cặp, slide vẫn trình chiếu; app báo số slide có nội dung song ngữ để mascot đọc. Không đoán bản dịch cho slide ảnh. Giọng đọc cần gói voice trên máy; không cần gói model dịch/OCR để dùng luồng browser.

Chốt file trình chiếu không tự duyệt quiz, trợ giảng mở rộng hoặc kho kiến thức. Văn bản không đủ cặp vẫn chưa đủ điều kiện cho phần classroom cần nội dung song ngữ. Sửa văn bản trong editor không tự sửa file PowerPoint nhận về; app chặn dùng bản chữ đã sửa cùng file cũ. Nhận bản PPTX mới để tiếp tục.

Gói nằm trong `chatgpt/<request-id>` của thư viện cá nhân, gồm prompt, cấu hình, bản sao nguồn, hướng dẫn, mẫu nếu dùng và ZIP. App nhớ gói cuối để tiếp tục sau khi đóng/mở. Tệp nguồn và kết quả lưu theo SHA-256; mở/chốt kiểm tra file, revision và chữ nhận từ file. Đổi file hoặc chữ làm mất hiệu lực xác nhận. Gói bài chuyển máy giữ kết quả nhưng yêu cầu giáo viên bên nhận kiểm tra lại.

## Kiểm tra phát triển

- `.venv`: `pytest` toàn bộ 189 kiểm thử đạt; Ruff đạt.
- `scripts/qt_chatgpt_handoff_smoke.py`: level/layout/workflow hiện trên luồng chính; gói đúng cấu hình; xem mẫu có hình; nhận PPTX nguyên byte; render bằng Office thật; xác nhận cả bài và map mascot; mở lại bài đã lưu.
- `scripts/qt_quick_conversion_smoke.py`: luồng ngoại tuyến vẫn dịch hai hướng bằng model thật, xuất/xem PowerPoint và chốt cả bài.
- Kiểm thử Qt chặn mở browser và phiên slideshow cuối, không gửi tài liệu lên ChatGPT. Chất lượng PowerPoint do ChatGPT tạo cần thử bằng tài liệu thật và tài khoản giáo viên.

Chạy bằng môi trường/cache của `scripts/run.ps1`. Kiểm thử dùng thư viện tạm dưới `.runtime`, bằng chứng nằm trong `reports`; không đưa dữ liệu giáo viên, gói hoặc bản build vào Git.
