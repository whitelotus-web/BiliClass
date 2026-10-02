import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "settingsPage"
    required property var bridge
    signal requestModelPack()
    signal requestBackup()
    signal requestLibrary()
    signal requestLogo()
    property int activeTab: 0
    onActiveTabChanged: { if (contentScroll.contentItem && contentScroll.contentItem.contentY !== undefined) contentScroll.contentItem.contentY = 0 }
    property string selectedMascot: bridge.settings.mascot
    property int mascotPreviewMode: 0
    readonly property bool wideMascotLayout: contentScroll.availableWidth >= 1020
    readonly property bool mascotPreviewVisible: mascotVisible.checked &&
        (mascotPreviewMode === 1 ? mascotExplanation.checked : mascotPreviewMode === 2 ? mascotQuiz.checked : true)
    readonly property string mascotPreviewText: selectedMascot === "Lumi"
        ? (mascotPreviewMode === 1 ? "Let's look at this idea step by step." : mascotPreviewMode === 2 ? "Take your time. Let's try the next question." : "Let's take this one step at a time.")
        : (mascotPreviewMode === 1 ? "Watch how this idea works!" : mascotPreviewMode === 2 ? "Great job! Ready for the next question?" : "Let's explore something new together!")
    function showMascotPreview(name) {
        selectedMascot = name
        mascotPreviewMode = 0
        if (!wideMascotLayout) Qt.callLater(function() {
            var viewport = contentScroll.contentItem
            var offset = stageCard.mapToItem(viewport, 0, 0).y
            viewport.contentY = Math.min(viewport.contentHeight - viewport.height, Math.max(0, viewport.contentY + offset - 10))
        })
    }
    clip: true

    readonly property color ink: "#112650"
    readonly property color muted: "#667997"
    readonly property color blue: "#0869f9"
    readonly property color line: "#dfe8f4"

    component Card: Frame {
        padding: 22
        background: Rectangle { color: "white"; radius: 16; border.color: page.line }
    }
    component Title: Label { color: page.ink; font.pixelSize: 19; font.weight: Font.Bold; wrapMode: Text.WordWrap }
    component Hint: Label { color: page.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Field: TextField {
        implicitHeight: 44; font.pixelSize: 13; color: page.ink; selectByMouse: true
        background: Rectangle { radius: 9; color: "#fbfdff"; border.color: parent.activeFocus ? page.blue : page.line }
    }
    component Choice: ComboBox {
        implicitHeight: 44; font.pixelSize: 13
        background: Rectangle { radius: 9; color: "#fbfdff"; border.color: parent.activeFocus ? page.blue : page.line }
    }
    component SaveButton: Button {
        id: saveButton
        implicitHeight: 44; leftPadding: 22; rightPadding: 22
        font.pixelSize: 13; font.weight: Font.DemiBold
        contentItem: Label { text: saveButton.text; color: "white"; font: saveButton.font; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: 9; color: saveButton.down ? "#0053d2" : saveButton.hovered ? "#147aff" : page.blue }
    }
    component SoftButton: Button {
        id: softButton
        property string iconName: ""
        implicitHeight: 42; leftPadding: 13; rightPadding: 13
        font.pixelSize: 12; font.weight: Font.DemiBold
        contentItem: RowLayout {
            spacing: 6
            Item { Layout.fillWidth: true }
            Image { visible: !!softButton.iconName; source: softButton.iconName ? "../assets/actions/" + softButton.iconName + ".png" : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 22; Layout.preferredHeight: 22; opacity: softButton.enabled ? 1 : .4 }
            Label { text: softButton.text; color: softButton.enabled ? page.blue : page.muted; font: softButton.font; verticalAlignment: Text.AlignVCenter }
            Item { Layout.fillWidth: true }
        }
        background: Rectangle { radius: 9; color: softButton.hovered ? "#edf5ff" : "white"; border.color: page.line }
    }

    ColumnLayout {
        anchors.fill: parent; spacing: 15
        Label { text: page.activeTab === 3 ? "Cài đặt Mascot" : "Cài đặt"; color: page.ink; font.pixelSize: 37; font.weight: Font.Bold }
        Hint { text: page.activeTab === 3 ? "Chọn bạn đồng hành và xem trước cách mascot xuất hiện trong tiết học." : "Thiết lập không gian dạy học của thầy cô. Mỗi nhóm có thể lưu riêng."; Layout.fillWidth: true }

        RowLayout {
            Layout.fillWidth: true; spacing: 5
            Repeater {
                model: [
                    {name: "Chung", icon: "settings"}, {name: "Song ngữ", icon: "bilingual"},
                    {name: "Giọng đọc", icon: "voice"}, {name: "Mascot", icon: "mascot"},
                    {name: "Lớp học", icon: "classroom"}, {name: "Dữ liệu", icon: "data"}
                ]
                Button {
                    id: tab
                    required property var modelData
                    required property int index
                    objectName: "settingsTab" + index
                    Layout.fillWidth: true; Layout.preferredWidth: 1; implicitHeight: 57
                    onClicked: page.activeTab = index
                    background: Rectangle {
                        color: page.activeTab === tab.index ? "#e7f2ff" : tab.hovered ? "#f5f8fc" : "transparent"
                        radius: 11
                        Rectangle { anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter; width: parent.width - 35; height: 2; color: page.blue; visible: page.activeTab === tab.index }
                    }
                    contentItem: RowLayout {
                        spacing: 7
                        Image { source: "../assets/navigation/" + tab.modelData.icon + (page.activeTab === tab.index ? "-active" : "") + ".png"; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 27; Layout.preferredHeight: 27 }
                        Label { text: tab.modelData.name; color: page.activeTab === tab.index ? page.blue : page.ink; font.pixelSize: 13; font.weight: page.activeTab === tab.index ? Font.Bold : Font.DemiBold; elide: Text.ElideRight; Layout.fillWidth: true }
                    }
                }
            }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: page.line }

        ScrollView {
            id: contentScroll
            objectName: "settingsContentScroll"
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
            ColumnLayout { width: contentScroll.availableWidth; spacing: 14

        RowLayout {
            visible: page.activeTab === 0; Layout.fillWidth: true; spacing: 14
            Card {
                Layout.fillWidth: true; Layout.preferredWidth: 2; Layout.alignment: Qt.AlignTop
                ColumnLayout { width: parent.width; spacing: 17
                    Title { text: "Thông tin thầy cô" }
                    Hint { text: "Hồ sơ dùng chung trên máy. Môn và khối lớp cụ thể được chọn cho từng bài; tên lớp được nhập khi bắt đầu tiết học."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; spacing: 6; Label { text: "Tên thầy/cô"; color: page.ink } Field { id: teacherName; objectName: "settingsTeacher"; text: bridge.settings.teacher; maximumLength: 100; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; spacing: 6; Label { text: "Trường"; color: page.ink } Field { id: schoolName; objectName: "settingsSchool"; text: bridge.settings.school; placeholderText: "Ví dụ: THPT ..."; maximumLength: 100; Layout.fillWidth: true } }
                    }
                    ColumnLayout { Layout.fillWidth: true; spacing: 6
                        Label { text: "Bộ môn giảng dạy"; color: page.ink }
                        Field { id: teachingSubjects; objectName: "settingsSubjects"; text: bridge.settings.subjects.join(", "); placeholderText: "Ví dụ: Ngữ văn, Lịch sử, Giáo dục kinh tế và pháp luật"; maximumLength: 500; Layout.fillWidth: true }
                        Hint { text: "Có thể nhập nhiều môn, ngăn cách bằng dấu phẩy. Đây là hồ sơ tham khảo; vẫn tạo được bài của mọi môn học."; Layout.fillWidth: true }
                    }
                    RowLayout { Layout.fillWidth: true
                        SoftButton { objectName: "uploadSchoolLogo"; text: "Tải logo trường (PNG/JPG)"; iconName: "upload"; onClicked: page.requestLogo() }
                        SoftButton { objectName: "removeSchoolLogo"; text: "Bỏ logo"; enabled: !!bridge.schoolLogoUrl; onClicked: bridge.removeSchoolLogo() }
                        Item { Layout.fillWidth: true }
                    }
                    Hint { text: "Logo tối đa 5 MB, tự lưu vào thư viện khi chọn và đi cùng bản sao lưu."; Layout.fillWidth: true }
                    CheckBox { id: showProfile; objectName: "settingsShowProfile"; text: "Hiện tên, trường và logo trên màn hình bài giảng"; checked: bridge.settings.show_profile }
                    RowLayout { Layout.fillWidth: true; Hint { text: "Mỗi bài chọn môn và khối 10, 11 hoặc 12 riêng; mỗi buổi chọn tên lớp riêng."; Layout.fillWidth: true } SaveButton { objectName: "saveProfile"; text: "Lưu thông tin"; onClicked: bridge.saveTeacherProfile(teacherName.text, schoolName.text, teachingSubjects.text, showProfile.checked) } }
                }
            }
            Card {
                Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.alignment: Qt.AlignTop
                ColumnLayout { width: parent.width; spacing: 9
                    Title { text: "Xem trước hồ sơ đã lưu" }
                    Hint { text: "Tên, trường và bộ môn bên dưới chỉ đổi sau khi bấm Lưu thông tin; logo được lưu ngay khi tải lên."; Layout.fillWidth: true }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 126; radius: 11; color: "#f2f7ff"
                        RowLayout { anchors.fill: parent; anchors.margins: 14; spacing: 10
                            Image { objectName: "savedProfileLogo"; visible: !!bridge.schoolLogoUrl; source: bridge.schoolLogoUrl; cache: false; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 56; Layout.preferredHeight: 70 }
                            Rectangle { visible: !bridge.schoolLogoUrl; Layout.preferredWidth: 56; Layout.preferredHeight: 56; radius: 10; color: "white"; border.color: page.line
                                Label { anchors.centerIn: parent; text: "Logo"; color: page.muted; font.pixelSize: 12 }
                            }
                            ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 5
                                Label { text: "BiliClass"; color: page.blue; font.pixelSize: 12 }
                                Label { objectName: "savedProfileTeacher"; text: bridge.settings.teacher || "Thầy cô"; color: page.ink; font.pixelSize: 17; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
                                Hint { objectName: "savedProfileSchool"; text: bridge.settings.school || "Chưa thêm trường"; Layout.fillWidth: true }
                                Hint { objectName: "savedProfileSubjects"; text: bridge.settings.subjects.length ? "Bộ môn: " + bridge.settings.subjects.join(", ") : "Chưa thêm bộ môn"; Layout.fillWidth: true }
                            }
                        }
                    }
                    Hint { objectName: "savedProfileVisibility"; text: bridge.settings.show_profile ? "Đang hiện tên, trường và logo trong bài giảng." : "Đang ẩn tên, trường và logo trong bài giảng."; Layout.fillWidth: true }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 1; Layout.fillWidth: true; spacing: 14
            Card {
                Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 13
                    Title { text: "Mức hỗ trợ song ngữ L0–L4" }
                    Hint { text: "Đây là hướng dẫn để chọn mức cho từng bài khi nhập tài liệu tiếng Việt và chuyển sang bài song ngữ. Level không cố định cho mọi môn hay mọi khối."; Layout.fillWidth: true }
                    Repeater {
                        model: [
                            {name: "L0 · Làm quen", detail: "Tiếng Việt là chính, thêm từ khóa tiếng Anh."},
                            {name: "L1 · Tiếp xúc", detail: "Thêm câu tiếng Anh ngắn cho hoạt động lớp."},
                            {name: "L2 · Cầu nối", detail: "Cặp Việt–Anh và English đơn giản khi đã chuẩn bị."},
                            {name: "L3 · Kết hợp", detail: "Dùng hai ngôn ngữ linh hoạt trong bài giảng."},
                            {name: "L4 · Ưu tiên English", detail: "English là chính, tiếng Việt hỗ trợ khi cần."}
                        ]
                        Frame { id: levelGuide; required property var modelData; required property int index
                            objectName: "settingsLevel" + index; Layout.fillWidth: true; padding: 12
                            background: Rectangle { radius: 10; color: "#fbfdff"; border.color: page.line }
                            contentItem: RowLayout { spacing: 14
                                Label { text: "L" + levelGuide.index; color: page.blue; font.pixelSize: 17; font.bold: true }
                                ColumnLayout { Layout.fillWidth: true; spacing: 2
                                    Label { text: levelGuide.modelData.name; color: page.ink; font.pixelSize: 14; font.bold: true }
                                    Hint { text: levelGuide.modelData.detail; Layout.fillWidth: true }
                                }
                            }
                        }
                    }
                    Hint { text: "Level điều chỉnh cách trợ giảng hỗ trợ ngôn ngữ; kiểu trình bày bên dưới quyết định chữ nào xuất hiện trên màn hình."; Layout.fillWidth: true }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 11
                    Title { text: "Bốn kiểu trình bày song ngữ" }
                    Hint { text: "Chọn cho từng bài tại bước tạo bài. Có thể đổi sau trong trình biên tập; ví dụ ở đây chỉ minh họa cách bố trí, không phải nội dung bài học."; Layout.fillWidth: true }
                    Repeater { model: [
                        {name: "Cùng dòng · từ khóa", detail: "Giữ câu tiếng Việt, chèn thuật ngữ tiếng Anh đã chuẩn bị ngay sau từ tương ứng: tế bào (cell)."},
                        {name: "Hai dòng", detail: "Dòng tiếng Việt trước; bản tiếng Anh in nghiêng ở dòng dưới."},
                        {name: "Hai cột", detail: "Tiếng Việt ở bên trái, bản tiếng Anh tương ứng ở bên phải."},
                        {name: "English toàn phần", detail: "Chỉ hiện bản tiếng Anh; thầy cô có thể bật VI Rescue khi cần."}
                    ]
                        Frame { required property var modelData; Layout.fillWidth: true; padding: 12
                            background: Rectangle { radius: 10; color: "#fbfdff"; border.color: page.line }
                            contentItem: ColumnLayout { spacing: 3
                                Label { text: modelData.name; color: page.ink; font.pixelSize: 14; font.bold: true }
                                Hint { text: modelData.detail; Layout.fillWidth: true }
                            }
                        }
                    }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 2; Layout.fillWidth: true; spacing: 14
            Card { objectName: "voicePairCard"; visible: bridge.voicePairs.length > 0; Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 9
                    Title { text: "Bộ giọng song ngữ gợi ý" }
                    Hint { text: "Chọn nhanh một cặp giọng Việt–Anh hài hòa. Sau đó có thể đổi riêng từng giọng ở hai cột bên dưới; mascot không đổi theo giọng."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 10
                        Choice { id: bilingualVoicePair; objectName: "settingsVoicePair"; model: bridge.voicePairs; textRole: "name"; Layout.fillWidth: true }
                        SaveButton { objectName: "applyVoicePair"; text: "Dùng bộ giọng"; onClicked: bridge.setVoicePair(bilingualVoicePair.currentIndex) }
                    }
                }
            }
            RowLayout {
                objectName: "voiceLanguageColumns"
                Layout.fillWidth: true; spacing: 14
                Card {
                    objectName: "voiceEnglishCard"
                    Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignTop
                    ColumnLayout { width: parent.width; spacing: 12
                        Title { text: "Giọng đọc tiếng Anh" }
                        Hint { text: bridge.kokoroReady ? "Năm giọng Kokoro chạy ngoại tuyến. Chọn giọng để dạy hoặc nghe thử trước." : "Chưa tìm thấy Kokoro. BiliClass đang dùng giọng Windows trên máy."; Layout.fillWidth: true }
                        Repeater {
                            model: bridge.englishVoices
                            Frame {
                                id: voiceOption
                                required property var modelData
                                required property int index
                                objectName: "settingsVoiceOption" + index
                                Layout.fillWidth: true; padding: 9
                                background: Rectangle { radius: 10; color: bridge.voiceSettings.en === voiceOption.modelData.id ? "#eef6ff" : "#fbfdff"; border.color: bridge.voiceSettings.en === voiceOption.modelData.id ? page.blue : page.line }
                                contentItem: ColumnLayout { spacing: 2
                                    RowLayout { Layout.fillWidth: true; spacing: 5
                                        RadioButton { objectName: "selectVoice" + voiceOption.index; text: voiceOption.modelData.name; font.pixelSize: 12; Layout.fillWidth: true; Layout.minimumWidth: 0; checked: bridge.voiceSettings.en === voiceOption.modelData.id; onClicked: bridge.setVoice("en", voiceOption.index) }
                                        SoftButton { objectName: "previewVoice" + voiceOption.index; text: "Nghe thử"; iconName: "play"; implicitHeight: 34; enabled: !bridge.busy; onClicked: bridge.previewVoiceChoice(voiceOption.index, voiceSample.text) }
                                    }
                                    Hint { text: voiceOption.modelData.detail || "Giọng Windows dự phòng"; Layout.fillWidth: true; leftPadding: 10; font.pixelSize: 11 }
                                }
                            }
                        }
                        ColumnLayout { Layout.fillWidth: true; spacing: 6
                            Label { text: "Câu nghe thử tiếng Anh"; color: page.ink }
                            Field { id: voiceSample; objectName: "settingsVoiceSample"; text: "Good morning, class. Let's explore today's lesson together."; maximumLength: 250; Layout.fillWidth: true }
                        }
                        RowLayout { Layout.fillWidth: true; SaveButton { objectName: "previewEnglishVoice"; text: "▶  Nghe thử English"; enabled: !bridge.busy && bridge.englishVoices.length > 0; onClicked: bridge.previewVoice(voiceSample.text) } SoftButton { text: "Dừng đọc"; onClicked: bridge.stopSpeech() } Item { Layout.fillWidth: true } }
                        Hint { text: "Lần nghe đầu cần nạp model. Âm thanh được lưu theo nội dung, giọng và tốc độ."; Layout.fillWidth: true }
                    }
                }
                Card {
                    objectName: "voiceVietnameseCard"
                    Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignTop
                    ColumnLayout { width: parent.width; spacing: 12
                        Title { text: "Giọng đọc tiếng Việt" }
                        Hint { text: bridge.vieneuReady ? "Bốn giọng VieNeu ngoại tuyến cho bài giảng tiếng Việt và VI Rescue." : bridge.vietnameseVoices.length ? "Chưa có VieNeu; đang dùng giọng tiếng Việt Windows tạm thời." : "Chưa có bộ giọng tiếng Việt trong bản này."; Layout.fillWidth: true }
                        Repeater {
                            model: bridge.vietnameseVoices
                            Frame {
                                id: viVoiceOption
                                required property var modelData
                                required property int index
                                objectName: "settingsVietnameseVoiceOption" + index
                                Layout.fillWidth: true; padding: 9
                                background: Rectangle { radius: 10; color: bridge.voiceSettings.vi === viVoiceOption.modelData.id ? "#eef6ff" : "#fbfdff"; border.color: bridge.voiceSettings.vi === viVoiceOption.modelData.id ? page.blue : page.line }
                                contentItem: ColumnLayout { spacing: 2
                                    RowLayout { Layout.fillWidth: true; spacing: 5
                                        RadioButton { objectName: "selectVietnameseVoice" + viVoiceOption.index; text: viVoiceOption.modelData.name; font.pixelSize: 12; Layout.fillWidth: true; Layout.minimumWidth: 0; checked: bridge.voiceSettings.vi === viVoiceOption.modelData.id; onClicked: bridge.setVoice("vi", viVoiceOption.index) }
                                        SoftButton { objectName: "previewVietnameseVoice" + viVoiceOption.index; text: "Nghe thử"; iconName: "play"; implicitHeight: 34; enabled: !bridge.busy; onClicked: bridge.previewVietnameseVoiceChoice(viVoiceOption.index, vietnameseVoiceSample.text) }
                                    }
                                    Hint { text: viVoiceOption.modelData.detail || "Giọng có sẵn trong Windows"; Layout.fillWidth: true; leftPadding: 10; font.pixelSize: 11 }
                                }
                            }
                        }
                        ColumnLayout { Layout.fillWidth: true; spacing: 6
                            Label { text: "Câu nghe thử tiếng Việt"; color: page.ink }
                            Field { id: vietnameseVoiceSample; objectName: "settingsVietnameseVoiceSample"; text: "Chào các em. Hôm nay chúng ta sẽ khám phá một ý tưởng mới."; maximumLength: 250; Layout.fillWidth: true }
                        }
                        RowLayout { Layout.fillWidth: true
                            SaveButton { objectName: "previewSelectedVietnameseVoice"; text: "▶ Nghe thử tiếng Việt"; enabled: !bridge.busy && bridge.vietnameseVoices.length > 0; onClicked: bridge.previewVietnameseVoice(vietnameseVoiceSample.text) }
                            Item { Layout.fillWidth: true }
                        }
                        Hint { text: "VieNeu có thể cần khoảng nửa phút để nạp lần đầu. Chỉ phát giọng khi bấm đọc hoặc chuẩn bị âm thanh."; Layout.fillWidth: true }
                    }
                }
            }
            Card { Layout.fillWidth: true
                RowLayout { width: parent.width; spacing: 14
                    Label { text: "Tốc độ đọc chung cho tiếng Anh và tiếng Việt"; color: page.ink; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                    Choice { id: voiceRate; objectName: "settingsVoiceRate"; model: ["Rất chậm", "Chậm", "Hơi chậm", "Bình thường", "Hơi nhanh", "Nhanh", "Rất nhanh"]; currentIndex: bridge.voiceSettings.rate + 3; Layout.preferredWidth: 220; onActivated: bridge.setVoiceRate(currentIndex - 3) }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 3; Layout.fillWidth: true; spacing: 14
            GridLayout {
                Layout.fillWidth: true; columns: page.wideMascotLayout ? 3 : 2; columnSpacing: 12; rowSpacing: 12
                Repeater { model: [
                    {name: "Milo", image: "../assets/milo-welcome.png", mood: "Năng động · vui vẻ", detail: "Mang năng lượng tích cực vào lớp học.", strengths: ["Khởi động bài", "Hỏi lớp nhanh", "Khích lệ học sinh", "Hoạt động quiz"]},
                    {name: "Lumi", image: "../assets/lumi-welcome.png", mood: "Bình tĩnh · thân thiện", detail: "Đồng hành nhẹ nhàng qua từng ý học.", strengths: ["Giải thích rõ", "Đọc từ vựng", "VI Rescue", "Củng cố cuối bài"]}
                ]
                    Rectangle { id: mascotCard; required property var modelData; required property int index
                        readonly property bool chosen: page.selectedMascot === modelData.name
                        Layout.row: 0; Layout.column: index; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: 337
                        radius: 16; color: chosen ? "#f3f8ff" : "white"; border.color: chosen ? page.blue : page.line; border.width: chosen ? 2 : 1
                        MouseArea { objectName: "mascot" + mascotCard.modelData.name; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: page.selectedMascot = mascotCard.modelData.name }
                        ColumnLayout { anchors.fill: parent; anchors.margins: 13; spacing: 7
                            RowLayout { Layout.fillWidth: true
                                Label { text: mascotCard.chosen ? "●  Đang chọn" : "○  Chọn bạn này"; color: mascotCard.chosen ? page.blue : page.muted; font.pixelSize: 12; font.bold: true }
                                Item { Layout.fillWidth: true }
                                Label { text: mascotCard.modelData.name === "Milo" ? "01 / NĂNG LƯỢNG" : "02 / ĐIỀM TĨNH"; color: page.muted; font.pixelSize: 9; font.bold: true }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                Image { source: mascotCard.modelData.image; Layout.preferredWidth: 118; Layout.preferredHeight: 139; fillMode: Image.PreserveAspectFit; sourceSize.width: 236; sourceSize.height: 278 }
                                ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                                    Label { text: mascotCard.modelData.name; color: page.ink; font.pixelSize: 25; font.bold: true }
                                    Label { text: mascotCard.modelData.mood; color: mascotCard.modelData.name === "Milo" ? page.blue : "#a66b24"; font.pixelSize: 12; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Hint { text: mascotCard.modelData.detail; Layout.fillWidth: true; font.pixelSize: 11 }
                                }
                            }
                            Rectangle { Layout.fillWidth: true; height: 1; color: page.line }
                            Label { text: "PHÙ HỢP KHI"; color: page.muted; font.pixelSize: 10; font.bold: true }
                            GridLayout { Layout.fillWidth: true; columns: 2; columnSpacing: 4; rowSpacing: 4
                                Repeater { model: mascotCard.modelData.strengths
                                    Label { required property string modelData; text: "✓  " + modelData; color: page.ink; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true; Layout.preferredWidth: 1 }
                                }
                            }
                            Item { Layout.fillHeight: true }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                SoftButton { text: "Nghe câu mẫu"; iconName: "play"; Layout.fillWidth: true; enabled: !bridge.busy; onClicked: { page.selectedMascot = mascotCard.modelData.name; bridge.previewVoice(page.mascotPreviewText) } }
                                SoftButton { objectName: "mascotSlide" + mascotCard.modelData.name; text: "Xem trên slide"; Layout.fillWidth: true; onClicked: page.showMascotPreview(mascotCard.modelData.name) }
                            }
                        }
                    }
                }
                Rectangle { id: stageCard
                    Layout.row: page.wideMascotLayout ? 0 : 1; Layout.column: page.wideMascotLayout ? 2 : 0
                    Layout.columnSpan: page.wideMascotLayout ? 1 : 2; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: 337
                    radius: 16; color: "white"; border.color: page.line
                    ColumnLayout { anchors.fill: parent; anchors.margins: 13; spacing: 8
                        RowLayout { Layout.fillWidth: true
                            Label { text: "Xem trước khi dạy"; color: page.ink; font.pixelSize: 17; font.bold: true; Layout.fillWidth: true }
                            Label { text: "TRÊN MÀN CHIẾU"; color: page.blue; font.pixelSize: 9; font.bold: true }
                        }
                        Rectangle { id: mascotMiniSlide; objectName: "mascotMiniSlide"; Layout.fillWidth: true; Layout.fillHeight: true; radius: 12; clip: true; color: "#dcecff"
                            Rectangle { anchors.fill: parent; anchors.margins: 8; radius: 10; color: "#fafdff"; border.color: "#b7d5f8" }
                            Label { anchors.left: parent.left; anchors.leftMargin: 20; anchors.top: parent.top; anchors.topMargin: 17; text: page.mascotPreviewMode === 2 ? "CÂU HỎI NHANH" : page.mascotPreviewMode === 1 ? "GIẢI THÍCH" : "BÀI GIẢNG SONG NGỮ"; color: page.blue; font.pixelSize: 10; font.bold: true }
                            Label { anchors.left: parent.left; anchors.leftMargin: 20; anchors.top: parent.top; anchors.topMargin: 41; width: parent.width - 115; text: page.mascotPreviewMode === 2 ? "Cả lớp sẵn sàng chưa?" : page.mascotPreviewMode === 1 ? "Cùng hiểu từng bước" : "Cùng khám phá bài học"; color: page.ink; font.pixelSize: 14; font.bold: true; wrapMode: Text.WordWrap }
                            Rectangle { visible: page.mascotPreviewVisible; width: Math.min(parent.width - 36, 225); height: 53; radius: 14; color: "white"; border.color: "#bed5f4"; anchors.top: parent.top; anchors.topMargin: 82; x: mascotPosition.currentIndex === 1 ? parent.width - width - 18 : 18
                                Label { anchors.fill: parent; anchors.margins: 8; text: page.mascotPreviewText; color: page.ink; font.pixelSize: 11; font.bold: true; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter; textFormat: Text.PlainText }
                            }
                            Mascot { id: mascotPreview; objectName: "mascotPreview"; visible: page.mascotPreviewVisible; character: page.selectedMascot; expression: page.mascotPreviewMode === 1 ? "thinking" : page.mascotPreviewMode === 2 ? "celebrate" : "speaking"; subject: mascotSubject.text; accessories: mascotAccessories.checked; reducedMotion: reducedMotion.checked; width: Math.max(65, Math.min(104, mascotSize.value * .68)); height: width + 15; anchors.bottom: parent.bottom; anchors.bottomMargin: 5; x: mascotPosition.currentIndex === 1 ? 16 : parent.width - width - 16 }
                            Label { visible: !page.mascotPreviewVisible; anchors.centerIn: parent; text: !mascotVisible.checked ? "Mascot đang ẩn khi dạy" : page.mascotPreviewMode === 1 ? "Mascot ẩn khi giải thích" : "Mascot ẩn khi quiz"; color: page.muted; font.pixelSize: 12 }
                        }
                        RowLayout { Layout.fillWidth: true; spacing: 5
                            Repeater { model: ["Slide", "Giải thích", "Quiz"]
                                Button { id: contextButton; required property string modelData; required property int index; objectName: "mascotPreviewMode" + index; text: modelData; Layout.fillWidth: true; implicitHeight: 34; onClicked: page.mascotPreviewMode = index
                                    background: Rectangle { radius: 8; color: page.mascotPreviewMode === contextButton.index ? "#e8f2ff" : "white"; border.color: page.mascotPreviewMode === contextButton.index ? page.blue : page.line }
                                    contentItem: Label { text: contextButton.text; color: page.mascotPreviewMode === contextButton.index ? page.blue : page.muted; font.pixelSize: 11; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }
                        Hint { text: "Ảnh mẫu dùng trạng thái thật; giọng English lấy từ tab Giọng đọc, không tự đổi theo Milo/Lumi."; Layout.fillWidth: true; font.pixelSize: 10 }
                    }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 13
                    Title { text: "Cách hiển thị trong lớp" }
                    Hint { text: "Bật theo từng tình huống. Bản xem trước phía trên cập nhật ngay; màn hình dạy áp dụng sau khi lưu."; Layout.fillWidth: true }
                    GridLayout { Layout.fillWidth: true; columns: page.wideMascotLayout ? 3 : 2; columnSpacing: 12
                        CheckBox { id: mascotVisible; objectName: "mascotVisible"; text: "Hiện khi dạy"; checked: bridge.mascotSettings.visible }
                        CheckBox { id: mascotExplanation; objectName: "mascotExplanation"; text: "Hiện khi giải thích"; checked: bridge.mascotSettings.show_explanation }
                        CheckBox { id: mascotQuiz; objectName: "mascotQuiz"; text: "Hiện khi quiz"; checked: bridge.mascotSettings.show_quiz }
                        CheckBox { id: mascotAccessories; objectName: "mascotAccessories"; text: "Hiện nhãn môn học"; checked: bridge.mascotSettings.accessories }
                        CheckBox { id: reducedMotion; objectName: "mascotReducedMotion"; text: "Giảm chuyển động"; checked: bridge.mascotSettings.reduced_motion }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: page.line }
                    RowLayout { Layout.fillWidth: true; spacing: 14
                        ColumnLayout { Layout.fillWidth: true; spacing: 5
                            Label { text: "Vị trí trên màn chiếu"; color: page.ink; font.bold: true }
                            Choice { id: mascotPosition; objectName: "mascotPosition"; model: ["Góc phải dưới", "Góc trái dưới"]; currentIndex: bridge.mascotSettings.position === "left" ? 1 : 0; Layout.fillWidth: true }
                        }
                        ColumnLayout { Layout.fillWidth: true; spacing: 5
                            Label { text: "Nhãn môn trong bản xem trước"; color: page.ink; font.bold: true }
                            Field { id: mascotSubject; objectName: "mascotSubject"; text: bridge.lesson.subject || "Môn học"; maximumLength: 60; Layout.fillWidth: true }
                        }
                    }
                    ColumnLayout { Layout.fillWidth: true; spacing: 5
                        RowLayout { Layout.fillWidth: true; Label { text: "Kích thước mascot"; color: page.ink; font.bold: true; Layout.fillWidth: true } Hint { text: Math.round(mascotSize.value) + " px" } }
                        RowLayout { Layout.fillWidth: true; spacing: 8
                            Slider { id: mascotSize; objectName: "mascotSize"; from: 60; to: 160; value: bridge.mascotSettings.size; Layout.fillWidth: true }
                            Repeater { model: [{label:"Nhỏ",size:80},{label:"Vừa",size:110},{label:"Lớn",size:150}]
                                Button { id: sizeChoice; required property var modelData; text: modelData.label; implicitWidth: 58; implicitHeight: 34; onClicked: mascotSize.value = modelData.size
                                    background: Rectangle { radius: 8; color: Math.abs(mascotSize.value - sizeChoice.modelData.size) < 16 ? "#e8f2ff" : "white"; border.color: Math.abs(mascotSize.value - sizeChoice.modelData.size) < 16 ? page.blue : page.line }
                                    contentItem: Label { text: sizeChoice.text; color: page.ink; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }
                    }
                    Hint { text: "Mỗi bài dùng tên môn riêng; nhãn chỉ hiện khi bật. Mascot dùng bốn hình trạng thái và chuyển động nhẹ khi không bật Giảm chuyển động; chưa phải hoạt hình nhiều khung hình."; Layout.fillWidth: true; font.pixelSize: 11 }
                    RowLayout { Layout.fillWidth: true; Hint { text: "Sau khi lưu, kéo trực tiếp mascot để đặt ở đâu tùy thích. Bấm nhanh để mở nút trợ giảng; chọn Về góc để đặt lại vị trí."; Layout.fillWidth: true } SaveButton { objectName: "saveMascot"; text: "Lưu cài đặt Mascot"; onClicked: bridge.saveMascotPreferences(page.selectedMascot, mascotVisible.checked, Math.round(mascotSize.value), mascotPosition.currentIndex ? "left" : "right", reducedMotion.checked, mascotAccessories.checked, mascotExplanation.checked, mascotQuiz.checked) } }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 4; Layout.fillWidth: true; spacing: 14
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 16
                    Title { text: "Mặc định khi mở lớp học" }
                    Hint { text: "Giúp bắt đầu tiết học nhanh hơn. Thầy cô vẫn đổi được từng mục ngay trước khi bắt đầu lớp hoặc mở câu hỏi."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Cách tham gia"; color: page.ink } Choice { id: classMode; objectName: "settingsClassMode"; model: ["Ẩn danh", "Số chỗ ngồi"]; currentIndex: bridge.classroomSettings.mode === "seat" ? 1 : 0; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Sĩ số tối đa"; color: page.ink } SpinBox { id: classCapacity; objectName: "settingsClassCapacity"; from: 1; to: 200; value: bridge.classroomSettings.capacity; editable: true; Layout.fillWidth: true } }
                    }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Thời gian trả lời mặc định"; color: page.ink } SpinBox { id: classDuration; from: 5; to: 3600; value: bridge.classroomSettings.duration; editable: true; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Ngôn ngữ câu hỏi"; color: page.ink } Choice { id: classLanguage; model: ["Việt–Anh", "Tiếng Việt", "English"]; currentIndex: ["both", "vi", "en"].indexOf(bridge.classroomSettings.language); Layout.fillWidth: true } }
                    }
                    Hint { text: "QR và địa chỉ LAN được tạo theo mạng thật lúc bắt đầu lớp. Nếu mạng hoặc cổng đổi, ứng dụng báo QR mới; học sinh có thể dùng mã khôi phục."; Layout.fillWidth: true }
                    SaveButton { objectName: "saveClassroom"; text: "Lưu mặc định lớp học"; Layout.alignment: Qt.AlignRight; onClicked: bridge.saveClassroomSettings(classMode.currentIndex ? "seat" : "anonymous", classCapacity.value, classDuration.value, ["both", "vi", "en"][classLanguage.currentIndex]) }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 5; Layout.fillWidth: true; spacing: 14
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 14
                    Title { text: "Thư viện bài giảng trên máy" }
                    Hint { text: "Bài học, thuật ngữ, bản sao lưu và âm thanh của thầy cô được lưu tại:"; Layout.fillWidth: true }
                    Hint { text: bridge.dataPath; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: page.ink }
                    RowLayout { Layout.fillWidth: true; SoftButton { text: "Mở thư mục dữ liệu"; onClicked: bridge.openData() } SoftButton { objectName: "settingsBackup"; text: "Sao lưu thư viện"; enabled: !bridge.busy; onClicked: bridge.backupLibrary() } SoftButton { text: "Khôi phục bản sao"; enabled: !bridge.busy; onClicked: page.requestBackup() } SoftButton { text: "Mở thư viện khác"; enabled: !bridge.busy; onClicked: page.requestLibrary() } }
                    Hint { text: "Khôi phục tạo thư mục mới; không ghi đè thư viện đang dùng. Bài riêng có thể xuất thành gói .biliclass trong trình biên tập."; Layout.fillWidth: true }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 12
                    Title { text: "Gói dịch ngoại tuyến" }
                    Hint { text: bridge.modelReady ? "● Việt → Anh: sẵn sàng" : "○ Việt → Anh: chưa cài"; color: bridge.modelReady ? "#168567" : page.muted }
                    Hint { text: bridge.reverseModelReady ? "● Anh → Việt: sẵn sàng" : "○ Anh → Việt: chưa cài"; color: bridge.reverseModelReady ? "#168567" : page.muted }
                    SoftButton { text: "Cài gói dịch từ máy / USB"; enabled: !bridge.busy; onClicked: page.requestModelPack() }
                    Hint { text: "Ứng dụng không tự tải bài giảng lên Internet. Bản dịch máy luôn là nháp để thầy cô sửa và duyệt."; Layout.fillWidth: true }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 8
                    Title { text: "Nhận dạng văn bản từ ảnh" }
                    Hint { text: bridge.ocrStatus; Layout.fillWidth: true }
                }
            }
        }
            }
        }
    }
}
