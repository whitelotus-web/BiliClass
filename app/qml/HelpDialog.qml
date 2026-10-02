import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: guide
    modal: true
    title: "Bắt đầu với BiliClass"
    width: Math.min(parent.width - 40, 760)
    height: Math.min(parent.height - 50, 660)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    contentItem: ScrollView {
        clip: true; contentWidth: availableWidth
        ColumnLayout { width: parent.width; spacing: 18
            Repeater {
                model: [
                    {title:"1 · Nhập bài của bất kỳ môn nào",body:"Tạo bài mới, chọn môn và khối 10–12 cho riêng bài đó, rồi chọn L0–L4 cùng kiểu trình bày. Dán nội dung hoặc nhập PPTX, DOCX, PDF, TXT, PNG/JPG. Chọn đúng ngôn ngữ nguồn. Ảnh và trang scan cần gói OCR ngôn ngữ có sẵn trong Windows."},
                    {title:"2 · Biên tập và duyệt Anh–Việt",body:"Kiểm tra văn bản trích xuất trước khi dịch. Bản nguồn giữ nguyên. Dịch ngoại tuyến tạo bản nháp; kiểm tra ý nghĩa, thuật ngữ, tên riêng và công thức. Có thể sửa, tách đoạn, khóa dịch tự động, xem 30 phiên bản trước. Chỉ nội dung đã duyệt được đưa lên màn hình lớp."},
                    {title:"3 · Level và cách hiện của từng bài",body:"L0: từ khóa; L1: thêm câu điều hành lớp; L2: English đơn giản; L3: hai ngôn ngữ; L4: ưu tiên English. Chọn riêng một trong bốn kiểu: từ khóa Anh cùng dòng Việt, hai dòng (Anh in nghiêng), hai cột Việt–Anh hoặc English toàn phần với VI Rescue. Từ khóa lấy từ thuật ngữ thầy cô đã chuẩn bị. Bài L5 cũ vẫn mở được."},
                    {title:"4 · Dạy ngoại tuyến",body:"Chuẩn bị lên lớp kiểm tra nguồn, nội dung và audio. Chọn giọng thật trong Cài đặt rồi tạo âm thanh. Xem trước có bàn điều khiển và cửa sổ lớp riêng. Máy chiếu Extend chỉ hiển thị cửa sổ lớp; Duplicate sẽ chiếu mọi thứ trên màn hình máy tính, nên chỉ mở cửa sổ lớp khi dùng Duplicate. Trợ giảng nổi có thể thu gọn hoặc đóng bằng Escape."},
                    {title:"5 · PowerPoint và câu hỏi",body:"Tệp PPTX có thể mở bằng PowerPoint đã cài, chỉ đọc. Tiến/lùi giữ xử lý animation của Office. Theo slide hiện tại đồng bộ đoạn; thầy cô đang sửa nội dung thì không tự chuyển. Học sinh dùng cùng mạng Wi-Fi, quét QR, không cần tài khoản. Đóng câu trước khi công bố đáp án. Kiểm tra lại tạo lượt riêng."},
                    {title:"6 · Kết quả và dùng lại bài",body:"Báo cáo luôn ghi số câu trả lời và mẫu số; khảo sát không chấm điểm. Mẫu ít không suy ra mức hiểu. Gợi ý level cần cặp câu tương đương được thầy cô gắn nhãn. Xuất gói bài kèm âm thanh để chuyển máy; máy nhận cần duyệt lại. Xuất PPTX tạo deck mới theo kiểu trình bày của bài, không tái tạo animation của bản gốc."},
                    {title:"Khi cần khôi phục hoặc đổi máy",body:"Cài đặt → Sao lưu thư viện. Tự sao lưu mỗi ngày khi mở ứng dụng, giữ tối đa 14 bản tự động. Khôi phục luôn vào thư mục mới, sau đó chọn Mở thư viện. Gỡ ứng dụng giữ dữ liệu trong thư mục BiliClass của tài khoản Windows. Model dịch được cài từ gói .bclanguage trên máy/USB; không tự tải Internet."},
                    {title:"Khi điện thoại không vào được lớp",body:"Chọn đúng địa chỉ Wi-Fi/Ethernet, không chọn 127.0.0.1 cho điện thoại. Cho phép BiliClass trên mạng riêng trong Windows Firewall nếu Windows hỏi. Kiểm tra hai máy cùng mạng và router không bật cô lập thiết bị. Khi đổi mạng, ngắt máy chủ rồi mở lại phiên trong Báo cáo; phát lại QR mới. Mất kết nối vẫn giữ câu trả lời đã được xác nhận."}
                ]
                ColumnLayout { required property var modelData; Layout.fillWidth: true; spacing: 5
                    Label { text: modelData.title; font.pixelSize: 17; font.bold: true; color: "#112650"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                    Label { text: modelData.body; font.pixelSize: 13; color: "#667997"; Layout.fillWidth: true; wrapMode: Text.WordWrap; lineHeight: 1.3 }
                }
            }
        }
    }
}
