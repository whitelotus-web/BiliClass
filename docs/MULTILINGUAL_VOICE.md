# Giọng chung Việt–Anh — RC17

**Cài đặt → Giọng đọc** chỉ chọn một giọng VieNeu cho bài giảng, English Reader,
đọc tiếng Việt, VI Rescue và mascot. Câu xen Việt–Anh cũng dùng cùng speaker.

1. Chọn một trong sáu giọng: Mai Anh, Thùy Dung, Ngọc Trân (nữ); Hải Đăng,
   Thái Sơn, Quang Sơn (nam). Nhãn Bắc/Trung/Nam mô tả giọng Việt của preset,
   không hứa giọng English bản ngữ Mỹ/Anh.
2. Kéo tốc độ từ **82% đến 118%**; nút **100%** trả về bình thường.
3. Bấm **Nghe thử**; có thể sửa câu mẫu thành câu trong môn đang dạy.
4. Bấm **Lưu giọng và tốc độ**. Chọn/nghe thử chưa thay cấu hình đã lưu.

Sáu preset lấy từ model **VieNeu-TTS v3 Turbo**, SDK **3.8.3**, suy luận
ONNX CPU fp32 và codec 48 kHz. Model đã có trong BiliClass; không cần cài thêm
VieNeuTTSApp. Đây là hỗ trợ Việt/Anh và code-switching của model, không phải
hỗ trợ mọi ngôn ngữ trên thế giới. Không cần API key, phí API hay mạng khi đọc.
Model tải một lần khi chuẩn bị bộ cài; ứng dụng buộc Hugging Face Hub offline.

Nguồn: [VieNeuTTSApp](https://github.com/NguyenSiTrung/VieNeuTTSApp),
[model VieNeu](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo),
[SDK](https://github.com/pnnbao97/VieNeu-TTS).

Tốc độ dùng WSOLA giữ cao độ, tham khảo transform Apache-2.0 của VieNeuTTSApp
(revision ghi trong `docs/licenses/VieNeuTTSApp-NOTICE.md`). Mẫu tốc độ 100%
giữ nguyên waveform. Tăng/giảm tốc độ không thay giọng hoặc đổi engine.

## Dữ liệu cũ và giới hạn

- Nếu chưa lưu cấu hình mới, giữ preset VieNeu tiếng Việt cũ làm giọng chung
  và giữ mức tốc độ đã chọn. Giọng cũ không còn/không hợp lệ dùng Mai Anh khi
  model sẵn sàng; thiếu model báo rõ, không giả vờ có giọng đa ngôn ngữ Windows.
- Cấu hình mới là một bản ghi `voice_options` (voice + rate), lưu nguyên tử.
  Hai khóa `vi/en` ở bộ đọc chỉ là alias của cùng ID, không còn hai bộ chọn giọng.
- Kokoro/SAPI không còn được dùng để tạo giọng mới hoặc đóng trong bộ cài.
  Bài học, audio cũ và thư viện giáo viên không bị xóa. WAV portable hợp lệ vẫn
  có thể phát; muốn giọng mới phải tạo lại âm thanh với cấu hình mới.
- Cache gồm nội dung, speaker, tốc độ và phiên bản engine/WSOLA. Đổi cấu hình
  dùng WAV mới; không phát nhầm cache tốc độ/giọng cũ. Bộ đọc dừng trước khi lưu.
- Giọng English của preset Việt cần giáo viên nghe và lựa chọn cho lớp;
  phép kiểm tra WAV không chứng nhận mọi thuật ngữ/công thức đều phát âm chuẩn.
  Quy tắc bỏ chữ trong ảnh, công thức và lời đọc không chắc vẫn giữ nguyên.

## Kiểm tra có thể chạy lại

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_multilingual_voice.py tests/test_speech_readiness.py tests/test_english_reader.py tests/test_browser_audio_cache.py tests/test_pack.py
.\.venv\Scripts\python.exe -m scripts.verify_multilingual_voice
.\.venv\Scripts\python.exe -m scripts.verify_settings_ui
.\.venv\Scripts\python.exe -m scripts.qt_english_reader_smoke
```

Script âm thanh tạo 18 WAV Việt/Anh/câu xen cho sáu preset, kiểm tra cache,
PCM mono 48 kHz, năng lượng/duration và tốc độ chậm/bình thường/nhanh. Kết quả
tại `reports/app/multilingual-voice/`, không đưa vào Git. Unit test kiểm tra
cao độ 220 Hz qua bảy mức tốc độ, dữ liệu cũ và cấu hình khi mở lại thư viện.
Qt kiểm tra draft/nghe thử/lưu và bộ đọc qua mascot trên PowerPoint thật.
