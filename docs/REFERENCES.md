# Tài liệu tham khảo kỹ thuật

Đã đối chiếu ngày 29/09/2026. Ưu tiên tài liệu chính thức. Các trang chứng minh khả năng của thành phần, không chứng minh BiliClass đã được xây hoặc đạt hiệu năng. Phiên bản cụ thể và tương thích cần kiểm chứng ở M0.

| Nguồn | Áp dụng trong kế hoạch |
|---|---|
| [Qt for Python — QML Application Tutorial](https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html) | Kết nối Python và Qt Quick/QML |
| [Qt — pyside6-deploy](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html) | Thử đóng gói và tài nguyên QML |
| [Microsoft — SlideShowNextSlide](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.application.slideshownextslide) | Event trước chuyển slide; cần xác nhận state thực tế |
| [Microsoft — SlideShowWindow](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowwindow) | Adapter trình chiếu PowerPoint |
| [python-pptx](https://python-pptx.readthedocs.io/en/latest/) | Đọc/tạo/cập nhật PPTX, phân biệt với render |
| [CTranslate2 — Installation](https://opennmt.net/CTranslate2/installation.html) | Windows x64 và runtime phụ thuộc |
| [CTranslate2 — Hardware support](https://opennmt.net/CTranslate2/hardware_support.html) | Yêu cầu CPU cho binary |
| [CTranslate2 — Quantization](https://opennmt.net/CTranslate2/quantization.html) | INT8 là ứng viên cần benchmark |
| [CTranslate2 — Transformers](https://opennmt.net/CTranslate2/guides/transformers.html) | Chuyển model trên máy build |
| [Helsinki-NLP — opus-mt-vi-en](https://huggingface.co/Helsinki-NLP/opus-mt-vi-en) | Ứng viên dịch VI→EN, tokenizer/model card |
| [Helsinki-NLP — opus-mt-en-vi](https://huggingface.co/Helsinki-NLP/opus-mt-en-vi) | Ứng viên dịch EN→VI; chú ý target language token |
| [Microsoft — SpeechSynthesizer.AllVoices](https://learn.microsoft.com/en-us/uwp/api/windows.media.speechsynthesis.speechsynthesizer.allvoices?view=winrt-26100) | Liệt kê voice thực tế của backend Windows tương ứng |
| [FastAPI — WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) | Kết nối thời gian thực và xử lý disconnect |
| [pypdf — Extract Text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | Text extraction và giới hạn PDF scan |
| [pypdfium2](https://pypdfium2.readthedocs.io/en/stable/) | Adapter render PDF |
| [Tesseract — Language data](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html) | Dữ liệu OCR local theo ngôn ngữ |

Đầu vào người dùng nằm ở refs/README.md và refs/inputs. Các đoạn tư vấn model lập trình trong đầu vào không cần thiết để quyết định kiến trúc BiliClass và không được dùng làm ràng buộc kế hoạch.

Giọng Windows SAPI: [SpeechVoiceSpeakFlags](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee125223(v=vs.85)) — dùng SVSFIsNotXML để nội dung bài luôn được đọc như văn bản.
