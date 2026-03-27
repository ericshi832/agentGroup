# How to Use the Android QA Skill

The Android QA skill helps Kyle test Android applications using unit tests, instrumented tests, Espresso/UIAutomator UI automation, and live device control via MCP Android tools.

## Basic Usage

### Verify a New Android Feature

```
@android-qa

Jarvis 刚完成登录功能，帮我验收：
- 项目路径：/Users/eric/Projects/MyApp
- APK：build/outputs/apk/debug/app-debug.apk
- 功能说明：用户输入邮箱+密码，点击登录按钮，成功后跳转到 MainActivity

请进行功能验收和代码审查。
```

### Generate Unit Tests

```
@android-qa

为以下 Kotlin 类生成 JUnit 单元测试：

文件：app/src/main/java/com/example/app/LoginViewModel.kt

需要覆盖：
- 邮箱格式验证
- 密码长度验证
- 登录成功/失败状态流
- 网络错误处理
```

### Analyze Coverage

```
@android-qa

分析测试覆盖率并找出缺口：

覆盖率报告：build/reports/jacoco/test/jacocoTestReport.xml
目标覆盖率：70%

重点关注 data 层和 domain 层的未覆盖路径。
```

### Live UI Testing with MCP

```
@android-qa

使用 MCP Android 工具测试注册流程：
- 设备已连接
- 包名：com.example.app
- 测试场景：完整注册流程（填写信息 → 提交 → 验证成功页面）
```

---

## Example Invocations

### Example 1: Full Feature Acceptance

```
@android-qa

请验收贾维斯完成的"购物车"功能：

代码路径：app/src/main/java/com/example/shop/cart/
PRD 需求：
1. 用户可以添加商品到购物车
2. 购物车显示商品数量和总价
3. 可以删除单个商品
4. 购物车为空时显示空状态页面

设备已连接，包名：com.example.shop
APK：build/outputs/apk/debug/app-debug.apk

请输出：1) 代码审查报告 2) UI 验收结果
```

### Example 2: Crash Investigation

```
@android-qa

用户反馈点击"提交订单"按钮偶发崩溃，帮我复现和分析：

设备：已连接（Pixel 7 API 34）
包名：com.example.shop
复现步骤：添加商品 → 进入购物车 → 点击提交订单

请：
1. 用 MCP 工具复现操作步骤
2. 抓取崩溃日志
3. 定位崩溃原因
4. 建议修复方向（由贾维斯实现）
```

### Example 3: Regression Test Suite

```
@android-qa

为以下核心流程生成 UIAutomator 回归测试套件：
- 启动 → 登录
- 登录 → 首页
- 首页 → 搜索商品
- 商品详情 → 加入购物车

AndroidManifest.xml 路径：app/src/main/AndroidManifest.xml
输出目录：app/src/androidTest/java/com/example/shop/regression/
```

### Example 4: Coverage Gap Report

```
@android-qa

生成详细覆盖率缺口报告：

JaCoCo 报告：build/reports/jacoco/test/jacocoTestReport.xml
重点模块：
- com.example.app.data.repository
- com.example.app.domain.usecase

按优先级（P0/P1/P2）输出缺失测试建议，并生成对应的测试桩代码。
```

### Example 5: MCP Screenshot Verification

```
@android-qa

截图验证"黑暗模式"下的 UI 显示：

设备已连接
包名：com.example.app
需要验证的页面：登录页、首页、个人中心页

请：
1. 切换系统到黑暗模式
2. 依次截图三个页面
3. 检查 UI 树中是否有文字截断或元素重叠问题
```

---

## What to Provide

### For Unit Test Generation
- Java 或 Kotlin 源文件路径（或粘贴代码）
- 类的职责说明（ViewModel/Repository/UseCase/Util）
- 需要覆盖的具体场景（可选）
- JUnit 版本偏好（4 或 5，默认 4）

