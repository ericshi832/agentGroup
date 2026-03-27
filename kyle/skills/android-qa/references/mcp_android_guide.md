# MCP Android Tools Guide

Kyle 使用 MCP Android 工具在真实设备或模拟器上执行 UI 验证，无需编写 Espresso 代码。

---

## 工具总览

| 工具 | 用途 |
|------|------|
| `mcp__android__list_devices` | 列出已连接设备和模拟器 |
| `mcp__android__get_device_info` | 获取设备型号、API Level、屏幕尺寸 |
| `mcp__android__list_avds` | 列出可用的模拟器 AVD |
| `mcp__android__start_emulator` | 启动指定 AVD |
| `mcp__android__install_apk` | 安装 APK |
| `mcp__android__launch_app` | 通过包名启动应用 |
| `mcp__android__get_current_activity` | 获取当前 Activity 类名 |
| `mcp__android__get_ui_tree` | 获取当前屏幕 UI 可访问性树 |
| `mcp__android__screenshot` | 截取当前屏幕截图 |
| `mcp__android__tap` | 按坐标点击 |
| `mcp__android__tap_element` | 按 resource-id 或 text 点击元素 |
| `mcp__android__tap_and_wait` | 点击并等待 UI 变化 |
| `mcp__android__multi_tap` | 多次快速点击（双击等） |
| `mcp__android__long_press` | 长按 |
| `mcp__android__type_text` | 向当前焦点输入文字 |
| `mcp__android__swipe` | 滑动（坐标）|
| `mcp__android__scroll_to_element` | 滚动直到元素可见 |
| `mcp__android__press_key` | 按系统按键（BACK, HOME, ENTER 等）|
| `mcp__android__wait_for_element` | 等待元素出现（超时机制）|
| `mcp__android__get_logs` | 获取 logcat 日志 |
| `mcp__android__clear_logs` | 清空 logcat 缓冲区 |
| `mcp__android__adb_shell` | 执行任意 ADB shell 命令 |
| `mcp__android__pull_file` | 从设备拉取文件 |

---

## 标准测试流程

### 1. 环境准备

```
# 确认设备连接
mcp__android__list_devices

# 查看设备信息
mcp__android__get_device_info

# 如果需要启动模拟器
mcp__android__list_avds
mcp__android__start_emulator --avd "Pixel_7_API_34"

# 安装待测 APK
mcp__android__install_apk --path "build/outputs/apk/debug/app-debug.apk"
```

### 2. 启动应用

```
# 通过包名启动
mcp__android__launch_app --package "com.example.app"

# 等待首屏加载（确认某个元素出现）
mcp__android__wait_for_element --resourceId "com.example.app:id/tv_welcome" --timeout 5000
```

### 3. UI 探索（确定元素 ID）

```
# 截图查看当前屏幕
mcp__android__screenshot

# 获取 UI 树（包含所有元素的 resource-id、text、class、bounds）
mcp__android__get_ui_tree
```

**UI 树输出示例**：
```json
{
  "class": "android.widget.LinearLayout",
  "children": [
    {
      "class": "android.widget.EditText",
      "resourceId": "com.example.app:id/et_email",
      "text": "",
      "bounds": "[48,320][1032,430]"
    },
    {
      "class": "android.widget.Button",
      "resourceId": "com.example.app:id/btn_login",
      "text": "登录",
      "bounds": "[48,500][1032,600]"
    }
  ]
}
```

### 4. 交互操作

```
# 按 resource-id 点击
mcp__android__tap_element --resourceId "com.example.app:id/et_email"

# 输入文字（元素需已获得焦点）
mcp__android__type_text --text "test@example.com"

# 点击并等待导航
mcp__android__tap_and_wait --resourceId "com.example.app:id/btn_login" --waitFor "com.example.app:id/fragment_home"

# 按 text 点击（适合动态 ID）
mcp__android__tap_element --text "确认"

# 按系统键
mcp__android__press_key --key BACK
mcp__android__press_key --key ENTER

# 滚动列表
mcp__android__swipe --startX 540 --startY 1200 --endX 540 --endY 400 --duration 300

# 滚动到指定文字元素
mcp__android__scroll_to_element --text "底部条款"
```

### 5. 验证

```
# 截图保存为证据
mcp__android__screenshot

# 检查当前 Activity
mcp__android__get_current_activity

# 清空日志后操作，避免旧日志污染
mcp__android__clear_logs
# ...执行操作...
mcp__android__get_logs --level ERROR --tag "AndroidRuntime"
```

### 6. 崩溃/ANR 调查

```
# 过滤崩溃日志
mcp__android__get_logs --level ERROR --tag "AndroidRuntime"

# 查看 ANR traces
mcp__android__adb_shell --command "cat /data/anr/traces.txt"

# 查看应用内存占用
mcp__android__adb_shell --command "dumpsys meminfo com.example.app"

# 检查当前 Activity 栈
mcp__android__adb_shell --command "dumpsys activity activities | grep -A 5 mCurrentFocus"
```

---

## 常见验证场景

### 登录流程验证

```
1. mcp__android__clear_logs
2. mcp__android__launch_app --package com.example.app
3. mcp__android__wait_for_element --resourceId com.example.app:id/et_email --timeout 3000
4. mcp__android__tap_element --resourceId com.example.app:id/et_email
5. mcp__android__type_text --text test@example.com
6. mcp__android__tap_element --resourceId com.example.app:id/et_password
7. mcp__android__type_text --text Password123
8. mcp__android__press_key --key HIDE_KEYBOARD
9. mcp__android__tap_and_wait --resourceId com.example.app:id/btn_login --waitFor com.example.app:id/fragment_home --timeout 5000
10. mcp__android__screenshot  ← 截图作为通过证据
11. mcp__android__get_logs --level ERROR ← 确认无错误日志
```

### 表单验证错误检查

```
1. 打开含表单的页面
2. 直接点击提交按钮（不填任何内容）
3. mcp__android__screenshot ← 截图确认错误提示显示
4. mcp__android__get_ui_tree ← 检查错误文字内容
5. 确认错误提示文本是否符合 PRD 描述
```

### 深色模式验证

```
# 切换系统深色模式
mcp__android__adb_shell --command "cmd uimode night yes"
mcp__android__screenshot

# 还原
mcp__android__adb_shell --command "cmd uimode night no"
```

### 权限授权检查

```
# 检查某个运行时权限状态
mcp__android__adb_shell --command "dumpsys package com.example.app | grep -A 1 CAMERA"

# 授予权限（用于测试环境）
mcp__android__adb_shell --command "pm grant com.example.app android.permission.CAMERA"

# 撤销权限（测试权限拒绝场景）
mcp__android__adb_shell --command "pm revoke com.example.app android.permission.CAMERA"
```

---

## 注意事项

| 场景 | 推荐做法 |
|------|----------|
| 元素找不到 | 先用 `get_ui_tree` 确认 resource-id，再用 `tap_element` |
| 异步加载 | 使用 `wait_for_element` 而非 `Thread.sleep` |
| 坐标点击 | 尽量用 resource-id，避免坐标（不同分辨率会失效）|
| 日志分析 | 操作前 `clear_logs`，操作后 `get_logs --level ERROR` |
| 截图证据 | 关键步骤前后各截一张图，形成操作链路记录 |
| 测试隔离 | 每个测试场景前重新 `launch_app`，或 `adb shell pm clear` 清除数据 |
