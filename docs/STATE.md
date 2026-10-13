# Trạng thái BiliClass

Ngày 13/10/2026 — nguồn RC23: thu gọn báo cáo vào Xem chi tiết, giữ cảnh báo
slide cần sửa trước khi dạy; âm thanh nền có trạng thái gọn và tín hiệu Qt
riêng. Nút cập nhật/phiên bản luôn hiện kể cả bản nguồn và cửa sổ thấp, có
hộp cài bản Windows tại trang đang mở. Tạo giọng chỉ xếp phần chưa có WAV;
đủ cache thì không nạp model hoặc chạy warmup. BLAS một luồng trong suy
luận, cùng model FP32/khóa cache, giảm khoảng 17% trên mẫu Việt/Anh đã đo.
Chuyển đổi tự động bỏ ZIP tài liệu không dùng, giữ hash/tệp đính kèm và
tương thích gói cũ. 138 ca liên quan và smoke Qt toàn quy trình qua (Office
preview thật, web/voice fixture, không warning). Kiểm tra chỉ đọc bài thật:
137/137 cache sẵn sàng trong 0,032 giây, không nạp model/gửi bài mới/duyệt
nội dung. Phạm vi và giới hạn tại [Session and speed](SESSION_AND_SPEED.md).
Kiểm tra gói cài đã phát hiện lỗi mở lại DLL từ đường dẫn có dấu; bản sửa
Windows dùng handle DLL đã nạp để điều chỉnh OpenBLAS, giữ khôi phục luồng.
Ca DLL thật ở thư mục tiếng Việt qua; bản lỗi chưa được phát hành.

Ngày 13/10/2026 — đã phát hành [RC22](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc22)
từ commit `e64c256728da477b45227bbe7d1eaeef2715ca4d`. ZIP 679.268.868 byte,
SHA-256 `6b93e62926a937ecb926dd7c70b3cada1f2b4828c1183c53d208ebbb3b652cbf`;
asset và checksum đã được đối chiếu sau tải lên. Build một lần sau kiểm tra
nguồn, 572,04 giây. Archive CRC/manifest qua. Do ổ chứa dự án đang có hàng
đợi I/O cao, kiểm tra cài/gỡ được thực hiện từ ZIP giải nén trong thư mục thử
trên ổ hệ thống: Unicode, Qt 1366×850 và portable 1080×700 qua, không warning;
VieNeu Việt/Anh/mixed/tốc độ/cache, mẫu, lớp học process/WebSocket và sao lưu
qua bằng runtime đóng gói. Đây là kiểm tra trên máy hiện tại với dữ liệu
riêng, chưa phải chứng nhận một Windows sạch. Báo cáo thuộc reports ngoài Git.

Đã nhận và lưu bản PPTX thật sau một lượt sửa trong cùng cuộc trò chuyện:
48 slide, 48 notes VI:/EN:, 69 media giữ nguyên byte và 41 slide giữ timing.
Office render đủ 48 slide; lỗi giảm từ 36 FAIL/12 CHECK xuống 15 FAIL/33 CHECK.
Kiểm tra ảnh vẫn thấy chỗ tràn/che chữ, nên chưa chứng nhận sẵn sàng dạy và
không tự duyệt nội dung/câu hỏi. Đã tạo đủ 137/137 đoạn WAV bằng cùng giọng
đa ngôn ngữ, không lỗi/bỏ qua; kiểm tra cache và mẫu WAV có tín hiệu qua,
không phát âm thanh trong kiểm tra. Bản nháp trước được giữ trong thùng rác
có thể khôi phục. Không đưa bài, prompt, âm thanh hay phiên tài khoản lên Git.

Ngày 13/10/2026 — nguồn RC22 xử lý thông báo dung lượng kho tệp khi web đã
nhận tệp vào cuộc trò chuyện: chỉ đóng đúng hộp “File added to chat only”,
không bấm quản lý/xóa kho tệp và không che lỗi tải tệp, hạn mức hay xác minh.
Kiểm tra bằng Chrome với overlay thực tại bước đính kèm và nhận kết quả.
Lượt sửa chất lượng dùng lại PPTX/tài liệu của đúng cuộc trò chuyện; báo cáo
được đưa trong prompt. Free không tải lại PPTX, báo cáo hoặc ảnh kiểm tra;
gói trả phí đính kèm tối đa hai ảnh ví dụ. Giữ một lượt sửa có bản ghi và
không tự duyệt bài/câu hỏi. Nhóm browser/account/dispatch/health 121 ca qua,
ca Free sửa một lần và cache không gửi lại qua; smoke Qt toàn quy trình qua
với Office preview thật, không QML warning. Web/voice trong smoke dùng fixture.

Kiểm tra trực tiếp sau khi giáo viên cho phép gửi lại một lần: đã nhận được
PPTX thật 48 slide, lưu vào thư viện; 69 tệp media giữ nguyên byte, 41 slide
giữ cấu trúc timing và đủ 48 notes VI:/EN:. Tác vụ không cần lượt yêu cầu
xuất tệp thêm. Bản nhận đầu có 36 FAIL/12 CHECK khi render và đo bằng Office;
không coi việc nhận tệp là xác nhận đủ chất lượng để dạy. Bài và bằng chứng
chi tiết thuộc thư viện cá nhân/reports ngoài Git.

Ngày 13/10/2026 — đã phát hành [RC21](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc21)
từ commit ứng dụng `8ad9710545e51d636996717ce3131c0b7d5ac0b4`.
Build một lần sau kiểm tra nguồn, 574,26 giây. ZIP Windows 679.268.139 byte,
SHA-256 `73e567a56d598a3ea766639bbf05b38e5e88bdd1f478463cb393039cc1b4b424`.
CRC/manifest/checksum qua; cài/gỡ Unicode, Qt 1366×850, portable Qt 1080×700,
giọng VieNeu Việt/Anh/mixed/tốc độ/cache, lớp học process/WebSocket, mẫu và
sao lưu qua, không warning Qt. Bài đang dở của giáo viên không bị gửi lại.
Phạm vi/bằng chứng ở reports/rc21-progress và
reports/release/1.0.0rc21-52a8494a (dữ liệu thử nghiệm ngoài Git).

RC21: sửa kích hoạt nút gửi trực tiếp thay Enter và mở nội dung user thu gọn
trước khi so khớp đầy đủ để tìm lại xác nhận. Tiến trình và footer dùng thông
tin phù hợp giáo viên, tách khỏi chẩn đoán kỹ thuật trong bản ghi. Tác vụ dừng
vẫn báo tạm dừng, không dùng loading để che lỗi hoặc tăng % theo thời gian.
Kiểm tra bài cũ trên Chrome thật chỉ đọc: tài khoản vẫn đăng nhập, bản nháp
đầu vào còn trong composer nhưng chưa thấy xác nhận phù hợp; không tự gửi
lại một lượt cũ chưa rõ kết quả. 112 ca browser/dispatch/progress qua; một ca
chỉ so chuỗi lỗi cũ đã đổi sang kiểm tra mã lỗi và hành vi không gửi lại,
chạy riêng qua (tổng 113 ca). Smoke Qt tiến trình mọi stage/lỗi qua, không
warning. Handoff Qt toàn luồng qua: gửi/nhận tự động bằng fixture, prompt đúng
preview, tiến trình/lỗi, byte PPTX, Office preview thật, duyệt bài, ánh xạ
mascot và mở lại bài. Fixture giọng đọc cập nhật theo worker nền RC19 và
khử trùng hai đoạn VI/EN, không chạy voice thật hoặc gửi ChatGPT trong smoke.