### For Coverage Analysis
- JaCoCo XML 报告路径：`build/reports/jacoco/test/jacocoTestReport.xml`
- 目标覆盖率百分比（默认 70%）
- 重点关注的包或模块（可选）

### For UI Test Scaffolding
- `AndroidManifest.xml` 路径，或 Activity 类名列表
- 测试框架偏好：Espresso（白盒）或 UIAutomator（黑盒）
- 输出目录

### For MCP Live Testing
- 已连接的 Android 设备或运行中的模拟器
- 应用包名（`applicationId`）
- 测试场景描述，或具体操作步骤

---

## What You'll Get

### Unit Test Output
- 完整测试文件，包含 `@Before` 初始化、Mockito mock 声明、`@Test` 方法桩
- 覆盖正常流程、错误场景、边界值的测试结构
- 可直接编译运行的代码框架

### Coverage Analysis Output
- 按模块的覆盖率汇总（行/分支/方法）
- 按优先级排序的缺口清单（P0 关键路径优先）
- 具体到文件和行号的未覆盖代码定位
- 针对性的补测建议

### MCP Live Test Output
- 每步操作的截图证据
- UI 树状态快照（关键节点）
- 错误日志摘要（ERROR 级别 logcat）
- 验收结论：通过 / 需修改 / 不通过

### Acceptance Report Output
标准验收报告，存入 `../shared/reviews/`：
```
# 验收报告 - [功能名称]
结论：通过 / 需修改 / 不通过
## PRD 符合度（逐条验证）
## 代码审查结果（安全/性能/规范）
## UI 验证截图
## 发现问题（严重/一般/建议）
```

---

## Tips for Best Results

### Unit Test Generation
1. **说明类的职责**：告诉 Kyle 这是 ViewModel 还是 Repository，生成的 mock 会更准确
2. **提供依赖关系**：如果类依赖 `UserRepository` 和 `NetworkClient`，提前说明
3. **指定关键场景**："`loginWithWrongPassword` 应该返回 `Error.InvalidCredentials`"

### MCP Live Testing
1. **先确认设备连接**：`mcp__android__list_devices` 确认设备在线
2. **清空日志再测试**：`mcp__android__clear_logs` 避免旧日志干扰
3. **遇到崩溃立即抓日志**：崩溃后立即执行 `mcp__android__get_logs --level ERROR`

### Coverage Analysis
1. **先跑测试再分析**：确保 `./gradlew test jacocoTestReport` 已执行
2. **关注分支覆盖率**：Android 中 `if/else` 和 `when` 语句的分支比行覆盖率更重要
3. **优先覆盖数据层**：Repository 和 UseCase 是最高价值的测试目标

---

## Troubleshooting

**Issue**: MCP 工具报 "no devices connected"
- **Solution**: 运行 `mcp__android__list_devices` 确认设备状态；检查 USB 连接或模拟器是否启动

**Issue**: JaCoCo 报告为空或覆盖率全为 0%
- **Solution**: 确认 `build.gradle` 中已启用 `enableUnitTestCoverage true`；运行 `./gradlew clean test jacocoTestReport`

**Issue**: 生成的 Espresso 测试编译失败
- **Solution**: 确认 `app/build.gradle` 中已添加 Espresso 依赖；检查 `testInstrumentationRunner` 配置

**Issue**: `mcp__android__tap_element` 找不到元素
- **Solution**: 先执行 `mcp__android__get_ui_tree` 查看当前界面的 resource-id 和 text；使用 `mcp__android__wait_for_element` 等待异步加载完成

**Issue**: 生成的测试覆盖的是 Kotlin 但格式像 Java
- **Solution**: 明确告知 Kyle "项目使用 Kotlin"，脚本会切换到 Kotlin 语法模板

---

## Version Support

- **Android API Level**: 26+ (Android 8.0+)
- **Kotlin**: 1.9+
- **Java**: 11+
- **JUnit**: 4.13+ / 5.10+
- **Espresso**: 3.5+
- **UIAutomator**: 2.2+
- **Gradle**: 8.0+
