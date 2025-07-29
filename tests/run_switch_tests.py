#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
现代开关组件测试运行器

使用方法:
python tests/run_switch_tests.py [选项]

选项:
--basic      只运行基本功能测试
--integration 只运行集成测试
--performance 只运行性能测试
--theme      只运行主题测试
--error      只运行错误处理测试
--accessibility 只运行可访问性测试
--all        运行所有测试（默认）
--verbose    详细输出
--quiet      静默模式
"""

import sys
import os
import argparse
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保可以导入PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
except ImportError as e:
    print(f"错误: 无法导入PyQt6: {e}")
    print("请确保已安装PyQt6: pip install PyQt6")
    sys.exit(1)

# 导入测试模块
try:
    from tests.test_modern_switch import (
        TestCustomSwitch,
        TestCustomSwitchIntegration,
        TestCustomSwitchThemeIntegration,
        TestCustomSwitchPerformance,
        TestCustomSwitchErrorHandling,
        TestCustomSwitchAccessibility,
    )
except ImportError as e:
    print(f"错误: 无法导入测试模块: {e}")
    sys.exit(1)


class ColoredTestResult(unittest.TextTestResult):
    """带颜色输出的测试结果类"""

    def __init__(self, stream, descriptions, verbosity, use_colors=True):
        super().__init__(stream, descriptions, verbosity)
        self.use_colors = use_colors and hasattr(stream, "isatty") and stream.isatty()

    def _color_text(self, text, color_code):
        """给文本添加颜色"""
        if self.use_colors:
            return f"\033[{color_code}m{text}\033[0m"
        return text

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✓ ", "32"))  # 绿色

    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✗ ", "31"))  # 红色

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✗ ", "31"))  # 红色

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(self._color_text("⚠ ", "33"))  # 黄色


class ColoredTestRunner(unittest.TextTestRunner):
    """带颜色输出的测试运行器"""

    def __init__(self, **kwargs):
        use_colors = kwargs.pop("use_colors", True)
        super().__init__(**kwargs)
        self.use_colors = use_colors

    def _makeResult(self):
        return ColoredTestResult(self.stream, self.descriptions, self.verbosity, self.use_colors)


def create_test_suite(test_types):
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = {
        "basic": TestCustomSwitch,
        "integration": TestCustomSwitchIntegration,
        "theme": TestCustomSwitchThemeIntegration,
        "performance": TestCustomSwitchPerformance,
        "error": TestCustomSwitchErrorHandling,
        "accessibility": TestCustomSwitchAccessibility,
    }

    for test_type in test_types:
        if test_type in test_classes:
            suite.addTest(loader.loadTestsFromTestCase(test_classes[test_type]))
        else:
            print(f"警告: 未知的测试类型 '{test_type}'")

    return suite


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="现代开关组件测试运行器", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__
    )

    # 测试类型选项
    parser.add_argument("--basic", action="store_true", help="只运行基本功能测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--theme", action="store_true", help="只运行主题测试")
    parser.add_argument("--error", action="store_true", help="只运行错误处理测试")
    parser.add_argument("--accessibility", action="store_true", help="只运行可访问性测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试（默认）")

    # 输出选项
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    parser.add_argument("--no-colors", action="store_true", help="禁用颜色输出")

    # 其他选项
    parser.add_argument("--failfast", action="store_true", help="遇到第一个失败就停止")
    parser.add_argument("--buffer", action="store_true", help="缓冲stdout和stderr")

    args = parser.parse_args()

    # 确定要运行的测试类型
    test_types = []
    if args.basic:
        test_types.append("basic")
    if args.integration:
        test_types.append("integration")
    if args.performance:
        test_types.append("performance")
    if args.theme:
        test_types.append("theme")
    if args.error:
        test_types.append("error")
    if args.accessibility:
        test_types.append("accessibility")

    # 如果没有指定特定测试或指定了--all，运行所有测试
    if not test_types or args.all:
        test_types = ["basic", "integration", "theme", "performance", "error", "accessibility"]

    # 确定详细程度
    verbosity = 1
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0

    # 创建QApplication实例
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # 创建测试套件
    suite = create_test_suite(test_types)

    # 创建测试运行器
    runner = ColoredTestRunner(
        verbosity=verbosity, failfast=args.failfast, buffer=args.buffer, use_colors=not args.no_colors
    )

    print(f"运行现代开关组件测试...")
    print(f"测试类型: {', '.join(test_types)}")
    print(f"详细程度: {verbosity}")
    print("-" * 50)

    # 运行测试
    result = runner.run(suite)

    # 输出结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    # 计算成功率
    if result.testsRun > 0:
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"成功率: {success_rate:.1f}%")

    print("=" * 50)

    # 如果有失败或错误，显示详细信息
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")

    # 返回适当的退出码
    if result.failures or result.errors:
        return 1
    else:
        print("\n🎉 所有测试通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())
