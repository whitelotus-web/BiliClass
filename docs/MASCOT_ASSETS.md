# Mascot dùng trong ứng dụng

Ngày 29/09/2026. Tạo bằng **built-in imagegen**, từ bảng mẫu người dùng; chưa tạo các trạng thái animation/phụ kiện môn.

| Tệp | Nội dung | Kiểm tra |
|---|---|---|
| `app/assets/milo-welcome.png` | Milo, cáo cam, hoodie navy, cầm tablet và vẫy tay | 1163×1352, RGBA, alpha 0–255 |
| `app/assets/lumi-welcome.png` | Lumi, rái cá nâu, khăn navy, ngồi cầm tablet và vẫy tay | 1290×1219, RGBA, alpha 0–255 |

Nguồn: `refs/images/01-milo.png` và `refs/images/02-lumi.png`. PNG đã được copy vào dự án và giữ bản gốc sinh ảnh; không phụ thuộc đường dẫn cache khi chạy app. Home/Settings hiển thị mascot theo cài đặt. Không sửa raster bằng Python; Python chỉ đọc metadata để kiểm tra alpha.

## Prompt Milo

Use case: background-extraction. Asset type: BiliClass desktop application mascot PNG with genuine transparent background. Using the attached Milo reference board as identity reference, create a clean standalone full-body cutout of the large central orange fox Milo. Keep the same orange fur, large pointed ears, cream muzzle and fluffy cream tipped tail, brown paws, navy hoodie with small open-book badge, tablet held against the body, cheerful wink and raised waving paw. Match the polished soft shaded illustration style of the reference. Exactly one mascot, centered, all ears/tail/paws inside canvas, generous transparent padding. No UI, no text, no speech bubbles, no other characters, no environment, no checkerboard drawn into the image. Intended to display around 200px tall on a white/blue classroom app.

## Prompt Lumi

Use case: background-extraction. Asset type: BiliClass desktop application mascot PNG with genuine transparent background. Using the supplied Lumi reference board as identity reference, create a clean standalone full-body cutout of the large central brown otter Lumi. Keep the same warm brown fur, rounded ears, cream muzzle and belly, fine whiskers, dark blue neckerchief with a small white open-book emblem, silver tablet held in one paw, friendly wink and other paw raised in a welcoming wave. Seated calm pose with visible rounded feet and curved tail. Match the polished soft shaded illustration style of the reference. Exactly one mascot, centered, all ears/tail/paws inside canvas, generous transparent padding. No UI, no text, no speech bubbles, no other characters, no environment, no checkerboard drawn into the image. Intended to display around 200px tall on a white/blue classroom app.


## Atlas biểu cảm RC1 — 30/09/2026

`app/assets/mascot-states.png` được tạo bằng built-in imagegen từ hai mascot standalone đã duyệt ở trên. Atlas 4 cột × 2 hàng: Milo trên, Lumi dưới; các cột idle/speaking/thinking/celebrate. Nền alpha thật, bản gốc giữ trong generated_images. QML hiển thị từng ô bằng clip vùng ảnh, không sửa raster bằng Python. Mascot hiển thị nhãn môn tự do làm phụ kiện dùng chung; không ép môn mới vào biểu tượng của môn khác.

Prompt: Create a production sprite atlas for the BiliClass desktop application from these TWO exact mascot identity references. Genuine transparent background. Exactly 4 columns and 2 rows of equal square cells, canvas aspect 2:1. Top row: orange fox Milo in navy hoodie. Bottom row: brown otter Lumi in navy neckerchief. Four expressions left to right in EACH row: (1) Idle, calm smile holding tablet; (2) Speaking, open smiling mouth and one paw presenting; (3) Thinking, closed mouth thoughtful paw under chin; (4) Celebrate, both paws raised cheerful closed eyes. Each full body mascot centered within its own equal square cell with 15% transparent margin so no overlaps or clipping. Same illustration style and consistent character size across all 8 cells. Entire characters, tails and ears inside cells. No text, labels, speech bubbles, borders, panels, drawn checkerboard, background, shadows outside characters, no extra objects. Preserve distinct fox/otter appearance and book emblem. High quality polished soft shaded educational illustration.
