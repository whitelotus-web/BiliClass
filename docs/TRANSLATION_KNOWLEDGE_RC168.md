# RC168 · Thuật ngữ theo môn và bộ nhớ tham khảo

Trong **Cài đặt → Dịch thuật → Thuật ngữ theo môn**, có hai lựa chọn:

1. **Dùng thuật ngữ theo môn và câu đã duyệt**: tự chọn phần liên quan trong kho
   nền, lấy môn/lớp/tên bài làm ngữ cảnh và dùng lại câu trùng đã được giáo viên
   duyệt. Không cần giáo viên nhập danh sách thuật ngữ trước.
2. **Tra cứu thêm thuật ngữ mới trên mạng**: đối chiếu tối đa ba cụm từ ngắn mỗi
   bài với nhãn Việt/Anh và mô tả trên Wikidata. Có thể tắt để chỉ dùng kho trên
   máy. Kho tích hợp và bộ nhớ câu đã duyệt không cần Internet; dịch vụ dịch vẫn
   cần mạng theo cấu hình đã chọn.

Bấm **Lưu lựa chọn thuật ngữ**. Lựa chọn được ghim cho bài/hàng đợi mới. Bài đang
dở và các mục chưa chạy trong cùng hàng đợi giữ lựa chọn cũ. Hàng đợi/checkpoint
trước tính năng này tiếp tục không dùng lớp bổ sung, kể cả khi Cài đặt đã bật.
Không đổi dịch vụ, key hay hạn mức dịch vì bật/tắt thuật ngữ.

## Kho nạp sẵn và phạm vi

