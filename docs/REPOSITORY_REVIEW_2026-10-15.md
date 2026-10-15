# Sàng lọc các kho GitHub cho BiliClass — 15/10/2026

Đọc cùng [kế hoạch và tiêu chí nghiệm thu](OPTIMIZATION_PLAN_2026-10-15.md).

Danh sách thực tế có **86 dòng URL, 85 URL kho khác nhau**; `browser-use/video-use`
lặp hai lần. 76 kho đọc được metadata GitHub; 9 URL trả HTTP 404 tại lần kiểm tra.
Không coi 404 là kết luận dự án đã bị xóa hoặc không tồn tại.

Phương pháp: kiểm tra mô tả, trạng thái archive và SPDX qua GitHub API; đọc README
nhóm TTS, browser, kiểm thử, thiết kế và quy trình được ưu tiên. Các dòng còn lại
là sàng lọc theo phạm vi, không phải đánh giá chất lượng toàn bộ mã. Chưa cài/chạy
benchmark, chưa kiểm toán bảo mật hoặc nghiệm thu khả năng đóng gói các công cụ này.
Mỗi tên kho bên dưới liên kết tới nguồn gốc để kiểm tra lại khi triển khai.

SPDX là giấy phép GitHub nhận diện ở cấp repository trong lần đọc, không tự bao
gồm weights/voice/assets hoặc mọi thư mục. “Chưa rõ” gồm không nhận diện hoặc
`NOASSERTION`; cần đọc file LICENSE tại commit cụ thể trước khi lấy mã/model.
Các quyết định là đề xuất theo nhu cầu BiliClass hiện tại, không phải xếp hạng
chất lượng tổng quát của dự án. “Dev” là công cụ cho người phát triển, không đưa
vào runtime/bộ cài của giáo viên.

