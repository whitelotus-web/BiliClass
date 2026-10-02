# Thành phần bên thứ ba — bản thử 1.0 RC12

Bản ứng dụng hiện tại dành để kiểm thử tại máy, chưa phải gói phát hành thương mại. Giữ nguyên thư mục `_internal`, các license kèm thư viện và thông tin gói model khi sao chép.

## Kokoro English TTS trong RC7

- Model **Kokoro 82M v1.0** và 5 giọng `af_heart`, `af_bella`, `am_michael`, `bf_emma`, `bm_george`: một model chung, lấy từ gói `kokoro-multi-lang-v1_0` của sherpa-onnx. Nguồn: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2 ; SHA-256 archive: `c5f7e2d2caf082bc1d20fb70334a61d99d20b484500aad32e7cf84c128ea3298`. Gói model có `LICENSE` Apache-2.0 và được giữ trong `models/kokoro-multi-lang-v1_0/`.
- **sherpa-onnx 1.13.8 / sherpa-onnx-core 1.13.8**: Python API + CPU inference; metadata gói ghi Apache-2.0. Nguồn: https://github.com/k2-fsa/sherpa-onnx ; bản đóng gói giữ METADATA/LICENSE trong `licenses/`.
- **ONNX Runtime 1.28.2** được sherpa-onnx-core dùng qua DLL: MIT; giữ LICENSE và ThirdPartyNotices từ tag v1.28.2 trong `licenses/Kokoro-TTS-stack/`. Nguồn: https://github.com/microsoft/onnxruntime/tree/v1.28.2 .
- **eSpeak NG** dùng để chuyển chữ sang âm vị: GPL-3.0-or-later; dữ liệu phát âm và giấy phép COPYING được đóng cùng gói. Nguồn: https://github.com/espeak-ng/espeak-ng . Upstream sherpa-onnx cũng [xác nhận ràng buộc GPL của phiên bản hiện tại](https://github.com/k2-fsa/sherpa-onnx/issues/3731). Cần rà soát nghĩa vụ nguồn tương ứng và phương án giấy phép trước khi phân phối rộng; RC7 là bản dùng thử nội bộ.

Âm thanh được tổng hợp ở máy qua CPU, không gọi API/cloud trong lúc phát âm. Model Kokoro được đóng kèm bản portable và installer RC10; giọng Windows vẫn là phương án tiếng Việt dự phòng nếu máy có sẵn.

## VieNeu tiếng Việt trong RC10

- **VieNeu SDK 3.8.3 / v3 Turbo**: chọn nhánh ONNX CPU fp32, 48 kHz, dùng bốn preset Mai Anh, Thùy Dung, Hải Đăng và Thái Sơn. SDK và model ghi Apache-2.0. Nguồn: https://github.com/pnnbao97/VieNeu-TTS và https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo . Nhánh 0.5B Q8 được cân nhắc từ tài liệu tham khảo nhưng là kiến trúc đời trước; RC10 dùng v3 Turbo sau khi chạy thử trên Windows.
- **MOSS-Audio-Tokenizer-Nano-ONNX**: codec đi kèm engine, model card ghi Apache-2.0. Nguồn: https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX .
- **sea-g2p 0.10.0**: chuẩn hóa và chuyển chữ sang âm vị; repository ghi Apache-2.0. Bản RC10 dùng pipeline này của VieNeu v3; giấy phép gói được giữ trong `licenses/sea-g2p-0.10.0/`. Nguồn: https://github.com/pnnbao97/sea-g2p . eSpeak NG trong phần trên vẫn thuộc stack Kokoro, không phải yêu cầu của VieNeu v3.
- **ONNX Runtime 1.30.0**, NumPy, librosa và các thư viện phụ: thông tin bản cài và notices được thu vào `licenses/DEPENDENCIES.json`. Model và codec tải một lần khi chuẩn bị bản build, rồi đóng tại `models/vieneu-hf/`. Trong ứng dụng, Hugging Face Hub bị buộc offline trước khi VieNeu khởi tạo; không tự tải model khi giáo viên đọc bài.
- Chỉ dùng preset có sẵn, không cung cấp voice cloning. Bốn giọng được nghe thử kỹ thuật trên máy phát triển; chưa có đánh giá chủ quan của giáo viên hoặc benchmark trên laptop 8 GB. Cần kiểm tra thêm với đa môn và Windows sạch trước khi phát hành rộng.

