import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: guide
    modal: true; anchors.centerIn: parent
    width: Math.min(parent.width - 48, 960); height: Math.min(parent.height - 40, 740)
    padding: 20
    property int activeTopic: 0
    property string searchText: ""
    function plain(value) { return String(value || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d") }
    function matchesTopic(index) {
        const topic = topics[index]
        const steps = index === 0 ? setup : workflows[index]
        const text = plain([topic.label, topic.title, topic.intro].concat(steps.map(function(step) { return step.title + " " + step.body })).join(" "))
        return plain(searchText).trim().split(/\s+/).every(function(word) { return text.indexOf(word) >= 0 })
    }
    readonly property var matchingTopics: topics.map(function(topic, index) { return index }).filter(matchesTopic)
    function moveTopic(direction) {
        const position = matchingTopics.indexOf(activeTopic) + direction
        if (position >= 0 && position < matchingTopics.length) activeTopic = matchingTopics[position]
    }
    onSearchTextChanged: if (matchingTopics.length && matchingTopics.indexOf(activeTopic) < 0) activeTopic = matchingTopics[0]
    onClosed: searchText = ""
    Shortcut { sequences: [StandardKey.Find]; enabled: guide.visible; onActivated: { helpSearch.forceActiveFocus(); helpSearch.selectAll() } }
    readonly property color ink: AppTheme.adapt("#112650")
    readonly property color muted: AppTheme.adapt("#667997")
    readonly property var topics: [
        {label:"Bắt đầu nhanh", icon:"home", title:"Tạo bài để dạy trong 4 bước", intro:"Lần đầu sử dụng? Cứ làm lần lượt theo các bước dưới đây."},
        {label:"Chuyển đổi bài giảng", icon:"bilingual", title:"Từ PowerPoint đến bài giảng song ngữ", intro:"Giữ thiết kế quen thuộc hoặc làm mới bằng mẫu BiliClass."},
        {label:"Tạo giọng đọc", icon:"narration", title:"Thêm giọng Việt–Anh cho bài giảng", intro:"Hai ngôn ngữ, hai loa riêng — chủ động đọc đúng phần cần dạy."},
        {label:"Dạy với Mascot", icon:"mascot", title:"Sẵn sàng lên lớp", intro:"Điều khiển bài chiếu và giọng đọc ngay từ trợ giảng nổi."},
        {label:"Tìm và tải bài", icon:"lessons", title:"Bài giảng luôn trong tầm tay", intro:"Tìm nhanh, chọn nhiều bài và tải đúng phiên bản cần dùng."},
        {label:"Cài đặt và sao lưu", icon:"settings", title:"Chuẩn bị một lần, dùng cho nhiều bài", intro:"Nếu máy đã được cài sẵn, bạn có thể bắt đầu tạo bài ngay."},
        {label:"Khi bị vướng", icon:"data", title:"Thử các cách đơn giản này", intro:"Đọc thông báo trên màn hình, rồi tìm tình huống giống của bạn."}
    ]
    readonly property var setup: [
        {title:"Chọn bài PowerPoint", body:"Chuyển đổi bài giảng → Chọn file PowerPoint → chọn bài trên máy → Mở."},
        {title:"Chuyển thành bài song ngữ", body:"Kiểm tra tên bài, môn và lớp → Song ngữ Việt–Anh → Chuyển đổi bài giảng. Chờ báo hoàn tất."},
        {title:"Thêm giọng đọc nếu cần", body:"Tạo giọng đọc bài giảng → chọn bài → chọn tiếng Anh/Việt → Nghe thử → Tạo giọng đọc."},
        {title:"Mở bài để dạy", body:"Bài giảng → Mở PowerPoint → bấm F5. Dùng trợ giảng nổi để đọc bài và chuyển phần đang chiếu."}
    ]
    readonly property var workflows: [[],
        [
            {title:"Chọn một hoặc nhiều bài", body:"Trong tab PowerPoint, bấm Chọn file PowerPoint hoặc kéo bài từ thư mục vào khung tải lên. Muốn chọn nhiều bài: giữ phím Ctrl rồi bấm từng bài, sau đó bấm Mở. Mỗi bài tối đa 200 MB; mỗi lượt tối đa 100 bài."},
            {title:"Chỉ dịch phần cần thiết trong Word", body:"Chuyển đổi bài giảng → Word → chọn .docx. Ở Nội dung gốc, chọn Tích đoạn / câu hoặc Bôi đen văn bản. Khi bôi đen, nhả chuột rồi bấm Chọn đoạn này để dịch; tiếp tục chọn ở những nơi khác. Các vùng đã xác nhận được giữ bên phải. Bấm Chuyển đổi: khi thành công, bài tự lưu cạnh file gốc với hậu tố (Song ngu VI-EN) và trong Bài giảng → Word. Có thể sửa bản Anh/từ khóa rồi bấm Lưu Word song ngữ để lưu lại."},
            {title:"Tên bài và định dạng Word", body:"Tên bài học tự lấy theo file; có thể sửa trong Cấu hình bài giảng. Mặc định tiếng Anh dùng màu gốc, phông gốc và in nghiêng. Chọn kiểu chữ hoặc màu khác nếu cần. Bỏ tích Giống văn bản gốc để hiện danh sách chọn phông. Tool nhớ lựa chọn định dạng gần nhất cho bài mới; khi mở lại bài cũ, dùng cấu hình đã lưu của bài đó."},
            {title:"Xem lại bài vừa chọn", body:"Ảnh slide nằm bên phải; bấm mũi tên dưới ảnh để xem slide khác. Với nhiều bài, bấm tên bài bên trái để đổi ảnh xem trước. Nút × nhỏ bỏ riêng bài đó; Chọn bài khác để chọn lại."},
            {title:"Chọn kiểu và thiết kế", body:"Chọn Song ngữ Việt–Anh hoặc Tiếng Anh 100%. Giữ thiết kế gốc hoặc chọn mẫu BiliClass; có thể Xem mẫu trước."},
            {title:"Chuyển đổi và lưu kết quả", body:"Chọn nhiều file: cấu hình dùng chung, tên bài lấy theo từng file; tool xử lý lần lượt và tự lưu kết quả cạnh file gốc. Nút Dừng ở thanh dưới, cạnh Đang xử lý. Dừng → Tiếp tục giữ phần đã làm. Thử lại bài lỗi chỉ chạy các bài chưa thành công; Xem bài mở đúng kết quả. Khi tất cả bài hoàn tất, màn hình giữ danh sách kết quả; bấm Về Thư viện hoặc Chuyển đổi bài khác khi sẵn sàng."}
        ],
        [
            {title:"Chọn bài cần tạo giọng", body:"Có thể chọn bài từ thư viện hoặc bấm Chọn file PowerPoint để lấy bài trên máy. Bài đã có sẵn hai ngôn ngữ thì dùng ngay công cụ này, không cần chuyển đổi lại."},
            {title:"Xem bài và chọn nhiều bài", body:"Ảnh slide và nút chuyển slide ở bên phải. Nếu chọn nhiều bài, bấm từng tên bên trái để xem. Trong thư viện, cũng có thể tích nhiều bài rồi bấm Tạo giọng đã chọn. Mở bài chỉ để xem hoặc chọn giọng, chưa tự tạo âm thanh. Nếu có báo bố cục cần xem lại, bấm Xem lỗi còn lại; chỉ bấm Thử căn lại khi muốn sửa."},
            {title:"Chọn giọng và ngôn ngữ", body:"Chọn cặp Việt–Mỹ, tốc độ và Nghe thử. Chọn Tiếng Việt, Tiếng Anh hoặc cả hai; mỗi ngôn ngữ được đọc bằng giọng tương ứng."},
            {title:"Tạo giọng và dùng để dạy", body:"Bấm Tạo giọng đọc. Mỗi bài hoàn tất tự lưu PowerPoint có giọng cạnh file gốc. Nếu bài đã có file kết quả do tool tự lưu, giọng được cập nhật vào chính file đó. File gốc luôn được giữ; file kết quả đang mở hoặc đã sửa được giữ riêng. Nút Dừng ở thanh dưới; Tiếp tục giữ các đoạn đã có. Nếu thư mục gốc không ghi được, tool lưu vào thư mục BiliClass và có nút Mở thư mục. Khi cả lượt xong, bấm Về Thư viện hoặc Tạo giọng cho bài khác khi sẵn sàng."}
        ],
        [
            {title:"Mở bài trong PowerPoint", body:"Bấm Mở PowerPoint từ Thư viện hoặc chọn bài trên Mascot. Bấm F5 khi sẵn sàng trình chiếu."},
            {title:"Điều khiển bằng nút hoặc chuột", body:"Bấm Trước/Sau để lùi/tiến hiệu ứng rồi đổi slide. Lăn chuột lên để lùi, xuống để tiến trên slide hoặc bảng trợ giảng; lăn trong hàng Âm lượng sẽ tăng/giảm âm lượng. Bấm loa Anh/Việt để đọc, bấm lại để tạm dừng."},
            {title:"Mở, thu gọn hoặc di chuyển trợ giảng", body:"Bấm nhân vật để mở bảng; bấm mũi tên xuống trên bảng để thu gọn. Giữ và kéo nhân vật hoặc chỗ trống trên bảng để đổi vị trí. Bấm mắt gạch chéo để ẩn; mở lại bằng Mở trợ giảng nổi ở thanh bên trái."}
        ],
        [
            {title:"Tìm đúng bài", body:"Gõ tên bài, môn hoặc khối — có thể gõ không dấu. Kết hợp bộ lọc, sắp xếp và đổi giữa Thẻ/Danh sách."},
            {title:"Chọn một hoặc nhiều bài", body:"Tích ô chọn; giữ Shift để chọn một dải, hoặc giữ chuột kéo qua các bài. Thanh tìm kiếm và tác vụ vẫn hiện khi cuộn."},
            {title:"Tải, tìm nơi lưu hoặc xóa bài", body:"Bấm icon mũi tên tải để lưu bản PowerPoint. Bấm nút … của một bài → Mở trong Explorer để xem thư mục chứa bài. Icon thùng rác đưa bài vào thùng rác của tool; muốn khôi phục, mở nút ⋮ ở góc trên → Thùng rác."}
        ],
        [
            {title:"Chọn dịch vụ dịch và lưu mã", body:"Trong Cài đặt → Chung, điền tên thầy cô, trường và môn. Trong Dịch thuật, chọn Google Cloud, Apps Script, Gemini hoặc DeepL rồi làm theo hướng dẫn bên dưới để lưu cấu hình. Apps Script không cần key Google Cloud nhưng cần triển khai một lần bằng tài khoản Google. Chuyển đổi cần Internet; bài đang dở tiếp tục bằng dịch vụ đã chọn lúc bắt đầu."},
            {title:"Chọn giọng đọc và nhân vật", body:"Trong Giọng đọc, chọn giọng → Nghe thử → chỉnh tốc độ → Lưu. Trong Mascot, chọn nhân vật và kích thước vừa màn hình. Tool sẽ nhớ lựa chọn cho lần sau."},
            {title:"Sao lưu thư viện", body:"Mở Cài đặt → Dữ liệu → Sao lưu dữ liệu, rồi chọn nơi giữ bản sao. BiliClass cũng tự sao lưu theo lịch khi mở ứng dụng."},
            {title:"Khôi phục khi cần", body:"Chọn Khôi phục bản sao và chọn tệp sao lưu. Tool kiểm tra, mở thư viện khôi phục; thư viện trước vẫn được giữ."},
            {title:"Đổi nơi lưu hoặc cập nhật", body:"Dùng Đổi nơi lưu nếu cần chuyển thư viện sang ổ khác. Kiểm tra bản mới tại Cài đặt → Thông tin BiliClass."}
        ],
        [
            {title:"Không chọn được bài PowerPoint", body:"Tool nhận bài có đuôi .pptx. Nếu bài là .ppt, mở bài bằng PowerPoint rồi lưu thành .pptx và chọn lại. Mỗi bài tối đa 200 MB."},
            {title:"Chuyển đổi bị dừng hoặc báo lỗi", body:"Kiểm tra mạng và mã trong Cài đặt → Dịch thuật. Sửa theo thông báo rồi bấm Tiếp tục hoặc Thử lại bài lỗi. Tool giữ phần đã làm; file gốc vẫn còn."},
            {title:"Nút tạo giọng hoặc loa bị mờ", body:"Hãy chọn bài trước. Nếu slide thiếu lời đọc, mở nút … cạnh Xem trước slide để xem và bổ sung lời. Loa trên trợ giảng chỉ dùng được khi đang trình chiếu và phần đó có giọng đã tạo."},
            {title:"Không nghe thấy tiếng", body:"Kiểm tra hàng Âm lượng trên trợ giảng và loa của máy. Thử bấm loa Anh hoặc Việt có sẵn; nếu bài chưa có giọng, quay lại Tạo giọng đọc bài giảng để tạo trước."},
            {title:"Không biết bài đã lưu ở đâu", body:"Vào Bài giảng → nút … của bài → Mở trong Explorer. Với bài vừa tạo, có thể dùng nút Mở thư mục ở phần hoàn tất. Muốn mang thư viện sang máy khác, xem mục Cài đặt và sao lưu."}
        ]
    ]
    background: Rectangle { color: AppTheme.surface; radius: 16; border.color: AppTheme.adapt("#d6e4f6") }
    header: Item {
        implicitHeight: 132
        Label { x:24; y:18; text:"Hướng dẫn BiliClass"; color:guide.ink; font.pixelSize:23; font.weight:Font.Bold }
        Label { x:24; y:51; text:"Chọn việc cần làm ở bên trái, rồi làm theo từng bước."; color:guide.muted; font.pixelSize:13 }
        TextField {
            id: helpSearch; objectName: "helpSearch"
            x:24; y:78; width:parent.width-48; height:38
            text: guide.searchText; onTextChanged: guide.searchText = text
            placeholderText: "Tìm điều cần làm… (gõ không dấu cũng được)"; font.pixelSize:13; rightPadding:38
            Accessible.name: "Tìm trong hướng dẫn"
            background: Rectangle { radius:8; color:AppTheme.adapt("#f7faff"); border.color:helpSearch.activeFocus?AppTheme.blue:AppTheme.line }
            ToolButton { objectName:"helpClearSearch"; anchors.right:parent.right; anchors.verticalCenter:parent.verticalCenter; width:36; height:36; visible:!!helpSearch.text; text:"×"; font.pixelSize:20; Accessible.name:"Xóa từ tìm"; onClicked:guide.searchText="" }
        }
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
                    visible: guide.matchesTopic(index)
                    Layout.fillWidth:true; implicitHeight:45
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
            visible: guide.matchingTopics.length > 0
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
                            Layout.fillWidth:true; implicitHeight:stepRow.implicitHeight+(guide.activeTopic===0?16:24); radius:11; color:AppTheme.adapt("#f7faff")
                            RowLayout {
                                id:stepRow; anchors.fill:parent; anchors.margins:guide.activeTopic===0?8:12; spacing:12
                                Rectangle { Layout.alignment:Qt.AlignTop; implicitWidth:29; implicitHeight:29; radius:15; color:AppTheme.adapt("#e6f0ff"); Label { anchors.centerIn:parent; text:index+1; font.weight:Font.Bold; color:AppTheme.adapt("#0869f9") } }
                                ColumnLayout {
                                    Layout.fillWidth:true; spacing:4
                                    Label { text:modelData.title; color:guide.ink; font.pixelSize:15; font.weight:Font.DemiBold; wrapMode:Text.WordWrap; Layout.fillWidth:true }
                                    Label { text:modelData.body; color:guide.muted; font.pixelSize:13; wrapMode:Text.WordWrap; lineHeight:1.2; Layout.fillWidth:true }
                                }
                            }
                        }
                    }
                    ShortcutGuide { visible:guide.activeTopic===3; Layout.fillWidth:true; settings:bridge.mascotShortcuts }
                }
            }
        }
        Label { objectName:"helpNoResults"; visible:!guide.matchingTopics.length; Layout.fillWidth:true; Layout.fillHeight:true; verticalAlignment:Text.AlignVCenter; horizontalAlignment:Text.AlignHCenter; wrapMode:Text.WordWrap; text:"Chưa tìm thấy hướng dẫn phù hợp.\nThử từ ngắn hơn, như: chọn bài, giọng đọc, âm lượng."; font.pixelSize:14; color:guide.muted }
    }
    onActiveTopicChanged:if(stepsScroll.contentItem) stepsScroll.contentItem.contentY=0
    footer:Item {
        implicitHeight:65
        RowLayout {
            anchors.fill:parent; anchors.margins:16; spacing:8
            ActionButton { objectName:"helpClose"; text:"Đóng hướng dẫn"; onClicked:guide.close() }
            Item { Layout.fillWidth:true }
            ActionButton { objectName:"helpPrevious"; text:"← Mục trước"; visible:guide.matchingTopics.indexOf(guide.activeTopic)>0; onClicked:guide.moveTopic(-1) }
            ActionButton { objectName:"helpNext"; text:"Mục tiếp →"; primary:true; visible:guide.matchingTopics.indexOf(guide.activeTopic)<guide.matchingTopics.length-1; onClicked:guide.moveTopic(1) }
        }
    }
}
