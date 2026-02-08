#!/usr/bin/env python3
"""
Secret Detection Script for MeKB
Scans files for potential secrets before commit.
"""

import json
import re
import sys
from pathlib import Path

# Secret patterns with descriptions
SECRET_PATTERNS = [
    {
        "name": "AWS Access Key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "high"
    },
    {
        "name": "AWS Secret Key",
        "pattern": r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})",
        "severity": "high"
    },
    {
        "name": "GitHub Token",
        "pattern": r"gh[pousr]_[A-Za-z0-9_]{36,}",
        "severity": "high"
    },
    {
        "name": "GitHub Personal Access Token (classic)",
        "pattern": r"ghp_[A-Za-z0-9]{36}",
        "severity": "high"
    },
    {
        "name": "Generic API Key",
        "pattern": r"(?i)(api[_\-]?key|apikey)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})",
        "severity": "medium"
    },
    {
        "name": "Generic Secret",
        "pattern": r"(?i)(secret|secret[_\-]?key)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})",
        "severity": "medium"
    },
    {
        "name": "Password Assignment",
        "pattern": r"(?i)(password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?([^\s'\"]{8,})",
        "severity": "high"
    },
    {
        "name": "Bearer Token",
        "pattern": r"(?i)bearer\s+[A-Za-z0-9_\-\.]+",
        "severity": "high"
    },
    {
        "name": "Private Key",
        "pattern": r"-----BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----",
        "severity": "critical"
    },
    {
        "name": "SSH Private Key",
        "pattern": r"-----BEGIN OPENSSH PRIVATE KEY-----",
        "severity": "critical"
    },
    {
        "name": "Connection String",
        "pattern": r"(?i)(mongodb|postgres|mysql|redis|amqp):\/\/[^\s]+:[^\s]+@",
        "severity": "high"
    },
    {
        "name": "Slack Token",
        "pattern": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}",
        "severity": "high"
    },
    {
        "name": "Stripe API Key",
        "pattern": r"sk_live_[0-9a-zA-Z]{24}",
        "severity": "high"
    },
    {
        "name": "Azure Storage Key",
        "pattern": r"(?i)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+",
        "severity": "high"
    },
    {
        "name": "Google API Key",
        "pattern": r"AIza[0-9A-Za-z_-]{35}",
        "severity": "high"
    },
    {
        "name": "Anthropic API Key",
        "pattern": r"sk-ant-[A-Za-z0-9_-]{40,}",
        "severity": "high"
    },
    {
        "name": "OpenAI API Key",
        "pattern": r"sk-[A-Za-z0-9]{48}",
        "severity": "high"
    },
    {
        "name": "JWT Token",
        "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
        "severity": "medium"
    },
    {
        "name": "High Entropy String (potential secret)",
        "pattern": r"['\"][A-Za-z0-9+/=]{40,}['\"]",
        "severity": "low"
    }
]

# Files/patterns to ignore
IGNORE_PATTERNS = [
    r"\.git/",
    r"node_modules/",
    r"\.secrets\.baseline$",
    r"package-lock\.json$",
    r"\.png$",
    r"\.jpg$",
    r"\.jpeg$",
    r"\.gif$",
    r"\.pdf$",
    r"\.ico$"
]

# Known false positives (add patterns here)
FALSE_POSITIVES = [
    r"example",
    r"placeholder",
    r"your[_-]?api[_-]?key",
    r"<.*>",
    r"\{\{.*\}\}",
    r"xxxx",
    r"test",
    r"dummy",
    r"sample",
    r"-----BEGIN AGE ENCRYPTED FILE-----",
]


def should_ignore_file(file_path):
    """Check if file should be ignored."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, str(file_path), re.IGNORECASE):
            return True
    return False


def is_false_positive(match_text):
    """Check if match is a known false positive."""
    for pattern in FALSE_POSITIVES:
        if re.search(pattern, match_text, re.IGNORECASE):
            return True
    return False


def scan_file(file_path):
    """Scan a single file for secrets."""
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError):
        return findings

    for pattern_info in SECRET_PATTERNS:
        pattern = pattern_info["pattern"]
        name = pattern_info["name"]
        severity = pattern_info["severity"]

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                match_text = match.group(0)

                # Skip false positives
                if is_false_positive(match_text):
                    continue

                # Truncate for display
                display_text = match_text[:50] + "..." if len(match_text) > 50 else match_text

                findings.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": name,
                    "severity": severity,
                    "match": display_text
                })

    return findings


def scan_files(file_list):
    """Scan multiple files for secrets."""
    all_findings = []

    for file_path in file_list:
        if should_ignore_file(file_path):
            continue

        path = Path(file_path)
        if not path.exists() or not path.is_file():
            continue

        findings = scan_file(path)
        all_findings.extend(findings)

    return all_findings


def scan_directory(directory="."):
    """Scan all files in a directory."""
    all_findings = []

    for path in Path(directory).rglob("*"):
        if path.is_file() and not should_ignore_file(path):
            findings = scan_file(path)
            all_findings.extend(findings)

    return all_findings


def format_findings(findings):
    """Format findings for display."""
    if not findings:
        return "✅ No secrets detected.\n"

    output = []
    output.append(f"🚨 SECRETS DETECTED: {len(findings)} potential secret(s) found\n")
    output.append("=" * 60)

    # Group by severity
    by_severity = {"critical": [], "high": [], "medium": [], "low": []}
    for f in findings:
        by_severity[f["severity"]].append(f)

    severity_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "⚪"
    }

    for severity in ["critical", "high", "medium", "low"]:
        if by_severity[severity]:
            output.append(f"\n{severity_icons[severity]} {severity.upper()} ({len(by_severity[severity])})")
            for f in by_severity[severity]:
                output.append(f"  {f['file']}:{f['line']}")
                output.append(f"    Type: {f['type']}")
                output.append(f"    Match: {f['match']}")

    output.append("\n" + "=" * 60)
    output.append("\n⚠️  DO NOT COMMIT THESE FILES")
    output.append("Remove secrets and use environment variables or a secrets manager.")
    output.append("\nTo bypass (NOT RECOMMENDED): git commit --no-verify")

    return "\n".join(output)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect secrets in files")
    parser.add_argument("files", nargs="*", help="Files to scan")
    parser.add_argument("--directory", "-d", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--baseline", help="Baseline file for known secrets")

    args = parser.parse_args()

    if args.directory:
        findings = scan_directory(args.directory)
    elif args.files:
        findings = scan_files(args.files)
    else:
        # Read file list from stdin (for pre-commit)
        files = [line.strip() for line in sys.stdin if line.strip()]
        if files:
            findings = scan_files(files)
        else:
            findings = scan_directory(".")

    # Filter against baseline if provided
    if args.baseline and Path(args.baseline).exists():
        try:
            with open(args.baseline) as f:
                baseline = json.load(f)
            baseline_keys = set(baseline.get("allowed", []))
            findings = [f for f in findings if f"{f['file']}:{f['line']}:{f['type']}" not in baseline_keys]
        except (json.JSONDecodeError, IOError):
            pass

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(format_findings(findings))

    # Exit with error if secrets found (for pre-commit)
    if findings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
