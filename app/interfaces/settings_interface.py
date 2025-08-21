#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""设置界面模块 - 纯UI层，业务逻辑已分离到module层"""

from contextlib import redirect_stdout

with redirect_stdout(None):
    from qfluentwidgets import (
        ScrollArea, VBoxLayout,
        SettingCardGroup, StrongBodyLabel, FluentIcon as FLF,
        OptionsConfigItem, OptionsValidator, InfoBar, InfoBarPosition
    )
    from PyQt5.QtWidgets import QWidget, QVBoxLayout
    from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from ..common.style_sheet import StyleSheet
from ..card.switch_setting_card import SwitchSettingCard
from ..card.combo_setting_card import ComboBoxSettingCard
from ..card.push_setting_card import PushSettingCard

# 业务逻辑模块
from module.settings.startup import StartupSettings
from module.settings.window import WindowSettings
from module.settings.logging import LoggingSettings
from module.settings.directory import DirectoryManager
from module.update.update_manager import UpdateManager
from module.theme.theme_manager import ThemeManager
from module.config import cfg
from app.tools import logger


class SettingsInterface(ScrollArea):
    """设置界面 - 纯UI层"""
    
    # UI事件信号
    themeChangeRequested = pyqtSignal(str)
    updateCheckRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("settingsInterface")
        
        # 创建滚动内容
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 初始化更新管理器
        self.update_manager = UpdateManager()
        self.update_manager.initialize()
        
        # 初始化界面
        self._initWidget()
        self._initLayout()
        self._initSettingGroups()
        self._loadSettings()
        self._connectUpdateSignals()
        
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
        
        # 系统设置组
        self._createSystemSettingsGroup()
        
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
            business_handler=lambda enabled: StartupSettings.toggle_auto_start(enabled, cfg.get_app_name()),
            parent=self.appGroup
        )
        
        # 启动时检查更新
        self.checkUpdateOnStartCard = SwitchSettingCard(
            FLF.UPDATE,
            "启动时检查更新",
            "应用启动时自动检查是否有新版本",
            business_handler=StartupSettings.toggle_check_update_on_start,
            parent=self.appGroup
        )
        
        # 关闭行为
        self.closeBehaviorCard = ComboBoxSettingCard(
            FLF.CLOSE,
            "关闭行为",
            "设置点击关闭按钮时的行为",
            texts=["直接退出", "最小化到托盘"],
            business_handler=lambda option: WindowSettings.set_close_behavior(option == "最小化到托盘"),
            parent=self.appGroup
        )
        
        # 调试模式
        self.debugModeCard = SwitchSettingCard(
            FLF.DEVELOPER_TOOLS,
            "调试模式",
            "启用调试模式以获取更详细的日志信息",
            business_handler=LoggingSettings.toggle_debug_mode,
            parent=self.appGroup
        )
        
        self.appGroup.addSettingCard(self.autoStartCard)
        self.appGroup.addSettingCard(self.checkUpdateOnStartCard)
        self.appGroup.addSettingCard(self.closeBehaviorCard)
        self.appGroup.addSettingCard(self.debugModeCard)
        self.vBoxLayout.addWidget(self.appGroup)
    
    def _createThemeSettingsGroup(self):
        """创建主题设置组"""
        self.themeGroup = SettingCardGroup("主题设置", self.scrollWidget)
        
        # 应用主题
        theme_options = {
            "auto": "跟随系统",
            "light": "浅色模式", 
            "dark": "深色模式"
        }
        self.themeCard = ComboBoxSettingCard(
            FLF.BRUSH,
            "应用主题",
            "选择应用程序的主题风格",
            business_handler=self._handle_theme_change,
            parent=self.themeGroup
        )
        self.themeCard.set_options(theme_options)
        
        self.themeGroup.addSettingCard(self.themeCard)
        self.vBoxLayout.addWidget(self.themeGroup)
    
    def _createSystemSettingsGroup(self):
        """创建系统设置组"""
        self.systemGroup = SettingCardGroup("系统设置", self.scrollWidget)
        
        # 打开配置目录
        self.openConfigDirCard = PushSettingCard(
            "打开目录",
            FLF.FOLDER,
            "配置文件目录",
            "打开应用程序配置文件所在目录",
            business_handler=DirectoryManager.open_config_directory,
            parent=self.systemGroup
        )
        
        # 打开日志目录
        self.openLogDirCard = PushSettingCard(
            "打开目录",
            FLF.DOCUMENT,
            "日志文件目录",
            "打开应用程序日志文件所在目录",
            business_handler=DirectoryManager.open_log_directory,
            parent=self.systemGroup
        )
        
        self.systemGroup.addSettingCard(self.openConfigDirCard)
        self.systemGroup.addSettingCard(self.openLogDirCard)
        self.vBoxLayout.addWidget(self.systemGroup)
    
    def _createAboutSettingsGroup(self):
        """创建关于设置组"""
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        
        # 检查更新
        self.checkUpdateCard = PushSettingCard(
            "检查更新",
            FLF.UPDATE,
            "检查更新",
            "检查应用程序是否有新版本",
            business_handler=self._handle_check_update,
            parent=self.aboutGroup
        )
        
        self.aboutGroup.addSettingCard(self.checkUpdateCard)
        self.vBoxLayout.addWidget(self.aboutGroup)
    
    def _loadSettings(self):
        """从配置加载设置到界面"""
        try:
            # 加载应用设置
            self.autoStartCard.load_value(StartupSettings.get_auto_start_status())
            self.checkUpdateOnStartCard.load_value(StartupSettings.get_check_update_on_start_status())
            
            # 加载关闭行为
            close_to_tray = WindowSettings.get_close_behavior()
            self.closeBehaviorCard.load_value("最小化到托盘" if close_to_tray else "直接退出")
            
            # 加载调试模式
            self.debugModeCard.load_value(LoggingSettings.get_debug_mode_status())
            
            # 加载主题设置
            current_theme = ThemeManager.get_current_theme()
            theme_display_name = ThemeManager.get_theme_display_name(current_theme)
            self.themeCard.load_value(theme_display_name)
            
        except Exception as e:
            logger.error(f"加载设置界面失败: {str(e)}")
    
    def _handle_check_update(self):
        """处理检查更新"""
        self.checkUpdateCard.set_button_text("检查中...")
        self.checkUpdateCard.set_button_enabled(False)
        self.update_manager.check_for_updates(silent_mode=False)
    
    def _connectUpdateSignals(self):
        """连接更新相关信号"""
        if hasattr(self.update_manager.version_checker, 'check_finished'):
            self.update_manager.version_checker.check_finished.connect(self._on_update_check_finished)
    
    def _on_update_check_finished(self, has_update, current_ver, latest_ver, update_info_str, error_msg):
        """更新检查完成处理"""
        self.checkUpdateCard.set_button_text("检查更新")
        self.checkUpdateCard.set_button_enabled(True)
        
        result = self.update_manager.process_update_result(
            has_update, current_ver, latest_ver, update_info_str, error_msg
        )
        
        if result.get('silent_mode'):
            return
        
        if result.get('has_update'):
            self._show_info_bar(
                "发现新版本", 
                f"发现新版本 v{latest_ver}，请前往下载页面更新", 
                InfoBar.success
            )
        elif result.get('error_msg'):
            self._show_info_bar(
                "检查更新失败", 
                result['error_msg'], 
                InfoBar.error
            )
        else:
            self._show_info_bar(
                "已是最新版本", 
                f"当前版本 v{current_ver} 已经是最新版本", 
                InfoBar.success
            )
    
    def _show_info_bar(self, title: str, content: str, bar_type=InfoBar.success):
        """显示信息条"""
        try:
            # 使用正确的InfoBar API
            bar_type(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent() or self
            )
        except Exception as e:
            logger.error(f"显示信息条失败: {str(e)}")
    
    def _handle_theme_change(self, theme_display_name: str):
        """处理主题变更
        
        Args:
            theme_display_name (str): 主题显示名称
            
        Returns:
            bool: 主题切换是否成功
        """
        try:
            # 支持中文和英文主题标识符
            theme_mapping = {
                # 中文显示名称
                "跟随系统": "auto",
                "浅色模式": "light", 
                "深色模式": "dark",
                # 英文标识符（直接使用）
                "auto": "auto",
                "light": "light",
                "dark": "dark"
            }
            
            theme = theme_mapping.get(theme_display_name)
            if theme is None:
                logger.error(f"无效的主题显示名称: {theme_display_name}")
                return False
            
            # 切换主题并保存配置
            success = ThemeManager.switch_theme(theme)
            
            if success:
                display_name = ThemeManager.get_theme_display_name(theme)
                self._show_info_bar(
                    "主题已切换", 
                    f"已切换到{display_name}", 
                    InfoBar.success
                )
                return True
            else:
                self._show_info_bar(
                    "主题切换失败", 
                    "主题切换或保存失败，请重试", 
                    InfoBar.error
                )
                return False
                
        except Exception as e:
            logger.error(f"处理主题变更失败: {str(e)}")
            self._show_info_bar(
                "主题切换失败", 
                f"主题切换时发生错误: {str(e)}", 
                InfoBar.error
            )
            return False