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
    # 强化路径设置 - 确保跨平台兼容
    current_dir = Path(__file__).resolve().parent
    current_dir_str = str(current_dir)

    # 清理并重新设置Python路径
    if current_dir_str in sys.path:
        sys.path.remove(current_dir_str)
    sys.path.insert(0, current_dir_str)

    # 确保工作目录正确
    os.chdir(current_dir)

    try:
        # 导入配置和语言管理
        from config_manager import get_config_manager
        from language_manager import get_language_manager, get_text

        # 如果没有在ImportError中初始化，在这里初始化
        if 'config_manager' not in locals():
            config_manager = get_config_manager()
            language_manager = get_language_manager(config_manager)

        print("=" * 50)
        print(get_text("console.starting"))
        print("=" * 50)
        print()

        # 导入并启动PyQt6 GUI
        from gui_qt6.main_window import main as gui_main

        print(get_text("console.gui_starting"))
        print(get_text("console.gui_tip"))
        print()

        # 启动PyQt6 GUI
        exit_code = gui_main()
        sys.exit(exit_code)

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print()
        print("🔧 正在尝试自动修复...")

        # 尝试多种路径修复方案
        possible_paths = [
            current_dir,
            current_dir.parent,
            Path.cwd(),
            Path(__file__).parent
        ]

        fixed = False
        for path in possible_paths:
            try:
                path_str = str(path.resolve())
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)

                # 尝试导入
                from config_manager import get_config_manager
                from language_manager import get_language_manager, get_text

                print(f"✅ 路径修复成功: {path_str}")
                fixed = True
                break
            except ImportError:
                continue

        if not fixed:
            print("❌ 自动修复失败")
            print()
            print("🔧 手动解决方案：")
            print("1. 确保在AugmentCode-Free目录中运行")
            print("2. 检查config_manager.py和language_manager.py是否存在")
            print("3. 运行: pip install -r requirements.txt")
            print("4. macOS用户可尝试: python3 main_macos.py")
            input("\n按回车键退出...")
            sys.exit(1)

        # 如果修复成功，继续执行
        config_manager = get_config_manager()
        language_manager = get_language_manager(config_manager)
    except Exception as e:
        print(f"❌ 启动错误: {e}")
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
