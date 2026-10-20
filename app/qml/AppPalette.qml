import QtQuick

Palette {
    window: AppTheme.canvas
    windowText: AppTheme.ink
    base: AppTheme.field
    alternateBase: AppTheme.raised
    text: AppTheme.ink
    button: AppTheme.surface
    buttonText: AppTheme.ink
    highlight: AppTheme.accent
    highlightedText: AppTheme.accentText
    placeholderText: AppTheme.muted
    toolTipBase: AppTheme.surface
    toolTipText: AppTheme.ink
    light: AppTheme.line
    midlight: AppTheme.raised
    mid: AppTheme.line
    dark: AppTheme.disabled
    shadow: AppTheme.canvas
    link: AppTheme.blue
    linkVisited: AppTheme.blue
    disabled {
        text: AppTheme.disabled
        windowText: AppTheme.disabled
        buttonText: AppTheme.disabled
        button: AppTheme.disabledSurface
        highlight: AppTheme.line
    }
}