RC20 đã phát hành từ commit `420d757b7f97b69a88535badac503af585671f20`:
ZIP Windows 679.265.709 byte, SHA-256
`ea187617445cbb23ac94d4261cd7457110ced48c7fb0334e43e5bba4387dfd5c`.
Cài vào đường dẫn Unicode, hai trang Qt, mẫu, một speaker VieNeu Việt/Anh,
classroom process, backup và gỡ giữ thư viện đều qua. Kiểm tra ở máy hiện tại,
không coi là chứng nhận Windows sạch. Máy chạy nguồn có tiêu đề
“Bản phát triển từ mã nguồn” và không hiện cập nhật bộ cài; không suy ra RC
chỉ từ ảnh giao diện nguồn.

RC20 nguồn đã kiểm tra ngày 13/10/2026: logo trường đã lưu hiển thị ở hồ sơ
thanh bên, thay ảnh/bỏ ảnh cập nhật ngay và không kéo méo. Dòng copyright tác
giả ở chân cửa sổ, riêng với trạng thái/lỗi và không tự thêm vào bài/prompt.
Browser AI đổi chỗ với Song ngữ nhưng giữ định danh tab/đường dẫn cũ; mỗi
profile có Mở tài khoản theo luồng Chrome hiện có, không tạo profile mới và
khóa khi tác vụ/profile đang dùng. Qt kiểm tra logo, hai vị trí tab, hai nút
mở đúng ID và footer ở 1366×850/1080×700 qua, không warning. Việc mở profile
trong smoke dùng fixture, không gửi bài/đăng nhập ChatGPT thật. 20 kiểm thử
thư viện và sức khỏe Browser AI qua. Smoke Qt Browser AI hiện có cũng qua,
gồm giữ phiên, retry đúng chat không gửi trùng, cache và Office preview thật;
bộ cài mới được tạo sau mốc kiểm tra.

RC19 nguồn đã kiểm tra ngày 13/10/2026: giữ phiên Chrome qua các lượt chạy nền,
không thêm tab trắng mỗi lần kiểm tra; lưu/mở PowerPoint trước rồi tự chuẩn bị
âm thanh ở nền, ưu tiên lượt cần đọc và chống tạo trùng WAV. Cấu trúc Settings
và quyền duyệt slide giữ nguyên. Phạm vi/bằng chứng tại [SESSION_AND_SPEED](SESSION_AND_SPEED.md).

78 ca core qua; lượt rộng browser/Chrome 78/79 qua, một fixture dùng hai URL
giả cho cùng yêu cầu nên bị chặn đúng bởi quy tắc không gửi trùng sau session
restore. Fixture sửa dùng cùng URL như server thật: 14 ca khôi phục/Chrome qua,
chín ca Chrome chạy lại qua, gồm cookie phiên/local storage, profile tách biệt,
không thêm tab trắng và Chrome đăng nhập thường với cookie có thời hạn.
Qt Browser AI, startup resume, luồng lưu trước âm thanh bị chặn/lỗi và reader
thật PowerPoint/VieNeu/MCI đều qua, không QML warning. Hai profile Free trên
máy đã kiểm tra lại thành công, không gửi bài mới. Không coi fixture là bằng
chứng một bài mới đã hoàn tất trên ChatGPT; không bảo đảm web không thu hồi
phiên hoặc luôn tạo được PPTX.

Ngày 13/10/2026 — đã phát hành [RC19](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc19),
commit ứng dụng `b9016f580385887b53deb9572cd6689be403d323`. Build một lần từ
mốc nguồn đã kiểm tra; ZIP có 3.879 tệp, 679.265.177 byte, SHA-256
`f43f83a20fe90c67a18b515e572fff3d4fe36c0e29708459f17c7aa5292c3de8`;
GitHub đã xác nhận digest và dung lượng. Bộ cài ở thư mục Unicode riêng qua
manifest, Qt nhập bài/Browser AI, mẫu/ảnh xem trước, VieNeu cùng giọng Việt/Anh,
tiến trình lớp học và sao lưu; gỡ giữ thư viện. Kiểm tra không dùng cache phát
triển. Phạm vi là máy Windows hiện tại, chưa chứng nhận Windows sạch/máy thứ hai.

Ngày 13/10/2026 — đã phát hành [RC18](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc18),
commit ứng dụng `61264c90dce533da69cce963516faa4a08997c28`. ZIP có 3.879 tệp,
679.257.153 byte, SHA-256 `2e37853924f4845b56d989a553f871259ec119e895d23b40867f6b816d902994`;
GitHub đã xác nhận digest và dung lượng. Cài/gỡ vào thư mục Unicode riêng qua:
Qt nhập bài/Browser AI, VieNeu cùng speaker Việt/Anh, templates, lớp học và
sao lưu, gỡ giữ thư viện. Đây là kiểm tra trên máy hiện tại, chưa phải chứng
nhận Windows sạch/máy thứ hai. RC18 đã mở đúng bài vừa nhận, cửa sổ phản hồi,
nhãn phiên bản và Slide 1/79 xác nhận qua UI Automation.

RC18 khôi phục xác nhận gửi, không gửi lại bài khi chưa rõ trạng thái, tự tiếp
tục tác vụ đã cho phép sau khởi động lại và giữ lệnh Dừng. Lỗi tác vụ không
được dùng làm lỗi đăng nhập chung của các profile. Chrome fixture kiểm tra
overlay, timeout sau phím gửi, mất URL, nhận lại không gửi trùng và chat không
khớp/trùng; Qt Browser AI và Qt startup timer/Dừng qua, không có QML warning.
Bộ kiểm tra rộng có 130 case qua và một assertion câu thông báo cũ thất bại;
sau sửa câu thông báo, riêng case đó qua. Bộ dispatch/health/progress 49 case,
bốn case nhận xác nhận và các smoke Qt cuối đều qua. Chi tiết: [BROWSER_RECOVERY](BROWSER_RECOVERY.md).

Yêu cầu thật bị kẹt đã tìm lại trên chính profile, nhận PPTX 75.246.124 byte,
lưu 79 slide và tạo 238/238 đoạn giọng đọc, 151 tác vụ trùng được gộp, không
có lỗi âm thanh; dữ liệu riêng không đưa vào Git/release. Kiểm tra slide báo
34 CHECK và 45 FAIL (chủ yếu chữ tràn/đối tượng vượt mép, có cảnh báo văn bản
kỹ thuật). Bài giữ bản nháp, cần đối chiếu/sửa; chưa khẳng định sẵn sàng dạy.
Yêu cầu cũ không có cờ `quality_review_version`, nên không tự thêm lượt sửa
web vào yêu cầu này. Luồng tạo bài mới hiện có kiểm tra và một lượt sửa có giới hạn.

