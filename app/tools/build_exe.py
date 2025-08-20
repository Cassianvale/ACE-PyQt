import os
import sys
import subprocess
import shutil
import argparse
import re
from utils import get_app_version
from config import ConfigManager

# 设置标准输出编码为UTF-8，解决Windows环境下中文输出问题
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6及更早版本兼容
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 初始化配置管理器
config_manager = ConfigManager()

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root_dir = os.path.dirname(current_dir)

# 设置图标文件路径
icon_path = os.path.join(root_dir, 'assets', 'icon', 'favicon.ico')
assets_icon_dir = os.path.join(root_dir, 'assets', 'icon')

# 检查资源文件是否存在
if not os.path.exists(icon_path):
    print(f"图标文件不存在: {icon_path}")
    sys.exit(1)

if not os.path.exists(assets_icon_dir):
    print(f"图标资源目录不存在: {assets_icon_dir}")
    sys.exit(1)

print(f"图标文件路径: {icon_path}")
print(f"图标资源目录: {assets_icon_dir}")

# 列出要包含的图标资源文件
icon_files = [f for f in os.listdir(assets_icon_dir) if os.path.isfile(os.path.join(assets_icon_dir, f))]
print(f"将包含的图标资源文件: {', '.join(icon_files)}")

app_name = config_manager.get_app_name()
print(f"使用应用名称进行打包: {app_name}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description=f'{app_name} Nuitka 打包工具')
    parser.add_argument('-v', '--version', 
                       help='指定新版本号 (格式: x.y.z)',
                       type=str)
    parser.add_argument('--no-version-update', 
                       action='store_true',
                       help='跳过版本号更新')
    return parser.parse_args()

# 解析命令行参数
args = parse_arguments()

current_version = get_app_version(config_manager)
print(f"使用版本号进行打包: {current_version}")

# 确保nuitka已安装
try:
    import nuitka
except ImportError:
    print("正在安装 Nuitka...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])

# 构建Nuitka打包命令
cmd = [
    sys.executable,
    "-m", "nuitka",
    "--standalone",  # 生成独立可执行文件
    "--windows-console-mode=disable",  # 禁用控制台
    "--windows-icon-from-ico=" + icon_path,  # 设置图标
    "--include-data-dir=%s=assets/icon" % assets_icon_dir,  # 包含整个图标资源目录
    "--windows-uac-admin",  # 请求管理员权限
    "--remove-output",  # 在重新构建前移除输出目录
    
    # PyQt5 相关配置
    "--enable-plugin=pyqt6",  # 启用PyQt5插件
    "--nofollow-import-to=PyQt5.QtWebEngineWidgets",
    "--nofollow-import-to=PyQt5.Qt3DCore",
    "--nofollow-import-to=PyQt5.Qt3DRender",
    "--nofollow-import-to=PyQt5.QtCharts",
    "--nofollow-import-to=PyQt5.QtDataVisualization",
    "--nofollow-import-to=PyQt5.QtMultimedia",
    "--nofollow-import-to=PyQt5.QtPositioning",
    "--nofollow-import-to=PyQt5.QtBluetooth",
    "--nofollow-import-to=PyQt5.QtSerialPort",
    "--nofollow-import-to=PyQt5.QtLocation",
    # 优化选项
    "--lto=yes",  # 链接时优化
    "--mingw64",  # 使用MinGW64
    "--jobs=4",  # 使用多核编译加速
    "--disable-cache=all",  # 禁用缓存
    "--clean-cache=all",  # 清除现有缓存
    "--output-filename=" + app_name + ".exe",  # 指定输出文件名
    "--nofollow-import-to=tkinter,PIL.ImageTk",  # 不跟随部分不必要模块
    "--prefer-source-code",  # 优先使用源代码而不是字节码
    "--python-flag=no_site",  # 不导入site
    "--python-flag=no_warnings",  # 不显示警告
    "main.py"
]

print("开始 Nuitka 打包...")
print("打包过程可能需要几分钟，请耐心等待...")

# 执行打包命令
try:
    # 切换到项目根目录执行打包命令
    os.chdir(root_dir)
    subprocess.check_call(cmd)
    
    # 查找生成的可执行文件
    main_exe = os.path.join(root_dir, "main.dist", app_name + ".exe")
    
    # 首先判断main_exe是否存在
    if os.path.exists(main_exe):
        print(f"打包成功！生成的可执行文件: {main_exe}")
        
        # 输出文件大小信息
        size_mb = os.path.getsize(main_exe) / (1024 * 1024)
        print(f"可执行文件大小: {size_mb:.2f} MB")
    else:
        print("打包完成，但未找到可执行文件")
        
except subprocess.CalledProcessError as e:
    print(f"打包失败: {e}")
    sys.exit(1)

# 压缩可执行文件目录
dist_dir = os.path.join(root_dir, "main.dist")
zip_name = f"{app_name}-v{current_version}-x64"
zip_path = os.path.join(root_dir, zip_name + ".zip")
if os.path.exists(dist_dir):
    print("正在压缩可执行文件目录...")
    # 确保在正确的位置创建zip文件
    shutil.make_archive(os.path.join(root_dir, zip_name), 'zip', dist_dir)
    print(f"压缩完成！生成的压缩包: {zip_path}")
else:
    print("未找到可执行文件目录，无法压缩")
    sys.exit(1)

print(f"{app_name} v{current_version} Nuitka 打包和压缩完成！")

# 显示使用说明
def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print(f"{app_name} 打包工具使用说明:")
    print("="*60)
    print("1. 直接运行 (交互式更新版本号):")
    print("   python utils/build_exe.py")
    print()
    print("2. 指定版本号:")
    print("   python utils/build_exe.py -v 1.2.3")
    print()
    print("3. 跳过版本号更新:")
    print("   python utils/build_exe.py --no-version-update")
    print()
    print("4. 显示帮助:")
    print("   python utils/build_exe.py -h")
    print("="*60)

# 仅在直接运行脚本时显示使用说明
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"\n当前项目版本: {get_app_version(config_manager)}")
        show_usage()
