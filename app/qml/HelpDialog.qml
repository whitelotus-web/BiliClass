import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: guide
    modal: true; anchors.centerIn: parent
    width: Math.min(parent.width - 48, 960); height: Math.min(parent.height - 56, 690)
    padding: 20
    property int activeTopic: 0
    readonly property color ink: AppTheme.adapt("#112650")
    readonly property color muted: AppTheme.adapt("#667997")
    readonly property var topics: [
        {label:"Cài đặt ban đầu", icon:"settings", title:"Bắt đầu từ 4 cài đặt này", intro:"Thiết lập một lần, BiliClass sẽ nhớ cho những lần dùng sau."},
        {label:"Chuyển đổi bài giảng", icon:"bilingual", title:"Từ PowerPoint đến bài giảng song ngữ", intro:"Giữ thiết kế quen thuộc hoặc làm mới bằng mẫu BiliClass."},
        {label:"Tạo giọng đọc", icon:"narration", title:"Thêm giọng Việt–Anh cho bài giảng", intro:"Hai ngôn ngữ, hai loa riêng — chủ động đọc đúng phần cần dạy."},
        {label:"Dạy với Mascot", icon:"mascot", title:"Sẵn sàng lên lớp", intro:"Điều khiển bài chiếu và giọng đọc ngay từ trợ giảng nổi."},
        {label:"Tìm và tải bài", icon:"lessons", title:"Bài giảng luôn trong tầm tay", intro:"Tìm nhanh, chọn nhiều bài và tải đúng phiên bản cần dùng."},
        {label:"Sao lưu dữ liệu", icon:"data", title:"Giữ bài giảng để dùng lâu dài", intro:"Thư viện lưu trên máy; sao lưu để yên tâm dùng lại hoặc đổi máy."}
    ]
    readonly property var setup: [
        {title:"Thông tin chung", body:"Nhập tên thầy cô, trường, bộ môn và thêm logo. Bật hiển thị hồ sơ nếu muốn đưa thông tin lên bài giảng."},
        {title:"Key Google Dịch", body:"Mở tab Google Dịch → nhập key được cấp → Lưu key. Đây là bước cần có trước khi chuyển đổi bài giảng."},
        {title:"Giọng đọc", body:"Chọn cặp giọng Việt–Mỹ, nghe thử, chỉnh tốc độ rồi lưu. Lần tạo giọng mới sẽ dùng lựa chọn gần nhất."},
        {title:"Mascot", body:"Chọn nhân vật yêu thích, kích thước và cách hiển thị trợ giảng nổi phù hợp với màn hình dạy học."}
    ]
    readonly property var workflows: [[],
        [
            {title:"Chọn PowerPoint", body:"Kéo thả hoặc bấm chọn tệp .pptx. Kiểm tra tên bài, môn học và khối lớp."},
            {title:"Chọn kiểu và thiết kế", body:"Chọn Song ngữ Việt–Anh hoặc Tiếng Anh 100%. Giữ thiết kế gốc hoặc chọn mẫu BiliClass; có thể Xem mẫu trước."},
            {title:"Tạo và xem ngay kết quả", body:"Bấm Chuyển đổi bài giảng. Khi xong, xem từng slide ngay trên tool, đối chiếu nội dung rồi mở PowerPoint hoặc thêm giọng đọc."}
        ],
        [
            {title:"Chọn bài cần tạo giọng", body:"Dùng bài vừa chuyển đổi hoặc chọn từ Thư viện. Bấm Xem trước slide khi cần đối chiếu."},
            {title:"Chọn giọng và ngôn ngữ", body:"Chọn cặp Việt–Mỹ, tốc độ và Nghe thử. Chọn Tiếng Việt, Tiếng Anh hoặc cả hai; mỗi ngôn ngữ được đọc bằng giọng tương ứng."},
            {title:"Tạo giọng và dùng để dạy", body:"Bấm Tạo giọng đọc. Chọn cả hai sẽ có hai loa VI và EN riêng trên slide. Có thể nghe, mở PowerPoint hoặc tải bài có giọng."}
        ],
        [
            {title:"Mở bài trong PowerPoint", body:"Bấm Mở PowerPoint từ Thư viện hoặc chọn bài trên Mascot. Bấm F5 khi sẵn sàng trình chiếu."},
            {title:"Điều khiển ngay trên Mascot", body:"Dùng Trước/Sau, loa Việt/Anh và âm lượng. Chọn Tự động, Đang hiện hoặc Toàn slide để đổi cách đọc; rê chuột xem giải thích. Bấm nhân vật để mở/thu bảng."},
            {title:"Thu gọn khi cần", body:"Chuột phải vào nhân vật để mở Cài đặt hoặc Ẩn mini. Có thể mở lại trợ giảng nổi từ thanh bên của BiliClass."}
        ],
        [
            {title:"Tìm đúng bài", body:"Gõ tên bài, môn hoặc khối — có thể gõ không dấu. Kết hợp bộ lọc, sắp xếp và đổi giữa Thẻ/Danh sách."},
            {title:"Chọn một hoặc nhiều bài", body:"Tích ô chọn; giữ Shift để chọn một dải, hoặc giữ chuột kéo qua các bài. Thanh tìm kiếm và tác vụ vẫn hiện khi cuộn."},
            {title:"Tải hoặc đưa vào thùng rác", body:"Nút Tải dùng tên bài và ghi rõ ngôn ngữ, giọng đọc đã có. Bài đã xóa có thể khôi phục trong Chia sẻ & quản lý → Thùng rác."}
        ],
        [
            {title:"Sao lưu thư viện", body:"Mở Cài đặt → Dữ liệu → Sao lưu dữ liệu, rồi chọn nơi giữ bản sao. BiliClass cũng tự sao lưu theo lịch khi mở ứng dụng."},
            {title:"Khôi phục khi cần", body:"Chọn Khôi phục bản sao và chọn tệp sao lưu. Tool kiểm tra, mở thư viện khôi phục; thư viện trước vẫn được giữ."},
            {title:"Đổi nơi lưu hoặc cập nhật", body:"Dùng Đổi nơi lưu nếu cần chuyển thư viện sang ổ khác. Kiểm tra bản mới tại Cài đặt → Thông tin BiliClass."}
        ]
    ]
    background: Rectangle { color: AppTheme.surface; radius: 16; border.color: AppTheme.adapt("#d6e4f6") }
    header: Item {
        implicitHeight: 82
        Label { x:24; y:18; text:"Hướng dẫn BiliClass"; color:guide.ink; font.pixelSize:23; font.weight:Font.Bold }
        Label { x:24; y:51; text:"Từ thiết lập lần đầu đến một tiết dạy song ngữ"; color:guide.muted; font.pixelSize:13 }
    }
    contentItem: RowLayout {
        spacing: 24
        ColumnLayout {
            Layout.preferredWidth:216; Layout.fillHeight:true; spacing:6
            Repeater {
                model:guide.topics
                delegate:ItemDelegate {
                    required property int index
                    required property var modelData
                    objectName:"helpTopic"+index
                    Layout.fillWidth:true; implicitHeight:51
                    contentItem:RowLayout {
                        spacing:10
                        NavigationIcon { name:modelData.icon; active:guide.activeTopic===index; Layout.preferredWidth:24; Layout.preferredHeight:24 }
                        Label { text:(index+1)+". "+modelData.label; Layout.fillWidth:true; color:guide.activeTopic===index?AppTheme.adapt("#0869f9"):guide.ink; font.pixelSize:13; font.weight:Font.DemiBold; wrapMode:Text.WordWrap }
                    }
                    background:Rectangle { radius:10; color:guide.activeTopic===index?AppTheme.adapt("#edf5ff"):parent.hovered?AppTheme.adapt("#f6f9fd"):"transparent" }
                    onClicked:guide.activeTopic=index
                }
            }
            Item { Layout.fillHeight:true }
            Label { text:"F1 · Mở hướng dẫn bất cứ lúc nào"; wrapMode:Text.WordWrap; Layout.fillWidth:true; font.pixelSize:11; color:guide.muted }
        }
        Rectangle { Layout.fillHeight:true; Layout.preferredWidth:1; color:AppTheme.adapt("#e6edf7") }
        ColumnLayout {
            Layout.fillWidth:true; Layout.fillHeight:true; spacing:10
            Label { objectName:"helpTopicHeading"; text:guide.topics[guide.activeTopic].title; color:guide.ink; font.pixelSize:22; font.weight:Font.Bold; wrapMode:Text.WordWrap; Layout.fillWidth:true }
            Label { text:guide.topics[guide.activeTopic].intro; color:guide.muted; font.pixelSize:13; wrapMode:Text.WordWrap; Layout.fillWidth:true }
            ContentScrollView {
                id:stepsScroll; objectName:"helpStepsScroll"
                Layout.fillWidth:true; Layout.fillHeight:true; contentWidth:availableWidth
                ColumnLayout {
                    width:stepsScroll.availableWidth; spacing:10
                    Repeater {
                        model:guide.activeTopic===0?guide.setup:guide.workflows[guide.activeTopic]
                        delegate:Rectangle {
                            required property int index
                            required property var modelData
                            objectName:"helpStep"+index
                            Layout.fillWidth:true; implicitHeight:stepRow.implicitHeight+24; radius:11; color:AppTheme.adapt("#f7faff")
                            RowLayout {
                                id:stepRow; anchors.fill:parent; anchors.margins:12; spacing:12
                                Rectangle { Layout.alignment:Qt.AlignTop; implicitWidth:29; implicitHeight:29; radius:15; color:AppTheme.adapt("#e6f0ff"); Label { anchors.centerIn:parent; text:index+1; font.weight:Font.Bold; color:AppTheme.adapt("#0869f9") } }
                                ColumnLayout {
                                    Layout.fillWidth:true; spacing:4
                                    Label { text:modelData.title; color:guide.ink; font.pixelSize:15; font.weight:Font.DemiBold; wrapMode:Text.WordWrap; Layout.fillWidth:true }
                                    Label { text:modelData.body; color:guide.muted; font.pixelSize:13; wrapMode:Text.WordWrap; lineHeight:1.2; Layout.fillWidth:true }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    onActiveTopicChanged:if(stepsScroll.contentItem) stepsScroll.contentItem.contentY=0
    footer:Item {
        implicitHeight:65
        RowLayout {
            anchors.fill:parent; anchors.margins:16; spacing:8
            ActionButton { objectName:"helpClose"; text:"Đóng"; onClicked:guide.close() }
            Item { Layout.fillWidth:true }
            ActionButton { objectName:"helpPrevious"; text:"← Trước"; visible:guide.activeTopic>0; onClicked:guide.activeTopic-- }
            ActionButton { objectName:"helpNext"; text:guide.activeTopic===0?"Xem cách tạo bài →":"Tiếp →"; visible:guide.activeTopic<guide.topics.length-1; onClicked:guide.activeTopic++ }
        }
    }
}
