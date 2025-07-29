#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""演示自定义选项卡栏的水平文本显示功能"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QTextEdit,
)
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styles import StyleApplier, StyleHelper, theme_manager
from ui.components.custom_tabbar import CustomTabWidget


class HorizontalTextDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义选项卡栏 - 水平文本演示")
        self.setGeometry(100, 100, 1000, 700)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 添加说明
        info_label = QLabel(
            "🎯 演示功能：左侧选项卡的文本保持水平显示\n" "✨ 特点：使用自定义QTabBar确保文本始终水平显示，提升用户体验"
        )
        info_label.setStyleSheet("padding: 10px; background-color: #f0f8ff; border-radius: 5px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)

        # 创建控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 创建选项卡演示区域
        demo_layout = QHBoxLayout()

        # 左侧：标准选项卡（对比）
        standard_group = QGroupBox("标准QTabWidget（对比）")
        standard_layout = QVBoxLayout(standard_group)

        from PyQt6.QtWidgets import QTabWidget

        self.standard_tabs = QTabWidget()
        StyleHelper.set_tab_position(self.standard_tabs, "West")
        self.create_demo_tabs(self.standard_tabs, "标准")
        standard_layout.addWidget(self.standard_tabs)
        demo_layout.addWidget(standard_group)

        # 右侧：自定义选项卡（水平文本）
        custom_group = QGroupBox("自定义选项卡栏（水平文本）")
        custom_layout = QVBoxLayout(custom_group)

        self.custom_tabs = CustomTabWidget()
        StyleHelper.set_tab_position(self.custom_tabs, "West")
        self.create_demo_tabs(self.custom_tabs, "自定义")
        custom_layout.addWidget(self.custom_tabs)
        demo_layout.addWidget(custom_group)

        main_layout.addLayout(demo_layout)

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("控制面板")
        layout = QHBoxLayout(group)

        # 位置切换按钮
        layout.addWidget(QLabel("选项卡位置:"))
        positions = [("顶部", "North"), ("底部", "South"), ("左侧", "West"), ("右侧", "East")]
        for text, pos in positions:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, p=pos: self.change_tab_position(p))
            if pos == "West":
                btn.setStyleSheet("background-color: #1890ff; color: white;")
            layout.addWidget(btn)

        layout.addWidget(QLabel("|"))

        # 主题切换按钮
        layout.addWidget(QLabel("主题:"))
        light_btn = QPushButton("☀️ 浅色")
        light_btn.clicked.connect(lambda: self.change_theme("light"))
        layout.addWidget(light_btn)

        dark_btn = QPushButton("🌙 深色")
        dark_btn.clicked.connect(lambda: self.change_theme("dark"))
        layout.addWidget(dark_btn)

        layout.addStretch()

        return group

    def create_demo_tabs(self, tab_widget, prefix):
        """创建演示选项卡"""
        # 设置选项卡
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        settings_layout.addWidget(QLabel(f"{prefix} - 设置页面"))
        settings_layout.addWidget(QCheckBox("启用通知"))
        settings_layout.addWidget(QCheckBox("自动更新"))
        settings_layout.addWidget(QCheckBox("深色模式"))
        settings_layout.addStretch()

        tab_widget.addTab(settings_tab, "⚙️ 设置")

        # 编辑器选项卡
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)

        editor_layout.addWidget(QLabel(f"{prefix} - 文本编辑器"))
        text_edit = QTextEdit()
        text_edit.setPlainText(
            f"这是{prefix}选项卡的文本编辑器。\n\n"
            "请注意左侧选项卡文本的显示效果：\n"
            "- 自定义选项卡栏：文本保持水平显示\n"
            "- 标准选项卡栏：文本可能会旋转显示\n\n"
            "这样可以提供更好的用户体验。"
        )
        editor_layout.addWidget(text_edit)

        tab_widget.addTab(editor_tab, "📝 编辑器")

        # 关于选项卡
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_text = QLabel(
            f"{prefix} - 关于页面\n\n"
            "这个演示展示了自定义选项卡栏的优势：\n\n"
            "✅ 文本始终水平显示\n"
            "✅ 更好的可读性\n"
            "✅ 一致的用户体验\n"
            "✅ 支持所有选项卡位置"
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        about_layout.addStretch()

        tab_widget.addTab(about_tab, "ℹ️ 关于")

    def change_tab_position(self, position):
        """改变选项卡位置"""
        StyleHelper.set_tab_position(self.standard_tabs, position)
        StyleHelper.set_tab_position(self.custom_tabs, position)
        print(f"选项卡位置已切换到: {position}")

        # 更新按钮样式
        for btn in self.findChildren(QPushButton):
            if btn.text() in ["顶部", "底部", "左侧", "右侧"]:
                if (
                    (position == "North" and btn.text() == "顶部")
                    or (position == "South" and btn.text() == "底部")
                    or (position == "West" and btn.text() == "左侧")
                    or (position == "East" and btn.text() == "右侧")
                ):
                    btn.setStyleSheet("background-color: #1890ff; color: white;")
                else:
                    btn.setStyleSheet("")

    def change_theme(self, theme):
        """切换主题"""
        theme_manager.set_theme(theme)
        print(f"主题已切换到: {theme}")


def main():
    app = QApplication(sys.argv)

    # 应用样式
    StyleApplier.apply_ant_design_theme(app)

    window = HorizontalTextDemo()
    window.show()

    print("🎯 自定义选项卡栏演示程序已启动")
    print("📋 功能说明：")
    print("   - 左侧：标准QTabWidget（文本可能旋转）")
    print("   - 右侧：自定义选项卡栏（文本保持水平）")
    print("   - 可以切换位置和主题进行对比")
    print("💡 注意观察左侧选项卡文本的显示差异")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
