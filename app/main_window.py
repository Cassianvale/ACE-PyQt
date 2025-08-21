#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qfluentwidgets import (
    NavigationItemPosition, MSFluentWindow, FluentIcon as FIF, SplashScreen,
    NavigationBarPushButton, toggleTheme, setThemeColor
)
from PyQt5.QtCore import Qt, QSize, QEventLoop, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from .interfaces import HomeInterface, HelpInterface, SettingsInterface, ChangelogInterface
from .tools.check_theme_change import checkThemeChange
from module.config import cfg
from .tools import setup_logger

setup_logger(
    log_dir=cfg.log_dir,
    log_retention_days=cfg.log_retention_days,
    log_rotation=cfg.log_rotation,
    debug_mode=cfg.debug_mode,
)


class MainWindow(MSFluentWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initWindow()
        self.initInterface()
        self.initNavigation()

    def initWindow(self):

        self.setMicaEffectEnabled(False)
        setThemeColor('#f18cb9', lazy=True)

        # 从配置文件应用主题，而不是硬编码
        from module.theme.theme_manager import ThemeManager
        ThemeManager.apply_theme_from_config()

        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        self.setWindowTitle("ACE-PyQt")
        self.setWindowIcon(QIcon("./assets/logo/March7th.ico"))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
    
        self.show()
        
        QApplication.processEvents()

    def initInterface(self):
        self.homeInterface = HomeInterface(self)
        self.helpInterface = HelpInterface(self)
        
        self.settingsInterface = SettingsInterface(self)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface,FIF.HOME,self.tr("主页"))
        self.addSubInterface(self.helpInterface,FIF.BOOK_SHELF,self.tr("帮助"))

        self.addSubInterface(self.settingsInterface,FIF.SETTING,self.tr("设置"),position=NavigationItemPosition.BOTTOM)
        
        
        self.stackedWidget.setCurrentWidget(self.homeInterface)
        
        self.splashScreen.finish()

        self.themeListener = checkThemeChange(self)
        
        
    def closeEvent(self, e):
        if self.themeListener and self.themeListener.isRunning():
            self.themeListener.terminate()
            self.themeListener.deleteLater()
        super().closeEvent(e)
