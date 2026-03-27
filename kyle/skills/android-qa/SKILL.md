---
name: android-qa
description: This skill should be used when the user asks to "test Android app", "write Espresso tests", "write UIAutomator tests", "analyze Android test coverage", "run Android UI tests", "test with MCP Android tools", "generate JUnit tests for Android", or "verify Android app behavior". Use for Android testing with JUnit, Espresso, UIAutomator, and MCP Android device control tools.
source: aiGroup团队定制
author: aiGroup团队
version: v1.0
license: MIT
triggers:
  - test Android
  - Android UI test
  - Espresso test
  - UIAutomator test
  - Android test coverage
  - JaCoCo
  - Android instrumented test
  - MCP Android
  - verify Android app
  - Android smoke test
---

# Android QA Engineer

Android application testing skill covering unit tests, instrumented tests, UI automation via Espresso/UIAutomator, and live device interaction via MCP Android tools.

## Table of Contents

- [Capabilities](#capabilities)
- [Workflows](#workflows)
- [Tools](#tools)
- [MCP Android Tools](#mcp-android-tools)
- [Input Requirements](#input-requirements)
- [Limitations](#limitations)

---

## Capabilities

| Capability | Description |
|------------|-------------|
| Unit Test Generation | Generate JUnit 4/5 + Mockito test stubs from Java/Kotlin source |
| Instrumented Test Generation | Generate AndroidJUnit4 instrumented test stubs |
| UI Test Scaffolding | Generate Espresso and UIAutomator test files from Activity/Fragment list |
| Coverage Analysis | Parse JaCoCo XML/HTML reports, identify gaps, prioritize fixes |
| Live Device Testing | Control real device or emulator via MCP Android tools |
| Logcat Analysis | Capture and analyze crash logs and ANR traces |
| Screenshot Verification | Capture and compare UI screenshots for regression detection |

---

## Workflows

### Unit Test Generation

1. Provide source code (Java or Kotlin)
2. Specify target class or package
3. Run `test_suite_generator.py` to generate JUnit stubs
4. Review and complete test assertions
5. **Validation:** Tests compile and cover happy path, error cases, edge cases

### Coverage Gap Analysis

1. Build project with JaCoCo: `./gradlew test jacocoTestReport`
2. Run `coverage_analyzer.py` on `build/reports/jacoco/test/jacocoTestReport.xml`
3. Review prioritized gaps (P0/P1/P2)
4. Generate missing tests for uncovered paths
5. **Validation:** Coverage meets target threshold (typically 70%+)

### UI Test with MCP Android Tools

1. Launch app on device/emulator: `mcp__android__launch_app`
2. Capture UI tree: `mcp__android__get_ui_tree`
3. Interact with elements: `mcp__android__tap_element`, `mcp__android__type_text`
4. Capture screenshots: `mcp__android__screenshot`
5. Verify logcat for errors: `mcp__android__get_logs`
6. **Validation:** All target flows complete without crash or ANR

### Espresso/UIAutomator Test Scaffolding

1. Provide Activity/Fragment list or AndroidManifest.xml path
2. Run `ui_test_scaffolder.py` to generate test file stubs
3. Review generated tests in `app/src/androidTest/`
4. Run on device: `./gradlew connectedAndroidTest`
5. **Validation:** All instrumented tests pass on target API level

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `test_suite_generator.py` | Generate JUnit/Mockito unit test stubs from Java/Kotlin source | `python scripts/test_suite_generator.py src/main/java/com/app/ --output src/test/java/` |
| `coverage_analyzer.py` | Parse JaCoCo XML reports, identify gaps, enforce thresholds | `python scripts/coverage_analyzer.py build/reports/jacoco/test/jacocoTestReport.xml --threshold 70` |
| `ui_test_scaffolder.py` | Scaffold Espresso/UIAutomator tests from Activity list | `python scripts/ui_test_scaffolder.py --manifest app/src/main/AndroidManifest.xml --output src/androidTest/` |

---

## MCP Android Tools

MCP Android tools allow Kyle to directly control a connected Android device or emulator for live UI verification. No Espresso setup required for exploratory testing.

### Device Setup

```
# List connected devices
mcp__android__list_devices

# Get device info
mcp__android__get_device_info

# Install APK for testing
mcp__android__install_apk --path build/outputs/apk/debug/app-debug.apk
```

### App Interaction

```
# Launch app by package name
mcp__android__launch_app --package com.example.app

# Get current Activity name
mcp__android__get_current_activity

# Get full UI accessibility tree
mcp__android__get_ui_tree

# Tap an element by resource-id or text
mcp__android__tap_element --resourceId "com.example.app:id/btn_login"

# Type text into focused field
mcp__android__type_text --text "test@example.com"

# Press system key (BACK, HOME, ENTER)
mcp__android__press_key --key BACK

# Swipe gesture
mcp__android__swipe --startX 500 --startY 1000 --endX 500 --endY 300

# Scroll to element
mcp__android__scroll_to_element --text "Submit"

# Wait for element to appear
mcp__android__wait_for_element --resourceId "com.example.app:id/tv_result" --timeout 5000
```

### Verification

```
# Capture screenshot
mcp__android__screenshot

# Get logcat output (filter by tag or level)
mcp__android__get_logs --tag "MyApp" --level ERROR

# Clear logcat buffer before test
mcp__android__clear_logs

# Run ADB shell command
mcp__android__adb_shell --command "dumpsys activity activities | grep mCurrentFocus"
```

---

## Input Requirements

**For Unit Test Generation:**
- Java or Kotlin source files (file path or pasted content)
- Class type: ViewModel, Repository, UseCase, Util, etc.
- Dependencies to mock (optional)

**For Coverage Analysis:**
- JaCoCo XML report: `build/reports/jacoco/test/jacocoTestReport.xml`
- Target coverage threshold (default: 70%)

**For UI Test Scaffolding:**
- AndroidManifest.xml path, or list of Activity/Fragment class names
- Target test type: Espresso (white-box) or UIAutomator (black-box)

**For MCP Live Testing:**
- Connected device or running emulator
- App package name and entry Activity
- Test scenario description

---

## Limitations

| Scope | Details |
|-------|---------|
| Language support | Java and Kotlin only |
| Unit test scope | Logic-layer classes; Android framework classes require Robolectric or instrumented tests |
| MCP tools | Require connected device or running emulator; cannot run on CI without device farm |
| Generated tests | Provide scaffolding; require human review for business logic assertions |
| Performance testing | Use Android Profiler or Macrobenchmark for performance; out of scope here |
| Screenshot comparison | MCP captures screenshots; pixel-diff comparison requires external tooling |

**When to use other tools:**
- Performance benchmarks: Macrobenchmark, Android Profiler
- Network mocking: OkHttp MockWebServer, WireMock
- Security scanning: MobSF, QARK
