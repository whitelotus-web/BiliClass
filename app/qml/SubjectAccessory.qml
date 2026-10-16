import QtQuick

Canvas {
    id: prop
    required property var theme
    onThemeChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onVisibleChanged: if (visible) requestPaint()
    onPaint: {
        const c = getContext("2d")
        c.reset(); c.scale(width / 64, height / 64)
        c.lineCap = "round"; c.lineJoin = "round"; c.lineWidth = 2.8
        c.strokeStyle = theme.color; c.fillStyle = theme.paper
        function line(points, fill) {
            c.beginPath(); c.moveTo(points[0][0], points[0][1])
            for (let i = 1; i < points.length; i++) c.lineTo(points[i][0], points[i][1])
            if (fill) { c.closePath(); c.fill() }
            c.stroke()
        }
        function circle(x, y, r, fill) { c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); if (fill) c.fill(); c.stroke() }
        function word(value, x, y, size) { c.fillStyle = theme.color; c.font = "bold " + size + "px Arial"; c.textAlign = "center"; c.fillText(value, x, y) }
        // A small translucent enamel pin sits on the existing book/tablet.
        // No oversized white disk outside the accessory silhouette.
        c.fillStyle = theme.paper; c.strokeStyle = theme.color; c.lineWidth = 2.8
        switch (theme.id) {
        case "math":
            line([[12, 51], [12, 12], [52, 51]], true)
            line([[23, 43], [23, 32], [34, 43]], true)
            for (let i = 0; i < 4; i++) line([[13, 20+i*8], [18, 20+i*8]], false)
            break
        case "physics":
            c.fillStyle = theme.paper; circle(32, 32, 28, true)
            c.globalAlpha = .82
            for (let i = 0; i < 3; i++) {
                c.save(); c.translate(32, 32); c.rotate(i*Math.PI/3); c.scale(1, .42)
                circle(0, 0, 21, false); c.restore()
            }
            c.fillStyle = theme.color; circle(32, 32, 5, true); circle(52, 27, 3, true)
            break
        case "chemistry":
            line([[24, 10], [40, 10], [40, 15], [37, 15], [37, 29], [51, 49], [48, 55], [16, 55], [13, 49], [27, 29], [27, 15], [24, 15]], true)
            c.fillStyle = "#bd95e7"; line([[23, 39], [41, 39], [48, 51], [17, 51]], true)
            c.fillStyle = "white"; circle(29, 45, 2, true); circle(36, 36, 2, true)
            break
        case "biology":
            c.beginPath(); c.moveTo(13, 51); c.bezierCurveTo(9, 20, 36, 10, 53, 13); c.bezierCurveTo(51, 42, 36, 58, 13, 51); c.fill(); c.stroke()
            line([[13, 52], [43, 24]], false); line([[25, 40], [25, 29]], false); line([[32, 34], [43, 34]], false)
            break
        case "technology":
            line([[13, 15], [51, 15], [51, 44], [13, 44]], true)
            line([[13, 44], [7, 51], [57, 51], [51, 44]], true)
            word("</>", 32, 35, 19)
            break
        case "geography":
            circle(32, 29, 22, true); line([[32, 51], [32, 57]], false); line([[22, 57], [42, 57]], false)
            line([[11, 29], [53, 29]], false)
            c.save(); c.translate(32, 29); c.scale(.45, 1); circle(0, 0, 22, false); c.restore()
            break
        case "music":
            line([[27, 45], [27, 15], [49, 10], [49, 39]], false)
            line([[27, 23], [49, 18]], false); c.fillStyle = theme.color
            circle(19, 47, 8, true); circle(41, 41, 8, true)
            break
        case "art":
            c.beginPath(); c.moveTo(51, 36); c.bezierCurveTo(66, 12, 20, 0, 10, 26); c.bezierCurveTo(-2, 51, 35, 66, 39, 45); c.bezierCurveTo(41, 34, 43, 45, 51, 36); c.fill(); c.stroke()
            for (let dot of [[18,24,"#ef9c2f"],[30,15,"#ed6572"],[43,20,"#4e9dce"],[18,40,"#68a16b"]]) {
                c.fillStyle = dot[2]; c.strokeStyle = dot[2]; circle(dot[0], dot[1], 4, true)
            }
            break
        case "sport":
            circle(32, 32, 24, true); line([[10, 22], [54, 42]], false); line([[22, 10], [42, 54]], false)
            c.beginPath(); c.moveTo(10, 44); c.quadraticCurveTo(43, 45, 44, 10); c.stroke()
            break
        case "civics":
            line([[32, 11], [32, 54]], false); line([[20, 55], [44, 55]], false); line([[10, 23], [54, 23]], false)
            line([[17, 24], [9, 40], [25, 40]], true); line([[47, 24], [39, 40], [55, 40]], true)
            circle(32, 15, 4, true)
            break
        case "defence":
            line([[12, 15], [32, 8], [52, 15], [49, 40], [32, 56], [15, 40]], true)
            word("★", 32, 41, 29)
            break
        case "experience":
            circle(32, 32, 24, true); c.fillStyle = theme.color
            line([[23, 43], [31, 22], [42, 18], [34, 39]], true)
            break
        case "local":
            c.beginPath(); c.moveTo(32, 56); c.bezierCurveTo(1, 23, 15, 8, 32, 8); c.bezierCurveTo(49, 8, 63, 23, 32, 56); c.fill(); c.stroke()
            circle(32, 25, 7, true)
            break
        case "science":
            circle(27, 26, 18, true); line([[40, 40], [54, 54]], false)
            line([[18, 30], [27, 18], [35, 30]], false)
            break
        case "history":
            line([[17, 13], [46, 13], [46, 50], [20, 50]], true)
            circle(17, 16, 6, true); circle(46, 48, 6, true)
            line([[26, 24], [39, 24]], false); line([[26, 32], [39, 32]], false)
            break
        case "language":
            line([[9, 13], [55, 13], [55, 45], [29, 45], [17, 55], [19, 45], [9, 45]], true)
            word("Aa", 32, 36, 23)
            break
        default:
            line([[8, 14], [29, 18], [32, 23], [35, 18], [56, 14], [56, 49], [35, 53], [32, 57], [29, 53], [8, 49]], true)
            line([[32, 24], [32, 52]], false); line([[15, 27], [25, 29]], false); line([[39, 29], [49, 27]], false)
        }
    }
}