| Kho do người dùng gửi | SPDX / tình trạng | Quyết định | Lý do và phạm vi |
|---|---|---|---|
| [Madona2000/gwen-tts](https://github.com/Madona2000/gwen-tts) | Chưa rõ | Thử sau | README tập trung giọng Việt, môi trường CUDA; chưa chứng minh cùng giọng đọc Anh tốt. Cần xác minh giấy phép trong thư mục license và weights. |
| [abus-aikorea/voice-pro](https://github.com/abus-aikorea/voice-pro) | GPL-3.0 | Tham khảo | Studio nhiều engine/dubbing; học quản lý lỗi/tải model. Quá rộng cho lõi, có GPL-3.0. |
| [flybirdxx/ComfyUI-Qwen-TTS](https://github.com/flybirdxx/ComfyUI-Qwen-TTS) | Chưa rõ | Thử sau | Node ComfyUI thêm runtime; chưa có bằng chứng cải thiện Việt–Anh trên cấu hình BiliClass. |
| [Geniust-Y/LuxTTS](https://github.com/Geniust-Y/LuxTTS) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; không suy ra khả năng từ kho LuxTTS khác. |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT | Ngoài lõi | Agent harness nghiên cứu/tác vụ dài; orchestration nặng hơn nhu cầu chuyển bài đã xác định. |
| [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) | Apache-2.0 | Để sau | Tạo video, không sửa lỗi dịch/bố cục PPTX hiện tại. URL hiện chuyển tới `ATH-MaaS/Pixelle-Video`. |
| [browser-use/video-use](https://github.com/browser-use/video-use) | MIT | Để sau | Công cụ chỉnh video bằng agent, không phải browser-use cho chat/PPTX. |
| [MoneyPrinterTurbo/MoneyPrinterTurbo](https://github.com/MoneyPrinterTurbo/MoneyPrinterTurbo) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; có kho cùng tên ở owner khác trong danh sách, không gộp tùy ý. |
| [mshumer/yt-thumbnail-creator](https://github.com/mshumer/yt-thumbnail-creator) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; thumbnail không nằm trong ưu tiên lõi. |
| [zhom/donutbrowser](https://github.com/zhom/donutbrowser) | AGPL-3.0 | Không chọn cho lõi | Anti-detect browser không chứng minh sửa được login/download; thêm runtime và AGPL-3.0. |
| [nav-v/buddy-ai](https://github.com/nav-v/buddy-ai) | MIT | Ngoài lõi | Ứng dụng chat/coaching prompt; không giải quyết dựng PowerPoint. |
| [github/spec-kit](https://github.com/github/spec-kit) | MIT | Dev | Tham khảo đặc tả, sửa lỗi và nghiệm thu; không đóng gói cho giáo viên. |
| [ggn-org/GitNexus](https://github.com/ggn-org/GitNexus) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; dùng sơ đồ phụ thuộc nội bộ/CodeFlow trước. |
| [OpenBMB/awesome-agent-skills](https://github.com/OpenBMB/awesome-agent-skills) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; không tự cài bộ skill từ tài liệu tham khảo. |
| [decolua/9router](https://github.com/decolua/9router) | MIT | Không chọn cho lõi | Router nhà cung cấp cho coding; không thay adapter chat đã kiểm thử hay dùng để vượt quota. |
| [CJackHwang/ds2api](https://github.com/CJackHwang/ds2api) | AGPL-3.0 / archive | Không chọn cho lõi | Middleware web protocol cho DeepSeek, đã archive; khác nhà cung cấp/luồng hiện tại. |
| [caamer20/Telegram-Drive](https://github.com/caamer20/Telegram-Drive) | Chưa rõ | Ngoài lõi | Lưu trữ Telegram; không thay backup/thư viện bài cục bộ. |
| [shiyongxin/awesome-design-md](https://github.com/shiyongxin/awesome-design-md) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; quy chuẩn slide cần viết/kiểm tra trực tiếp cho bốn kiểu đang có. |
| [interlumpen/Telegram-shop](https://github.com/interlumpen/Telegram-shop) | MIT | Ngoài lõi | Bot bán hàng Telegram, không thuộc chuyển bài/trợ giảng. |
| [indmdev/Free-Telegram-Store-Bot](https://github.com/indmdev/Free-Telegram-Store-Bot) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; không thuộc ưu tiên sản phẩm. |
| [cosmicstack-labs/mercury-agent](https://github.com/cosmicstack-labs/mercury-agent) | MIT | Ngoài lõi | Agent đa kênh hoạt động dài; không cần cho pipeline xác định của giáo viên. |
| [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic) | MIT / archive | Thử sau | Chuyển sang supertone-oss-archive; chỉ thử v3 Việt–Anh sau kiểm tra model/license và phương án bảo trì. URL hiện chuyển tới `supertone-oss-archive/supertonic`. |
| [braedonsaunders/codeflow](https://github.com/braedonsaunders/codeflow) | MIT | Dev | Tham khảo sơ đồ phụ thuộc Python; dữ liệu/token của repo riêng phải ở môi trường nội bộ. |
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | Apache-2.0 | Dev tùy chọn | CLI lập trình, không phải phiên web Gemini của giáo viên và không chứng minh xuất PPTX. |
| [opencut-app/OpenCut](https://github.com/opencut-app/OpenCut) | MIT | Để sau | Video editor; chỉ xem lại nếu có yêu cầu xuất video bài giảng. |
| [Hmbown/DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI) | MIT | Dev tùy chọn | Coding agent terminal, không phải engine chuyển đổi bài. URL hiện chuyển tới `codewhale-hq/Codewhale`. |
| [ruzin/stenoai](https://github.com/ruzin/stenoai) | MIT | Để sau | Ghi chú/ghi âm; không cần thêm luồng thu âm lúc sửa chất lượng PPTX. URL hiện chuyển tới `stenolabs/stenoai`. |
| [alibaba/page-agent](https://github.com/alibaba/page-agent) | MIT | Thử trong dev | Agent in-page JS; cần LLM riêng, đo độ trễ và độ đúng trước khi dùng làm fallback. |
| [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) | Chưa rõ | Dev tham khảo | Tài liệu học phát triển sản phẩm, không phải thư viện tăng tốc runtime. |
| [Lap-Platform/LAP](https://github.com/Lap-Platform/LAP) | Apache-2.0 | Dev tùy chọn | Đặc tả API cho agent; không tạo thêm API hợp lệ từ tài khoản web. |
| [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) | GPL-3.0 | Ngoài lõi | Agent harness; thêm dịch vụ/GPL chưa có lợi ích đo được cho pipeline hiện tại. |
| [nexu-io/html-anything](https://github.com/nexu-io/html-anything) | Apache-2.0 | Tham khảo | Mẫu và preview cho nhánh thiết kế mới; không dùng như công cụ bảo toàn PPTX gốc. |
| [pixel-point/media-downloader](https://github.com/pixel-point/media-downloader) | Chưa rõ | Ngoài lõi | Video downloader macOS; BiliClass hiện là Windows/Qt và bảo toàn media từ nguồn. |
| [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) | Apache-2.0 | Dev tùy chọn | Plugin liên kết coding agent; không thuộc runtime và chưa cài trong đợt đánh giá. |
| [angristan/openvpn-install](https://github.com/angristan/openvpn-install) | MIT | Ngoài lõi | Cài VPN server Linux, không phải cách sửa phiên đăng nhập của tool. |
| [ysharma3501/LuxTTS](https://github.com/ysharma3501/LuxTTS) | Apache-2.0 | Thử sau | README có CPU/GPU nhưng chưa chứng minh Việt–Anh chung giọng; con số 150x không là số đo BiliClass. |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | MIT | Dev tùy chọn | Coding agent, không cần thêm vào bộ cài giáo viên. |
| [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | MIT | Ngoài lõi | Trading không liên quan học liệu/trình chiếu. |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | Apache-2.0 | Dev tham khảo | Kho ví dụ; chọn từng ý tưởng có bài toán cụ thể, không thêm toàn bộ dependency. |
| [crisng95/flowboard](https://github.com/crisng95/flowboard) | Chưa rõ | Để sau | Canvas video sản phẩm, không phải bố cục bài PowerPoint. |
| [Z4nzu/hackingtool](https://github.com/Z4nzu/hackingtool) | MIT | Ngoài lõi | Bộ công cụ an ninh không thuộc chức năng giáo viên yêu cầu. |
| [usebruno/bruno](https://github.com/usebruno/bruno) | MIT | Dev tùy chọn | Kiểm thử REST nội bộ khi có API; không thay Qt smoke và bài kiểm tra Office. |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | Dev | Tham khảo chẩn đoán, kế hoạch và kiểm chứng; tránh chồng nhiều bộ quy trình. |
| [1jehuang/jcode](https://github.com/1jehuang/jcode) | MIT | Dev tùy chọn | Coding agent harness, không phải giải pháp tăng tốc bản dịch. |
| [browserbase/skills](https://github.com/browserbase/skills) | Chưa rõ | Dev tham khảo | Học cách mô tả thao tác browser; dịch vụ cloud không tự dùng được phiên Chrome local. |
| [virattt/dexter](https://github.com/virattt/dexter) | Chưa rõ | Ngoài lõi | Nghiên cứu tài chính, không phù hợp lõi giáo dục. |
| [soxoj/maigret](https://github.com/soxoj/maigret) | MIT | Ngoài lõi | Tìm thông tin tài khoản công khai, không cần cho bài giảng. |
| [freemocap/freemocap](https://github.com/freemocap/freemocap) | AGPL-3.0 | Để sau | Motion capture quá nặng cho mascot phản ứng theo trạng thái đọc; có AGPL-3.0. |
| [google/skills](https://github.com/google/skills) | Apache-2.0 | Dev tùy chọn | Tham khảo skill sản phẩm Google khi có nhu cầu; không cài hàng loạt hoặc thay adapter hiện tại. |
| [chauanhdung995/video-pipeline](https://github.com/chauanhdung995/video-pipeline) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; chưa có căn cứ tích hợp. |
| [hoquanghai/Auto-Create-Video](https://github.com/hoquanghai/Auto-Create-Video) | MIT | Để sau | Nhánh tạo video theo tên kho; metadata không có mô tả, chưa xác minh sâu khả năng. |
| [chauanhdung995/vibe-tool-video](https://github.com/chauanhdung995/vibe-tool-video) | Chưa xác minh / HTTP 404 | Chưa xác minh | URL trả 404; chưa có căn cứ tích hợp. |
| [yikart/AiToEarn](https://github.com/yikart/AiToEarn) | MIT | Ngoài lõi | Nền tảng nội dung/kiếm tiền, không giải quyết lỗi chuyển đổi bài. |
| [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) | Apache-2.0 | Dev tùy chọn | Bộ nhớ agent lập trình; không trộn với dữ liệu/ghi nhớ kiến thức của giáo viên. |
| [stablyai/orca](https://github.com/stablyai/orca) | MIT | Dev tùy chọn | Môi trường quản lý nhiều coding agent, không phải browser driver hay PPTX engine. |
| [vakra-dev/reader](https://github.com/vakra-dev/reader) | Apache-2.0 | Thử sau | Hạ tầng web scraping/session; chỉ khảo sát nếu import trang web trở thành yêu cầu. |
| [OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM) | Apache-2.0 | Thử sau | VoxCPM2 có Việt/Anh; ứng viên chất lượng cao, cần đo tài nguyên và nghe thử trước. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | MIT | Dev tham khảo | Quy trình agent/skills chồng lấn Spec Kit/Superpowers; chọn ít quy tắc có ích. |
| [debpalash/OmniVoice-Studio](https://github.com/debpalash/OmniVoice-Studio) | AGPL-3.0 | Thử sau | Studio giọng đa chức năng, AGPL; số ngôn ngữ quảng cáo không là kiểm chứng phát âm học thuật. URL hiện chuyển tới `debpalash/VoiceStudio`. |
| [fspecii/ace-step-ui](https://github.com/fspecii/ace-step-ui) | Chưa rõ | Ngoài lõi | Sinh nhạc, không phải đọc bài Việt–Anh. |
| [jamiepine/voicebox](https://github.com/jamiepine/voicebox) | MIT | Tham khảo ưu tiên | Hàng đợi, bản audio gốc/biến thể, quản lý model; không mang cả studio vào Qt. |
| [onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx) | Chưa rõ | Để sau | Nền tảng chat/RAG rộng; chưa có nhu cầu và số đo để thêm một hệ thống tìm kiếm riêng. |
| [web-infra-dev/midscene](https://github.com/web-infra-dev/midscene) | MIT | Thử trong dev | Kiểm thử web và Windows desktop/ảnh render; không tự chứng nhận PPTX đúng nghĩa hay giữ hiệu ứng. |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | MIT | Để sau | Sinh video ngắn, không sửa bố cục hai cột hoặc thiếu bản dịch. |
| [beelzebub-labs/beelzebub](https://github.com/beelzebub-labs/beelzebub) | GPL-3.0 | Ngoài lõi | Deception/security runtime, không thuộc pipeline giáo viên. |
| [DigitalPlatDev/FreeDomain](https://github.com/DigitalPlatDev/FreeDomain) | AGPL-3.0 | Ngoài lõi | Tên miền/DNS không tăng tốc chuyển đổi local. |
| [webmin/webmin](https://github.com/webmin/webmin) | BSD-3-Clause | Ngoài lõi | Quản trị server; không cần cho app Windows desktop. |
| [nguyenhonglinh/codex9router](https://github.com/nguyenhonglinh/codex9router) | MIT | Không chọn cho lõi | Chưa chứng minh ích lợi cho PPTX; không dùng router thay phiên chat hoặc vượt hạn mức. |
| [techgocodingnow/brew-manager](https://github.com/techgocodingnow/brew-manager) | Chưa rõ | Chưa đủ thông tin | Metadata không có mô tả/SPDX; chưa có căn cứ phù hợp, không tích hợp theo tên. |
| [alecm20/story-flicks](https://github.com/alecm20/story-flicks) | Chưa rõ | Để sau | Sinh video truyện, không thuộc đầu ra hiện tại. |
| [AhmadIbrahiim/Website-downloader](https://github.com/AhmadIbrahiim/Website-downloader) | MIT | Ngoài lõi | Tải source website không thay nội dung file bài giảng hay quản lý phiên chat. |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | BSD-3-Clause | Thử sau | Có ý tưởng selector thích ứng; chỉ nghiên cứu nhận diện phần tử, không thêm anti-bot/proxy để chữa login. |
| [denizsafak/abogen](https://github.com/denizsafak/abogen) | MIT | Tham khảo | Phân đoạn văn bản dài, audio/caption; không thay bằng engine chưa có giọng Việt–Anh phù hợp. |
| [NVlabs/LongLive](https://github.com/NVlabs/LongLive) | Apache-2.0 | Để sau | Hạ tầng sinh video/world model, tài nguyên và phạm vi không phù hợp lúc này. |
| [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | MIT | Để sau | Storyboarding/video/asset; chỉ xem lại khi làm học liệu video. |
| [xuanyustudio/LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama) | MIT | Để sau | Sản xuất phim ngắn, không phải chuyển PowerPoint nguồn. |
| [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code) | MIT | Dev tùy chọn | Coding CLI, không cần cài kèm app giáo viên. |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Apache-2.0 | Ngoài lõi | Agent tài chính, không liên quan. |
| [huytranvan2010/AI-auto-generate-video](https://github.com/huytranvan2010/AI-auto-generate-video) | MIT | Để sau | Sinh video, không xử lý lỗi tiếng Anh thân bài và bố cục PPTX. |
| [HuyKira/KiraAP](https://github.com/HuyKira/KiraAP) | MIT | Thử sau | Tích hợp AI đa phương tiện/Vertex; chỉ dùng khi có nhu cầu API chính thức và chi phí được chọn. |
| [notepower2k1/CapCap](https://github.com/notepower2k1/CapCap) | Apache-2.0 | Tham khảo sau | Windows dubbing, workflow dự án/voice/subtitle; chỉ học luồng, không thêm cả video editor. |
| [krillinai/KrillinAI](https://github.com/krillinai/KrillinAI) | Apache-2.0 | Để sau | Workspace media/dubbing mở rộng; không cần để đọc và trình chiếu bài hiện tại. URL hiện chuyển tới `krillinai/OpenCreator`. |
| [Anning01/novelvids](https://github.com/Anning01/novelvids) | Chưa rõ | Để sau | Novel-to-video/API bên thứ ba; giấy phép metadata chưa xác định. |
| [pnnbao97/VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) | Apache-2.0 | Lõi đang dùng | Tối ưu v3 Turbo hiện có: cache gốc/biến thể, benchmark CPU, gói GPU và streaming tùy chọn. |
| [Lake1059/FFmpegFreeUI](https://github.com/Lake1059/FFmpegFreeUI) | MIT | Tham khảo sau | UI cho ffmpeg, có thể học tiến độ/xử lý media nếu thêm xuất video; không tích hợp toàn app. |

Office Kit PPTX được nhắc trong bản đánh giá sơ bộ nhưng không nằm trong 86 URL
người dùng liệt kê, nên không tính thêm thành dòng thứ 86 trong bảng kho duy nhất.
Khả năng thử nghiệm và giới hạn của công cụ này nằm trong kế hoạch chính.

Không cài dependency/skill, sao chép mã dự án ngoài, thay profile hay gửi tài liệu
giáo viên cho dịch vụ mới trong đợt sàng lọc này.
