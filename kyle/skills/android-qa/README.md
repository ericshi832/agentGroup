# Android QA Engineer Skill

Production-ready Android testing skill covering unit tests, instrumented tests, UI automation, and live device control via MCP Android tools.

## Tech Stack Focus

| Category | Technologies |
|----------|--------------|
| Unit Testing | JUnit 4/5, Mockito, Robolectric |
| Instrumented Testing | AndroidJUnit4, Espresso, UIAutomator 2 |
| Coverage | JaCoCo (XML/HTML) |
| Live Device Control | MCP Android Tools |
| Build | Gradle, Android SDK |

## Quick Start

```bash
# Generate unit test stubs for a package
python scripts/test_suite_generator.py app/src/main/java/com/example/app/ --output app/src/test/java/

# Analyze JaCoCo coverage report
python scripts/coverage_analyzer.py build/reports/jacoco/test/jacocoTestReport.xml --threshold 70

# Scaffold Espresso tests from AndroidManifest
python scripts/ui_test_scaffolder.py --manifest app/src/main/AndroidManifest.xml --output app/src/androidTest/java/
```

## Scripts

### test_suite_generator.py

Scans Java/Kotlin source files and generates JUnit + Mockito test stubs with proper structure.

**Features:**
- Detects ViewModel, Repository, UseCase, and Util classes
- Generates `@Before` setup, `@Test` stubs, and Mockito mocks
- Supports both JUnit 4 (`@RunWith(JUnit4.class)`) and JUnit 5 (`@ExtendWith`)
- Optional `--robolectric` flag for Android framework classes

**Usage:**
```bash
python scripts/test_suite_generator.py <source-dir> [options]

Options:
  --output DIR        Output directory for test files (mirrors source structure)
  --framework junit4  Use JUnit 4 annotations (default)
  --framework junit5  Use JUnit 5 annotations
  --robolectric       Add @RunWith(RobolectricTestRunner.class)
  --scan-only         List classes without generating test files
```

### coverage_analyzer.py

Parses JaCoCo XML coverage reports and identifies testing gaps with prioritized recommendations.

**Features:**
- Parses `jacocoTestReport.xml` (line, branch, method, class coverage)
- Identifies critical untested paths (auth, payment, network, data layer)
- Generates text and HTML summary reports
- Threshold enforcement with `--strict` flag (exits non-zero if below threshold)

**Usage:**
```bash
python scripts/coverage_analyzer.py <jacoco-xml-report> [options]

Options:
  --threshold N     Minimum line coverage percentage (default: 70)
  --strict          Exit with error if below threshold
  --format FORMAT   Output format: text, json, html (default: text)
  --output FILE     Output file path
```

### ui_test_scaffolder.py

Reads AndroidManifest.xml and generates Espresso or UIAutomator test file stubs for each Activity.

**Features:**
- Parses `AndroidManifest.xml` to discover all Activity entries
- Generates `@RunWith(AndroidJUnit4.class)` instrumented test stubs
- Supports Espresso (white-box, with `ActivityScenarioRule`) and UIAutomator 2 (black-box)
- Generates common interaction patterns: launch, click, type, assert visible

**Usage:**
```bash
python scripts/ui_test_scaffolder.py [options]

Options:
  --manifest PATH     Path to AndroidManifest.xml
  --framework espresso     Generate Espresso tests (default)
  --framework uiautomator  Generate UIAutomator 2 tests
  --output DIR        Output directory for androidTest files
  --package NAME      Override test package name
```

## Workflows

### Workflow 1: Unit Test Coverage for New Feature

1. Identify new classes added by Jarvis in `app/src/main/java/`
2. Run `test_suite_generator.py` to generate test stubs
3. Fill in assertions based on expected behavior
4. Run `./gradlew test` to verify tests pass
5. Run `./gradlew jacocoTestReport` and check with `coverage_analyzer.py`

### Workflow 2: UI Verification with MCP Tools (No Code Required)

1. Connect device or start emulator
2. Install debug APK: `mcp__android__install_apk`
3. Launch app: `mcp__android__launch_app`
4. Navigate via `mcp__android__tap_element`, `mcp__android__type_text`, `mcp__android__swipe`
5. Verify UI state via `mcp__android__get_ui_tree` and `mcp__android__screenshot`
6. Check for errors via `mcp__android__get_logs --level ERROR`

### Workflow 3: Regression Testing

1. Install new build APK
2. Execute critical user flows using MCP tools
3. Screenshot key screens and compare with baseline
4. Run `./gradlew connectedAndroidTest` for instrumented test suite
5. Collect JaCoCo coverage delta if enabled

### Workflow 4: Crash Investigation

1. Reproduce issue via MCP tools
2. Capture logcat: `mcp__android__get_logs --level ERROR --tag "AndroidRuntime"`
3. Identify stack trace
4. Write regression unit test targeting the failing code path
5. Confirm fix with Jarvis

## Test Pyramid Targets (Android)

| Test Type | Ratio | Tools |
|-----------|-------|-------|
| Unit | 70% | JUnit, Mockito, Robolectric |
| Integration | 20% | AndroidJUnit4, Espresso |
| E2E / UI | 10% | UIAutomator 2, MCP Android |

## Coverage Targets

| Project Type | Line | Branch | Method |
|--------------|------|--------|--------|
| MVP | 50% | 40% | 60% |
| Production | 70% | 60% | 75% |
| Enterprise | 85% | 75% | 90% |

## Gradle Setup Reference

```groovy
// app/build.gradle
android {
    defaultConfig {
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes {
        debug {
            enableUnitTestCoverage true
            enableAndroidTestCoverage true
        }
    }
}

dependencies {
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.mockito:mockito-core:5.7.0'
    testImplementation 'org.robolectric:robolectric:4.11.1'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    androidTestImplementation 'androidx.test.uiautomator:uiautomator:2.2.0'
}
```

## CI/CD Integration

```yaml
# .github/workflows/android-test.yml
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Run unit tests with coverage
        run: ./gradlew test jacocoTestReport
      - name: Check coverage threshold
        run: python kyle/skills/android-qa/scripts/coverage_analyzer.py \
               build/reports/jacoco/test/jacocoTestReport.xml \
               --threshold 70 --strict

  instrumented-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | \
          sudo tee /etc/udev/rules.d/99-kvm4all.rules
      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          script: ./gradlew connectedAndroidTest
```

## Related Skills

- **tdd-guide** - TDD workflow with Red-Green-Refactor cycle
- **senior-qa** - React/Next.js web testing counterpart
- **engineering-team** - Full Android development (Jarvis)

---

**Version:** 1.0.0
**Last Updated:** March 2026
**Tech Focus:** Android API 26+, JUnit 4/5, Espresso 3.5+, UIAutomator 2, MCP Android Tools