Kho hiện có **495 khái niệm**, ánh xạ thành **1.195 mục theo môn** cho **30 lựa
chọn môn/hoạt động giáo dục** đang có trong ứng dụng. Môn tích hợp dùng chung
nhóm kiến thức thành phần. Danh mục căn cứ chương trình phổ thông; xem
[nguồn và phạm vi danh mục](SCHOOL_SUBJECTS.md) và
[Thông tư 17/2025](https://congbao.chinhphu.vn/van-ban/thong-tu-so-17-2025-tt-bgddt-46255.htm).

Đây là cặp thuật ngữ Việt–Anh do BiliClass biên soạn, **không phải từ điển chính
thức của Bộ GDĐT**, không bao phủ mọi kiến thức của từng lớp và không phải
chứng nhận mỗi cặp của nhà xuất bản. Nguồn tham khảo chuyên môn nằm trong
`app/terminology_seed.py`, gồm OpenStax, NIST, British Council, National
Geographic, Open Music Theory, Tate, UNESCO, WHO, ILO và Liên Hợp Quốc. Không
tải/sao chép toàn văn sách giáo khoa. Các lựa chọn Ngoại ngữ/Tiếng dân tộc thiểu
số chỉ có một số thuật ngữ ngôn ngữ học cơ bản Việt–Anh, không phải từ điển
riêng cho mọi ngôn ngữ.

Kho cài một lần vào bảng kiến thức hiện có, không đổi schema, không ghi đè thuật
ngữ của giáo viên. Mục mới là tham chiếu cho từ/cụm đứng riêng; không khóa một
danh từ số ít vào mọi câu, tránh phá ngữ pháp số nhiều. Thuật ngữ giáo viên đã
khóa vẫn được ưu tiên. Các bản PowerPoint đã hoàn thành không tự đổi.

Môn/lớp người dùng chọn được giữ nguyên. Nếu môn là “Khác”, có thể suy ra môn
tham khảo khi có ít nhất ba dấu hiệu và không gần hòa với nhóm khác; thông tin
này chỉ phục vụ dịch, không tự sửa môn của bài. Chưa đủ bằng chứng thì không
đoán. Không có cơ chế tự kết luận đề/đáp án nguồn đúng hay tự sửa kiến thức.

## Phần chung và phần riêng từng dịch vụ

| Dịch vụ | Lớp bổ sung được dùng |
| --- | --- |
| Google Cloud / Apps Script | Thuật ngữ đứng riêng, lớp bảo vệ/thuật ngữ chung, câu trùng đã duyệt, cache theo ngữ cảnh |
| Gemini | Các phần chung và dữ liệu tham chiếu môn/lớp/tên bài/thuật ngữ trong prompt; vẫn kiểm tra chỉ số, token, số liệu |
| DeepL | Các phần chung và thông tin bài trong trường `context`; không coi context là lệnh buộc dịch theo một từ |

Định dạng context theo [hướng dẫn DeepL](https://developers.deepl.com/docs/learning-how-tos/examples-and-guides/how-to-use-context-parameter)
và dữ liệu tra cứu theo [Wikibase API](https://www.mediawiki.org/wiki/Wikibase/API).
Không có lời hứa mọi dịch vụ sẽ cho cùng bản dịch hoặc mọi câu đều đúng nghĩa.

## “Học dần” có kiểm soát

- Câu đã duyệt chỉ dùng lại khi trùng nội dung/cách viết, cùng môn và lớp,
  không có bản duyệt khác mâu thuẫn, không đổi số hoặc chứa token bảo vệ.
  Không dùng nháp, lịch sử cũ hay bài đã xóa. Nếu phạm vi bộ nhớ lớn hơn 100 bài
  hoặc 8 MiB nội dung, bỏ qua phần tìm câu để tránh đọc quá nhiều dữ liệu.
- Bài mới chỉ tạo danh sách cụm từ ứng viên; tối đa ba cụm ngắn, không gửi cả
  bài/slide hoặc key sang Wikidata. Chỉ nhận nhãn/biệt danh tiếng Việt khớp,
  có nhãn Anh, mô tả phù hợp môn đã hỗ trợ và một nghĩa duy nhất. Không đoán
  nghĩa khi mơ hồ. Không chạy mã hay làm theo chỉ dẫn trong dữ liệu trả về.
- Mục tra cứu có URL/ID nguồn và trạng thái **tham khảo**, không được đưa vào
  danh sách thuật ngữ khóa. Không đạt tiêu chí thì ghi nhận chưa tìm được,
  tiếp tục dịch bằng kho trên máy. Mất mạng/hỏng cache không chặn chuyển đổi.
- Bộ nhớ tham khảo lưu ở `translation_knowledge/references.db`: tối đa 5.000
  mục và 500 tóm tắt lượt bài; chặn DB ở 24 MiB. Mục cũ được loại khi vượt số
  lượng. Lượt không tìm thấy có hạn dùng một ngày, mục tham khảo 30 ngày.
- `terminology-context.json` trong checkpoint giữ bộ ngữ cảnh đã chọn cho
  dừng/tiếp tục; không tra lại mỗi lần resume. Cache bản dịch tách theo ngữ
  cảnh để không dùng nhầm môn/lớp. Ngân sách tra cứu mục tiêu khoảng 5 giây,
  mỗi yêu cầu có timeout, không có vòng lặp tự học vô hạn.

Đây là tích lũy dữ liệu tham khảo và dùng lại nội dung đã duyệt, **không huấn
luyện lại mô hình**, không tự sửa mã nguồn và không biến một câu dịch máy thành
kiến thức chuẩn. Mục khó chưa xác minh vẫn cần đối chiếu tài liệu chuyên môn.

## Kết quả và dung lượng

Trong **Chi tiết và phạm vi**, bài mới có số thuật ngữ đã chọn, mục tham khảo,
câu đã duyệt được dùng lại, nguồn và dấu hiệu còn cần xem. Báo cáo gắn với hash
PowerPoint cuối; khi đổi file, báo cáo cũ không được trình bày như kiểm tra của
file mới. Chưa chứng nhận toàn bộ ngữ nghĩa, đáp án, công thức hoặc chữ trong ảnh.

Đo riêng lớp bổ sung trên máy phát triển ngày 25/10/2026, bằng
`scripts/benchmark_translation_knowledge.py`:

- JSON gói tham chiếu khoảng **0,43 MB**; tăng DB thư viện khoảng **0,44 MB**.
- Bài giả lập 100 slide: chọn thuật ngữ khoảng **1,06 giây**, dùng checkpoint
  khoảng **0,014 giây**, với `tracemalloc` đang bật.
- Đỉnh cấp phát Python của đoạn đo khoảng **1,9 MB**; đây **không phải RAM toàn
  ứng dụng**, không đo PowerPoint hay model giọng đọc.
- Context checkpoint khoảng **12 KB**; context gửi thử khoảng **1.311 ký tự**.
  Bộ nhớ tham khảo ban đầu khoảng **20 KB**. Không tải thêm model/phụ thuộc.
- Một truy vấn công khai thật “không gian vectơ” nhận được nhãn *vector space*
  với nguồn `https://www.wikidata.org/wiki/Q125977`; không suy rộng thành mức
  bao phủ hoặc tốc độ dịch của mọi môn/dịch vụ.

Dữ liệu cá nhân, cache, bằng chứng kiểm tra và file thực thi không nằm trong
commit. Cache tham khảo có thể tạo lại nên không nằm trong sao lưu thư viện;
câu đã duyệt vẫn nằm trong dữ liệu bài và được sao lưu như trước.

## Kiểm tra lại

```powershell
. ./reports/rc155/source-env.ps1
& ./.venv/Scripts/python.exe -m pytest tests/test_translation_knowledge.py tests/test_translation_provider.py tests/test_alternative_translation.py tests/test_google_conversion.py tests/test_batch_jobs.py -q
& ./.venv/Scripts/python.exe -m scripts.qt_translation_provider_smoke reports/rc168-knowledge-qt
& ./.venv/Scripts/python.exe -m scripts.benchmark_translation_knowledge
```

HTTP dịch trong kiểm tra tự động là fixture; không tuyên bố đã đánh giá chất
lượng dịch thật của cả bốn nhà cung cấp qua mọi môn. Tính năng trên nhánh
`codex/translation-providers-rc168`; không đổi main/tag/bộ cài RC167 và không
tạo bộ cài mới trong đợt này.
