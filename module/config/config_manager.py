#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import threading
from pathlib import Path
from typing import Any, Dict
from ruamel.yaml import YAML

from app.tools import logger, check_auto_start, enable_auto_start, disable_auto_start
from module.config.app_config import APP_INFO, DEFAULT_CONFIG, SYSTEM_CONFIG
from utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):

    # 配置属性映射：(属性名, 配置路径, 类型转换函数, 验证函数)
    CONFIG_MAPPING = {
        "log_retention_days": ("logging.retention_days", int, lambda x: x if x > 0 else None),
        "log_rotation": ("logging.rotation", str, lambda x: x if x in ["1 day", "1 week", "1 month"] else None),
        "debug_mode": ("logging.debug_mode", bool, None),
        "auto_start": ("application.auto_start", bool, None),
        "close_to_tray": ("application.close_to_tray", bool, None),
        "theme": ("application.theme", str, lambda x: x if x in ["auto", "light", "dark"] else None),
        "check_update_on_start": ("application.check_update_on_start", bool, None),
        "window_width": ("window.width", int, lambda x: x if 300 <= x <= 3000 else None),
        "window_height": ("window.height", int, lambda x: x if 200 <= x <= 2000 else None),
    }

    def __init__(self, custom_app_info=None, custom_default_config=None, custom_system_config=None):
        """
        初始化配置管理器

        Args:
            custom_app_info (dict, optional): 自定义应用信息，用于覆盖默认值
            custom_default_config (dict, optional): 自定义默认配置，用于覆盖默认值
            custom_system_config (dict, optional): 自定义系统配置，用于覆盖默认值
        """
        # 线程锁，确保线程安全
        self._lock = threading.RLock()
        
        # YAML实例，使用ruamel.yaml保持格式化
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.width = 4096
        self._yaml.indent(mapping=2, sequence=4, offset=2)
        
        # 合并配置
        self.app_info = self._merge_config(APP_INFO, custom_app_info)
        self.default_config = self._merge_config(DEFAULT_CONFIG, custom_default_config, deep=True)
        self.system_config = self._merge_config(SYSTEM_CONFIG, custom_system_config)

        # 设置配置路径
        self._setup_paths()

        # 初始化配置属性
        self._init_config_attributes()

        # 确保配置目录存在并加载配置文件
        self._ensure_directories()
        self.load_config()

    def _merge_config(self, base_config, custom_config, deep=False):
        """
        合并配置字典

        Args:
            base_config (dict): 基础配置
            custom_config (dict, optional): 自定义配置
            deep (bool): 是否进行深度合并

        Returns:
            dict: 合并后的配置
        """
        result = base_config.copy()
        if custom_config:
            if deep:
                self._deep_update(result, custom_config)
            else:
                result.update(custom_config)
        return result

    def _deep_update(self, d, u):
        """
        递归更新嵌套字典

        Args:
            d (dict): 要更新的目标字典
            u (dict): 包含更新值的字典
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def _setup_paths(self):
        """设置配置相关路径"""
        # 获取项目根目录（脚本所在目录的上级目录）
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent

        # 如果 config_dir_name 为空，使用项目根目录；否则使用用户主目录
        if self.system_config["config_dir_name"]:
            self.config_dir = Path.home() / self.system_config["config_dir_name"]
        else:
            self.config_dir = project_root

        self.log_dir = self.config_dir / self.system_config["log_dir_name"]
        self.config_file = self.config_dir / self.system_config["config_file_name"]

    def _init_config_attributes(self):
        """初始化配置属性为默认值"""
        for attr_name, (config_path, type_func, _) in self.CONFIG_MAPPING.items():
            default_value = self._get_nested_value(self.default_config, config_path)
            setattr(self, attr_name, default_value)

    def _get_nested_value(self, data, path, default=None):
        """
        从嵌套字典中获取值

        Args:
            data (dict): 数据字典
            path (str): 点分隔的路径，如 'application.theme'
            default: 默认值

        Returns:
            获取到的值或默认值
        """
        keys = path.split(".")
        current = data
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def _set_nested_value(self, data, path, value):
        """
        在嵌套字典中设置值

        Args:
            data (dict): 数据字典
            path (str): 点分隔的路径
            value: 要设置的值
        """
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _ensure_directories(self):
        """确保配置和日志目录存在"""
        # 确保配置目录存在
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"创建配置目录失败: {str(e)}")

        # 确保日志目录存在
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"创建日志目录失败: {str(e)}")

    def load_config(self) -> bool:
        """
        加载配置文件

        Returns:
            bool: 是否加载成功
        """
        with self._lock:
            try:
                if not self.config_file.exists():
                    logger.debug("配置文件不存在，将创建默认配置文件")
                    return self._create_default_config()

                with self.config_file.open("r", encoding="utf-8") as f:
                    config_data = self._yaml.load(f)

                if not config_data:
                    logger.warning("配置文件为空或无效，将使用默认配置")
                    return self._create_default_config()

                # 加载所有配置属性
                self._load_config_attributes(config_data)

                # 处理特殊的开机自启逻辑
                self._handle_auto_start_config(config_data)

                return True

            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
                return self._create_default_config()

    def _load_config_attributes(self, config_data: Dict[str, Any]) -> None:
        """
        从配置数据中加载所有配置属性（带深拷贝保护）

        Args:
            config_data: 配置数据
        """
        for attr_name, (config_path, type_func, validator) in self.CONFIG_MAPPING.items():
            value = self._get_nested_value(config_data, config_path)
            if value is not None:
                try:
                    # 类型转换
                    converted_value = type_func(value)

                    # 验证
                    if validator:
                        validated_value = validator(converted_value)
                        if validated_value is None:
                            logger.warning(f"配置项 {config_path} 的值 {converted_value} 无效，使用默认值")
                            continue
                        converted_value = validated_value

                    # 深拷贝保护可变对象
                    safe_value = self._safe_copy_value(converted_value)
                    setattr(self, attr_name, safe_value)

                except (ValueError, TypeError) as e:
                    logger.warning(f"配置项 {config_path} 类型转换失败: {e}，使用默认值")

    def _handle_auto_start_config(self, config_data):
        """
        处理开机自启的特殊逻辑

        Args:
            config_data (dict): 配置数据
        """
        auto_start_value = self._get_nested_value(config_data, "application.auto_start")

        if auto_start_value is not None:
            # 检查实际开机自启状态与配置是否一致
            actual_auto_start = check_auto_start(self.app_info["name"])
            if self.auto_start != actual_auto_start:
                logger.warning(
                    f"开机自启配置与实际状态不一致，配置为:{self.auto_start}，实际为:{actual_auto_start}，将以配置为准"
                )

            # 确保开机自启状态与配置一致
            if self.auto_start:
                enable_auto_start(self.app_info["name"])
            else:
                disable_auto_start(self.app_info["name"])
        else:
            # 如果配置中没有自启设置，检查系统中是否已设置
            if check_auto_start(self.app_info["name"]):
                self.auto_start = True
                
    def _create_default_config(self):
        """
        创建默认配置文件

        Returns:
            bool: 是否创建成功
        """
        try:
            with self.config_file.open("w", encoding="utf-8") as f:
                self._yaml.dump(self.default_config, f)

            # 重新初始化配置属性为默认值
            self._init_config_attributes()
            return True
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {str(e)}")
            return False

    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 保存是否成功
        """
        with self._lock:
            try:
                config_data = self._build_config_data()
                
                with self.config_file.open("w", encoding="utf-8") as f:
                    self._yaml.dump(config_data, f)

                return True
                
            except Exception as e:
                logger.error(f"保存配置文件失败: {str(e)}")
                return False

    def _build_config_data(self):
        """
        构建配置数据字典

        Returns:
            dict: 配置数据
        """
        config_data = {}
        for attr_name, (config_path, _, _) in self.CONFIG_MAPPING.items():
            value = getattr(self, attr_name)
            self._set_nested_value(config_data, config_path, value)
        return config_data
    
    def _safe_copy_value(self, value: Any) -> Any:
        """
        安全拷贝值，对可变对象进行深拷贝
        
        Args:
            value: 要拷贝的值
            
        Returns:
            安全的值副本
        """
        if isinstance(value, (list, dict, set)):
            return copy.deepcopy(value)
        return value
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值，如果值是可变对象，则返回其拷贝
        
        Args:
            key: 配置项名称
            default: 默认值
            
        Returns:
            配置项的值
        """
        with self._lock:
            # 首先检查是否是映射的属性
            for attr_name, (config_path, _, _) in self.CONFIG_MAPPING.items():
                if attr_name == key:
                    value = getattr(self, attr_name, default)
                    return self._safe_copy_value(value)
            
            # 如果不是映射属性，检查直接属性
            if hasattr(self, key):
                value = getattr(self, key)
                return self._safe_copy_value(value)
            
            return default
    
    def set_value(self, key: str, value: Any) -> bool:
        """
        设置配置项的值并保存
        
        Args:
            key: 配置项名称
            value: 要设置的值
            
        Returns:
            bool: 设置是否成功
        """
        with self._lock:
            try:
                # 重新加载配置确保数据最新
                self.load_config()
                
                # 深拷贝保护
                safe_value = self._safe_copy_value(value)
                
                # 检查是否是映射的属性
                for attr_name, (config_path, type_func, validator) in self.CONFIG_MAPPING.items():
                    if attr_name == key:
                        # 类型验证和转换
                        try:
                            converted_value = type_func(safe_value)
                            if validator:
                                validated_value = validator(converted_value)
                                if validated_value is None:
                                    logger.error(f"配置项 {key} 的值 {safe_value} 验证失败")
                                    return False
                                converted_value = validated_value
                            safe_value = converted_value
                        except (ValueError, TypeError) as e:
                            logger.error(f"配置项 {key} 类型转换失败: {e}")
                            return False
                        break
                
                setattr(self, key, safe_value)
                return self.save_config()
                
            except Exception as e:
                logger.error(f"设置配置项 {key} 失败: {str(e)}")
                return False
    
    def __getattr__(self, attr: str) -> Any:
        """
        允许通过属性访问配置项的值（带深拷贝保护）
        
        Args:
            attr: 属性名
            
        Returns:
            属性值
        """
        # 避免递归调用
        if attr.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' 对象没有属性 '{attr}'")
        
        # 检查是否是配置映射中的属性
        if attr in [name for name, _ in self.CONFIG_MAPPING.keys()]:
            value = object.__getattribute__(self, attr)
            return self._safe_copy_value(value)
        
        raise AttributeError(f"'{type(self).__name__}' 对象没有属性 '{attr}'")

    # ==================== 应用信息获取方法 ====================
    
    def get_app_name(self):
        """获取应用名称"""
        return self.app_info["name"]

    def get_app_version(self):
        """获取应用版本"""
        return self.app_info["version"]

    def get_app_author(self):
        """获取应用作者"""
        return self.app_info["author"]

    def get_app_description(self):
        """获取应用描述"""
        return self.app_info["description"]

    def get_github_repo(self):
        """获取GitHub仓库地址"""
        return self.app_info["github_repo"]

    def get_github_api_url(self):
        """获取GitHub API URL"""
        return self.app_info["github_api_url"]

    def get_github_releases_url(self):
        """获取GitHub发布页面URL"""
        return self.app_info["github_releases_url"]

    def get_require_admin_privileges(self):
        """获取是否要求管理员权限启动应用程序"""
        return self.system_config.get("require_admin_privileges", True)

    # ==================== 窗口尺寸相关方法 ====================
    
    def save_window_size(self, width, height):
        """
        保存窗口尺寸到配置文件

        Args:
            width (int): 窗口宽度
            height (int): 窗口高度

        Returns:
            bool: 保存是否成功
        """
        try:
            self.window_width = width
            self.window_height = height
            success = self.save_config()

            if success:
                logger.debug(f"窗口尺寸已保存: {width}x{height}")
            else:
                logger.error("保存窗口尺寸失败")
            return success
        except Exception as e:
            logger.error(f"保存窗口尺寸时发生错误: {str(e)}")
            return False

    def get_window_size(self):
        """获取窗口尺寸"""
        return (self.window_width, self.window_height)