[RC17 đã phát hành](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc17),
commit ứng dụng `5551e17d6bf1456fded89f9dd05e9f2c981795dc`. ZIP có 3.879 tệp,
679.251.550 byte, SHA-256 `6de934458266044d3ba779b095bb5b0687f771dd0fb34310bfa364846f5f7b8b`;
GitHub xác nhận digest và updater RC16 chọn đúng RC17. Cài/gỡ bản đã đóng gói
ở đường dẫn Unicode qua, không dùng cache phát triển: Qt nhập bài/Browser AI,
VieNeu VI/EN/câu xen với cùng speaker, tốc độ/cache, templates, lớp học và sao
lưu đều qua; gỡ giữ thư viện riêng. Giới hạn: chưa chứng nhận Windows sạch/máy
thứ hai hay phát âm mọi thuật ngữ. Đã mở RC17 tại Giọng đọc trên máy này, xác
nhận cửa sổ phản hồi và nhãn phiên bản đúng. Hướng dẫn: [USER_GUIDE](USER_GUIDE.md).

Ngày 13/10/2026 — RC17: chuyển sang một giọng VieNeu chung Việt/Anh/câu xen,
sáu preset (3 nam/3 nữ), draft chọn giọng/tốc độ 82–118%, nghe thử rồi lưu nguyên
tử. English Reader, lời đọc Việt, audio chuyển đổi và mascot cùng ID/tốc độ.
Giữ preset Việt/tốc độ cũ khi chưa có cấu hình mới; không xóa bài/audio riêng.
Kokoro/SAPI và model Kokoro không còn nằm trong runtime/bộ cài mới. WSOLA dùng
NumPy, giữ cao độ; nguồn/Apache license đi cùng gói. Chi tiết: [MULTILINGUAL_VOICE](MULTILINGUAL_VOICE.md).

Kiểm chứng nguồn RC17: 70 ca giọng/readiness/pack/thư viện qua sau sửa giữ WAV
khi thiếu model và giữ hai metadata cho waveform chung. Sáu preset tạo 18 WAV
VI/EN/mixed thật, cache và tốc độ qua; Qt Settings nghe thử draft, lưu/mở lại qua
không cảnh báo; Qt English Reader/mascot phát VieNeu trong PowerPoint thật,
pause/resume và dừng đổi slide qua. Kiểm tra waveform không thay đánh giá phát
âm thuật ngữ của giáo viên. Bản RC16 và bằng chứng các mốc trước ghi bên dưới.

Ngày 13/10/2026 — [RC16 đã phát hành](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc16), commit ứng dụng `f921ef347d4df4d39ba37b4ec2da1471073e67f5`: thêm % theo mốc chuyển đổi và số slide/đoạn voice; giữ mốc chờ vì web không cung cấp % tạo bài. Tiến trình lưu riêng, retry không lùi và không gửi trùng. Dùng lại render/phép đo native theo hash PPTX/PNG/phiên bản khi nhập thư viện và xem bài, render tiếp phần thiếu; voice bỏ tác vụ trùng và dùng WAV có sẵn. Thông báo rõ ChatGPT chưa trả PPTX sau một yêu cầu xuất thêm, lỗi voice không làm mất bài; chờ menu model sẵn sàng có giới hạn. Cài đặt giữ cấu trúc. Phạm vi: [CONVERSION_PROGRESS](CONVERSION_PROGRESS.md).

Kiểm chứng nguồn: lượt rộng 195/196 ca qua, một ca menu model chạy chậm không có lựa chọn; sau bổ sung chờ sẵn sàng, 7 ca model (gồm ca menu trì hoãn 800 ms mới) và 91 ca liên quan chạy lại qua. Hai smoke Qt handoff/Browser AI qua, gồm % chờ 25%, lỗi giữ %, lưu 100%, retry cùng chat và native Office preview; không QML warning. 9 ca progress/cache/voice mới qua. Đo Office thật 6 slide: render đầu 7,995 giây, nhập dùng cache 0,121 giây, xem slide đầu 0,006 giây; hash nguồn giữ nguyên. Không suy rộng thành mức tăng tốc ChatGPT hay chứng nhận bài giáo viên thật đã chuyển đổi xong. Tệp/ảnh/báo cáo/profile/model không vào Git.

Bản đóng gói build một lần, cài/gỡ độc lập ở đường dẫn Unicode qua; giao diện new/Browser AI không QML warning, ba mẫu/mười hai bố cục, cả hai giọng offline thật, tiến trình lớp học và backup qua khi bỏ cache phát triển; gỡ giữ thư viện thử riêng. ZIP có 4.257 tệp, 1.038.961.538 byte, SHA-256 `b015da82a18147018d063a511ae15e45a3fdf0399a2348a154492d3549fc5da4`; GitHub xác nhận digest. Updater RC15 nhận đúng RC16 cùng size/hash. Đã mở RC16 ở màn tạo bài, kiểm tra nhãn phiên bản và cửa sổ phản hồi; đóng RC15 bình thường sau kiểm tra không có tác vụ đang chạy. Phạm vi là máy Windows phát triển; chưa chứng nhận máy Windows sạch hay lượt tạo/sửa ChatGPT thật trong đợt này.

Ngày 12/10/2026 — [RC15 đã phát hành](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc15), commit ứng dụng `c6ad431595bbb4aa15351df69c9066f302010b7a`. Thư viện có giờ/ngày tạo và sắp xếp theo tạo/cập nhật, Sửa/Xóa từng bài. Xóa vào thùng rác để khôi phục, giữ nguồn/audio/lịch sử và snapshot báo cáo; bài bị xóa không tham gia memory dịch. Ngày tạo được giữ khi sửa/khôi phục; bài cũ lấy từ lịch sử, mốc ước tính được ghi rõ. Màn slide có Trở lại thư viện/Tải PowerPoint/Dùng để dạy; lưu nguyên tệp đã kiểm hash, không dựng lại và không ghi đè vào dữ liệu nguồn. Gói .biliclass và các thao tác phụ giữ trong menu chia sẻ. Các tab Cài đặt và voice/mascot/Browser AI giữ cấu trúc.

Kiểm chứng: 71 ca thư viện/pack/khôi phục/metadata/tải/updater và các phần liên quan qua; Qt workflow native đã qua sửa, sắp xếp, xác nhận xóa/hủy/khôi phục, Back và Save dialog, không cảnh báo QML. Tệp tải khớp byte với PPTX đang xem. Qt handoff nhập/chuyển đổi/nhận/xem bài qua với Office preview thật. Đã xem ảnh 1366/1080 px. Bản đóng gói cài/gỡ, Qt new/Browser AI, mẫu, hai giọng offline thật, tiến trình lớp học và backup qua với dữ liệu riêng, không cache phát triển; gỡ giữ thư viện. ZIP SHA-256 `a28c2ad7ede615b0304d51df4b9220dc4dc31fc470c9bb97ee512aabfe4fee6f`, GitHub xác nhận digest; updater RC14 chọn RC15. Đã mở bản RC15 ở thư viện trên máy. Không xóa bài giáo viên để kiểm thử; model/bài/profile/ảnh báo cáo không vào Git. Giới hạn QC/ảnh/công thức/animation của RC14 vẫn áp dụng.



