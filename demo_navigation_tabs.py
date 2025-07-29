#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导航选项卡组件演示

展示新的左侧垂直导航选项卡组件的效果和功能。
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit,
                             QGroupBox, QFormLayout, QLineEdit, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, '.')

from ui.components.navigation_tabs import NavigationTabWidget, NavigationTabs
from ui.components.custom_tabbar import CustomTabWidget
from ui.styles import theme_manager, StyleApplier


class CatSettingsWidget(QWidget):
    """猫咪设置页面"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🐱 猫咪设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 设置表单
        form_group = QGroupBox("猫咪配置")
        form_layout = QFormLayout()
        
        # 猫咪名称
        name_edit = QLineEdit("小橘")
        form_layout.addRow("猫咪名称:", name_edit)
        
        # 猫咪品种
        breed_combo = QComboBox()
        breed_combo.addItems(["橘猫", "英短", "美短", "布偶", "暹罗", "波斯"])
        form_layout.addRow("猫咪品种:", breed_combo)
        
        # 是否绝育
        sterilized_check = QCheckBox("已绝育")
        sterilized_check.setChecked(True)
        form_layout.addRow("绝育状态:", sterilized_check)
        
        # 特殊需求
        special_text = QTextEdit()
        special_text.setPlainText("喜欢晒太阳，不喜欢洗澡")
        special_text.setMaximumHeight(80)
        form_layout.addRow("特殊需求:", special_text)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        layout.addStretch()
        self.setLayout(layout)


class GeneralSettingsWidget(QWidget):
    """通用设置页面"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("⚙️ 通用设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 设置表单
        form_group = QGroupBox("应用配置")
        form_layout = QFormLayout()
        
        # 语言设置
        language_combo = QComboBox()
        language_combo.addItems(["中文", "English", "日本語"])
        form_layout.addRow("界面语言:", language_combo)
        
        # 主题设置
        theme_combo = QComboBox()
        theme_combo.addItems(["浅色主题", "深色主题", "跟随系统"])
        form_layout.addRow("主题模式:", theme_combo)
        
        # 自动保存
        auto_save_check = QCheckBox("启用自动保存")
        auto_save_check.setChecked(True)
        form_layout.addRow("自动保存:", auto_save_check)
        
        # 启动时检查更新
        check_update_check = QCheckBox("启动时检查更新")
        check_update_check.setChecked(False)
        form_layout.addRow("更新检查:", check_update_check)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        layout.addStretch()
        self.setLayout(layout)


class ModelManagementWidget(QWidget):
    """模型管理页面"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🔧 模型管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 模型列表
        model_group = QGroupBox("已安装的模型")
        model_layout = QVBoxLayout()
        
        models = [
            "GPT-4 Turbo (最新)",
            "Claude-3 Sonnet",
            "Gemini Pro",
            "LLaMA 2 70B"
        ]
        
        for model in models:
            model_frame = QFrame()
            model_frame.setFrameStyle(QFrame.Shape.Box)
            model_frame.setStyleSheet("padding: 10px; margin: 5px; border-radius: 5px;")
            
            model_item_layout = QHBoxLayout()
            model_label = QLabel(model)
            model_label.setStyleSheet("font-weight: 500;")
            
            status_label = QLabel("✅ 已激活")
            status_label.setStyleSheet("color: green;")
            
            model_item_layout.addWidget(model_label)
            model_item_layout.addStretch()
            model_item_layout.addWidget(status_label)
            
            model_frame.setLayout(model_item_layout)
            model_layout.addWidget(model_frame)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addStretch()
        self.setLayout(layout)


class NavigationDemoWindow(QMainWindow):
    """导航选项卡演示窗口"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        self.setWindowTitle("导航选项卡组件演示")
        self.setGeometry(100, 100, 900, 600)
        
        # 中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 标题栏
        header = QLabel("左侧垂直导航选项卡演示")
        header.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            padding: 16px; 
            background-color: #f0f0f0; 
            border-radius: 8px;
            margin-bottom: 16px;
        """)
        layout.addWidget(header)
        
        # 演示区域
        demo_layout = QHBoxLayout()
        
        # 左侧：新的导航选项卡组件
        nav_group = QGroupBox("新的导航选项卡组件")
        nav_layout = QVBoxLayout()
        
        # 创建导航选项卡组件
        self.nav_widget = NavigationTabWidget()
        
        # 添加页面
        self.nav_widget.addTab(CatSettingsWidget(), "猫咪设置", "🐱")
        self.nav_widget.addTab(GeneralSettingsWidget(), "通用设置", "⚙️")
        self.nav_widget.addTab(ModelManagementWidget(), "模型管理", "🔧")
        
        # 连接信号
        self.nav_widget.currentChanged.connect(self._on_nav_changed)
        
        nav_layout.addWidget(self.nav_widget)
        nav_group.setLayout(nav_layout)
        
        demo_layout.addWidget(nav_group)
        
        # 右侧：传统选项卡组件对比
        traditional_group = QGroupBox("传统选项卡组件对比")
        traditional_layout = QVBoxLayout()
        
        # 创建传统选项卡
        self.traditional_tabs = CustomTabWidget()
        self.traditional_tabs.setTabPosition(CustomTabWidget.TabPosition.West)
        
        # 添加页面
        self.traditional_tabs.addTab(QLabel("传统猫咪设置页面\n\n这是使用传统QTabWidget的效果"), "猫咪设置")
        self.traditional_tabs.addTab(QLabel("传统通用设置页面\n\n注意样式的差异"), "通用设置")
        self.traditional_tabs.addTab(QLabel("传统模型管理页面\n\n对比新组件的优势"), "模型管理")
        
        traditional_layout.addWidget(self.traditional_tabs)
        traditional_group.setLayout(traditional_layout)
        
        demo_layout.addWidget(traditional_group)
        
        layout.addLayout(demo_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        theme_btn = QPushButton("切换主题")
        theme_btn.clicked.connect(self._toggle_theme)
        button_layout.addWidget(theme_btn)
        
        reset_btn = QPushButton("重置到猫咪设置")
        reset_btn.clicked.connect(lambda: self.nav_widget.setCurrentIndex(0))
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪 - 当前选中: 猫咪设置")
    
    def _on_nav_changed(self, index: int):
        """导航选项卡改变时的处理"""
        tab_names = ["猫咪设置", "通用设置", "模型管理"]
        if 0 <= index < len(tab_names):
            self.statusBar().showMessage(f"当前选中: {tab_names[index]}")
            # 同步传统选项卡
            self.traditional_tabs.setCurrentIndex(index)
    
    def _toggle_theme(self):
        """切换主题"""
        current_theme = theme_manager.get_current_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        theme_manager.set_theme(new_theme)
        
        # 重新应用样式
        StyleApplier.apply_ant_design_theme(QApplication.instance())


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 应用主题
    StyleApplier.apply_ant_design_theme(app)
    
    # 创建演示窗口
    window = NavigationDemoWindow()
    window.show()
    
    print("=" * 60)
    print("导航选项卡组件演示")
    print("=" * 60)
    print("功能特点:")
    print("1. 左侧垂直导航布局")
    print("2. 图标 + 文本显示")
    print("3. 激活状态蓝色高亮")
    print("4. 悬浮交互效果")
    print("5. 主题切换支持")
    print("6. 与传统组件对比")
    print()
    print("操作说明:")
    print("- 点击左侧导航按钮切换页面")
    print("- 点击'切换主题'按钮查看深色模式效果")
    print("- 对比左右两侧组件的视觉差异")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
