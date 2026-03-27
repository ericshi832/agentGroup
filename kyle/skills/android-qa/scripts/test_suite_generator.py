#!/usr/bin/env python3
"""
Android Unit Test Suite Generator
Scans Java/Kotlin source files and generates JUnit + Mockito test stubs.

Usage:
    python test_suite_generator.py <source-dir> [options]

Options:
    --output DIR        Output directory for test files
    --framework         junit4 (default) or junit5
    --robolectric       Add RobolectricTestRunner annotation
    --scan-only         List classes without generating files
"""

import os
import re
import sys
import argparse
from pathlib import Path


# ─── Class type detection ────────────────────────────────────────────────────

CLASS_PATTERNS = {
    "ViewModel": [
        r"class\s+\w+\s*:\s*\w*ViewModel",
        r"class\s+\w+ViewModel",
    ],
    "Repository": [
        r"class\s+\w+Repository",
        r"class\s+\w+\s*:\s*\w*Repository",
    ],
    "UseCase": [
        r"class\s+\w+UseCase",
        r"class\s+\w+Interactor",
    ],
    "Util": [
        r"object\s+\w+(Util|Helper|Extensions|Ext)",
        r"class\s+\w+(Util|Helper)",
    ],
    "Activity": [
        r"class\s+\w+Activity\s*:",
        r"class\s+\w+Activity\b",
    ],
    "Fragment": [
        r"class\s+\w+Fragment\s*:",
        r"class\s+\w+Fragment\b",
    ],
    "Service": [
        r"class\s+\w+Service\s*:",
    ],
    "Generic": [],  # fallback
}

DEPENDENCY_PATTERN = re.compile(
    r"(?:constructor|fun\s+\w+)\s*\([^)]*\b(\w+(?:Repository|Service|Client|Manager|DataSource|Dao))\b"
)

KOTLIN_FUN_PATTERN = re.compile(r"(?:fun\s+)(\w+)\s*\(")
JAVA_METHOD_PATTERN = re.compile(
    r"(?:public|protected|private|internal)\s+\w[\w<>?,\s]*\s+(\w+)\s*\("
)


# ─── Template rendering ───────────────────────────────────────────────────────

def detect_class_type(content: str) -> str:
    for class_type, patterns in CLASS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content):
                return class_type
    return "Generic"


def detect_dependencies(content: str) -> list[str]:
    return list(set(DEPENDENCY_PATTERN.findall(content)))


def detect_public_methods(content: str, is_kotlin: bool) -> list[str]:
    pattern = KOTLIN_FUN_PATTERN if is_kotlin else JAVA_METHOD_PATTERN
    methods = pattern.findall(content)
    # Filter out constructors and common noise
    excluded = {"init", "toString", "hashCode", "equals", "copy", "invoke"}
    return [m for m in methods if m not in excluded][:10]  # cap at 10


def render_junit4_kotlin(class_name: str, package: str, class_type: str,
                          dependencies: list[str], methods: list[str],
                          robolectric: bool) -> str:
    runner = "RobolectricTestRunner::class" if robolectric else "JUnit4::class"
    runner_import = (
        "import org.robolectric.RobolectricTestRunner\n"
        if robolectric
        else "import org.junit.runner.RunWith\n"
    )
    mock_fields = "\n".join(
        f"    @Mock private lateinit var {dep[0].lower() + dep[1:]}: {dep}"
        for dep in dependencies
    )
    test_methods = "\n\n".join(
        f"    @Test\n    fun `{method} should TODO`() {{\n        // Arrange\n\n        // Act\n\n        // Assert\n        TODO(\"implement test\")\n    }}"
        for method in methods
    ) or "    @Test\n    fun `initial state should be correct`() {\n        TODO(\"implement test\")\n    }"

    return f"""package {package}

import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
{runner_import}import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever
import com.google.common.truth.Truth.assertThat

@RunWith({runner})
class {class_name}Test {{

{mock_fields if mock_fields else "    // TODO: add @Mock fields for dependencies"}

    private lateinit var sut: {class_name}

    @Before
    fun setUp() {{
        MockitoAnnotations.openMocks(this)
        sut = {class_name}(
            {", ".join(dep[0].lower() + dep[1:] for dep in dependencies) or "/* TODO: pass dependencies */"}
        )
    }}

{test_methods}
}}
"""


def render_junit5_kotlin(class_name: str, package: str, class_type: str,
                          dependencies: list[str], methods: list[str]) -> str:
    mock_fields = "\n".join(
        f"    private val {dep[0].lower() + dep[1:]}: {dep} = mock()"
        for dep in dependencies
    )
    test_methods = "\n\n".join(
        f"    @Test\n    fun `{method} should TODO`() {{\n        // Arrange\n\n        // Act\n\n        // Assert\n        TODO(\"implement test\")\n    }}"
        for method in methods
    ) or "    @Test\n    fun `initial state should be correct`() {\n        TODO(\"implement test\")\n    }"

    return f"""package {package}

import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import com.google.common.truth.Truth.assertThat

@ExtendWith(MockitoExtension::class)
class {class_name}Test {{

{mock_fields if mock_fields else "    // TODO: add mock fields for dependencies"}

    private lateinit var sut: {class_name}

    @BeforeEach
    fun setUp() {{
        sut = {class_name}(
            {", ".join(dep[0].lower() + dep[1:] for dep in dependencies) or "/* TODO: pass dependencies */"}
        )
    }}

{test_methods}
}}
"""