Ngày 12/10/2026 — [RC14 đã phát hành](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc14), commit ứng dụng `c55814fb4557df7627c6e723b188c6426d0ee21d`. Thêm English Reader theo đối tượng thực của slide, cả group/bảng/AlternateContent; trạng thái ẩn của nhóm được truyền xuống con. Không chỉ đọc EN trong Notes, không đọc mã rác/nội dung chưa rõ hiển thị. Có pause/resume/stop/replay bằng WAV/MCI thật và hủy khi đổi slide/build. Kiểm tra/render từng slide, đối chiếu body/Notes/metadata và chặn xác nhận FAIL. Bài mới từ UI có tối đa một lượt yêu cầu ChatGPT sửa trong cùng cuộc trò chuyện, giữ bản nháp và dấu chống gửi trùng. Cài đặt giữ nguyên. Chi tiết và phần chưa hỗ trợ: [SMART_SLIDES_READER](SMART_SLIDES_READER.md).

Kiểm chứng RC14: 140 ca reader/slide/refinement/handoff/conversion/PowerPoint/template/dispatch/readiness/updater qua; 75 ca browser/health qua (215 ca tổng). Qt handoff qua với render Office thật, không cảnh báo; Qt English Reader đã phát Kokoro WAV thật qua nút mascot, pause/resume, đọc title + body, dừng khi đổi slide và báo slide chỉ có Việt. Hồi quy bài 65 slide đã render 65/65, phát hiện thân bài thiếu Anh/công thức và ký tự bất thường; không tuyên bố đã sửa xong bài này. Lượt browser sửa sau kiểm tra được thử bằng fixture, chưa chứng nhận lượt sửa ChatGPT thật cho bài đó.

Bộ cài RC14 cài/gỡ độc lập ở đường dẫn Unicode, Qt new/Browser AI không cảnh báo, template/ảnh, cả hai giọng offline thực, tiến trình lớp học và backup đều qua, không dựa vào cache phát triển; gỡ giữ thư viện riêng. ZIP SHA-256 `8897bfc664fe089ac266c25c0d23a2dcda0c09c87a5406381aac239558129f9f`, GitHub xác nhận digest; updater RC13 chọn được RC14. Model/ảnh báo cáo/bài giáo viên/Chrome profile không vào commit. Phạm vi là máy Windows phát triển; chưa chứng nhận chữ trong mọi ảnh, công thức, mọi trigger/animation, mọi môn hay máy Windows sạch. Mốc đầu build được dừng để bổ sung kiểm tra hidden group, bản phát hành được build/kiểm tra lại từ commit trên.



Ngày 11/10/2026 — đã phát hành [RC13](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc13) từ commit `c5437a6c7eb9305b470bd0a0bad3fa89b159f562`. Gói `BiliClass-RC13-Windows.zip` chứa ứng dụng, bộ cài, mẫu/ảnh xem trước, Kokoro/VieNeu và giấy phép; không chứa thư viện giáo viên hoặc Chrome profile. SHA-256: `4558d04de6925ef49609a78930e8e7662ef47bfea262081a474376f679f9a98d`. Mã nguồn vẫn sửa/chạy qua môi trường phát triển bình thường; người dùng Windows tải gói trong Assets thay vì Source code.

Trước phát hành: 76 kiểm thử chuyển đổi/mẫu/updater qua; Qt nhập/chọn cấu hình/xem mẫu và Office preview qua. Kiểm tra bản đóng gói tại thư mục Unicode và dữ liệu riêng đã qua cài/gỡ với manifest, giao diện chuyển đổi/Browser AI không cảnh báo QML, ba mẫu/12 ảnh kiểu ngôn ngữ, giọng Anh và Việt tạo WAV thật (gồm chỉnh tốc độ/cache), tiến trình lớp học và backup. Khi kiểm tra đã bỏ đường dẫn thư viện/model cache phát triển; gỡ ứng dụng vẫn giữ thư viện. ZIP được kiểm CRC và GitHub xác nhận SHA-256 sau upload. Phạm vi là máy Windows phát triển, chưa chứng nhận Windows sạch hoặc mọi môn/bài/mạng lớp. Máy mới cần Chrome, PowerPoint desktop và đăng nhập ChatGPT riêng.



Ngày 11/10/2026 — tích hợp thư viện mẫu người dùng cung cấp: ba PPTX trung tính (12 slide), 12 ảnh bố cục và 12 ảnh kiểu ngôn ngữ, sửa nhãn môn demo. Tách ảnh xem trước khỏi tài liệu gửi; prompt chọn một phong cách, thích ứng theo lớp/môn và giữ độc lập bốn kiểu ngôn ngữ. Giữ PowerPoint gốc không đính kèm mẫu. Gói lưu hash mẫu và giữ nguyên prompt khi tiếp tục qua nâng cấp. 36 ca mới + 33 ca hiện có qua; smoke Qt kiểm tra 12 tổ hợp xem trước, nhập/prompt/chuyển đổi fixture và Office preview thật, không cảnh báo. Các mẫu trống mở/dựng được bằng PowerPoint. Không gửi bài thật hoặc tạo exe/Release mới trong đợt này. Các tab Cài đặt giữ nguyên. Chi tiết: [Thư viện mẫu](TEMPLATE_LIBRARY.md).

Ngày 11/10/2026 — sửa nút Chuyển đổi chạy tự động qua giao diện ChatGPT mới: Send/Stop, vùng câu trả lời theo role và nút tải pressable không có href. Phân biệt tệp chưa tải với không tìm được nút Gửi. Prompt bị web xóa khi đính kèm được khôi phục một lần; prompt bị thay đổi nội dung không được gửi. Lỗi upload/giao diện trước gửi và lỗi chờ kết quả có phục hồi giới hạn; bài đã gửi luôn tiếp tục đúng tài khoản/cuộc trò chuyện, không gửi lại nguồn. Lưu ID câu trả lời để không bỏ sót tệp khi web thu gọn suy luận. Cấu trúc Cài đặt giữ nguyên.

Đã gửi/nhận bài thật trên Free: nguồn khoảng 100 MB; đầu ra 101.583.982 byte, 65 slide, 65 cặp VI/EN, giữ nguyên byte của 118 mục media nguồn. Web tạo bài trong khoảng 21 phút; app tự tải/kiểm tra, hoàn tất 130/130 lời đọc không lỗi/bỏ qua và lưu bài. Cache có đủ 65 Việt/65 Anh hợp lệ; 4 câu hỏi giữ trạng thái nháp. Office dựng được ảnh slide đầu; trang kết quả và nút Dùng để dạy đã hiển thị, sẵn sàng để giáo viên xem/xác nhận. Không kết luận toàn bộ bố cục/bản dịch đã đạt yêu cầu sư phạm chỉ từ kiểm tra cấu trúc. Chi tiết trong BROWSER_AI.md; dữ liệu thầy cô/phiên/PowerPoint/WAV/bằng chứng ngoài Git.

