# Kế hoạch tối ưu BiliClass từ danh sách công cụ GitHub

Ngày đối chiếu: **15/10/2026**. Trạng thái: **đề xuất, chưa triển khai các thay đổi bên dưới**.
Mốc triển khai tiếp theo: [phạm vi RC35 và giới hạn còn lại](OPTIMIZATION_RC35.md).
Đối chiếu mã nguồn RC34 (`0dd792f`), hồ sơ nghiệm thu tại `13dc87a`, tài liệu
đánh giá sơ bộ người dùng gửi và nguồn chính thức của các dự án được chọn.

## 1. Quyết định đề xuất

**Ưu tiên hoàn thiện PowerPoint và loại bỏ các chỗ chờ vô ích trước khi thêm engine mới.**
BiliClass đã có phần lớn nền tảng mà tài liệu sơ bộ đề xuất. Điểm cần cải thiện là
chất lượng đầu ra và hiệu quả vận hành của nền tảng đó.

- Giữ Python/PySide6/QML, Chrome profile riêng, bộ xử lý OOXML và PowerPoint tại máy.
- Giữ quy trình hai bước: **bài song ngữ → tải/trình chiếu**, rồi giáo viên chủ động
  chọn **tạo giọng Việt, Anh hoặc cả hai → dùng voice/mascot**. Voice không kéo dài bước đầu.
- Giữ bốn kiểu song ngữ và các tab Cài đặt hiện có. Một giọng đa ngôn ngữ vẫn đọc cả VI/EN.
- Tận dụng VieNeu đang có; học cách tổ chức audio của Voicebox/Abogen, dùng Midscene
  để thử kiểm tra giao diện; tham khảo Spec Kit/Superpowers cho quy trình phát triển.
- Chưa thay toàn bộ browser driver bằng AI agent; chưa đưa một studio video hoặc
  một dàn engine vào bộ cài dành cho giáo viên.

[Ma trận toàn bộ danh sách](REPOSITORY_REVIEW_2026-10-15.md) có **86 liên kết,
85 URL kho khác nhau**, vì `browser-use/video-use` xuất hiện hai lần. Đọc được metadata
của 76 kho; 9 URL trả 404 trong lần kiểm tra này. 404 không chứng minh dự án đã bị xóa:
có thể đổi tên, đổi quyền hoặc URL không còn đúng. Đây là sàng lọc metadata và đọc sâu
tài liệu nhóm phù hợp, **không phải đã kiểm toán toàn bộ mã hay đo hiệu năng 85 dự án**.

## 2. Hiện trạng cần lấy làm mốc

| Phần | Đã có trong BiliClass | Việc tiếp theo có giá trị |
|---|---|---|
| Chuyển đổi | Nhánh dịch JSON theo ID và nhánh xử lý slide trực quan; cache, checkpoint, tối đa hai tab trong cùng profile | Mở rộng nhánh dựng tại máy an toàn; giảm phần phải đợi file AI dựng lại |
| Tệp và bố cục | Giữ nguồn, ghép quan hệ OOXML, phục hồi media, render/đo chữ bằng Office, cache render | Dịch đủ nội dung và bố trí đúng; phân biệt lỗi nguồn với lỗi phát sinh |
| Browser | Profile Chrome lưu phiên; biên nhận gửi, đối chiếu hội thoại, khôi phục có giới hạn | Phân loại lỗi chính xác, giảm chờ/lặp và kiểm thử các thay đổi giao diện web |
| Giọng đọc | VieNeu v3 Turbo ONNX fp32, sáu preset đa ngôn ngữ, model giữ nóng, cache WAV, chỉnh tốc độ giữ cao độ | Tái sử dụng audio gốc khi đổi tốc độ; đo CPU/GPU và thời gian có tiếng đầu tiên |
| Tạo voice | QThread nền, bỏ qua audio đã có, ưu tiên thao tác đọc trước tác vụ nền | Tối ưu phân đoạn/hàng đợi và bổ sung backend GPU tùy máy sau thử nghiệm |
| Giao diện | Có tiến độ, thời gian, hủy; nhập/mở bài lớn từng có lúc không phản hồi | Đo vòng lặp UI, rút nhẹ callback khi nhập bài, tránh đọc lại dữ liệu lớn |

