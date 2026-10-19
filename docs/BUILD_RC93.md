# RC93 — Xếp cặp giọng theo giới tính và vùng miền

Danh sách cặp giọng dùng thứ tự: Nữ Bắc, Nữ Trung, Nữ Nam, Nam Bắc,
Nam Trung, Nam Nam. Ở bố cục ba cột, hàng đầu là ba giọng nữ và hàng
thứ hai là ba giọng nam, từ Bắc tới Nam. Giao diện tiếp tục tự giảm cột
ở cửa sổ hẹp để giữ chữ và nút dễ đọc.

Chỉ đổi thứ tự danh sách. Mỗi cặp giữ ID, giọng Việt, giọng Mỹ và khóa
cache hiện có; lựa chọn đã lưu vẫn chỉ đúng cặp trước đó. Không thay
mô hình, cách phát hoặc tạo lại âm thanh bài đã có. Giữ các tab Cài đặt.

## Kiểm tra trước đóng gói

- Ruff đạt; 42 kiểm thử về cặp giọng, nghe thử, cấu hình và tên tải về đạt.
- Qt: nghe sáu cặp, lưu lựa chọn, ba chế độ tạo, dùng bản cũ và hai loa
  riêng đạt; nguồn giữ nguyên, không cảnh báo QML.
- Đã xem ảnh Qt ở 1366 × 850 và xác nhận hai hàng đúng thứ tự yêu cầu;
  có thêm ảnh kiểm tra cửa sổ 1080 × 700 trong báo cáo riêng.

## Đóng gói

Phiên bản `1.0.0rc93`. Dựng lại toàn bộ mã ứng dụng, dùng runtime và
mô hình RC92 đã kiểm checksum. Không thay dependency hoặc model.

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc92-voice-pairs --output dist/rc93-voice-order
```

- Commit ứng dụng: `7c784052c74c9f9cdd25af8361384d9d11df6fb2`.
- CI Source checks đạt:
  https://github.com/whitelotus-web/BiliClass/actions/runs/39268483748
- ZIP: `BiliClass-RC93-Windows.zip`, 1.232.964.657 byte; 4.613 tệp
  ứng dụng (4.617 mục trong ZIP). Đã xác minh đủ manifest/checksum.
- SHA256: `c9c9211d2a08fb184d7e066a0c414c7b2c3d81e9540c39422f749498cb80c96c`.

Bản cài tạm đã xác minh đầy đủ tại
`reports/release/1.0.0rc93-af7156e4/installer.json` (cài/gỡ, mô hình thật,
Qt và thư viện riêng). Gói chỉ tải lên bản nháp GitHub; chưa công bố hoặc
cài vào thư viện cá nhân. Người dùng mở rộng yêu cầu sang giao diện tự ghép
và mẫu dài trong khi kiểm tra, nên mốc tiếp theo là RC94.