Kiểm chứng: lượt nhóm browser/dispatch/health/Chrome có 105 ca qua; 11 ca cho câu trả lời mới/ID khi thu gọn/tái gửi an toàn chạy lại sau bổ sung ID, cùng ca tải pressable bổ sung đều qua. Qt handoff và Browser AI qua bằng fixture web/voice với Office preview thật, không QML warning. Qt teaching qua với PowerPoint toàn màn hình, kéo/click mascot, giọng English cục bộ, đổi slide/thoát/mở lại và hash nguồn không đổi. Ruff qua. Chưa tạo exe/Release mới hoặc nghiệm thu Plus/máy thứ hai trong đợt này.

Ngày 10/10/2026 — Môn học trong luồng chuyển đổi đổi thành danh sách chung ba cấp, theo bảng chữ cái tiếng Việt, có môn tích hợp/môn tự chọn/hoạt động giáo dục; Khác ở cuối hiện ô nhập tay. Chưa chọn hoặc nhập trống thì chưa chuyển đổi. Môn chọn/nhập tay truyền đúng vào prompt xem trước, yêu cầu gửi và bài lưu. Có nguồn chương trình Bộ/giải thích phạm vi trong SCHOOL_SUBJECTS.md; không đổi các tab Cài đặt.

Cùng đợt, tái hiện lỗi Browser AI trên hồ sơ thật: đã đăng nhập trên Chrome nhưng bộ nhận diện ô prompt cũ không thấy textbox mới nên trả `interface`. Bổ sung textbox Ask ChatGPT/Hỏi ChatGPT trong form và bỏ Loading profile khỏi tên. Kiểm tra lại bằng đúng hồ sơ Chrome: tên tài khoản, Free, ready=True, Think đang bật; lưu trạng thái xác nhận thành công mà không gửi tin/tài liệu. Model có bộ chọn phải được xác nhận sau chọn trước khi upload; nếu không có bộ chọn dùng mặc định web + suy luận được phép, không khẳng định tên model cụ thể của Free. Chưa nghiệm thu chuyển đổi một bài thật/Plus thật trong đợt này.

Kiểm chứng: 62 test danh sách môn/cấu hình/prompt/handoff; 92 test Browser AI/Chrome/health/dispatch đạt (90 trong lượt đầy đủ, 2 test textbox mới chạy lại sau sửa charset UTF-8 của fixture và đối chiếu toàn bộ nội dung thay vì số dòng trắng do contenteditable tạo). Qt handoff/Browser AI qua cả luồng và Office preview, không QML warning; dropdown có cuộn, chọn bằng bàn phím, Khác và prompt gửi kiểm tra đủ. Ruff và diff sạch. Đã mở bản nguồn ở Browser AI với phiên Free đã xác nhận; chưa đóng gói exe/phát hành mới.

Ngày 10/10/2026 — sửa nhập tài liệu và cấu hình theo phản hồi giáo viên. Tái hiện ba bài Vật lý không hiện do vượt 50 MB: dung lượng 70.906.619, 104.330.108 và 76.958.905 byte. PPTX nay hỗ trợ 200 MB, đồng bộ chọn/tạo gói/browser/nhận/lưu nguồn; loại khác giữ 50 MB. Lỗi hiện ngay ô tài liệu, có tên tệp/Đã nhận tệp khi thành công, không gửi nhầm nguồn trước nếu lần đổi tệp lỗi. Chrome do tool mở trên máy khai báo kết nối local để tệp trên 50 MB đính kèm được; không thay hạn mức tài khoản web.

Giữ thiết kế PowerPoint gốc chọn được trước khi nhập, PPTX mặc định giữ gốc, giữ lựa chọn mẫu mới nếu giáo viên đã chọn; tài liệu khác giải thích rõ dùng mẫu. Thêm ghi chú giáo viên tối đa 6.000 ký tự, ghép đúng một lần sau cấu hình phương pháp/thiết kế trong prompt và lưu/mở lại yêu cầu. Quá giới hạn không cắt mất ghi chú. Khối lớp chỉ 1–5/6–9/10–12 theo cấp, đổi cấp đặt lại khối hợp lệ. Tên bài dài không ép co ô môn/cấp/khối. Bỏ tệp xóa tên tự điền, giữ tên do giáo viên đổi. Cấu trúc Cài đặt hiện có giữ nguyên.

Kiểm tra: hộp chọn Windows thật đã nhận đủ chín bài gốc Toán/Tin/Vật lý và một PPTX mẫu tên Unicode/đuôi viết hoa; đổi/hủy lựa chọn qua, SHA256 các nguồn không đổi. Ca browser PPTX 51 MB dùng Chrome thật và HTTP local qua đính kèm/tải/lưu/mở lại/cache, không gửi trùng. Smoke Qt handoff, Browser AI và native picker qua, không QML warning; ảnh đã được xem, gồm ghi chú, tên bài dài và cửa sổ nhỏ. Gửi/nhận AI và voice trong smoke dùng fixture, preview dùng Office thật. Hai lượt kiểm tra liên quan đều sạch: 76 ca input/prompt/handoff/dispatch/thư viện/gói, 60 ca browser/Chrome (tổng 136, không phải toàn bộ suite). Ruff và diff qua. Chưa gửi tài liệu giáo viên thật lên ChatGPT trong đợt này, chưa đóng gói/phát hành lại exe. Xem [quy trình](FOUR_FORMAT_WORKFLOW.md).

Ngày 10/10/2026 — trang chuyển đổi có kéo thả/chọn một tài liệu với kiểm tra định dạng và 50 MB; bốn ô chọn loại chuyển đổi độc quyền, mỗi ô có ví dụ bố cục lớn và nút chọn từ ví dụ. Hai ô thiết kế giữ PPTX đầu vào/tạo theo mẫu mới; cấp học đưa cạnh thông tin cơ bản. Ô prompt Hiện/Ẩn dùng cùng bộ tạo với yêu cầu gửi thật, cập nhật theo cấu hình và tên tệp gốc, không tạo gói khi gõ. Bỏ Tùy chọn thêm/gửi nhận thủ công/bật tắt chuẩn bị voice trong luồng mới; chuyển đổi luôn tự động nhận PPTX và chuẩn bị cặp giọng đã lưu. Bỏ liên kết phục hồi thủ công cũ; giữ tài liệu/yêu cầu thủ công đã lưu và cấu trúc các tab Cài đặt hiện có. Nút chuyển đổi cố định cuối màn hình.

