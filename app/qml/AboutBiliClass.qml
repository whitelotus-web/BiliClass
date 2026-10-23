import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: card
    objectName: "aboutBiliClassCard"
    required property var bridge
    readonly property color ink: "#112650"
    readonly property color muted: "#4a6284"
    readonly property bool compact: width < 900
    readonly property bool narrow: width < 650
    readonly property bool footerBelow: information.width < 400
    readonly property bool artworkReady: artwork.status === Image.Ready
    implicitHeight: Math.max(width * 941 / 1672, information.implicitHeight + information.spacing + description.implicitHeight + 48)

    // The illustration has its own light palette, including in dark mode.
    // Fit the entire image so narrow windows never crop either mascot.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0; color: "#e4f2ff" }
            GradientStop { position: 0.5; color: "#f5faff" }
            GradientStop { position: 1; color: "#c9e5ff" }
        }
    }
    Image {
        id: artwork
        objectName: "aboutBiliClassArtwork"
        anchors.fill: parent
        source: "../assets/brand/about-mascots.png"
        fillMode: Image.PreserveAspectFit
        Accessible.ignored: true
    }

    component Caption: Label {
        color: card.muted
        font.pixelSize: 13
        wrapMode: Text.WordWrap
        textFormat: Text.PlainText
        horizontalAlignment: Text.AlignHCenter
        Layout.fillWidth: true
    }
    ColumnLayout {
        id: information
        objectName: "aboutBiliClassInfo"
        x: card.width * 0.025
        width: card.width * 0.42
        height: implicitHeight
        y: (card.height - height - spacing - description.height) / 2
        spacing: card.compact ? 14 : 18

        Row {
            id: brand
            objectName: "aboutBiliClassBrand"
            Layout.alignment: Qt.AlignHCenter
            spacing: card.narrow ? 10 : card.compact ? 14 : 18
            Image {
                id: logo
                objectName: "aboutBiliClassLogo"
                source: "../assets/brand/biliclass.svg"
                sourceSize.width: 224; sourceSize.height: 224
                width: card.narrow ? 54 : card.compact ? 74 : 92
                height: width
                anchors.verticalCenter: parent.verticalCenter
                fillMode: Image.PreserveAspectFit
                Accessible.name: "Logo BiliClass"
            }
            Column {
                objectName: "aboutBiliClassBrandText"
                width: Math.min(Math.max(brandName.implicitWidth, tagline.implicitWidth, subtitle.implicitWidth),
                                Math.max(0, information.width - logo.width - brand.spacing))
                spacing: 7
                Label {
                    id: brandName
                    width: parent.width
                    text: "Bili<span style='color:#ff7d2b'>Class</span>"
                    textFormat: Text.RichText
                    color: card.ink
                    font.pixelSize: card.narrow ? 26 : card.compact ? 33 : 38
                    font.bold: true
                }
                Label {
                    id: tagline
                    width: parent.width
                    text: "CHUYỂN NGỮ THÔNG MINH\nNÂNG TẦM BÀI GIẢNG"
                    color: card.muted
                    font.pixelSize: card.compact ? 10 : 11
                    font.letterSpacing: 0.4
                    wrapMode: Text.WordWrap
                }
                Label {
                    id: subtitle
                    width: parent.width
                    text: card.bridge.appSubtitle
                    color: card.muted
                    font.pixelSize: card.compact ? 14 : 15
                    wrapMode: Text.WordWrap
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: "#cadff2"
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            Caption { text: "PHIÊN BẢN"; font.pixelSize: 10; font.letterSpacing: 1 }
            Caption {
                objectName: "aboutBiliClassVersion"
                text: card.bridge.appVersion
                color: card.ink
                font.pixelSize: 20; font.bold: true
            }
            Caption { text: card.bridge.developmentMode ? "Đang chạy từ mã nguồn" : "Ứng dụng BiliClass cho Windows" }
            ActionButton {
                objectName: "aboutCheckUpdate"
                Layout.alignment: Qt.AlignHCenter
                text: card.bridge.updateState.checking ? "Đang kiểm tra…" : "Kiểm tra cập nhật"
                iconName: "refresh"
                iconSize: 16
                enabled: !card.bridge.updateState.checking && !card.bridge.updateState.downloading
                onClicked: card.bridge.checkForUpdates(false)
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            Caption { text: "BẢN QUYỀN"; font.pixelSize: 10; font.letterSpacing: 1 }
            Caption {
                objectName: "aboutBiliClassCopyright"
                text: "Copyright © 2026 Nguyễn Diệu Linh"
                color: card.ink
                font.pixelSize: 17; font.bold: true
            }
            Caption { text: "Giáo viên Tin học · Trường THPT Vân\u00a0Cốc" }
            Caption { objectName: "aboutBiliClassContact"; text: "Liên hệ tác giả: 0972.360.036" }
            Caption { text: "All rights reserved."; font.pixelSize: 11; Layout.topMargin: 4 }
        }
    }
    Caption {
        id: description
        objectName: "aboutBiliClassDescription"
        // On small windows, place both lines below the artwork rather than
        // shrinking this text or letting it wrap across the mascots.
        width: card.footerBelow ? card.width - 48 : information.width
        x: card.footerBelow ? 24 : information.x
        y: information.y + information.height + information.spacing
        text: "Chuyển đổi bài giảng song ngữ, hỗ trợ trình chiếu\nvới giọng đọc, mascot trợ giảng và thư viện lưu trữ ngay trên máy."
        font.pixelSize: 12
    }
}
