import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Item {
    id: page
    required property var appBridge
    readonly property var word: appBridge.wordDocuments
    readonly property var documentState: word.state
    property string shownIdentity: ""
    readonly property bool available: !appBridge.busy && !appBridge.narrationBusy
    readonly property bool compact: height < 700
    signal showPowerPoint()
    signal showLibrary()
    property var modeCodes: ["below", "columns", "keywords", "english"]
    property var colorCodes: ["1667B1", "666666", "000000"]
    property var densityCodes: ["few", "normal", "deep"]
    readonly property bool highlightSelection: selectionMethod.currentIndex === 1
    onVisibleChanged: if (!visible && highlightPopup) highlightPopup.close()
    onWidthChanged: if (highlightPopup) highlightPopup.close()
    onHeightChanged: if (highlightPopup) highlightPopup.close()
    function offerHighlightedText() {
        if (!page.visible || !page.available || !page.highlightSelection || !page.documentState.id || !continuousText.selectedText.trim()) return
        highlightPopup.documentIdentity = page.documentState.id
        highlightPopup.rangeStart = continuousText.selectionStart
        highlightPopup.rangeEnd = continuousText.selectionEnd
        highlightPopup.excerpt = continuousText.selectedText
        const caret = continuousText.cursorRectangle
        const point = continuousText.mapToItem(page, caret.x, caret.y)
        highlightPopup.x = Math.max(12, Math.min(point.x + 8, page.width - highlightPopup.width - 12))
        const below = point.y + caret.height + 8
        highlightPopup.y = Math.max(12, Math.min(below + highlightPopup.height <= page.height - 12 ? below : point.y - highlightPopup.height - 8, page.height - highlightPopup.height - 12))
        highlightPopup.open()
    }
    function openDocument(url) {
        word.openConfiguredFile(url, {options: draftOptions(), subject: subject.currentText, grade: grade.text})
    }
    function showDocument() {
        const flick = wordScroll.contentItem
        flick.cancelFlick()
        flick.contentY = Math.max(0, Math.min(documentPanels.y - 12, flick.contentHeight - flick.height))
    }
    readonly property bool configurationMatches: modeCodes[mode.currentIndex] === (page.documentState.options.mode || "below")
        && colorCodes[englishColor.currentIndex] === (page.documentState.options.color || "1667B1")
        && italic.checked === (page.documentState.options.italic === undefined ? true : page.documentState.options.italic)
        && densityCodes[density.currentIndex] === (page.documentState.options.density || "normal")
        && subject.currentText === (page.documentState.subject || "Toán") && grade.text === (page.documentState.grade || "11")
    function draftOptions() { return {mode: modeCodes[mode.currentIndex], color: colorCodes[englishColor.currentIndex], italic: italic.checked, density: densityCodes[density.currentIndex]} }
    function syncLoaded() {
        if (!page.documentState.id || shownIdentity === page.documentState.id) return
        highlightPopup.close()
        shownIdentity = page.documentState.id
        mode.currentIndex = Math.max(0, modeCodes.indexOf(page.documentState.options.mode || "below"))
        englishColor.currentIndex = Math.max(0, colorCodes.indexOf(page.documentState.options.color || "1667B1"))
        density.currentIndex = Math.max(0, densityCodes.indexOf(page.documentState.options.density || "normal"))
        italic.checked = page.documentState.options.italic === undefined ? true : page.documentState.options.italic
        subject.currentIndex = Math.max(0, appBridge.conversionSubjects.indexOf(page.documentState.subject || "Toán"))
        grade.text = page.documentState.grade || "11"
    }
    Connections { target: page.word; function onChanged() { if (!page.available) highlightPopup.close(); page.syncLoaded() }
        function onConfigurationRestored() { page.shownIdentity = ""; page.syncLoaded() }
    }
    FileDialog { id: choose; objectName: "wordFileDialog"; title: "Chọn bài giảng Word"; nameFilters: ["Bài giảng Word (*.docx)"]; onAccepted: page.openDocument(selectedFile.toString()) }
    Pane {
        id: highlightPopup; objectName: "wordHighlightPopup"; z: 100; visible: false
        property string documentIdentity: ""
        property int rangeStart: 0
        property int rangeEnd: 0
        property string excerpt: ""
        width: Math.min(340, page.width - 24); padding: 10
        function open() { visible = true }
        function close() { if (visible) { visible = false; continuousText.deselect() } }
        Accessible.name: "Xác nhận vùng văn bản cần dịch"
        background: Rectangle { color: AppTheme.surface; radius: 10; border.color: AppTheme.blue }
        contentItem: ColumnLayout { spacing: 8
            Label { text: highlightPopup.excerpt.slice(0, 180); textFormat: Text.PlainText; color: AppTheme.muted; font.pixelSize: 11; wrapMode: Text.WordWrap; maximumLineCount: 3; elide: Text.ElideRight; Layout.fillWidth: true }
            RowLayout { Layout.fillWidth: true; spacing: 8
                WordAction { objectName: "wordAcceptHighlight"; text: "Chọn đoạn này để dịch"; primary: true; Layout.fillWidth: true; enabled: page.available
                    onClicked: { page.word.addTextSelection(highlightPopup.documentIdentity, highlightPopup.rangeStart, highlightPopup.rangeEnd); highlightPopup.close() }
                }
                WordAction { objectName: "wordDismissHighlight"; text: "Hủy"; onClicked: highlightPopup.close() }
            }
        }
    }
    Dialog {
        id: keywordDialog; property string regionIdentity: ""; title: "Thêm từ khóa vào vùng chọn"; modal: true
        anchors.centerIn: parent; width: Math.min(440, page.width - 30); standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: page.word.addKeyword(regionIdentity, keywordVi.text, keywordEn.text)
        contentItem: ColumnLayout { spacing: 10
            Label { text: "Từ tiếng Việt có trong vùng đã chọn"; color: AppTheme.ink; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField { id: keywordVi; objectName: "wordAddKeywordVi"; Layout.fillWidth: true; maximumLength: 160 }
            Label { text: "Thuật ngữ tiếng Anh"; color: AppTheme.ink }
            TextField { id: keywordEn; objectName: "wordAddKeywordEn"; Layout.fillWidth: true; maximumLength: 160 }
        }
    }
    component Hint: Label { color: AppTheme.muted; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Choice: ComboBox {
        implicitHeight: 38; font.pixelSize: 12; leftPadding: 0; rightPadding: 0
        contentItem: Label { text: parent.displayText; color: AppTheme.ink; font: parent.font; verticalAlignment: Text.AlignVCenter; leftPadding: 10; rightPadding: 28; elide: Text.ElideRight }
        background: Rectangle { color: AppTheme.field; radius: 8; border.color: parent.activeFocus ? AppTheme.blue : AppTheme.line }
    }
    ColumnLayout {
        anchors.fill: parent; spacing: page.compact ? 8 : 12
        ContentScrollView {
        id: wordScroll; objectName: "wordWorkflowScroll"; Layout.fillWidth: true; Layout.fillHeight: true
        outerGutter: true; contentWidth: availableWidth
        ColumnLayout {
        width: wordScroll.availableWidth; spacing: page.compact ? 8 : 12
        RowLayout { Layout.fillWidth: true
            Label { objectName: "wordPageHeading"; text: "Chuyển đổi bài giảng song ngữ"; color: AppTheme.ink; font.pixelSize: page.compact ? 24 : 27; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        RowLayout { Layout.fillWidth: true
            ConversionDocumentTab { objectName: "wordTabPowerPoint"; onClicked: page.showPowerPoint() }
            ConversionDocumentTab { objectName: "wordTabWord"; word: true; selected: true }
            Item { Layout.fillWidth: true }
        }
        Hint { objectName: "wordWorkflowGuide"; text: "Chọn Word → Chọn cấu hình song ngữ → Chọn vùng cần dịch → Xem và lưu Word."; font.pixelSize: 13; Layout.fillWidth: true }
        WordUpload {
            objectName: "wordSourceArea"; Layout.fillWidth: true; busy: !page.available; reading: !!page.documentState.working
            fileName: page.documentState.id ? page.documentState.title + ".docx" : ""
            paragraphCount: (page.documentState.paragraphs || []).length
            onChooseFile: choose.open()
            onFileDropped: function(url) { page.openDocument(url) }
            onShowDocument: page.showDocument()
        }
        Rectangle {
            objectName: "wordConfiguration"; Layout.fillWidth: true
            implicitHeight: configuration.implicitHeight + (page.compact ? 18 : 26)
            color: AppTheme.surface; radius: 14; border.color: AppTheme.line
            ColumnLayout {
            id: configuration; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: page.compact ? 9 : 13; spacing: page.compact ? 6 : 10
            Label { text: "Cấu hình bài giảng"; color: AppTheme.ink; font.pixelSize: 15; font.weight: Font.DemiBold }
            GridLayout {
            Layout.fillWidth: true; columns: page.width >= 760 ? 4 : 2; columnSpacing: 12; rowSpacing: 8
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 2; spacing: 4
                Hint { text: "Môn học" }
                Choice { id: subject; objectName: "wordSubject"; model: page.appBridge.conversionSubjects; currentIndex: Math.max(0, page.appBridge.conversionSubjects.indexOf("Toán")); Layout.fillWidth: true; enabled: page.available }
            }
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1; spacing: 4
                Hint { text: "Khối lớp" }
                TextField { id: grade; objectName: "wordGrade"; text: "11"; maximumLength: 20; color: AppTheme.ink; implicitHeight: 38; Layout.fillWidth: true; enabled: page.available
                    background: Rectangle { color: AppTheme.field; radius: 8; border.color: AppTheme.line } }
            }
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 3; spacing: 4
                Hint { text: "Kiểu chuyển đổi" }
                Choice { id: mode; objectName: "wordMode"; model: ["Anh ngay dưới Việt", "Việt–Anh hai cột", "Từ khóa tiếng Anh", "Tiếng Anh 100% ở vùng chọn"]; Layout.fillWidth: true; enabled: page.available }
            }
            RowLayout { Layout.fillWidth: true; Layout.preferredWidth: 2; spacing: 8
                ColumnLayout { Layout.fillWidth: true; spacing: 4
                    Hint { text: mode.currentIndex === 2 ? "Mức từ khóa" : "Màu tiếng Anh" }
                    Choice { id: englishColor; objectName: "wordEnglishColor"; visible: mode.currentIndex !== 2; model: ["Xanh", "Xám", "Đen"]; Layout.fillWidth: true; enabled: page.available }
                    Choice { id: density; objectName: "wordKeywordDensity"; visible: mode.currentIndex === 2; model: ["Ít", "Vừa phải", "Chuyên sâu"]; currentIndex: 1; Layout.fillWidth: true; enabled: page.available }
                }
                CheckBox { id: italic; objectName: "wordItalic"; text: "In nghiêng"; checked: true; enabled: page.available; palette.windowText: AppTheme.ink }
            }
            }
            }
        }
        Rectangle {
            visible: !!page.documentState.message; Layout.fillWidth: true
            implicitHeight: message.implicitHeight + 20; radius: 9
            color: page.documentState.phase === "paused" ? AppTheme.warningSurface : AppTheme.selected
            border.color: page.documentState.phase === "paused" ? AppTheme.warningLine : AppTheme.line
            Hint { id: message; anchors.fill: parent; anchors.margins: 10; text: page.documentState.message || ""; color: page.documentState.phase === "paused" ? AppTheme.warningInk : AppTheme.ink }
        }
        Hint { visible: (page.documentState.notices || []).length > 0; text: (page.documentState.notices || []).slice(-1).join(""); color: AppTheme.warning; font.pixelSize: 11; Layout.fillWidth: true }
        Hint { visible: !!page.documentState.id; text: "Nội dung để chọn vùng; công thức và hình được giữ trong tệp Word. Thêm bản dịch có thể làm tăng số trang."; Layout.fillWidth: true; font.pixelSize: 11 }
        RowLayout {
            id: documentPanels; objectName: "wordDocumentPanels"; Layout.fillWidth: true; spacing: 12
            Layout.preferredHeight: page.documentState.id ? Math.max(320, Math.min(560, page.height * .58)) : 210
            Layout.minimumHeight: Layout.preferredHeight; Layout.maximumHeight: Layout.preferredHeight
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; color: AppTheme.surface; radius: 11; border.color: AppTheme.line
                ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                    RowLayout { Layout.fillWidth: true
                        Label { text: "Nội dung gốc"; font.bold: true; color: AppTheme.ink }
                        Choice {
                            id: selectionMethod; objectName: "wordSelectionMethod"; model: ["Tích đoạn / câu", "Bôi đen văn bản"]
                            enabled: page.available; Layout.fillWidth: true; Layout.preferredWidth: 155; Layout.minimumWidth: 110
                            Accessible.name: "Cách chọn văn bản"
                            ToolTip.visible: hovered; ToolTip.text: currentIndex === 0 ? "Tích chọn từng đoạn hoặc câu cần dịch" : "Bôi đen, nhả chuột rồi xác nhận vùng cần dịch"
                            onCurrentIndexChanged: { if (highlightPopup) highlightPopup.close(); if (continuousText) continuousText.deselect() }
                        }
                        Choice { id: scope; objectName: "wordSelectionScope"; visible: !page.highlightSelection; model: ["Theo đoạn", "Theo câu"]; enabled: page.available && !!page.documentState.id; Layout.preferredWidth: 110 }
                    }
                    RowLayout { Layout.fillWidth: true
                        WordAction { objectName: "wordSelectAll"; text: page.highlightSelection ? "Bôi đen tất cả" : "Chọn tất cả"; enabled: page.available && !!page.documentState.id
                            onClicked: {
                                if (page.highlightSelection) { continuousText.forceActiveFocus(); continuousText.selectAll(); Qt.callLater(page.offerHighlightedText) }
                                else page.word.selectAll(scope.currentIndex === 1 ? "sentences" : "paragraphs")
                            }
                        }
                        WordAction { objectName: "wordClearSelection"; text: "Bỏ chọn"; enabled: page.available && page.documentState.selected_count > 0; onClicked: page.word.clearSelection() }
                        WordAction { objectName: "wordConfirmHighlight"; visible: page.highlightSelection && continuousText.selectedText.length > 0; text: "Thêm vùng"; enabled: page.available; onClicked: page.offerHighlightedText() }
                    }
                    Hint { visible: page.highlightSelection; text: "Bôi đen rồi nhả chuột để chọn vùng dịch. Các vùng đã xác nhận được giữ ở bên phải."; font.pixelSize: 11; Layout.fillWidth: true }
                    ListView {
                        id: sources; objectName: "wordSourceList"; visible: !page.highlightSelection; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 9
                        model: { const revision = page.documentState; return page.word.items(scope.currentIndex === 1 ? "sentences" : "paragraphs") }
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        Hint { visible: !page.documentState.id; anchors.centerIn: parent; width: parent.width - 24; horizontalAlignment: Text.AlignHCenter; text: "Tải file Word ở trên để xem nội dung và chọn phần cần dịch." }
                        delegate: Rectangle {
                            id: sourceRow; required property var modelData; required property int index
                            width: ListView.view.width - 12; height: sourceContents.implicitHeight + 16; radius: 8
                            color: modelData.selected ? AppTheme.selected : AppTheme.surface; border.color: AppTheme.line
                            ColumnLayout { id: sourceContents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 8; spacing: 3
                                RowLayout { Layout.fillWidth: true
                                    CheckBox { objectName: "wordSelect_" + sourceRow.index; checked: sourceRow.modelData.selected; enabled: page.available && sourceRow.modelData.editable
                                        onClicked: page.word.toggle(sourceRow.modelData.paragraph, sourceRow.modelData.start, sourceRow.modelData.end, checked) }
                                    Hint { text: sourceRow.modelData.location; font.pixelSize: 10; Layout.fillWidth: true }
                                }
                                TextArea {
                                    id: sourceText; objectName: "wordSourceText_" + sourceRow.index; Layout.fillWidth: true; implicitHeight: contentHeight + 12
                                    text: sourceRow.modelData.text; textFormat: TextEdit.PlainText; readOnly: true; selectByMouse: true; persistentSelection: true; wrapMode: TextEdit.Wrap
                                    color: AppTheme.ink; selectedTextColor: AppTheme.accentText; selectionColor: AppTheme.accent; font.pixelSize: 13
                                    background: Rectangle { color: "transparent" }
                                }
                                WordAction { objectName: "wordAddRange_" + sourceRow.index; text: "Thêm vùng bôi đen"; visible: sourceText.selectedText.length > 0; enabled: page.available && sourceRow.modelData.editable
                                    onClicked: page.word.addRange(sourceRow.modelData.paragraph, sourceRow.modelData.start, sourceText.selectionStart, sourceText.selectionEnd) }
                                Hint { visible: !sourceRow.modelData.editable; text: sourceRow.modelData.reason; font.pixelSize: 10; Layout.fillWidth: true }
                            }
                        }
                    }
                    ContentScrollView {
                        id: textScroll; objectName: "wordContinuousScroll"; visible: page.highlightSelection
                        Layout.fillWidth: true; Layout.fillHeight: true; contentWidth: availableWidth
                        TextArea {
                            id: continuousText; objectName: "wordContinuousText"; width: textScroll.availableWidth
                            text: page.highlightSelection ? page.word.selectionText : ""; textFormat: TextEdit.PlainText
                            placeholderText: "Tải file Word ở trên để bôi đen phần cần dịch."
                            readOnly: true; selectByMouse: true; persistentSelection: true; wrapMode: TextEdit.Wrap
                            Keys.onEscapePressed: function(event) { if (highlightPopup.visible) highlightPopup.close(); else event.accepted = false }
                            enabled: page.available && !!page.documentState.id; color: AppTheme.ink
                            selectedTextColor: AppTheme.accentText; selectionColor: AppTheme.accent; font.pixelSize: 13; padding: 9
                            background: Rectangle { color: AppTheme.field; radius: 7 }
                            PointHandler {
                                acceptedButtons: Qt.LeftButton
                                onActiveChanged: {
                                    if (active) {
                                        highlightPopup.close()
                                        continuousText.cursorPosition = continuousText.positionAt(point.position.x, point.position.y)
                                        continuousText.forceActiveFocus()
                                    }
                                    else Qt.callLater(page.offerHighlightedText)
                                }
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; color: AppTheme.surface; radius: 11; border.color: AppTheme.line
                ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                    Label { objectName: "wordSelectedCount"; text: page.documentState.id ? "Đã chọn " + (page.documentState.selected_count || 0) + " vùng" : "Bản dịch xem trước"; font.bold: true; color: AppTheme.ink }
                    Hint { text: !page.documentState.id ? "Bản dịch sẽ hiện tại đây sau khi chọn vùng và chuyển đổi." : page.documentState.can_export ? "Xem phần Việt và chỉnh bản Anh trước khi lưu." : page.documentState.selected_count ? "Tiếp tục chọn vùng hoặc bấm Chuyển đổi ở thanh dưới để xem bản Anh." : page.highlightSelection ? "Bôi đen bên trái, nhả chuột rồi bấm Chọn đoạn này để dịch." : "Tích chọn đoạn/câu hoặc thêm vùng bôi đen ở bên trái."; Layout.fillWidth: true }
                    ListView {
                        objectName: "wordReviewList"; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10; model: page.documentState.regions
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        delegate: Rectangle {
                            id: selectedRow; required property var modelData; required property int index
                            width: ListView.view.width - 12; height: selectedContents.implicitHeight + 20; radius: 8; color: AppTheme.field; border.color: AppTheme.line
                            ColumnLayout { id: selectedContents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 10; spacing: 5
                                RowLayout { Layout.fillWidth: true
                                    Hint { text: "Vùng " + (selectedRow.index + 1); font.pixelSize: 10; Layout.fillWidth: true }
                                    WordAction { objectName: "wordRemoveRange_" + selectedRow.index; text: "Bỏ vùng"; implicitHeight: 28; enabled: page.available; onClicked: page.word.removeRange(selectedRow.modelData.id) }
                                }
                                Label { text: selectedRow.modelData.vi; textFormat: Text.PlainText; color: AppTheme.ink; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                TextArea {
                                    objectName: "wordEnglishDraft_" + selectedRow.index; visible: !!selectedRow.modelData.en && page.documentState.options.mode !== "keywords"; Layout.fillWidth: true; implicitHeight: contentHeight + 16
                                    text: selectedRow.modelData.display_en || ""; textFormat: TextEdit.PlainText; wrapMode: TextEdit.Wrap; selectByMouse: true; color: AppTheme.blue; font.pixelSize: 13; font.italic: true; enabled: page.available
                                    onTextChanged: if (activeFocus) page.word.setDraft(selectedRow.modelData.id, text)
                                    background: Rectangle { color: AppTheme.surface; radius: 6; border.color: AppTheme.line }
                                }
                                Repeater { model: selectedRow.modelData.annotations || []
                                    RowLayout { id: keywordRow; required property var modelData; required property int index; Layout.fillWidth: true
                                        Hint { text: (modelData.vi || "Từ khóa") + " →"; Layout.preferredWidth: 110; font.pixelSize: 11 }
                                        TextField { objectName: "wordKeyword_" + selectedRow.index + "_" + keywordRow.index; text: keywordRow.modelData.en; color: AppTheme.blue; font.pixelSize: 12; Layout.fillWidth: true; enabled: page.available
                                            onTextEdited: page.word.setKeywordDraft(selectedRow.modelData.id, keywordRow.index, text)
                                            placeholderText: "Để trống để bỏ từ khóa"
                                            background: Rectangle { color: AppTheme.surface; radius: 6; border.color: AppTheme.line } }
                                    }
                                }
                                WordAction { visible: page.documentState.options.mode === "keywords" && !!selectedRow.modelData.en; text: "+ Thêm từ khóa"; enabled: page.available
                                    onClicked: { keywordDialog.regionIdentity = selectedRow.modelData.id; keywordVi.text = ""; keywordEn.text = ""; keywordDialog.open() } }
                            }
                        }
                    }
                }
            }
        }
        }
        }
        ProgressBar { objectName: "wordProgress"; visible: page.documentState.working; Layout.fillWidth: true; from: 0; to: 100; value: page.documentState.percent || 0; indeterminate: value <= 0 }
        Flow {
            Layout.fillWidth: true; spacing: 8
            WordAction { objectName: "wordPreview"; text: page.documentState.phase === "paused" ? "Tiếp tục chuyển đổi" : page.documentState.phase === "completed" ? "Chuyển đổi lại" : "Chuyển đổi · " + (page.documentState.selected_count || 0) + " vùng"; primary: page.documentState.phase !== "completed"
                enabled: page.available && page.documentState.selected_count > 0; onClicked: page.word.preview(page.draftOptions(), subject.currentText, grade.text) }
            WordAction { objectName: "wordSave"; visible: !!page.documentState.id && (page.documentState.phase !== "completed" || page.word.draftsPending); text: "Lưu Word song ngữ"; primary: page.documentState.phase === "review"; enabled: page.available && page.documentState.can_export && page.configurationMatches; onClicked: page.word.save() }
            WordAction { objectName: "wordStop"; visible: page.documentState.working; text: "■ Dừng"; danger: true; onClicked: page.word.stop() }
            WordAction { objectName: "wordOpenOutput"; visible: !!page.documentState.output_sha256; text: "Mở Word đã lưu"; primary: page.documentState.phase === "completed"; enabled: page.available; onClicked: page.word.openOutput(page.documentState.id) }
            WordAction { objectName: "wordOpenFolder"; visible: !!page.documentState.output_sha256; text: "Mở thư mục"; enabled: page.available; onClicked: page.word.openFolder(page.documentState.id) }
            WordAction { id: more; objectName: "wordMore"; visible: !!page.documentState.output_sha256; text: "⋮"; enabled: page.available; onClicked: moreMenu.popup()
                Menu { id: moreMenu; MenuItem { objectName: "wordUndo"; text: "Khôi phục bản xuất trước"; enabled: !!page.documentState.has_previous; onTriggered: page.word.restorePrevious() } }
            }
            WordAction { objectName: "wordGoLibrary"; text: "Về thư viện"; enabled: page.available; onClicked: page.showLibrary() }
        }
        Hint { visible: page.word.draftsPending; text: "Có chỉnh sửa bản dịch/từ khóa. Bấm Lưu Word song ngữ để áp dụng."; Layout.fillWidth: true }
        Hint { visible: !!page.documentState.id && !page.configurationMatches; text: "Cấu hình đã đổi. Bấm Chuyển đổi để cập nhật trước khi lưu."; Layout.fillWidth: true }
    }
}
