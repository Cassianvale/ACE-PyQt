#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""日志封装"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_dir, log_retention_days=7, log_rotation="1 day", debug_mode=False):
    """
    配置日志系统

    Args:
        log_dir: 日志文件目录
        log_retention_days: 日志保留天数
        log_rotation: 日志轮转周期
        debug_mode: 是否启用调试模式

    Returns:
        logger: 配置好的logger实例

    Raises:
        OSError: 当无法创建日志目录时
        PermissionError: 当没有写入权限时
    """
    try:
        # 移除默认的日志处理器
        logger.remove()

        # 确定日志级别
        log_level = "DEBUG" if debug_mode else "INFO"

        # 确保日志目录存在
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # 配置控制台输出
        console_format = (
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
            if not debug_mode
            else "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        )

        logger.add(sys.stderr, level=log_level, format=console_format, colorize=True)

        # 配置文件输出
        log_file = log_path / "{time:YYYY-MM-DD}.log"
        file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"

        logger.add(
            str(log_file),
            level=log_level,
            format=file_format,
            rotation=log_rotation,
            retention=f"{log_retention_days} days",
            encoding="utf-8",
            compression="zip",
            enqueue=True,
            catch=True,
        )
        
        return logger

    except Exception as e:
        # 如果配置失败，至少保证有基本的控制台输出
        logger.remove()
        logger.add(sys.stderr, level="ERROR")
        logger.error(f"日志系统配置失败: {e}")
        raise


if __name__ == "__main__":
    """测试日志系统"""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            setup_logger(temp_dir, debug_mode=True)

            logger.debug("这是一条调试日志")
            logger.info("这是一条信息日志")
            logger.warning("这是一条警告日志")
            logger.error("这是一条错误日志")
            logger.critical("这是一条严重日志")

            # 模拟异常以记录堆栈跟踪信息
            try:
                1 / 0
            except ZeroDivisionError:
                logger.exception("发生了除零异常")

            print("✅ 日志测试完成")

            logger.remove()

        except Exception as e:
            print(f"❌ 日志测试失败: {e}")
            logger.remove()  # 确保清理
            raise
