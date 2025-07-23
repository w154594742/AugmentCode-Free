# AugmentCode-Free 国际化功能说明

## 概述

AugmentCode-Free 现已支持中英双语切换功能，并添加了版权信息和防诈骗提示。

## 新增功能

### 1. 中英双语切换
- 支持简体中文（zh_CN）和英文（en_US）
- 可在运行时动态切换语言，无需重启应用程序
- 语言设置自动保存，下次启动时记住用户选择

### 2. 版权信息显示
- 在GUI界面底部显示版权信息
- 包含开源协议说明
- 提供GitHub仓库链接
- 显示防诈骗警告

### 3. 欢迎界面
- 首次运行时显示欢迎对话框
- 可选择首选语言
- 显示重要的防诈骗提示
- 可设置是否下次显示

### 4. 关于对话框
- 通过"关于"按钮访问
- 显示完整的项目信息
- 包含版权声明和GitHub链接
- 醒目的防诈骗警告

## 文件结构

```
AugmentCode-Free/
├── languages/                 # 语言配置文件目录
│   ├── zh_CN.json            # 简体中文语言包
│   └── en_US.json            # 英文语言包
├── config/                   # 配置文件目录
│   └── settings.json         # 用户设置文件
├── language_manager.py       # 语言管理器
├── config_manager.py         # 配置管理器
├── welcome_dialog.py         # 欢迎对话框
├── gui.py                    # 主GUI界面（已更新）
├── main.py                   # 启动文件（已更新）
└── augment_tools_core/
    └── cli.py                # CLI界面（已更新）
```

## 使用方法

### GUI界面
1. 启动应用程序：`python main.py`
2. 在界面顶部选择语言
3. 点击"关于"按钮查看项目信息
4. 首次运行会显示欢迎对话框

### 命令行界面
```bash
# 使用默认语言
python -m augment_tools_core.cli --help

# 指定语言
python -m augment_tools_core.cli --language zh_CN --help
python -m augment_tools_core.cli --language en_US clean-db --help
```

## 配置文件

### 用户设置 (config/settings.json)
```json
{
  "language": "zh_CN",           // 当前语言
  "first_run": true,             // 是否首次运行
  "window_geometry": "420x680",  // 窗口大小
  "last_selected_ide": "VS Code", // 上次选择的IDE
  "show_welcome": true,          // 是否显示欢迎对话框
  "theme": "default"             // 主题设置
}
```

### 语言包结构 (languages/*.json)
```json
{
  "app": {
    "title": "应用标题",
    "welcome": "欢迎文本"
  },
  "buttons": {
    "run_all": "按钮文本"
  },
  "dialogs": {
    "titles": {
      "close_confirm": "对话框标题"
    },
    "messages": {
      "close_warning": "对话框消息"
    }
  },
  "status": {
    "success": "状态消息"
  },
  "copyright": {
    "notice": "版权声明",
    "fraud_warning": "防诈骗警告"
  }
}
```

## API 参考

### LanguageManager
```python
from language_manager import get_language_manager, get_text

# 获取语言管理器实例
lm = get_language_manager()

# 设置语言
lm.set_language("en_US")

# 获取翻译文本
text = get_text("buttons.run_all")

# 带参数的翻译
text = get_text("dialogs.titles.close_confirm", ide_name="VS Code")
```

### ConfigManager
```python
from config_manager import get_config_manager

# 获取配置管理器实例
cm = get_config_manager()

# 获取/设置语言
language = cm.get_language()
cm.set_language("zh_CN")

# 检查首次运行
if cm.is_first_run():
    cm.mark_first_run_complete()
```

## 添加新语言

1. 在 `languages/` 目录下创建新的语言文件，如 `fr_FR.json`
2. 复制现有语言文件的结构并翻译所有文本
3. 在 `language_manager.py` 中的 `available_languages` 字典添加新语言：
   ```python
   self.available_languages = {
       "zh_CN": "简体中文",
       "en_US": "English",
       "fr_FR": "Français"  # 新增
   }
   ```

## 测试

运行测试脚本验证国际化功能：
```bash
python test_internationalization.py
```

## 注意事项

1. 所有用户界面文本都已国际化，包括按钮、标签、对话框和状态消息
2. 语言设置会自动保存到配置文件中
3. 如果语言文件缺失或损坏，系统会回退到英文
4. CLI命令行界面也支持语言切换
5. 首次运行会显示重要的防诈骗提示

## 版权信息

© 2025 BasicProtein. All rights reserved.
Licensed under MIT License

⚠️ **重要提示**：本项目完全开源免费！如果有人向您收费，请立即联系销售方退款并举报诈骗行为。

项目地址：https://github.com/BasicProtein/AugmentCode-Free
