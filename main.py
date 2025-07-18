#!/usr/bin/env python3
"""
AugmentCode-Free 主程序
启动图形用户界面

这是AugmentCode-Free工具的主启动程序。
双击此文件或在命令行中运行 'python main.py' 来启动GUI界面。

功能包括：
- 清理 VS Code 数据库
- 修改 VS Code 遥测 ID  
- 运行所有可用工具
"""

import sys
import os
from pathlib import Path

def main():
    """主函数 - 启动GUI应用程序"""
    print("=" * 50)
    print("🚀 AugmentCode-Free 工具启动中...")
    print("=" * 50)
    print()
    
    # 添加当前目录到Python路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        # 导入并启动GUI
        from gui import main as gui_main
        
        print("✅ 正在启动图形界面...")
        print("💡 提示：如果界面没有出现，请检查是否有防火墙或安全软件阻止")
        print()
        
        # 启动GUI
        gui_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print()
        print("🔧 解决方案：")
        print("1. 确保所有依赖都已安装：pip install -r requirements.txt")
        print("2. 确保Python版本为3.7或更高")
        print("3. 确保所有项目文件都在同一目录下")
        print("4.其他问题请提交issue")
        input("\n按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 启动GUI时发生错误: {e}")
        print()
        print("🔧 可能的解决方案：")
        print("1. 重新安装依赖：pip install -r requirements.txt")
        print("2. 检查Python环境是否正确配置")
        print("3. 确保有足够的系统权限")
        print("4.其他问题请提交issue")
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
