#!/usr/bin/env python3
"""
Android JaCoCo Coverage Analyzer
Parses JaCoCo XML reports and identifies testing gaps with prioritized recommendations.

Usage:
    python coverage_analyzer.py <jacoco-xml-report> [options]

Options:
    --threshold N     Minimum line coverage percentage (default: 70)
    --strict          Exit with error if below threshold
    --format FORMAT   Output format: text, json, html (default: text)
    --output FILE     Output file path
"""

import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field


# ─── Data models ─────────────────────────────────────────────────────────────

@dataclass
class CounterStats:
    missed: int = 0
    covered: int = 0

    @property
    def total(self) -> int:
        return self.missed + self.covered

    @property
    def pct(self) -> float:
        return (self.covered / self.total * 100) if self.total > 0 else 0.0


@dataclass
class ClassCoverage:
    name: str
    package: str
    line: CounterStats = field(default_factory=CounterStats)
    branch: CounterStats = field(default_factory=CounterStats)
    method: CounterStats = field(default_factory=CounterStats)

    @property
    def priority(self) -> str:
        """P0 = critical business logic, P1 = important, P2 = nice to have."""
        critical_keywords = ["auth", "login", "payment", "order", "cart",
                             "repository", "usecase", "interactor", "network", "api"]
        name_lower = self.name.lower()
        if any(kw in name_lower for kw in critical_keywords):
            return "P0"
        if self.line.pct < 30:
            return "P0"
        if self.line.pct < 60:
            return "P1"
        return "P2"


@dataclass
class PackageCoverage:
    name: str
    classes: list[ClassCoverage] = field(default_factory=list)

    @property
    def line(self) -> CounterStats:
        stats = CounterStats()
        for c in self.classes:
            stats.missed += c.line.missed
            stats.covered += c.line.covered
        return stats

    @property
    def branch(self) -> CounterStats:
        stats = CounterStats()
        for c in self.classes:
            stats.missed += c.branch.missed
            stats.covered += c.branch.covered
        return stats


# ─── XML parsing ─────────────────────────────────────────────────────────────

def parse_counter(element, counter_type: str) -> CounterStats:
    for counter in element.findall("counter"):
        if counter.get("type") == counter_type:
            return CounterStats(
                missed=int(counter.get("missed", 0)),
                covered=int(counter.get("covered", 0)),
            )
    return CounterStats()


def parse_jacoco_xml(xml_path: Path) -> tuple[list[PackageCoverage], CounterStats, CounterStats]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    packages = []
    for pkg_elem in root.findall("package"):
        pkg_name = pkg_elem.get("name", "").replace("/", ".")
        pkg = PackageCoverage(name=pkg_name)

        for cls_elem in pkg_elem.findall("class"):
            cls_name = Path(cls_elem.get("name", "")).name
            if cls_name.endswith("Kt"):
                cls_name = cls_name[:-2]  # strip Kotlin file suffix

            cls = ClassCoverage(
                name=cls_name,
                package=pkg_name,
                line=parse_counter(cls_elem, "LINE"),
                branch=parse_counter(cls_elem, "BRANCH"),
                method=parse_counter(cls_elem, "METHOD"),
            )
            pkg.classes.append(cls)

        packages.append(pkg)

    overall_line = parse_counter(root, "LINE")
    overall_branch = parse_counter(root, "BRANCH")
    return packages, overall_line, overall_branch


# ─── Report rendering ─────────────────────────────────────────────────────────

def bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def status_icon(pct: float, threshold: float) -> str:
    if pct >= threshold:
        return "✅"
    if pct >= threshold * 0.8:
        return "⚠️"
    return "❌"