Bài 6 dùng làm ca hồi quy hiện có: **79 slide, 64 đi nhánh trực quan, 15 nhánh chữ**.
File đã nhận/lưu nhưng còn **24 FAIL, 55 CHECK**. Vì vậy chưa thể gọi RC34 là hoàn thiện
để dạy ngay. 100% nhận/lưu file không đồng nghĩa 100% chất lượng. Các số liệu này là
hồ sơ cũ đã ghi nhận, không phải kết quả chạy thử mới trong đợt lập kế hoạch này.
Xem [trạng thái](STATE.md), [ca nhận kết quả](TRANSLATION_RECOVERY.md),
[kiến trúc hybrid](HYBRID_CONVERSION.md).

Các điểm tìm thấy trực tiếp trong mã:

- `app/native_bilingual.py::extract` phân loại cả slide thành nhánh trực quan khi có
  nhóm chữ, hiệu ứng ở hai kiểu song ngữ, ảnh đáng kể, chart hoặc vùng chữ chật.
  Một ảnh/đối tượng khó có thể kéo cả slide sang nhánh chậm. Không nên gỡ các chốt
  này hàng loạt; cần chứng minh những trường hợp nào xử lý tại máy được.
- `app/speech.py::_vieneu_engine` cố định ONNX/CPU/fp32 với bốn luồng. Hàng đợi nền
  `app/narration_preparation.py` tạo các đoạn còn thiếu tuần tự. Tăng số worker có
  thể tranh CPU và tải thêm model, không mặc nhiên nhanh hơn.
- Khóa WAV hiện gồm cả tốc độ. Đổi tốc độ làm mất khả năng dùng lại file của tốc độ
  trước, dù thao tác WSOLA nằm sau suy luận. Đây là cơ hội tối ưu cụ thể.
- Callback hoàn tất trong `app/ui.py::_run_web_conversion` tạo bản ghi bài và mở bài
  trên luồng UI. Cần profile chi phí tạo/mở/serialize dữ liệu; đây là vị trí cần đo,
  chưa đủ bằng chứng kết luận là nguyên nhân duy nhất làm cửa sổ đứng.

## 3. Công cụ nên lấy gì, dùng ở đâu

