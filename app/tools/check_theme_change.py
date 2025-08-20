#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qfluentwidgets import setTheme, Theme, qconfig
from PyQt5.QtCore import QThread, pyqtSignal
import darkdetect
import sys

class SystemThemeListener(QThread):
    systemThemeChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._isSupported = False
    
    def run(self):
        # 运行时检测监听能力
        try:
            # 测试性调用检测实际支持情况
            darkdetect.listener(lambda _: None)
            self._isSupported = True
        except NotImplementedError:
            return

        darkdetect.listener(self._onThemeChanged)

    def _onThemeChanged(self, theme: str):
        theme = Theme.DARK if theme.lower() == "dark" else Theme.LIGHT
        if qconfig.themeMode.value != Theme.AUTO or theme == qconfig.theme:
            return
        qconfig.theme = Theme.AUTO
        qconfig._cfg.themeChanged.emit(Theme.AUTO)
        self.systemThemeChanged.emit()


def checkThemeChange(self):
    def handle_theme_change():
        setTheme(Theme.AUTO, lazy=True)

    self.themeListener = SystemThemeListener(self)
    
    if self.themeListener.isRunning():
        self.themeListener.systemThemeChanged.connect(handle_theme_change)
    else:
        self.themeListener = None
    
    return self.themeListener