Kiểm tra đợt giao diện: 105/105 ca input/prompt/handoff/browser/account/dispatch qua; hai smoke Qt nhập/chuyển đổi và Browser AI qua, không QML warning. Đã kiểm tra kéo thả native Qt, chooser, chọn đúng một kiểu, cả bốn ví dụ, mặc định PPTX/ảnh, prompt xem trước bằng đúng prompt gửi, cửa sổ 1366×850 và 1080×700, tự nhận PPTX/chuẩn bị narration, xem trước Office thật, duyệt/mở lại bài và giữ câu hỏi nháp. Đã xem ảnh giao diện được dựng. Gửi/nhận ChatGPT và voice trong smoke dùng fixture, không gửi tài liệu thật hoặc đổi thư viện của giáo viên. Ruff và kiểm tra diff qua. Chưa đóng gói/phát hành lại exe; cần giáo viên thử bài thật để đánh giá kết quả AI.

Ngày 10/10/2026 — đã đọc phần browser của VeoSuite_V3 và áp dụng cơ chế phù hợp: Chrome profile riêng có khóa và kiểm tra tiến trình đang dùng, giữ renderer nền hoạt động thay vì thu nhỏ cửa sổ, chọn/đọc lại mức suy luận được phép, health check một profile cần kiểm tra khi rảnh. Phân biệt mạng tạm gián đoạn, mất phiên và hết lượt; kiểm tra đăng nhập không xóa quota. Thời gian thử lại lấy từ thông báo tương đối hoặc tạm hoãn 30 phút khi chưa rõ; không coi đây là số dư hạn mức. Bấm Chuyển đổi kết thúc probe nền rồi tiếp tục, không bắt đăng nhập lại. Kết quả đã tải được nhập tiếp dù tài khoản mất phiên/hết lượt; bài đã gửi giữ đúng account/URL. Cấu trúc Cài đặt và bốn phương pháp chuyển đổi giữ nguyên. Xem [tham khảo và vận hành](BROWSER_VEOSUITE_REFERENCE.md).

Kiểm tra đợt này: nhóm browser/account/dispatch/Chrome/handoff 98/98 qua; sau bổ sung nhường probe cho chuyển đổi, chạy nhóm health/reasoning liên quan 22/22 qua (gồm một ca mới dùng QThread thật); ba ca khóa/xóa/cooldown qua sau thêm chặn xóa profile đang mở. Qt Browser AI qua toàn luồng fixture Plus hết lượt → Free gửi một lần → phục hồi đúng cuộc trò chuyện → PPTX/lời đọc/xem trước Office → cảnh báo phiên và xóa từng profile. Không QML warning; Ruff và diff sạch. Browser dùng Chrome thật với fixture chặn mạng/localhost, chưa thử gửi một bài thật ở đợt sửa này. Chưa đóng gói/phát hành lại exe.

Ngày 09/10/2026 — đã thực hiện kế hoạch thu gọn sau bước chuyển sang bốn **Kiểu chuyển đổi**. Bài mới: Hai cột song ngữ, Song ngữ từng câu, Tích hợp từ khóa, Tiếng Anh 100%; tài liệu → phương pháp → giữ PowerPoint/mẫu → Browser ChatGPT → nhận/xem → dùng để dạy. Prompt giữ số lượng/thứ tự slide PPTX; số slide kết quả khác nguồn được cảnh báo. Ghi chú VI:/EN: tách khỏi CHECK/QUIZ; câu hỏi nhận thành nháp theo slide, cần duyệt riêng. Tiếng Anh 100% giữ Việt ở ghi chú lời đọc.

Đã gỡ module OAuth/Responses, đăng nhập OAuth cũ, đường gọi dịch/OCR và bộ chọn cũ trong editor; yêu cầu OAuth đang dở được báo đã nghỉ, không tự gửi lại. Dữ liệu trợ giảng gom nội dung thầy cô đã duyệt và kiến thức có nguồn trong một mục. Báo cáo gợi ý phương pháp có mô tả, không tăng/giảm level số. Bài/gói/AI hỗ trợ đã lưu vẫn có bộ đọc tương thích, không cần token hoặc model dịch. Không xóa model, thư viện hoặc Chrome profile cá nhân. Cài đặt Chung/Giọng đọc/Mascot/Browser AI giữ cấu trúc. Xem [quy trình và phần đã thu gọn](FOUR_FORMAT_WORKFLOW.md).

Kiểm tra sau thu gọn: pytest toàn bộ 276 ca qua, một ca CDP Chrome localhost timeout; chạy lại ca đó cùng nhóm báo cáo/lớp học bằng cache đầy đủ: 39/39 qua. Tổng cộng 277 ca qua sau chạy lại. Qt menu dữ liệu/bài L5 cũ, handoff, browser fixture, Office preview, PowerPoint fullscreen/mascot/English voice đều qua; không QML warning. `verify_settings_ui.py` đầy đủ đã qua với phát voice Anh–Việt thật và lưu Cài đặt. Sửa offline Hugging Face và cache thư viện/model đã có trên ổ người dùng khắc phục timeout khi nạp từ ổ dự án. Ruff và diff sạch. Hai ca bổ sung cho script thu giấy phép cũng qua; không chạy lại toàn bộ suite sau sửa script đóng gói.

Bản độc lập RC13 tại `dist/rc13/BiliClass` đã tạo và kiểm tra riêng trên bản sao ổ người dùng: archive đúng phiên bản, không có module OAuth/dịch/OCR đã nghỉ, chỉ hai thư mục model voice; Playwright driver 1.63.0 chạy được. Qt trang nhập bài lưu ảnh, không QML warning. Self-test `.exe` qua với DOCX/PPTX, bốn prompt, SQLite/gói/lịch sử, WAV Kokoro/VieNeu thật, chỉnh tốc độ và cache, tiến trình lớp học/WebSocket/báo cáo, export và sao lưu/khôi phục. Không dùng PYTHONPATH hoặc model cache của bản nguồn. Đã sửa thiếu DLL llvmlite và dependency MSVC đi kèm ở bước finalize; script giấy phép đọc RECORD/SOURCES trực tiếp để tránh stat mọi tệp thư viện phát triển. Báo cáo/mẫu dữ liệu/bộ cài nằm ngoài Git; build record ghi phiên bản và commit trong thư mục build. Đây là bản thử trên máy phát triển, Release công khai vẫn RC12. Chưa gửi bốn bài thật lên ChatGPT để nghiệm thu chất lượng sư phạm, thử cài/nâng cấp trên Windows sạch hoặc máy thứ hai.

Ngày 04/10/2026 — bổ sung đặt mascot cùng màn hình với slideshow ngay khi bắt đầu bài, kể cả vị trí cũ nằm trên màn hình khác; sau đó vẫn kéo tự do. Smoke Qt/Office đã chạy lại thành công trên cấu hình màn hình hiện tại, gồm vị trí cũ/màn hình chiếu, voice, slide trống và đóng/mở lại. Bài thật 12 slide đã mở trong PowerPoint toàn màn hình trên màn hình phụ của máy; không còn cửa sổ BiliClass nhân đôi. Chưa chứng nhận mọi cấu hình máy chiếu hoặc bộ cài RC12.

