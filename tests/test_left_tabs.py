#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试左侧选项卡功能的完整测试脚本"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
)
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styles import StyleApplier, StyleHelper, theme_manager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("左侧选项卡功能测试")
        self.setGeometry(100, 100, 900, 700)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 创建选项卡 - 使用自定义选项卡组件支持水平文本
        from ui.components.custom_tabbar import CustomTabWidget

        self.tabs = CustomTabWidget()
        # 使用新的辅助方法设置左侧位置
        StyleHelper.set_tab_position(self.tabs, "West")

        # 添加多个测试选项卡
        self.create_test_tabs()

        main_layout.addWidget(self.tabs)

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("选项卡位置控制")
        layout = QHBoxLayout(group)

        # 位置切换按钮
        positions = [("顶部", "North"), ("底部", "South"), ("左侧", "West"), ("右侧", "East")]
        for text, pos in positions:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, p=pos: self.change_tab_position(p))
            layout.addWidget(btn)

        # 主题切换按钮
        layout.addWidget(QLabel("|"))

        light_btn = QPushButton("☀️ 浅色主题")
        light_btn.clicked.connect(lambda: self.change_theme("light"))
        layout.addWidget(light_btn)

        dark_btn = QPushButton("🌙 深色主题")
        dark_btn.clicked.connect(lambda: self.change_theme("dark"))
        layout.addWidget(dark_btn)

        return group

    def create_test_tabs(self):
        """创建测试选项卡"""
        # 设置选项卡
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        # 添加一些设置组件
        group1 = QGroupBox("通知设置")
        group1_layout = QVBoxLayout(group1)
        group1_layout.addWidget(QCheckBox("启用通知"))
        group1_layout.addWidget(QCheckBox("声音提醒"))
        settings_layout.addWidget(group1)

        group2 = QGroupBox("显示设置")
        group2_layout = QVBoxLayout(group2)
        group2_layout.addWidget(QCheckBox("显示托盘图标"))
        group2_layout.addWidget(QCheckBox("最小化到托盘"))
        settings_layout.addWidget(group2)

        settings_layout.addStretch()
        self.tabs.addTab(settings_tab, "设置")

        # 关于选项卡
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_label = QLabel("这是关于页面\n\n测试左侧选项卡的显示效果")
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_label)
        about_layout.addStretch()
        self.tabs.addTab(about_tab, "关于")

        # 帮助选项卡
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_label = QLabel("帮助信息\n\n1. 选项卡现在显示在左侧\n2. 可以通过按钮切换位置\n3. 支持主题切换")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_layout.addWidget(help_label)
        help_layout.addStretch()
        self.tabs.addTab(help_tab, "帮助")

    def change_tab_position(self, position):
        """改变选项卡位置"""
        StyleHelper.set_tab_position(self.tabs, position)
        print(f"选项卡位置已切换到: {position}")

    def change_theme(self, theme):
        """切换主题"""
        theme_manager.set_theme(theme)
        print(f"主题已切换到: {theme}")


def main():
    app = QApplication(sys.argv)

    # 应用样式
    StyleApplier.apply_ant_design_theme(app)

    window = TestWindow()
    window.show()

    print("左侧选项卡测试程序已启动")
    print("- 选项卡默认显示在左侧")
    print("- 可以通过顶部按钮切换位置和主题")
    print("- 按 Ctrl+C 或关闭窗口退出")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