| Nguồn | Đề xuất cho BiliClass | Điều kiện và giới hạn |
|---|---|---|
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) | Giữ engine chính, thử GPU batching và streaming; đo cấu hình CPU thích hợp | Đã tích hợp v3 Turbo. README nói `infer_batch` trên CPU vẫn tuần tự; Nano preview giảm chất lượng Anh/song ngữ. Không chuyển Nano chỉ vì tốc độ quảng cáo. GPU cần backend/gói riêng được thử trên Windows |
| [Voicebox](https://github.com/jamiepine/voicebox) | Tham khảo hàng đợi không chặn UI, bản audio gốc và bản hậu xử lý, quản lý model | Chọn ý tưởng phù hợp, không chạy kèm cả studio. Số ngôn ngữ của studio không chứng minh từng engine đều đọc được Việt |
| [Abogen](https://github.com/denizsafak/abogen) | Tham khảo phân đoạn văn bản dài và đồng bộ lời đọc | Chia theo ý/câu, giữ nguồn và thuật ngữ; không thay lời đọc đã kiểm tra bằng văn bản LLM tự viết lại |
| [Midscene](https://github.com/web-infra-dev/midscene) | Thử trong môi trường kiểm thử: thao tác Windows/QML và kiểm tra ảnh slide đã render | Hiện có Windows desktop, không chỉ web. Cần cấu hình model thị giác; có thể thêm chi phí/độ trễ. Không thay phép đo Office hoặc chứng nhận đúng kiến thức |
| [Spec Kit](https://github.com/github/spec-kit), [Superpowers](https://github.com/obra/superpowers) | Tham khảo mẫu đặc tả, sửa lỗi theo nguyên nhân, kiểm chứng trước phát hành | Chỉ phục vụ phát triển. Chọn một quy trình gọn, không cài chồng nhiều bộ chỉ dẫn hoặc đưa vào runtime giáo viên |
| [CodeFlow](https://github.com/braedonsaunders/codeflow) | Sơ đồ phụ thuộc để giảm sửa dây chuyền sai | Có hỗ trợ Python; dùng môi trường nội bộ với dữ liệu đã lọc. Không đưa token, profile hay thư viện cá nhân lên web demo |
| [HTML Anything](https://github.com/nexu-io/html-anything) | Tham khảo mẫu và preview cho lựa chọn “Tạo theo mẫu mới” | HTML đẹp không bảo đảm PPTX tương đương. Phải kiểm tra khi xuất sang PowerPoint; không áp dụng như công cụ bảo toàn bản gốc |
| [VoxCPM](https://github.com/OpenBMB/VoxCPM) | Thử **VoxCPM2** cho giọng chất lượng cao ở giai đoạn sau | Bản 2 hỗ trợ Việt/Anh, 2B tham số; cần đo RAM/VRAM và phát âm. Không làm mặc định trên máy CPU phổ thông |
| [Supertonic](https://github.com/supertone-oss-archive/supertonic) | Chỉ thử **Supertonic 3** như ứng viên CPU dự phòng | 31 ngôn ngữ có VI/EN; repo đã archive, không còn hỗ trợ. Chỉ nhận nếu chất lượng, giấy phép model và khả năng tự bảo trì đạt yêu cầu |
| [Page Agent](https://github.com/alibaba/page-agent) | Thử riêng trong phòng kiểm thử khi cần phục hồi thao tác web | Agent JavaScript trong trang, thường cần LLM riêng; demo miễn phí chỉ dành thử kỹ thuật. Chưa có bằng chứng thay Playwright sẽ nhanh/ổn định hơn |

Ba sửa đổi đối với đánh giá sơ bộ: VieNeu/cache đã có; Midscene có desktop; README
[Voice-Pro](https://github.com/abus-aikorea/voice-pro) có các cập nhật sau ghi chú
tạm ngừng quản lý ở phiên bản cũ, nên không coi ghi chú cũ là trạng thái hiện tại.
Voice-Pro vẫn quá rộng cho lõi BiliClass và có GPL-3.0; không nhập nguyên mã vào
sản phẩm chỉ vì có nhiều tính năng.

Tài liệu sơ bộ còn nhắc [Office Kit PPTX](https://github.com/office-kit/pptx), ngoài
danh sách URL của người dùng. Có thể thử đọc/sửa PPTX ở một nhánh nghiên cứu; đây là
thư viện JS/TS pre-1.0, cần runtime/adaptor và kiểm thử round-trip. Không thay bộ
OOXML/Python hiện tại hoặc tuyên bố giữ mọi hiệu ứng chỉ từ README.

Không chọn Donutbrowser làm cách chữa mất đăng nhập: thay browser bằng anti-detect
không chứng minh sửa được phiên hay tải file. Không dùng 9router/ds2api/codex9router
để biến phiên web thành API hoặc đổi tài khoản vượt hạn mức. Orca là môi trường quản
lý agent lập trình, không phải driver browser hay bộ dựng PPTX.

## 4. Thứ tự triển khai và điều kiện qua từng mốc

### P0 — Đo đúng chỗ chậm, khóa bộ ca kiểm tra

1. Ghi thời gian riêng: phân tích nguồn, nhận bản dịch, nhận file, ghép OOXML,
   render, sửa bố cục, lưu/mở thư viện, rồi voice ở bước hai. Log kỹ thuật ở máy,
   không phơi prompt/tài khoản/các thao tác nội bộ ra màn loading.
2. Dùng bài 79 slide và bộ bài nhỏ có công thức, bảng, hình có chữ, hiệu ứng,
   slide dày chữ và bài văn bản. Có nguồn theo ba cấp, cả bốn kiểu song ngữ,
   “giữ nguồn” và “mẫu mới”. Dùng tệp giáo viên cho phép; chỉ commit fixture tổng hợp.
3. Chạy lại cùng cấu hình/máy/tài khoản để có baseline cold/warm. Tách thời gian
   dịch vụ web với thời gian tại máy; ghi số lượt gửi/sửa, dung lượng và cache hit.
4. Đo UI heartbeat, thời gian click được phản hồi, CPU/RAM/VRAM và thời gian hủy.
   Đếm sự cố/lần lặp thay vì chỉ nhìn %.

**Điều kiện qua:** có bảng số đo tái lập và lỗi theo slide/đối tượng. Không hứa nhanh
gấp nhiều lần khi chưa có baseline. Không dùng thời gian khôi phục từ checkpoint
làm thời gian chuyển đổi cả bài.

### P1 — Bản dịch đủ và bố cục đúng, mở rộng dựng tại máy

1. Giữ ID slide/shape/paragraph; lập danh sách vùng nội dung cần dịch, phần giữ
   nguyên và phần chưa đọc chắc. AI trả bản dịch có cấu trúc, thuật ngữ dùng chung
   theo môn/khối, tránh phải tạo lại toàn bộ PPTX cho những vùng chữ xử lý được.
   Prompt có phần chung và phần cấu hình rõ: môn, cấp/khối, kiểu song ngữ, thiết kế,
   ghi chú giáo viên, thuật ngữ khóa và định dạng trả về. Không dùng một ví dụ Vật lý
   làm quy tắc mặc định cho Ngữ văn, Lịch sử, Ngoại ngữ hay bậc Tiểu học.
2. Tiến dần từ phân loại cả slide sang vùng đối tượng. Ví dụ: ảnh kiến thức giữ
   nguyên, dịch hộp chữ độc lập bên cạnh; chỉ vùng nhãn trong ảnh hoặc tương tác
   phức tạp cần xử lý trực quan. Giữ nhánh cũ nếu chưa chứng minh bảo toàn hiệu ứng.
3. Kiểm tra đủ ID/nội dung thân bài; không chấp nhận chỉ dịch tiêu đề. Khóa số,
   đơn vị, biểu thức, chỉ số, công thức và đáp án ẩn; giữ font/runs hợp lệ. Nội dung
   chưa đọc được trong hình phải được đánh dấu, không suy đoán để lấp chỗ trống.
4. Bố cục là bộ quy tắc tại máy: tiêu đề Việt trên/Anh dưới, cùng font; Anh nghiêng,
   nhỏ hơn nhưng còn đọc tốt; nội dung hai cột thật, từng câu hoặc từ khóa đúng kiểu.
   Mẫu mới có vùng riêng cho hình, chữ và ghi chú, đo text thực tế sau khi đặt.
5. Chế độ giữ nguồn bảo toàn ảnh/media/theme và quan hệ; thêm chữ song ngữ vẫn có
   thể cần thay vùng chữ. Nếu bố cục quá chật, không tự giảm chữ tới mức khó đọc
   hoặc che hình. Giữ bản nguồn và đưa trường hợp cần quyết định ra danh sách ngắn;
   không tự đổi mẫu/tách thêm slide khi giáo viên chưa chọn.
6. Render và đo tràn/chồng; so nguồn/kết quả đúng đối tượng. Tự sửa lỗi xác định
   được tại máy rồi kiểm tra lại; lỗi nghĩa/thiếu dịch gửi đúng phần lỗi, giới hạn
   số vòng, lưu phương án tốt nhất. Không lặp sửa toàn bộ bài.

**Điều kiện qua:** không thiếu bản dịch theo kê khai; không sinh lỗi cứng mới trên
bộ ca; Bài 6 không còn FAIL chưa giải quyết. Các lỗi có sẵn chỉ được phân loại riêng
khi có đối chiếu nguồn, không đổi FAIL thành CHECK để làm đẹp số. Kiểm tra cơ học
không thay giáo viên xác nhận nghĩa và công thức khó.

Với kiến trúc này, một dịch vụ chỉ trả bản dịch có cấu trúc vẫn có ích, không nhất
thiết tự xuất PPTX. Gemini có thể là ứng viên ở vai trò đó, nhưng adapter phải được
thử bằng tài khoản thật trước khi giới thiệu như lựa chọn đã vận hành tương đương;
đề xuất này không tự xóa profile hoặc đổi nhà cung cấp của tác vụ đang chạy.

### P2 — Browser có giới hạn chờ và giao diện không đứng

1. Giữ Chrome profile riêng; khóa quyền sở hữu profile để tránh hai tiến trình
   mở cùng thư mục. Phân biệt hết phiên, xác minh, hạn mức, mất kết nối, lỗi upload,
   lỗi nhận file và kết quả sai định dạng. Lỗi tải file không đồng nghĩa đăng xuất.
2. Upload phải có bằng chứng tệp đã sẵn sàng; sau gửi lưu biên nhận ngay. Khi phục
   hồi, mở lại đúng hội thoại/nhóm đã gửi, không tự gửi lại hoặc đổi tài khoản nếu
   chưa biết lượt cũ thành công hay chưa. Đối chiếu bằng ID và fingerprint hiện có.
3. Chờ theo giai đoạn với tín hiệu tiến triển thực. Có backoff và trần retry cho
   thao tác an toàn; không retry vô hạn. Đang suy luận còn hoạt động khác với đã
   mất liên lạc. Không chờ cả giờ chỉ vì một thanh loading còn chuyển động.
4. Giữ model/suy luận cao nhất thực sự chọn được như yêu cầu sản phẩm. Đo tuần tự
   so với hai tab hiện có trước khi tăng concurrency. Không hứa nhiều tab/tài khoản
   sẽ nhanh hơn; không tự đổi gói hoặc hạ chất lượng để đạt chỉ tiêu tốc độ.
5. Tối ưu UI sau profile: chuyển parse/serialize/ghi bản ghi nặng ra worker phù hợp,
   một bên ghi dữ liệu, trả DTO gọn; chỉ cập nhật model/QML trên luồng chính. Hạn chế
   phát progress/đọc lại mọi slide cho từng sự kiện nhỏ. COM có vòng đời riêng đúng
   luồng; nếu dùng process trên Windows phải bảo vệ entry point/freeze_support để
   không sinh cửa sổ ứng dụng thứ hai.
6. Chỉ một nút Dừng, thời gian trôi thật, trạng thái rõ. % dựa công việc đo được;
   đoạn đợi dịch vụ không biết thời lượng thì dùng chỉ báo đang xử lý, không tăng
   % giả hoặc countdown chắc chắn. Hiện kết quả/việc cần làm khi có vấn đề thực sự.

**Điều kiện qua:** mô phỏng lỗi + thử live có ghi kết quả; không gửi trùng trong ca
khôi phục; UI vẫn thao tác được khi nhập bài lớn. Mục tiêu thử nghiệm: heartbeat
p95 dưới 250 ms, xác nhận nhận lệnh Dừng trong 2 giây; điều đó không đồng nghĩa tác
vụ AI trên web dừng trong 2 giây. Đăng nhập/xác minh bắt buộc vẫn cần chủ tài khoản.

### P3 — Voice nhanh hơn với chính engine hiện tại

1. Hoàn chỉnh hợp đồng provider và giới hạn tài nguyên quanh `speech.py` hiện có;
   vẫn một giọng cho cả Việt/Anh. Giữ model nóng theo phiên, không tải engine cho
   từng đoạn; ưu tiên lời đọc đang dùng và các slide gần đó sau khi giáo viên chọn tạo voice.
2. Tách cache audio gốc khỏi cache biến thể tốc độ. Khóa gốc theo model/version,
   preset, văn bản đã chuẩn hóa, cấu hình phát âm; WSOLA tạo biến thể nhanh/chậm
   từ audio gốc. Di trú giữ các WAV cũ, không làm mất giọng đã tạo.
3. Đo độ dài đoạn và CPU thread budget; thử 1/2/4 luồng suy luận với BLAS được giới
   hạn. Không chạy hàng chục worker CPU trên model có khóa chung. Chỉ đổi số worker
   khi đo được tăng throughput mà không làm UI/âm thanh đang phát bị giật.
   Có thể thử int8 nếu CPU có VNNI và có gói model tương thích; so nghe Việt–Anh
   trước khi bật. Không thay fp32 trên mọi máy chỉ từ một benchmark upstream.
4. Máy NVIDIA đủ bộ nhớ: gói VieNeu GPU riêng, benchmark batch nhỏ tăng dần và
   fallback CPU khi thiếu VRAM. Streaming giúp có tiếng sớm; batch giúp tổng lượng
   audio. Đo riêng hai mục tiêu, không đánh đồng với tốc độ tạo xong cả bài.
   [Tài liệu streaming của VieNeu](https://github.com/pnnbao97/VieNeu-TTS/blob/main/docs/streaming.md)
   có cách đo tiếng đầu/RTF; số của máy tác giả không phải số đã đạt trên BiliClass.
5. Giữ sáu giọng ổn định trước khi tăng lựa chọn. Bộ nghe thử gồm Việt, Anh, xen kẽ,
   tên riêng, số/đơn vị và thuật ngữ nhiều môn. Không đọc mã CHECK hay đáp án ẩn;
   từ khó cần quy tắc phát âm có nguồn, không tự đổi nghĩa công thức.

**Điều kiện qua:** phát âm không giảm trên bộ nghe đã duyệt; cache hit không chạy
lại suy luận; đổi tốc độ dùng lại audio gốc; resume không làm lại đoạn đã đủ. Ghi
thời gian có tiếng đầu tiên, tổng thời gian, hệ số thời gian xử lý/độ dài audio và
RAM/VRAM. Chỉ thêm VoxCPM2/Supertonic sau khi chúng thắng một tiêu chí thực tế.

### P4 — Kiểm thử hình ảnh và phát hành có bằng chứng

- Thử Midscene bằng bản sao dữ liệu tổng hợp: chọn tài liệu, bốn kiểu, sửa lỗi,
  tải PPTX, tạo voice tùy chọn, mở trình chiếu, điều khiển mascot. So ảnh render
  theo vùng; LLM thị giác chỉ bổ sung cho phép đo/quy tắc và kiểm tra giáo viên.
- Dùng quy trình đặc tả → ca lỗi → sửa nhỏ → kiểm chứng. Spec Kit/Superpowers là
  tài liệu tham khảo; chưa cài plugin/skill nào chỉ từ tài liệu người dùng dán.
- Mỗi mốc có bản ghi commit/version, log so sánh, kiểm tra project venv và Qt,
  Office mở/render, rồi mới build một lần. Thử bản source và bản đóng gói trên
  máy Windows thứ hai; kiểm tra updater, đường dẫn Unicode, máy không GPU.

**Điều kiện qua:** không mất bài/profile/audio, nguồn không bị sửa; có thể quay lại
phiên bản trước. Dữ liệu cá nhân và log chứa nội dung bài không đưa lên Git.

## 5. Cách đánh giá “nhanh hơn” và “hoàn thiện”

| Thước đo | Cách nghiệm thu |
|---|---|
| Chất lượng PowerPoint | Đủ slide/đơn vị dịch, đúng số/công thức, không lỗi chồng/tràn mới; media/quan hệ/hiệu ứng kiểm tra theo phạm vi hỗ trợ |
| Thời gian | Báo riêng tổng từ đầu, phần web, phần local, lần đầu và cache; median và p95 sau đủ lượt đo, không báo p95 có ý nghĩa từ một lần chạy |
| Độ ổn định | Số hoàn tất/số chạy, số phải can thiệp, gửi trùng, retry, khôi phục checkpoint; lỗi vẫn được lưu và trình bày đúng |
| Voice | Nghe thử có tiêu chí, thời gian tiếng đầu, tổng thời gian, cache hit, sửa một đoạn chỉ tạo lại đoạn đó |
| Máy giáo viên | CPU-only RAM phổ thông và máy GPU ghi rõ cấu hình; kiểm tra mạng chậm, ngoại tuyến sau khi có bài/audio/model |
| Trải nghiệm | UI phản hồi, một nút dừng, nhãn “Bài song ngữ”/“Có giọng đọc”, chi tiết kỹ thuật thu gọn |

**Mục tiêu thử nghiệm**, không phải mức đã đạt: giảm 30% phần xử lý local so với
baseline cùng máy cho nhóm bài đo được, không giảm chất lượng; phần web báo riêng
vì phụ thuộc dịch vụ/model/tài khoản. Ưu tiên giảm việc phải gửi và sửa hơn là tăng
số tab. Nếu không đạt mục tiêu thì giữ cấu hình cũ và báo số đo.

“Đã lưu bài”, “Có giọng đọc” và “Sẵn sàng dạy” là ba thuộc tính khác nhau. Không
chạy voice để che lỗi PPTX. CHECK do chưa xác minh kiến thức/hiệu ứng phải có đường
xem và quyết định phù hợp, không tự coi đúng mọi môn/cấp chỉ vì qua bộ test kỹ thuật.

## 6. Giới hạn tích hợp và thứ tự chọn cuối cùng

1. **Làm trước:** P0 + P1 + P2, tái sử dụng lõi hiện có; xây ca hồi quy ngay từ P0.
2. **Sau đó:** P3 trên VieNeu; học thiết kế cache/hàng đợi từ Voicebox, phân đoạn từ
   Abogen. GPU là gói tùy chọn, không ép tải về mọi máy.
3. **Thử có kiểm soát:** Midscene cho kiểm thử; mẫu HTML chỉ ở nhánh mẫu mới.
4. **Chưa đưa vào bản mặc định:** VoxCPM2, Supertonic, Page Agent, Office Kit. Chọn
   sau benchmark và kiểm tra khả năng đóng gói/bảo trì.
5. **Để ngoài phạm vi hiện tại:** studio video/âm nhạc, trading, Telegram store,
   OSINT, VPN, quản trị server và các agent harness chồng lấn. Mascot hiện có chỉ
   cần phản ứng theo trạng thái phát/đọc; chưa cần motion capture hay video avatar.

Trước khi lấy mã/model thật: kiểm tra LICENSE ở commit được ghim, giấy phép weights
và từng giọng/tài sản, yêu cầu thông báo phân phối, tương thích dependency và kích
thước gói. SPDX từ GitHub chỉ là sàng lọc; `NOASSERTION`/không có SPDX không tự động
nghĩa là được phép đóng gói. Model packs và executable tách khỏi commit mã nguồn.
Không tự nâng model hoặc thay provider ngầm làm đổi giọng người dùng đã chọn.

Kế hoạch này bổ sung [đề xuất tốc độ 14/10](CONVERSION_SPEED_PLAN.md), cập nhật theo
thực tế RC34; không coi các mục đề xuất trước đó là chưa có nếu mã đã triển khai.
Đợt này chỉ lập và lưu kế hoạch, chưa cài công cụ, thay engine, sửa app hay phát hành RC mới.
