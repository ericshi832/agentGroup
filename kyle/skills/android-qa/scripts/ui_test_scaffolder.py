#!/usr/bin/env python3
"""
Android UI Test Scaffolder
Reads AndroidManifest.xml and generates Espresso or UIAutomator 2 test stubs.

Usage:
    python ui_test_scaffolder.py --manifest <path> [options]

Options:
    --manifest PATH       Path to AndroidManifest.xml
    --framework           espresso (default) or uiautomator
    --output DIR          Output directory for androidTest files
    --package NAME        Override test package name
    --activities LIST     Comma-separated Activity class names (alternative to manifest)
"""

import re
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


# ─── Manifest parsing ─────────────────────────────────────────────────────────

def parse_manifest(manifest_path: Path) -> tuple[str, list[dict]]:
    """Returns (app_package, list of activity info dicts)."""
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    app_package = root.get("package", "com.example.app")
    ns = "http://schemas.android.com/apk/res/android"

    activities = []
    for activity in root.findall(f".//activity"):
        name = activity.get(f"{{{ns}}}name", "")
        if not name:
            continue
        # Resolve relative names (e.g., ".MainActivity" → "com.example.app.MainActivity")
        if name.startswith("."):
            name = app_package + name
        elif "." not in name:
            name = f"{app_package}.{name}"

        exported = activity.get(f"{{{ns}}}exported", "false").lower() == "true"
        label = activity.get(f"{{{ns}}}label", "")

        # Check for LAUNCHER intent filter
        is_launcher = any(
            action.get(f"{{{ns}}}name") == "android.intent.action.MAIN"
            for action in activity.findall(f".//action")
        )

        activities.append({
            "full_name": name,
            "simple_name": name.split(".")[-1],
            "package": ".".join(name.split(".")[:-1]),
            "exported": exported,
            "is_launcher": is_launcher,
            "label": label,
        })

    return app_package, activities


# ─── Espresso template ────────────────────────────────────────────────────────

def render_espresso(activity: dict, test_package: str) -> str:
    simple = activity["simple_name"]
    pkg = activity["package"]
    return f"""package {test_package}

import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import {pkg}.{simple}

/**
 * Espresso instrumented tests for [{simple}].
 *
 * Run with: ./gradlew connectedAndroidTest
 */
@RunWith(AndroidJUnit4::class)
class {simple}Test {{

    private lateinit var scenario: ActivityScenario<{simple}>

    @Before
    fun setUp() {{
        scenario = ActivityScenario.launch({simple}::class.java)
    }}

    @After
    fun tearDown() {{
        scenario.close()
    }}

    @Test
    fun activityLaunches_displaysCorrectly() {{
        // Verify the activity starts without crashing and shows expected root view
        onView(isRoot()).check(matches(isDisplayed()))
        // TODO: verify specific views are visible, e.g.:
        // onView(withId(R.id.tv_title)).check(matches(isDisplayed()))
    }}

    @Test
    fun primaryAction_completesSuccessfully() {{
        // TODO: Identify the primary action on this screen (e.g., button click, form submit)
        // onView(withId(R.id.btn_primary)).perform(click())
        // onView(withId(R.id.tv_result)).check(matches(withText("Expected result")))
        TODO("implement primary action test")
    }}

    @Test
    fun inputValidation_showsErrorOnInvalidInput() {{
        // TODO: Test invalid input scenarios if this screen has forms
        // onView(withId(R.id.et_email)).perform(typeText("invalid"))
        // onView(withId(R.id.btn_submit)).perform(click())
        // onView(withId(R.id.til_email)).check(matches(hasDescendant(withText("Invalid email"))))
        TODO("implement validation test if applicable")
    }}

    @Test
    fun backNavigation_returnsToParent() {{
        // TODO: Verify back navigation works correctly
        // pressBack()
        // Verify parent screen is shown
        TODO("implement back navigation test if applicable")
    }}
}}
"""


# ─── UIAutomator template ─────────────────────────────────────────────────────

