# Nguồn và kênh cập nhật

Kho Git đồng bộ source không bắt buộc là kho chứa gói cập nhật. Quyền xem
source là quyết định của chủ kho. Hiện updater tin đúng kho
`whitelotus-web/BiliClass` trên GitHub; không tự đổi visibility hoặc phát
hành sang một kho khác trong đợt sửa này.

Nếu tách nguồn riêng tư và gói phát hành công khai:

1. Chủ kho chọn kho nguồn và kho release, bảo đảm có quyền phân phối model,
   runtime và tài nguyên đi kèm. Giữ dữ liệu/key/báo cáo ngoài cả hai kho.
2. Đổi `RELEASES_API` và `DOWNLOAD_PREFIX` trong `app/updater.py` cùng một
   lần để chỉ tin kho release mới. Giữ kiểm URL HTTPS, đúng asset, version,
   hash SHA-256, giới hạn ZIP, manifest và đường dẫn giải nén.
3. Phát hành một bản chuyển tiếp ở kênh cũ trước khi đổi/ẩn kênh đó. Kiểm
   cập nhật từ hai phiên bản cũ, tải ngắt quãng, hash sai và quay về bản cũ.
   Không đặt token cá nhân hoặc token nguồn riêng tư trong bộ cài.
4. Nếu chọn release riêng tư, phải thiết kế xác thực của người nhận trước;
   updater công khai hiện tại không tự đọc được release riêng tư.

`scripts/build_from_runtime.py` nhận rõ baseline và kiểm mọi SHA-256 trước
khi tái dùng runtime/model. Nó biên dịch lại toàn bộ module ứng dụng, copy
QML/assets hiện tại và ghi commit/version/baseline vào `BUILD_INFO.json`.
Chạy từ source đã commit, không có thay đổi chưa lưu:

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/<baseline> --output dist/<milestone>
powershell -ExecutionPolicy Bypass -File scripts/verify_release.ps1 -DistRoot dist/<milestone>
```

Nếu đổi dependency/model/native runtime, dùng `scripts/build.ps1` để dựng
lại dependency; không tái dùng baseline khác hợp đồng. Baseline, ZIP, EXE,
model và dữ liệu nghiệm thu là artifact ngoài Git. Không phải mọi ZIP cục
bộ đều đã được công bố lên GitHub Releases.