def render_junit4_java(class_name: str, package: str,
                        dependencies: list[str], methods: list[str]) -> str:
    mock_fields = "\n".join(
        f"    @Mock private {dep} {dep[0].lower() + dep[1:]};"
        for dep in dependencies
    )
    test_methods = "\n\n".join(
        f"    @Test\n    public void {method}_shouldTODO() {{\n        // Arrange\n\n        // Act\n\n        // Assert\n        // TODO: implement test\n    }}"
        for method in methods
    ) or "    @Test\n    public void initialState_shouldBeCorrect() {\n        // TODO: implement test\n    }"

    return f"""package {package};

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import static org.mockito.Mockito.*;
import static com.google.common.truth.Truth.assertThat;

@RunWith(JUnit4.class)
public class {class_name}Test {{

{mock_fields if mock_fields else "    // TODO: add @Mock fields for dependencies"}

    private {class_name} sut;

    @Before
    public void setUp() {{
        MockitoAnnotations.openMocks(this);
        sut = new {class_name}(
            {", ".join(dep[0].lower() + dep[1:] for dep in dependencies) or "/* TODO: pass dependencies */"}
        );
    }}

{test_methods}
}}
"""


# ─── File discovery and processing ───────────────────────────────────────────

def extract_package(content: str) -> str:
    match = re.search(r"^package\s+([\w.]+)", content, re.MULTILINE)
    return match.group(1) if match else "com.example.test"


def extract_class_name(file_path: Path) -> str:
    return file_path.stem


def process_file(source_file: Path, output_dir: Path, framework: str,
                 robolectric: bool, scan_only: bool) -> dict:
    content = source_file.read_text(encoding="utf-8")
    is_kotlin = source_file.suffix == ".kt"
    class_name = extract_class_name(source_file)
    package = extract_package(content) + ".test"
    class_type = detect_class_type(content)
    dependencies = detect_dependencies(content)
    methods = detect_public_methods(content, is_kotlin)

    result = {
        "file": str(source_file),
        "class": class_name,
        "type": class_type,
        "dependencies": dependencies,
        "methods": methods,
        "generated": False,
    }

    if scan_only:
        return result

    # Render test content
    if is_kotlin and framework == "junit5":
        test_content = render_junit5_kotlin(class_name, package, class_type, dependencies, methods)
    elif is_kotlin:
        test_content = render_junit4_kotlin(class_name, package, class_type, dependencies, methods, robolectric)
    else:
        test_content = render_junit4_java(class_name, package, dependencies, methods)

    # Mirror source structure under output_dir
    test_file = output_dir / source_file.with_name(f"{class_name}Test{source_file.suffix}").name
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(test_content, encoding="utf-8")
    result["generated"] = True
    result["output"] = str(test_file)
    return result


def should_skip(file_path: Path) -> bool:
    name = file_path.stem
    # Skip test files, generated files, and non-testable classes
    skip_patterns = ["Test", "Spec", "Mock", "Fake", "Stub", "Generated",
                     "Binding", "BR", "R", "BuildConfig"]
    return any(name.endswith(p) or name == p for p in skip_patterns)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Android Unit Test Suite Generator")
    parser.add_argument("source_dir", help="Source directory to scan")
    parser.add_argument("--output", default="generated_tests", help="Output directory")
    parser.add_argument("--framework", choices=["junit4", "junit5"], default="junit4")
    parser.add_argument("--robolectric", action="store_true")
    parser.add_argument("--scan-only", action="store_true")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"[ERROR] Source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    source_files = [
        f for f in source_dir.rglob("*")
        if f.suffix in (".kt", ".java") and not should_skip(f)
    ]

    if not source_files:
        print("[WARN] No Java/Kotlin source files found.")
        sys.exit(0)

    results = []
    for source_file in source_files:
        try:
            result = process_file(source_file, output_dir, args.framework,
                                   args.robolectric, args.scan_only)
            results.append(result)
        except Exception as e:
            print(f"[WARN] Skipping {source_file}: {e}")

    # Summary
    print(f"\nScanning: {source_dir}")
    print(f"Found {len(results)} source files\n")

    if args.scan_only:
        for r in results:
            print(f"  {r['class']} ({r['type']}) — {len(r['methods'])} methods, deps: {r['dependencies'] or 'none'}")
    else:
        generated = [r for r in results if r.get("generated")]
        print("Generated tests:")
        for r in generated:
            print(f"  {r['output']}  ({r['type']}, {len(r['methods'])} test methods)")
        print(f"\nSummary: {len(generated)}/{len(results)} files generated")
        if not args.scan_only:
            print(f"Output: {output_dir}/")


if __name__ == "__main__":
    main()
