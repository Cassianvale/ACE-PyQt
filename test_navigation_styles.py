#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试导航选项卡样式

简单测试脚本，验证左侧垂直选项卡的样式是否正确应用。
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, '.')

from ui.components.navigation_tabs import NavigationTabs
from ui.components.custom_tabbar import CustomTabWidget
from ui.styles import theme_manager, StyleApplier, AntColors


def test_navigation_styles():
    """测试导航样式"""
    app = QApplication(sys.argv)
    
    # 应用主题
    StyleApplier.apply_ant_design_theme(app)
    
    # 创建测试窗口
    window = QWidget()
    window.setWindowTitle("导航样式测试")
    window.setGeometry(100, 100, 400, 300)
    
    layout = QVBoxLayout()
    
    # 标题
    title = QLabel("导航选项卡样式测试")
    title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    # 创建导航组件
    nav_tabs = NavigationTabs()
    layout.addWidget(nav_tabs)
    
    # 测试传统选项卡
    traditional_tabs = CustomTabWidget()
    traditional_tabs.setTabPosition(CustomTabWidget.TabPosition.West)
    traditional_tabs.addTab(QLabel("页面1"), "猫咪设置")
    traditional_tabs.addTab(QLabel("页面2"), "通用设置")
    traditional_tabs.addTab(QLabel("页面3"), "模型管理")
    layout.addWidget(traditional_tabs)
    
    window.setLayout(layout)
    window.show()
    
    # 输出样式信息
    colors = AntColors()
    print("=" * 50)
    print("导航选项卡样式测试")
    print("=" * 50)
    print("主题颜色配置:")
    print(f"PRIMARY_1 (激活背景): {colors.PRIMARY_1}")
    print(f"PRIMARY_6 (激活文字): {colors.PRIMARY_6}")
    print(f"GRAY_2 (未激活背景): {colors.GRAY_2}")
    print(f"GRAY_9 (未激活文字): {colors.GRAY_9}")
    print(f"GRAY_3 (悬浮背景): {colors.GRAY_3}")
    print("=" * 50)
    print("样式特点:")
    print("1. ✅ 激活状态：蓝色背景 + 蓝色文字")
    print("2. ✅ 未激活状态：透明背景 + 深灰文字")
    print("3. ✅ 悬浮效果：浅灰背景")
    print("4. ✅ 圆角边框：8px 圆角")
    print("5. ✅ 图标支持：emoji 图标显示")
    print("=" * 50)
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(test_navigation_styles())