Ngày 04/10/2026 — sửa luồng **Dùng để dạy**: mở PowerPoint gốc nhận về ở chế độ trình chiếu toàn màn hình, tự hiện mascot trong suốt đã bật, đọc English theo slide thực tế và dừng lời đọc khi đổi/đóng slide. Bỏ âm thanh tổng hợp xong muộn của slide trước; không dùng lời đọc cũ cho slide trống. Khắc phục hộp Save As làm kẹt lần mở tiếp theo bằng cách bỏ thay đổi thiết lập của riêng deck chỉ đọc, không ghi tệp. Bản thử trước đã chạy qua launcher thiếu main guard gây nhân đôi app; dùng entry chính thức `python -m app --page result --lesson-id <id>` để mở đúng bài đã lưu. 30 kiểm thử liên quan và smoke Qt/PowerPoint/giọng Anh thật đã qua: xác nhận cả bài → fullscreen/mascot → phát WAV → điều khiển slide trong Office và mascot → đóng → mở lại; cả hai bản nguồn giữ nguyên SHA, không QML warning. Thử trên một màn hình; chưa nghiệm thu máy chiếu/máy giáo viên khác. Mã nguồn mới, chưa thay bộ cài RC12.

Ngày 04/10/2026 — đã gửi và nhận PowerPoint thật qua Chrome web sau khi sửa timeout đính kèm, tên tệp đánh số, xuống dòng ProseMirror và nút artifact/Download file của giao diện hiện tại. Kết quả hợp lệ 12 slide/25 mục media/12 ghi chú; số slide/media bằng nguồn, chưa xác nhận chất lượng sư phạm/bố cục. Tự phục hồi mạng/browser/tải kết quả tối đa hai lần trên cùng bài khi trạng thái gửi chắc chắn; giữ tài khoản và không gửi trùng. Chrome của đúng tiến trình BiliClass chạy ẩn trên Windows; bước đăng nhập vẫn hiện. Gửi/nhận thủ công nằm trong Tùy chọn khác. 78 kiểm thử và smoke Qt web/Office đã qua; các ca nhận tệp chạy lại sau sửa Download. App đã lưu bài thật, xác nhận đủ 12 WAV Việt/12 WAV Anh và render ảnh xem trước bằng Office; bài chưa tự duyệt. Chưa phát hành bộ cài mới. Xem [Browser AI](BROWSER_AI.md).

Ngày 04/10/2026 — đã xác nhận đăng nhập thật thành công qua Chrome thường và lưu phiên. Thu gọn Browser AI thành từng dòng tài khoản với tên/gói, đèn trạng thái và **Xóa profile** trực tiếp; ẩn menu, chính sách lựa chọn và số dư chưa đọc được. Tự chọn Plus còn dùng được rồi Free; chuyển tài khoản chỉ khi chưa gửi bài, giữ cuộc trò chuyện khi đã gửi/chưa rõ xác nhận. Kiểm tra phiên chỉ đọc khi mở tab và định kỳ năm phút; mất phiên yêu cầu đăng nhập lại, hết lượt không làm đăng xuất. 66 kiểm thử và smoke Qt web/Office, Qt OAuth cũ đã qua; chuyển tài khoản và gửi/nhận là fixture. Chưa nghiệm thu gửi/nhận PowerPoint thật hoặc phát hành bộ cài mới. Xem [Browser AI](BROWSER_AI.md).

Ngày 04/10/2026 — sau phản hồi lỗi **400 Invalid content type** và chưa đăng nhập được, tách bước đăng nhập sang Chrome thường với hồ sơ riêng, chưa gắn Playwright/DevTools. Nút chính đổi thành **Kiểm tra và lưu**; sau xác nhận hoặc đóng Chrome, mở lại cùng hồ sơ và xác nhận phiên trước khi lưu. Nhận diện lỗi 400 riêng, gỡ trạng thái sẵn sàng và giữ dữ liệu hồ sơ. 54 kiểm thử browser/Chrome/handoff, smoke Qt web/Office và đăng nhập OAuth cũ đã qua; ca Chrome thường thật chỉ dùng cookie fixture trên localhost. Lần chờ đăng nhập thật chưa có xác nhận trước khi hết thời gian, **chưa kết nối được tài khoản thật và chưa chứng minh khắc phục lỗi web**. Xem [Browser AI](BROWSER_AI.md). Chưa phát hành bộ cài mới.

Ngày 04/10/2026 — chuyển Browser AI sang **Chrome riêng** theo yêu cầu. Bỏ việc luôn ép hồ sơ về Edge; giữ hồ sơ cũ và yêu cầu đăng nhập lại một lần. Mở Chrome cài trên máy qua DevTools cục bộ; tác vụ thu nhỏ dùng cùng chế độ browser với đăng nhập. Chỉ đánh dấu kết nối sau khi đóng/mở lại Chrome và xác nhận phiên đã lưu; không tự đóng xác minh sau một phút. 47 kiểm thử browser/Chrome/handoff và smoke Qt/Office đã qua; dữ liệu đăng nhập và AI là fixture. Chưa xác nhận tài khoản ChatGPT thật. Bằng chứng và giới hạn ghi trong [Browser AI](BROWSER_AI.md). Đây là mã nguồn mới; bộ cài RC12 chưa bao gồm.
Đợt ổn định Browser AI ngày 04/10/2026: browser chạy trên máy và lưu hồ sơ Free/Plus, không thêm API key hay dịch vụ browser trả phí. Giữ tài khoản mới chưa đăng nhập được để mở lại đúng hồ sơ; gỡ trạng thái sẵn sàng khi phiên hết hạn/cần xác minh. Nút **Đăng nhập và tiếp tục** nối lại đúng bài/tài khoản sau khi xác nhận đăng nhập; giữ bước phục hồi qua lần mở tool. Tránh nhận PPTX từ câu trả lời cũ, nhầm nội dung bài về giới hạn với quota, hoặc gửi prompt bị mất trong lúc tải tệp. 38 kiểm thử browser/handoff và smoke Qt web/Office, Qt OAuth cũ đã qua với fixture. Chưa xác nhận đăng nhập/chuyển đổi bằng tài khoản ChatGPT thật. Xem [Browser AI](BROWSER_AI.md).

Thử thật ngày 04/10/2026: xác minh Cloudflare bị lặp cả trong browser riêng của tool và browser thường theo phản hồi người dùng; chưa kết nối được. Đã bổ sung nhận diện, thông báo và dừng trang xác minh bị kẹt sau một phút, lưu lỗi và lựa chọn gửi/nhận thủ công. 21 kiểm thử browser và Qt/Office fixture qua; chưa chứng minh khắc phục được chặn thực tế. Không suy đoán nguyên nhân là Free/Plus. Cần kiểm tra truy cập bình thường trên mạng khác trước khi thử lại tích hợp.

Ngày 04/10/2026: Browser AI mặc định dùng phiên web Free/Plus, mỗi tài khoản một hồ sơ Edge. Có thêm/xóa, ưu tiên Plus cho bài mới, cố định Free để kiểm thử, giữ tài khoản cho bài đã gửi. Nhận PPTX, chuẩn bị âm thanh nháp và xem trước; không tự duyệt. Đã qua kiểm thử browser và Qt/Office với web/AI giả lập; chưa xác nhận tài khoản thật đăng nhập/chuyển đổi được. Luồng OAuth cũ và dữ liệu được giữ riêng. Xem [Browser AI](BROWSER_AI.md). Release RC12 chưa có thay đổi này.

