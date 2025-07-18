#!/usr/bin/env python3
"""
启动脚本 - AugmentCode-Free GUI
此文件已弃用，请使用 main.py 启动GUI
"""

import sys

print("⚠️  注意：run_gui.py 已弃用")
print("✅ 请使用 main.py 启动GUI界面")
print("💡 运行命令：python main.py")
print()

# 自动启动main.py
try:
    from main import main
    main()
except Exception as e:
    print(f"❌ 启动失败: {e}")
    print("请直接运行: python main.py")
    sys.exit(1)