def render_uiautomator(activity: dict, app_package: str, test_package: str) -> str:
    simple = activity["simple_name"]
    return f"""package {test_package}

import android.content.Context
import android.content.Intent
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiSelector
import androidx.test.uiautomator.Until
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.assertNotNull

private const val APP_PACKAGE = "{app_package}"
private const val LAUNCH_TIMEOUT = 5_000L

/**
 * UIAutomator 2 black-box tests for [{simple}].
 *
 * Run with: ./gradlew connectedAndroidTest
 */
@RunWith(AndroidJUnit4::class)
class {simple}UiTest {{

    private lateinit var device: UiDevice

    @Before
    fun setUp() {{
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())

        // Start from home screen
        device.pressHome()

        // Launch app
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = context.packageManager.getLaunchIntentForPackage(APP_PACKAGE)
            ?.apply {{ addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK) }}
        context.startActivity(intent)

        // Wait for app to appear
        device.wait(Until.hasObject(By.pkg(APP_PACKAGE).depth(0)), LAUNCH_TIMEOUT)
    }}

    @Test
    fun appLaunches_packageIsVisible() {{
        val appWindow = device.findObject(UiSelector().packageName(APP_PACKAGE))
        assertNotNull("App window should be visible", appWindow)
    }}

    @Test
    fun primaryFlow_completesWithoutCrash() {{
        // TODO: Implement primary user flow using UiDevice interactions
        // val button = device.findObject(UiSelector().resourceId("$APP_PACKAGE:id/btn_primary"))
        // button.click()
        // device.wait(Until.hasObject(By.res(APP_PACKAGE, "tv_result")), 3_000L)
        TODO("implement primary flow test")
    }}

    @Test
    fun screenRotation_preservesState() {{
        // TODO: Test screen rotation if activity handles configuration changes
        // device.setOrientationLeft()
        // Thread.sleep(500)
        // verify state is preserved
        // device.setOrientationNatural()
        TODO("implement rotation test if applicable")
    }}
}}
"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Android UI Test Scaffolder")
    parser.add_argument("--manifest", help="Path to AndroidManifest.xml")
    parser.add_argument("--activities", help="Comma-separated Activity class names")
    parser.add_argument("--framework", choices=["espresso", "uiautomator"], default="espresso")
    parser.add_argument("--output", default="androidTest_generated", help="Output directory")
    parser.add_argument("--package", dest="test_package", help="Override test package name")
    args = parser.parse_args()

    if not args.manifest and not args.activities:
        parser.error("Provide --manifest or --activities")

    output_dir = Path(args.output)

    # Resolve activities
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
            sys.exit(1)
        app_package, activities = parse_manifest(manifest_path)
    else:
        app_package = "com.example.app"
        activities = [
            {
                "full_name": name.strip(),
                "simple_name": name.strip().split(".")[-1],
                "package": ".".join(name.strip().split(".")[:-1]) or app_package,
                "exported": True,
                "is_launcher": False,
                "label": "",
            }
            for name in args.activities.split(",")
        ]

    if not activities:
        print("[WARN] No activities found.")
        sys.exit(0)

    test_package = args.test_package or f"{app_package}.test.ui"

    print(f"\nScanning: {args.manifest or 'provided activity list'}")
    print(f"Found {len(activities)} activities")
    print(f"Framework: {args.framework}")
    print(f"Output: {output_dir}/\n")

    generated = []
    for activity in activities:
        if args.framework == "uiautomator":
            content = render_uiautomator(activity, app_package, test_package)
            filename = f"{activity['simple_name']}UiTest.kt"
        else:
            content = render_espresso(activity, test_package)
            filename = f"{activity['simple_name']}Test.kt"

        out_file = output_dir / filename
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")

        launcher_tag = " [LAUNCHER]" if activity.get("is_launcher") else ""
        print(f"  {out_file}{launcher_tag}")
        generated.append(str(out_file))

    print(f"\nGenerated: {len(generated)} test files")
    print(f"Run with: ./gradlew connectedAndroidTest")


if __name__ == "__main__":
    main()
