#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Setting Card Components
参考 March7thAssistant 的设计模式，提供功能完整、易用性强的设置卡片组件

组件特性：
- 自动配置绑定 (configname 参数)
- 智能错误处理和用户反馈
- 业务逻辑集成 (business_handler)
- 丰富的交互体验
- 类型安全和参数验证
"""

from .switch_setting_card import SwitchSettingCard
from .combo_setting_card import ComboBoxSettingCard
from .push_setting_card import PushSettingCard
from .range_setting_card import RangeSettingCard
from .time_setting_card import TimeSettingCard
from .messagebox_custom import (
    MessageBoxEdit, MessageBoxEditMultiple, MessageBoxDate, MessageBoxCombo,
    MessageBoxKeyBind, MessageBoxConfig, MessageBoxFormFields, MessageBoxPairList
)

# 基础设置卡片
__all__ = [
    # 基础组件
    'SwitchSettingCard',      # 开关设置卡片
    'ComboBoxSettingCard',    # 下拉选择卡片
    'PushSettingCard',        # 按钮设置卡片
    
    # 高级组件
    'RangeSettingCard',       # 数值范围滑块卡片
    'TimeSettingCard',        # 时间选择卡片
    
    # 对话框组件
    'MessageBoxEdit',         # 单行文本编辑对话框
    'MessageBoxEditMultiple', # 多行文本编辑对话框
    'MessageBoxDate',         # 日期时间选择对话框
    'MessageBoxCombo',        # 下拉选择对话框
    'MessageBoxKeyBind',      # 快捷键绑定对话框
    'MessageBoxConfig',       # 通用配置对话框
    'MessageBoxFormFields',   # 表单字段对话框
    'MessageBoxPairList',     # 键值对列表对话框
]