- **PySide6 / Qt**: LGPLv3/GPLv3/commercial theo thành phần. Bản thử dùng Qt động qua PySide6-Essentials. Xem license trong thư viện đã cài và https://doc.qt.io/qtforpython-6/licenses.html. Bộ phát hành chính thức còn phải hoàn thiện thông báo, nguồn tương ứng và nghĩa vụ của từng thành phần.
- **Be Vietnam Pro**: SIL Open Font License 1.1. Tệp đầy đủ tại `biliclass_m0/assets/OFL.txt`, được đóng kèm tài nguyên ứng dụng.
- **CTranslate2**: MIT; **SentencePiece**: Apache-2.0. Dùng suy luận CPU local, không thay đổi mã thư viện.
- **python-pptx**, **python-docx**: MIT; **pypdf**: BSD-3-Clause. Giấy phép và metadata giữ trong môi trường phát triển.

## Gói dịch thử Việt → Anh

Gói Argos `translate-vi_en-1_9.argosmodel`, version 1.9, lấy từ index chính thức Argos và mirror package công khai. Dùng model có sẵn với CTranslate2; chưa tinh chỉnh trọng số. Bản dịch chưa được đánh giá sư phạm để phát hành.

Nguồn package: https://data.argosopentech.com/argospm/v1/translate-vi_en-1_9.argosmodel

SHA-256 archive: `ebd51b7189b13eccb9238a5777de1d343008c4c05284a8b89610242364433953`.

README trong package ghi model OPUS gốc được cấp phép **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/).

Attribution từ package: Jörg Tiedemann and Santhosh Thottingal, *OPUS-MT — Building open translation services for the World*, Proceedings of the 22nd Annual Conference of the European Association for Machine Translation (EAMT), Lisbon, Portugal, 2020.

Giữ `models/vi-en-1.9/provenance.json` và README nguyên bản. Đóng kèm model là tùy chọn `scripts/build.ps1 -IncludeTrialModel`; cài đặt ứng dụng không tự tải model hoặc gửi nội dung bài học ra dịch vụ ngoài.

## Gói dịch thử Anh → Việt

Argos `translate-en_vi-1_9.argosmodel`, version 1.9. Nguồn: https://data.argosopentech.com/argospm/v1/translate-en_vi-1_9.argosmodel

SHA-256 archive: `86957101aa4099aa9a1a7492e41987d938d3cf0fdaf4fb684c0797a9d567dd16`.

README package ghi cùng attribution OPUS-MT và CC BY 4.0 như phía trên; giữ README/provenance tại `models/en-vi-1.9`. Không tinh chỉnh trọng số. `-IncludeTrialModel` đóng kèm cả hai hướng trong bản portable RC1.


## Thành phần bổ sung trong RC1

- FastAPI, Uvicorn, Starlette, httpx, websockets: server lớp học nội bộ và WebSocket. Không gọi dịch vụ cloud.
- qrcode/Pillow: tạo QR và xử lý ảnh tài liệu; PyWinRT: gọi OCR cài trong Windows. Chỉ phân phối binding, không phân phối lại voice/OCR pack của Microsoft.
- pypdfium2/PDFium: render trang scan phục vụ OCR. Giữ notices PDFium và các thành phần đi kèm.
- SQLite được dùng qua Python; thư viện và runtime không chỉnh sửa.

`dist/BiliClass/licenses/` chứa METADATA gốc, bản giấy phép/NOTICE/COPYING tìm thấy trong các distribution đã cài và `DEPENDENCIES.json`. Phiên bản chính xác còn được ghi trong `requirements-lock.txt`. Qt/PySide6 được liên kết động: không khóa việc thay thư viện tương thích; nguồn tương ứng của upstream Qt 6.11 và PySide6 có tại https://download.qt.io/official_releases/qt/6.11/ và https://download.qt.io/official_releases/QtForPython/. Thư mục model giữ nguyên attribution và provenance OPUS/Argos. Bản RC thử tại máy chưa ký số, chưa phải chứng nhận phân phối thương mại.
