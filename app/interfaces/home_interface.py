#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""主页界面模块"""

from contextlib import redirect_stdout

with redirect_stdout(None):
    from qfluentwidgets import (
        ScrollArea, VBoxLayout,
        CardWidget, StrongBodyLabel, CaptionLabel,
        FluentIcon, IconWidget, PushButton
    )
    from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout
    from PyQt5.QtCore import Qt

from ..common.style_sheet import StyleSheet


class HomeInterface(ScrollArea):
    """主页界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("homeInterface")
        
        # 创建滚动内容
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 初始化界面
        self._initWidget()
        self._initLayout()
        
        # 应用样式
        StyleSheet.HOME_INTERFACE.apply(self)
    
    def _initWidget(self):
        """初始化组件"""
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建欢迎卡片
        self._createWelcomeCard()
        
        # 创建功能卡片
        self._createFeatureCards()
    
    def _initLayout(self):
        """初始化布局"""
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
    
    def _createWelcomeCard(self):
        """创建欢迎卡片"""
        self.welcomeCard = CardWidget()
        self.welcomeCard.setObjectName("cardFrame")
        
        layout = QVBoxLayout(self.welcomeCard)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        titleLabel = StrongBodyLabel("欢迎使用 ACE-PyQt")
        titleLabel.setObjectName("titleLabel")
        
        # 副标题
        subtitleLabel = CaptionLabel("基于 PyQt-Fluent-Widgets 的现代化桌面应用程序")
        subtitleLabel.setObjectName("subtitleLabel")
        
        layout.addWidget(titleLabel)
        layout.addWidget(subtitleLabel)
        
        self.vBoxLayout.addWidget(self.welcomeCard)
    
    def _createFeatureCards(self):
        """创建功能卡片"""
        features = [
            {
                "title": "自动化任务",
                "description": "配置和管理各种自动化任务",
                "icon": FluentIcon.PLAY,
                "action": self._onAutomationClicked
            },
            {
                "title": "设置配置",
                "description": "个性化设置和偏好配置",
                "icon": FluentIcon.SETTING,
                "action": self._onSettingsClicked
            },
            {
                "title": "日志查看",
                "description": "查看应用程序运行日志",
                "icon": FluentIcon.DOCUMENT,
                "action": self._onLogsClicked
            }
        ]
        
        for feature in features:
            card = self._createFeatureCard(
                feature["title"],
                feature["description"],
                feature["icon"],
                feature["action"]
            )
            self.vBoxLayout.addWidget(card)
    
    def _createFeatureCard(self, title, description, icon, action):
        """创建单个功能卡片"""
        card = CardWidget()
        card.setObjectName("cardFrame")
        card.setFixedHeight(80)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # 图标
        iconWidget = IconWidget(icon)
        iconWidget.setFixedSize(32, 32)
        
        # 文本容器
        textLayout = QVBoxLayout()
        titleLabel = StrongBodyLabel(title)
        descLabel = CaptionLabel(description)
        
        textLayout.addWidget(titleLabel)
        textLayout.addWidget(descLabel)
        textLayout.setContentsMargins(0, 0, 0, 0)
        textLayout.setSpacing(4)
        
        # 按钮
        button = PushButton("打开")
        button.setFixedSize(60, 32)
        button.clicked.connect(action)
        
        layout.addWidget(iconWidget)
        layout.addLayout(textLayout)
        layout.addStretch()
        layout.addWidget(button)
        
        return card
    
    def _onAutomationClicked(self):
        """自动化按钮点击事件"""
        print("打开自动化任务")
    
    def _onSettingsClicked(self):
        """设置按钮点击事件"""
        print("打开设置页面")
    
    def _onLogsClicked(self):
        """日志按钮点击事件"""
        print("打开日志页面")