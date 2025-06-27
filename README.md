# ACE-PyQt

> 使用PyQt6构建的桌面应用程序，用于简化Gui应用开发流程  
> 在[ACE-KILLER](https://github.com/Cassianvale/ACE-KILLER)项目基础上进行拆解和开发  

## 特性
- [x] 配置管理
- [x] 日志系统
- [x] Windows 系统通知
- [x] Antd明暗主题切换
- [x] version版本检查
- [x] 托盘支持
- [x] 开机静默自启支持
- [x] Windows端自动构建和发布

## 运行

1. 创建并激活Python虚拟环境（推荐）  

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. 安装依赖  

   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. 环境变量修改  
- 更改`app_config.py`文件  