def render_text(packages: list[PackageCoverage], overall_line: CounterStats,
                overall_branch: CounterStats, threshold: float) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  Android Coverage Analysis Report")
    lines.append("=" * 60)
    lines.append(f"\nOverall Line Coverage: {overall_line.pct:.1f}% (target: {threshold}%)")
    lines.append(f"  {bar(overall_line.pct)} {overall_line.covered}/{overall_line.total} lines")
    lines.append(f"\nOverall Branch Coverage: {overall_branch.pct:.1f}%")
    lines.append(f"  {bar(overall_branch.pct)} {overall_branch.covered}/{overall_branch.total} branches")

    # Gaps by priority
    all_classes = [cls for pkg in packages for cls in pkg.classes]
    uncovered = [c for c in all_classes if c.line.pct < threshold]
    uncovered.sort(key=lambda c: c.line.pct)

    p0 = [c for c in uncovered if c.priority == "P0"]
    p1 = [c for c in uncovered if c.priority == "P1"]
    p2 = [c for c in uncovered if c.priority == "P2"]

    if p0:
        lines.append(f"\n🔴 P0 - Critical Gaps ({len(p0)} classes):")
        for c in p0[:10]:
            lines.append(f"  {c.package}.{c.name}: {c.line.pct:.1f}% lines, {c.branch.pct:.1f}% branches")

    if p1:
        lines.append(f"\n🟡 P1 - Important Gaps ({len(p1)} classes):")
        for c in p1[:8]:
            lines.append(f"  {c.package}.{c.name}: {c.line.pct:.1f}% lines")

    if p2:
        lines.append(f"\n🟢 P2 - Minor Gaps ({len(p2)} classes, showing top 5):")
        for c in p2[:5]:
            lines.append(f"  {c.package}.{c.name}: {c.line.pct:.1f}% lines")

    # Package summary
    lines.append("\nPackage Summary:")
    lines.append(f"  {'Package':<45} {'Line':>7} {'Branch':>9}")
    lines.append("  " + "-" * 63)
    for pkg in sorted(packages, key=lambda p: p.line.pct):
        icon = status_icon(pkg.line.pct, threshold)
        lines.append(f"  {icon} {pkg.name:<43} {pkg.line.pct:>5.1f}%  {pkg.branch.pct:>6.1f}%")

    # Recommendations
    lines.append("\nRecommendations:")
    if p0:
        lines.append(f"  1. [URGENT] Add tests for {len(p0)} P0 classes (critical business logic)")
        for c in p0[:3]:
            lines.append(f"     - {c.name}: focus on error handling and edge cases")
    if overall_branch.pct < threshold * 0.9:
        lines.append(f"  2. Branch coverage is low ({overall_branch.pct:.1f}%). "
                     "Add tests for if/else and when branches.")
    if len(uncovered) > 10:
        lines.append(f"  3. {len(uncovered)} classes below threshold. "
                     "Run test_suite_generator.py --scan-only to prioritize.")

    lines.append("\n" + "=" * 60)
    verdict = "PASS" if overall_line.pct >= threshold else "FAIL"
    lines.append(f"  Result: {verdict} ({overall_line.pct:.1f}% / {threshold}% threshold)")
    lines.append("=" * 60)
    return "\n".join(lines)


def render_json(packages: list[PackageCoverage], overall_line: CounterStats,
                overall_branch: CounterStats, threshold: float) -> str:
    all_classes = [cls for pkg in packages for cls in pkg.classes]
    gaps = [
        {
            "class": f"{c.package}.{c.name}",
            "priority": c.priority,
            "line_pct": round(c.line.pct, 1),
            "branch_pct": round(c.branch.pct, 1),
        }
        for c in all_classes if c.line.pct < threshold
    ]
    gaps.sort(key=lambda g: g["line_pct"])

    report = {
        "overall": {
            "line_pct": round(overall_line.pct, 1),
            "branch_pct": round(overall_branch.pct, 1),
            "threshold": threshold,
            "pass": overall_line.pct >= threshold,
        },
        "gaps": gaps,
        "package_summary": [
            {
                "package": pkg.name,
                "line_pct": round(pkg.line.pct, 1),
                "branch_pct": round(pkg.branch.pct, 1),
            }
            for pkg in packages
        ],
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Android JaCoCo Coverage Analyzer")
    parser.add_argument("report", help="Path to jacocoTestReport.xml")
    parser.add_argument("--threshold", type=float, default=70.0)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    xml_path = Path(args.report)
    if not xml_path.exists():
        print(f"[ERROR] Report not found: {xml_path}", file=sys.stderr)
        print("Hint: Run './gradlew test jacocoTestReport' first", file=sys.stderr)
        sys.exit(1)

    try:
        packages, overall_line, overall_branch = parse_jacoco_xml(xml_path)
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse XML: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = render_json(packages, overall_line, overall_branch, args.threshold)
    else:
        output = render_text(packages, overall_line, overall_branch, args.threshold)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(output)

    if args.strict and overall_line.pct < args.threshold:
        sys.exit(1)


if __name__ == "__main__":
    main()
