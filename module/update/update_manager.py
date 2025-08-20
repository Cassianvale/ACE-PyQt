#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新检查业务逻辑
"""

import os
import webbrowser
from app.tools import logger, get_version_checker, create_update_message
from module.config import cfg


class UpdateManager:
    """更新管理业务逻辑"""
    
    def __init__(self):
        self.version_checker = None
        self.download_url = None
        
    def initialize(self):
        """初始化更新管理器"""
        self.version_checker = get_version_checker(cfg)
        
    def check_for_updates(self, silent_mode: bool = False):
        """
        检查更新
        
        Args:
            silent_mode (bool): 是否静默检查（不显示弹窗）
        """
        if not self.version_checker:
            self.initialize()
            
        self.version_checker.check_for_updates_async(silent_mode=silent_mode)
    
    def get_current_version(self) -> str:
        """
        获取当前版本号
        
        Returns:
            str: 当前版本号
        """
        if not self.version_checker:
            self.initialize()
            
        return self.version_checker.get_current_version()
    
    def process_update_result(self, has_update: bool, current_ver: str, latest_ver: str, 
                             update_info_str: str, error_msg: str) -> dict:
        """
        处理更新检查结果
        
        Args:
            has_update (bool): 是否有更新
            current_ver (str): 当前版本
            latest_ver (str): 最新版本
            update_info_str (str): 更新信息JSON字符串
            error_msg (str): 错误信息
            
        Returns:
            dict: 处理结果信息
        """
        try:
            # 检测是否为静默模式
            silent_mode = error_msg == "silent_mode"
            
            # 保存下载URL
            self.download_url = None
            if has_update and update_info_str:
                try:
                    import json
                    update_info = json.loads(update_info_str)
                    self.download_url = update_info.get("download_url")
                    if not self.download_url:
                        self.download_url = update_info.get("url", cfg.get_github_releases_url())
                except:
                    self.download_url = cfg.get_github_releases_url()
            
            # 构建版本信息
            version_info = self._build_version_info(has_update, current_ver, latest_ver)
            
            result = {
                'has_update': has_update,
                'current_version': current_ver,
                'latest_version': latest_ver,
                'version_info': version_info,
                'silent_mode': silent_mode,
                'download_url': self.download_url,
                'error_msg': error_msg if not silent_mode else None
            }
            
            # 如果不是静默模式，创建更新对话框数据
            if not silent_mode:
                dialog_result = create_update_message(
                    has_update, current_ver, latest_ver, update_info_str, 
                    error_msg, cfg.get_github_releases_url()
                )
                result['dialog'] = {
                    'title': dialog_result[0],
                    'message': dialog_result[1],
                    'type': dialog_result[2],
                    'extra_data': dialog_result[3]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"处理更新结果失败: {str(e)}")
            return {
                'has_update': False,
                'current_version': current_ver,
                'latest_version': latest_ver,
                'version_info': f"当前版本: v{current_ver}",
                'silent_mode': False,
                'download_url': None,
                'error_msg': f"处理更新结果失败: {str(e)}"
            }
    
    def _build_version_info(self, has_update: bool, current_ver: str, latest_ver: str) -> str:
        """
        构建版本信息文本
        
        Args:
            has_update (bool): 是否有更新
            current_ver (str): 当前版本
            latest_ver (str): 最新版本
            
        Returns:
            str: 版本信息文本
        """
        if has_update and latest_ver:
            return (f"当前版本: v{current_ver} | 🆕 <b>最新版本: v{latest_ver} </b> "
                   f"<a href='#download' style='color: #28C940; font-weight: bold; font-size: 14px; text-decoration: none;'> 👉 前往下载</a>")
        else:
            return f"当前版本: v{current_ver}"
    
    def open_download_url(self, download_url: str = None, is_direct_download: bool = False) -> bool:
        """
        打开下载链接或发布页面
        
        Args:
            download_url (str): 下载链接，如果为None则使用保存的下载URL
            is_direct_download (bool): 是否为直接下载链接
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 确定最终使用的下载URL
            final_url = download_url if download_url else (self.download_url or cfg.get_github_releases_url())
            
            # 如果是直接下载链接
            if is_direct_download:
                # 在Windows上使用默认浏览器下载
                if os.name == "nt":
                    os.startfile(final_url)
                else:
                    webbrowser.open(final_url)
                logger.debug(f"用户直接下载新版本: {final_url}")
            else:
                # 如果不是直接下载链接，打开网页
                webbrowser.open(final_url)
                logger.debug(f"用户访问下载页面: {final_url}")
                
            return True
        except Exception as e:
            logger.error(f"打开下载链接失败: {str(e)}")
            return False