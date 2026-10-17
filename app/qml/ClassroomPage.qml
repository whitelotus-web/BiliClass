import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ContentScrollView {
    id: page; outerGutter: true
    required property var classroom
    required property var bridge
    signal requestLibrary()
    signal requestPreparation()
    signal requestEditor()
    signal requestReports()
    readonly property var round: classroom.state.round || ({})
    property real now: Date.now()
    property real clockOffset: 0
    property string selectedQuestion: ""
    readonly property bool active: classroom.running && classroom.state.status === "active"
    readonly property int approvedQuestions: (bridge.lesson.questions || []).filter(function(q) { return q.approved }).length
    function chooseNetwork() {
        const index = classroom.interfaces.findIndex(function(row) { return row.host === classroom.preferredHost })
        host.currentIndex = Math.max(0, index)
    }
    Connections {
        target: page.classroom
        function onInterfacesChanged() { Qt.callLater(page.chooseNetwork) }
        function onChanged() { if (page.classroom.state.server_time) page.clockOffset = page.classroom.state.server_time * 1000 - Date.now() }
    }
    Timer { interval: 250; repeat: true; running: page.visible && page.active && page.round.status === "open"; onTriggered: page.now = Date.now() }
    onVisibleChanged: if (visible) { classroom.refreshInterfaces(); if (bridge.lesson.id) bridge.refreshReadiness() }
    contentWidth: availableWidth
    component Copy: Label { color: "#687b94"; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText; Layout.fillWidth: true }
    component Title: Label { color: "#152d4d"; font.pixelSize: 17; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    component Panel: Frame { padding: 18; background: Rectangle { color: "white"; radius: 12; border.color: "#dce5f0" } }
    ColumnLayout { width: page.availableWidth; spacing: 18
        RowLayout { Layout.fillWidth: true
            ColumnLayout { Layout.fillWidth: true; spacing: 6
                Label { text: "Lớp học"; color: "#152d4d"; font.pixelSize: 28; font.bold: true }
                Copy { text: "Hỏi đáp trực tiếp qua điện thoại học sinh. Không cần mở lớp nếu chỉ trình chiếu và đọc bài." }
            }
            ActionButton { objectName: "classroomReportsButton"; text: "Kết quả lớp học"; iconName: "view"; onClicked: page.requestReports() }
        }
        Copy { objectName: "classroomMessage"; text: classroom.message; color: "#41648c" }
        GridLayout { visible: !classroom.running; Layout.fillWidth: true; columns: width > 940 ? 2 : 1; columnSpacing: 16; rowSpacing: 14
            Panel { Layout.fillWidth: true; Layout.alignment: Qt.AlignTop; Layout.preferredWidth: 1
                ColumnLayout { width: parent.width; spacing: 13
                    Title { text: "01  Chọn bài và chuẩn bị câu hỏi" }
                    RowLayout { Layout.fillWidth: true
                        SelectBox { id: lessonPicker; objectName: "classroomLessonPicker"; model: bridge.lessons; textRole: "title"; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                        ActionButton { objectName: "classroomSelectLesson"; text: "Dùng bài này"; enabled: !classroom.busy && !bridge.narrationBusy && lessonPicker.currentIndex >= 0; onClicked: bridge.selectLessonForClass(bridge.lessons[lessonPicker.currentIndex].id) }
                    }
                    Title { objectName: "classroomSelectedTitle"; text: bridge.lesson.title || "Chưa chọn bài giảng"; font.pixelSize: 15 }
                    Copy { text: !bridge.lesson.id ? "Chọn bài đã có trong thư viện để bắt đầu." : bridge.readiness.prepared_ready ? "✓ Bản bài hiện tại đã duyệt và chốt." : "Cần duyệt nội dung và chốt bản chuẩn bị trước khi mở lớp."; color: bridge.readiness.prepared_ready ? "#168567" : "#9e6423" }
                    Copy { text: page.approvedQuestions + " câu hỏi đã duyệt" + (page.approvedQuestions ? " · Chỉ các câu này được gửi cho học sinh." : " · Thêm câu hỏi để học sinh có nội dung trả lời.") }
                    Flow { Layout.fillWidth: true; spacing: 8
                        ActionButton { objectName: "classroomPrepareButton"; text: "Kiểm tra và chốt bài"; enabled: !!bridge.lesson.id && !classroom.busy; onClicked: page.requestPreparation() }
                        ActionButton { objectName: "classroomQuizButton"; text: "Soạn câu hỏi"; enabled: !!bridge.lesson.id && !classroom.busy; onClicked: page.requestEditor() }
                        ActionButton { objectName: "classroomLibraryButton"; text: "Thư viện"; enabled: !classroom.busy; onClicked: page.requestLibrary() }
                    }
                    Copy { text: "Câu hỏi trắc nghiệm hoặc khảo sát phải được thầy cô soạn và duyệt. BiliClass không tự lấy đáp án từ hình slide." }
                }
            }
            Panel { Layout.fillWidth: true; Layout.alignment: Qt.AlignTop; Layout.preferredWidth: 1
                ColumnLayout { width: parent.width; spacing: 12
                    Title { text: "02  Mở tiết học" }
                    TextField { id: title; objectName: "classTitle"; placeholderText: "Tên lớp / tiết, ví dụ: Vật lý 11A · Dao động"; maximumLength: 150; Layout.fillWidth: true; selectByMouse: true }
                    RowLayout { Layout.fillWidth: true
                        SelectBox { id: mode; objectName: "classMode"; model: ["Ẩn danh", "Số chỗ ngồi"]; currentIndex: bridge.classroomSettings.mode === "seat" ? 1 : 0; Layout.fillWidth: true }
                        Label { text: "Tối đa"; color: "#687b94" }
                        SpinBox { id: size; objectName: "classSize"; from: 1; to: 200; value: bridge.classroomSettings.capacity; editable: true }
                    }
                    Copy { text: mode.currentIndex ? "Mỗi học sinh chọn số chỗ riêng, không cần tài khoản." : "Không thu tên học sinh; kết quả dùng mã người tham gia." }
                    SelectBox { id: host; objectName: "classroomNetwork"; model: classroom.interfaces; textRole: "name"; enabled: !classroom.scanningInterfaces; Layout.fillWidth: true }
                    Copy { text: classroom.interfaces[host.currentIndex] && classroom.interfaces[host.currentIndex].host === "127.0.0.1" ? "Chỉ thử trên máy này. Chọn Wi-Fi/Ethernet để điện thoại vào lớp." : "Máy giáo viên và điện thoại học sinh cần cùng mạng Wi-Fi/LAN."; color: classroom.interfaces[host.currentIndex] && classroom.interfaces[host.currentIndex].host === "127.0.0.1" ? "#9e6423" : "#687b94" }
                    ActionButton { text: classroom.scanningInterfaces ? "Đang tìm mạng…" : "Làm mới mạng"; enabled: !classroom.scanningInterfaces; onClicked: classroom.refreshInterfaces() }
                    Copy { objectName: "classroomStartHelp"; visible: !bridge.lesson.id || !bridge.readiness.prepared_ready || !title.text.trim(); text: !bridge.lesson.id ? "Chọn bài ở bước 1." : !bridge.readiness.prepared_ready ? "Bấm Kiểm tra và chốt bài ở bước 1." : "Điền tên lớp / tiết để mở QR."; color: "#9e6423" }
                    ActionButton { objectName: "startClassButton"; text: classroom.busy ? "Đang mở lớp…" : "Mở lớp · Hiện QR"; primary: true; Layout.fillWidth: true; enabled: !classroom.busy && !bridge.narrationBusy && !classroom.scanningInterfaces && host.currentIndex >= 0 && !!bridge.lesson.id && !!bridge.readiness.prepared_ready && !!title.text.trim(); onClicked: classroom.start(title.text, mode.currentIndex ? "seat" : "anonymous", size.value, classroom.interfaces[host.currentIndex].host, "") }
                }
            }
        }
        Panel { visible: classroom.running; Layout.fillWidth: true
            RowLayout { width: parent.width; spacing: 20
                Image { source: classroom.qrImage; Layout.preferredWidth: 156; Layout.preferredHeight: 156; fillMode: Image.PreserveAspectFit; smooth: false; Accessible.name: "QR tham gia lớp" }
                ColumnLayout { Layout.fillWidth: true; spacing: 9
                    Title { text: classroom.state.title || ""; font.pixelSize: 22 }
                    Title { text: (classroom.state.joined || 0) + " / " + (classroom.state.capacity || 0) + " đã tham gia"; color: "#0869f9" }
                    Copy { text: classroom.state.status === "ended" ? "Tiết đã kết thúc. Mở Kết quả lớp học để xem và tải dữ liệu." : "Quét QR bằng điện thoại cùng mạng. Chọn Thử trên máy để kiểm tra trước." }
                    TextField { text: classroom.joinUrl; readOnly: true; selectByMouse: true; Layout.fillWidth: true; font.pixelSize: 11 }
                    Flow { Layout.fillWidth: true; spacing: 8
                        ActionButton { text: "Sao chép link"; enabled: page.active; onClicked: classroom.copyUrl() }
                        ActionButton { objectName: "classroomTryStudent"; text: "Thử trên máy"; enabled: page.active; onClicked: classroom.openStudentPage() }
                        ActionButton { text: "Chiếu câu hỏi"; enabled: page.active; onClicked: bridge.requestClassroomProjection() }
                    }
                }
            }
        }
        Panel { visible: classroom.running; Layout.fillWidth: true
            ColumnLayout { width: parent.width; spacing: 13
                RowLayout { Layout.fillWidth: true
                    Title { text: "03  Điều khiển câu hỏi" }
                    Label { objectName: "classroomCountdown"; visible: page.round.status === "open"; text: Math.max(0, Math.ceil((page.round.deadline * 1000 - page.now - page.clockOffset) / 1000)) + " giây"; font.pixelSize: 22; font.bold: true; color: "#0869f9" }
                }
                Copy { visible: !(classroom.state.questions || []).length; text: "Tiết này chưa có câu hỏi đã duyệt. Có thể kết thúc, soạn câu hỏi rồi mở tiết mới. Bản câu hỏi trong tiết đang mở được giữ cố định." }
                RowLayout { Layout.fillWidth: true
                    SelectBox { id: question; objectName: "classroomQuestionPicker"; model: classroom.state.questions || []; textRole: "vi"; Layout.fillWidth: true; Layout.minimumWidth: 0
                        onActivated: page.selectedQuestion = model[currentIndex].id
                        onModelChanged: Qt.callLater(function() { const found = (question.model || []).findIndex(function(q) { return q.id === page.selectedQuestion }); question.currentIndex = Math.max(0, found) })
                    }
                    SpinBox { id: duration; objectName: "classroomDuration"; from: 5; to: 3600; value: bridge.classroomSettings.duration; editable: true }
                    Label { text: "giây"; color: "#687b94" }
                    SelectBox { id: language; objectName: "classroomLanguage"; model: ["Việt–Anh", "Tiếng Việt", "English"]; currentIndex: ["both", "vi", "en"].indexOf(bridge.classroomSettings.language); Layout.preferredWidth: 122 }
                }
                Flow { Layout.fillWidth: true; spacing: 8
                    ActionButton { text: "Mở câu hỏi"; objectName: "openQuestionButton"; primary: true; enabled: page.active && !classroom.actionBusy && question.currentIndex >= 0 && question.currentIndex < (classroom.state.questions || []).length && page.round.status !== "open"; onClicked: classroom.openQuestion(question.model[question.currentIndex].id, duration.value, ["both","vi","en"][language.currentIndex], false) }
                    ActionButton { objectName: "classroomCloseQuestion"; text: "Đóng nhận trả lời"; enabled: page.active && !classroom.actionBusy && page.round.status === "open"; onClicked: classroom.action("close") }
                    ActionButton { objectName: "classroomReveal"; text: "Hiện đáp án"; enabled: page.active && !classroom.actionBusy && page.round.status === "closed"; onClicked: classroom.action("reveal") }
                    ActionButton { objectName: "classroomRecheck"; text: "Hỏi lại câu này"; enabled: page.active && !classroom.actionBusy && !!page.round.id && page.round.status !== "open"; onClicked: classroom.openQuestion(page.round.question_id, duration.value, ["both","vi","en"][language.currentIndex], true) }
                }
                Copy { text: !page.round.id ? "Chọn câu và bấm Mở câu hỏi. Học sinh trả lời trên điện thoại." : page.round.status === "open" ? "Đang nhận trả lời · học sinh được đổi lựa chọn trước khi đóng câu." : page.round.status === "closed" ? "Đã đóng · bấm Hiện đáp án khi sẵn sàng giải thích." : "Đã công bố đáp án · mở câu tiếp theo hoặc hỏi lại." }
                Title { text: page.round.vi || ""; font.pixelSize: 20 }
                Copy { text: page.round.en || ""; font.pixelSize: 15 }
                Copy { objectName: "classroomResponseCount"; visible: !!page.round.id; text: (page.round.answered || 0) + " / " + (page.round.eligible || 0) + " đã trả lời"; color: "#0869f9" }
                Repeater { model: page.round.options || []
                    RowLayout { required property var modelData; Layout.fillWidth: true; spacing: 12
                        Copy { text: modelData.id + " · " + modelData.vi; Layout.preferredWidth: 2 }
                        ProgressBar { Layout.fillWidth: true; Layout.preferredWidth: 1; value: ((page.round.counts || {})[modelData.id] || 0) / Math.max(1, page.round.answered || 0) }
                        Label { text: ((page.round.counts || {})[modelData.id] || 0) + " chọn"; color: "#687b94" }
                    }
                }
                Flow { Layout.fillWidth: true; spacing: 8
                    ActionButton { objectName: "classroomEnd"; text: "Kết thúc và lưu kết quả"; enabled: page.active && !classroom.actionBusy; onClicked: endDialog.open() }
                    ActionButton { objectName: "classroomDisconnect"; text: page.active ? "Tạm đóng máy chủ" : "Đóng lớp"; enabled: !classroom.actionBusy; onClicked: classroom.disconnect() }
                    ActionButton { text: "Xem kết quả"; onClicked: page.requestReports() }
                }
                Copy { text: "Tạm đóng máy chủ giữ lại tiết để mở tiếp trong Kết quả lớp học. Kết thúc tiết sẽ khóa việc nhận trả lời." }
            }
        }
        Copy { text: "Không vào được lớp? Kiểm tra cùng mạng, cho BiliClass qua Windows Firewall và tắt cô lập thiết bị trên Wi-Fi. Lớp học không tự vượt qua cấu hình mạng của trường." }
    }
    Dialog { id: endDialog; objectName: "classroomEndDialog"; anchors.centerIn: parent; modal: true; title: "Kết thúc tiết và lưu kết quả?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: classroom.action("end") }
}