Mã nguồn ngày 03/10/2026 có luồng **tài liệu → level → Chuyển đổi → xem trình chiếu → Dùng để dạy**. App tự đánh giá đầu vào, giữ cặp có sẵn, bổ sung phần thiếu và tạo PPTX; thầy cô xác nhận toàn bài một lần. Các tùy chọn bố cục, dịch từng đoạn, trợ giảng và quiz nằm trong phần mở rộng. Đã qua 178 kiểm thử, Ruff và Qt với model/PowerPoint thật; OCR vẫn sai một số dấu cần sửa. Xem [quy trình hiện tại](INPUT_WORKFLOW.md) và [thiết kế chuyển đổi nhanh](QUICK_CONVERSION.md). Các mục RC12 bên dưới mô tả bản đóng gói cũ, chưa bao gồm những thay đổi này.

Cập nhật: 02/10/2026. Mã nguồn: **1.0.0rc12**; bản đóng gói mới cần kiểm thử riêng. Trọng tâm: chuẩn bị và dạy song ngữ Anh–Việt cho nhiều môn THPT, khối 10–12 và môn tự tạo. Các bài trong ảnh chỉ là ví dụ.

## Đã triển khai trong ứng dụng

- M1: Qt/QML, SQLite v2/WAL, migration có backup, settings, log xoay vòng, tác vụ nền/hủy, thư viện cá nhân và sao lưu tự động hằng ngày.
- M2: PPTX/DOCX/PDF text/TXT, nhóm shape, vị trí nguồn, nguồn bất biến theo hash, biên tập/duyệt hai cột, metadata, tách đoạn, tự lưu 1,8 giây, 30 revision, khôi phục; Lesson Pack schema 3 có nguồn, trợ giảng, quiz và âm thanh portable.
- M3: dịch CPU hai chiều offline; thuật ngữ có phạm vi môn; memory đã duyệt và gợi ý gần giống do giáo viên chọn; bảo vệ số/biểu thức/thuật ngữ; cảnh báo trước duyệt; 24 tổ hợp level/layout. Bản dịch luôn là nháp.
- M4: nội dung trợ giảng do giáo viên chuẩn bị và duyệt; bàn điều khiển, cửa sổ lớp riêng, VI Rescue, Kokoro English offline/cache và SAPI Việt khi có, PowerPoint companion theo slide và điều khiển thủ công; Milo/Lumi với bốn tư thế, trợ giảng nổi và tùy chỉnh hiển thị.
- M5: tiến trình lớp học riêng, QR/LAN, trang học sinh, ẩn danh/số chỗ, một đáp án/đúng-sai/khảo sát, deadline, ACK, chống gửi trùng, đổi đáp án, reconnect và mã khôi phục; đáp án chỉ công bố sau đóng câu.
- M6: lịch sử phiên, tỷ lệ có mẫu số, chủ đề, gợi ý hiểu nhầm, recheck tách lượt, so sánh ngôn ngữ có điều kiện, gợi ý level để giáo viên quyết định; CSV tổng hợp/từng phản hồi và xóa phiên đã kết thúc.
- M7: OCR Windows chạy trong tiến trình cách ly, ảnh/PDF scan có giới hạn và báo thiếu ngôn ngữ; xuất deck song ngữ mới; asset mascot, nhãn môn dự phòng, hướng dẫn F1.
- M8 phần phần mềm: build Windows độc lập, bộ cài theo tài khoản với checksum, gói dịch cài từ máy/USB, thu thập giấy phép, hướng dẫn sử dụng và bộ kiểm tra tích hợp.

RC12 thêm cập nhật tự động từ GitHub Releases, tải gói có checksum, cài phiên bản mới cạnh phiên bản cũ và giữ thư viện bài học. Các thay đổi nền tảng của RC11 vẫn gồm tách nhiều ý trong một slide PowerPoint để duyệt, xuất VI/EN cùng trang và ảnh thường, chốt bản chuẩn bị theo revision, chọn bài ở Lớp học, nối báo cáo với bài gốc. Mẫu bài vẫn ở mức đầu tiên; chưa tái tạo đầy đủ bố cục/hiệu ứng của PowerPoint nguồn.

## Bằng chứng và giới hạn

Các kết quả hiện hành lưu trong `APP_RESULTS.md` và `reports/app/`; `TASKS.md` tách phần đã có mã nguồn khỏi nghiệm thu thực địa chưa làm. RC2 khôi phục phiên lớp khi cổng cũ bị chiếm bằng QR mới, giữ câu trả lời và danh tính. RC3 chia Cài đặt thành sáu tab. RC4 lưu nhiều môn và logo trong hồ sơ chung; môn, khối, level L0–L4 và một trong bốn kiểu trình bày được chọn cho từng bài, tên lớp cho từng tiết. RC5 sắp lại chỗ tải logo và xem trước hồ sơ đã lưu. RC6 thêm năm giọng Kokoro English offline. RC7 bổ sung bản xem trước Mascot theo ngữ cảnh và tùy chọn hiện riêng khi giải thích/quiz. Bài L5 cũ vẫn mở được. Các giá trị lớp/level toàn cục cũ không áp cho bài mới.

Máy hiện tại có PowerPoint 16, năm giọng Kokoro English chạy CPU offline và Windows OCR en-US; chưa có giọng/OCR Việt qua các backend này. App báo đúng khả năng và vẫn cho biên tập/dạy bằng chữ.

Model dịch không phải model sinh giáo án: giải thích/ví dụ/câu hỏi cần chuẩn bị và duyệt. Công thức Office dạng đối tượng, video, biểu đồ và bố cục gốc không được tái tạo bằng text importer; có cảnh báo và bản nguồn để đối chiếu. PowerPoint gốc phụ trách trình chiếu nội dung Office. Deck xuất là deck mới theo mẫu.

## Nghiệm thu còn cần môi trường thật

1. Cài/nâng cấp/gỡ trên Windows sạch không Python; kiểm tra dependency với máy khác.
2. Android/iPhone, ít nhất năm điện thoại và tải lớp mục tiêu trên Wi‑Fi/router/hotspot trường, không Internet.
3. Máy chiếu, DPI, Extend/Duplicate, Presenter View và animation/video trong tài liệu dạy thật.
4. Giáo viên nhiều nhóm môn chấm bản dịch/thuật ngữ và thử trọn tiết; ghi thời gian chuẩn bị, sửa dịch và thao tác.
5. Đánh giá giọng/OCR Việt khi máy được cài thành phần ngôn ngữ phù hợp.

RC12 là bản thử nội bộ cần hai giáo viên kiểm tra thêm. Phiếu thao tác/bằng chứng cho các bước còn mở ở `FIELD_ACCEPTANCE.md`. **Chưa đánh dấu toàn bộ M0/M4/M5/M8 nghiệm thu hoàn tất**, vì kiểm tra trên máy phát triển không thay thế các bước trên. Không cần dịch vụ cloud hoặc tài khoản học sinh để thử chức năng hiện có.
