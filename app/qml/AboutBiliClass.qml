import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: card
    objectName: "aboutBiliClassCard"
    required property var bridge
    property real viewportHeight: 0
    readonly property color ink: "#112650"
    readonly property color muted: "#4a6284"
    readonly property bool compact: width < 900
    readonly property real brandScale: Math.max(0.4, Math.min(1.1, information.width / 460))
    readonly property bool artworkReady: artwork.status === Image.Ready
    implicitHeight: Math.max(information.implicitHeight + 72,
                             Math.min(width * 941 / 1672, viewportHeight > 0 ? viewportHeight : Infinity))

    // The illustration has its own light palette, including in dark mode.
    // Crop only the outer waves on wide windows; preserve both mascots when
    // the information needs a taller canvas on narrow windows.
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
        fillMode: card.width / card.height > 1672 / 941 ? Image.PreserveAspectCrop : Image.PreserveAspectFit
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
        y: 32
        height: Math.max(0, card.height - 72)
        spacing: card.compact ? 14 : 18

        Item {
            id: brandHeader
            Layout.fillWidth: true
            implicitHeight: brand.height + 12 + description.height
            Row {
                id: brand
                objectName: "aboutBiliClassBrand"
                x: (parent.width - width) / 2
                spacing: Math.round(22 * card.brandScale)
                Image {
                    id: logo
                    objectName: "aboutBiliClassLogo"
                    source: "../assets/brand/biliclass.svg"
                    sourceSize.width: 224; sourceSize.height: 224
                    width: Math.round(148 * card.brandScale)
                    height: width
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    Accessible.name: "Logo BiliClass"
                }
                Column {
                    objectName: "aboutBiliClassBrandText"
                    width: Math.min(Math.max(brandName.implicitWidth, tagline.implicitWidth, subtitle.implicitWidth),
                                    Math.max(0, information.width - logo.width - brand.spacing))
                    spacing: Math.round(10 * card.brandScale)
                    Label {
                        id: brandName
                        width: parent.width
                        text: "Bili<span style='color:#ff7d2b'>Class</span>"
                        textFormat: Text.RichText
                        color: card.ink
                        font.pixelSize: Math.round(54 * card.brandScale)
                        font.bold: true
                    }
                    Label {
                        id: tagline
                        width: parent.width
                        text: "CHUYỂN NGỮ THÔNG MINH\nNÂNG TẦM BÀI GIẢNG"
                        color: card.muted
                        font.pixelSize: Math.max(9, Math.round(13 * card.brandScale))
                        font.letterSpacing: 0.4
                        wrapMode: Text.WordWrap
                    }
                    Label {
                        id: subtitle
                        width: parent.width
                        text: card.bridge.appSubtitle
                        color: card.muted
                        font.pixelSize: Math.max(12, Math.round(18 * card.brandScale))
                        wrapMode: Text.WordWrap
                    }
                }
            }
            Caption {
                id: description
                objectName: "aboutBiliClassDescription"
                // Keep the two-line introduction directly under the centered brand.
                width: Math.max(information.width, Math.min(390, card.width * 0.47))
                x: (parent.width - width) / 2
                y: brand.height + 12
                text: "Chuyển đổi bài giảng song ngữ, hỗ trợ trình chiếu\nvới giọng đọc, mascot trợ giảng và thư viện lưu trữ ngay trên máy."
                font.pixelSize: 12
                fontSizeMode: Text.HorizontalFit
                minimumPixelSize: 8
                wrapMode: Text.NoWrap
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
        Item { Layout.fillHeight: true; Layout.minimumHeight: 0 }
        ColumnLayout {
            objectName: "aboutBiliClassCopyrightBlock"
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
            Caption { objectName: "aboutBiliClassRights"; text: "All rights reserved."; font.pixelSize: 11; Layout.topMargin: 4 }
        }
    }
}
