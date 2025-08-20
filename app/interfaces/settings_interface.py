#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""设置界面模块"""

from contextlib import redirect_stdout

with redirect_stdout(None):
    from qfluentwidgets import (
        ScrollArea, VBoxLayout,
        SettingCardGroup, SwitchSettingCard, ComboBoxSettingCard,
        PushSettingCard, StrongBodyLabel, FluentIcon as FLF,
        OptionsConfigItem, OptionsValidator
    )
    from PyQt5.QtWidgets import QWidget, QVBoxLayout
    from PyQt5.QtCore import Qt

from ..common.style_sheet import StyleSheet


class SettingsInterface(ScrollArea):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("settingsInterface")
        
        # 创建滚动内容
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 初始化界面
        self._initWidget()
        self._initLayout()
        self._initSettingGroups()
        
        # 应用样式
        StyleSheet.SETTINGS_INTERFACE.apply(self)
    
    def _initWidget(self):
        """初始化组件"""
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    
    def _initLayout(self):
        """初始化布局"""
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
    
    def _initSettingGroups(self):
        """初始化设置组"""
        # 应用设置组
        self._createAppSettingsGroup()
        
        # 主题设置组
        self._createThemeSettingsGroup()
        
        # 自动化设置组
        self._createAutomationSettingsGroup()
        
        # 关于设置组
        self._createAboutSettingsGroup()
    
    def _createAppSettingsGroup(self):
        """创建应用设置组"""
        self.appGroup = SettingCardGroup("应用设置", self.scrollWidget)
        
        # 开机自启动
        self.autoStartCard = SwitchSettingCard(
            FLF.POWER_BUTTON,
            "开机自启动",
            "开机时自动启动应用程序",
            parent=self.appGroup
        )
        
        # 最小化到托盘
        self.minimizeToTrayCard = SwitchSettingCard(
            FLF.MINIMIZE,
            "最小化到托盘",
            "关闭窗口时最小化到系统托盘",
            parent=self.appGroup
        )
        
        self.appGroup.addSettingCard(self.autoStartCard)
        self.appGroup.addSettingCard(self.minimizeToTrayCard)
        self.vBoxLayout.addWidget(self.appGroup)
    
    def _createThemeSettingsGroup(self):
        """创建主题设置组"""
        self.themeGroup = SettingCardGroup("主题设置", self.scrollWidget)
        
        # 简化版主题设置 - 使用 PushSettingCard 暂时替代
        self.themeCard = PushSettingCard(
            "选择主题",
            FLF.BRUSH,
            "应用主题",
            "选择应用程序的主题风格：跟随系统、浅色模式、深色模式",
            parent=self.themeGroup
        )
        
        # 主题色设置
        self.themeColorCard = PushSettingCard(
            "选择主题色",
            FLF.PALETTE,
            "主题色",
            "选择应用程序的主题颜色：默认蓝、紫色、绿色、橙色、红色",
            parent=self.themeGroup
        )
        
        # 连接信号
        self.themeCard.clicked.connect(self._onThemeClicked)
        self.themeColorCard.clicked.connect(self._onThemeColorClicked)
        
        self.themeGroup.addSettingCard(self.themeCard)
        self.themeGroup.addSettingCard(self.themeColorCard)
        self.vBoxLayout.addWidget(self.themeGroup)
    
    def _createAutomationSettingsGroup(self):
        """创建自动化设置组"""
        self.automationGroup = SettingCardGroup("自动化设置", self.scrollWidget)
        
        # 启用自动化
        self.enableAutomationCard = SwitchSettingCard(
            FLF.PLAY,
            "启用自动化",
            "启用自动化任务执行",
            parent=self.automationGroup
        )
        
        # 任务间隔 - 简化版
        self.taskIntervalCard = PushSettingCard(
            "设置间隔",
            FLF.CALENDAR,
            "任务执行间隔",
            "设置自动化任务的执行间隔：1分钟、5分钟、10分钟、30分钟、1小时",
            parent=self.automationGroup
        )
        
        # 连接信号
        self.taskIntervalCard.clicked.connect(self._onTaskIntervalClicked)
        
        self.automationGroup.addSettingCard(self.enableAutomationCard)
        self.automationGroup.addSettingCard(self.taskIntervalCard)
        self.vBoxLayout.addWidget(self.automationGroup)
    
    def _createAboutSettingsGroup(self):
        """创建关于设置组"""
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        
        # 检查更新
        self.checkUpdateCard = PushSettingCard(
            "检查更新",
            FLF.UPDATE,
            "检查更新",
            "检查应用程序是否有新版本",
            parent=self.aboutGroup
        )
        
        # 重置设置
        self.resetSettingsCard = PushSettingCard(
            "重置设置",
            FLF.DELETE,
            "重置所有设置",
            "将所有设置恢复为默认值",
            parent=self.aboutGroup
        )
        
        # 连接信号
        self.checkUpdateCard.clicked.connect(self._onCheckUpdateClicked)
        self.resetSettingsCard.clicked.connect(self._onResetSettingsClicked)
        
        self.aboutGroup.addSettingCard(self.checkUpdateCard)
        self.aboutGroup.addSettingCard(self.resetSettingsCard)
        self.vBoxLayout.addWidget(self.aboutGroup)
    
    def _onThemeClicked(self):
        """主题设置按钮点击事件"""
        print("打开主题选择")
    
    def _onThemeColorClicked(self):
        """主题色设置按钮点击事件"""
        print("打开主题色选择")
    
    def _onTaskIntervalClicked(self):
        """任务间隔设置按钮点击事件"""
        print("打开任务间隔设置")
    
    def _onCheckUpdateClicked(self):
        """检查更新按钮点击事件"""
        print("检查更新")
    
    def _onResetSettingsClicked(self):
        """重置设置按钮点击事件"""
        print("重置设置")