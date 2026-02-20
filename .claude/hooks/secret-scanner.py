#!/usr/bin/env python3
"""
Secret Scanner Hook for Claude Code
Scans file content during Edit/Write operations for potential secrets.

Hook Type: PreToolUse (matcher: Edit|Write)
Exit Codes:
  0 - Content is safe
  2 - Blocked: potential secret detected

Reads tool input JSON from stdin. Checks the content being written
against common credential patterns. Blocks the operation if a match
is found, preventing secrets from being written to disk.
"""

import json
import re
import sys

# Patterns that indicate potential secrets — same library as scripts/detect-secrets.py
SECRET_PATTERNS = [
    (r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+", "password"),
    (r"(?i)\b(secret|api_?secret)\s*[:=]\s*\S+", "secret"),
    (r"(?i)\b(api_?key|apikey)\s*[:=]\s*\S+", "API key"),
    (r"(?i)\b(token|auth_?token|access_?token)\s*[:=]\s*\S+", "token"),
    (r"(?i)\b(private_?key)\s*[:=]\s*\S+", "private key"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API key"),
    (r"sk-ant-[a-zA-Z0-9-]{20,}", "Anthropic API key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub server token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
    (r"(?i)aws_secret_access_key\s*[:=]\s*\S+", "AWS secret key"),
    (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}", "Slack token"),
    (r"sk_live_[0-9a-zA-Z]{24}", "Stripe API key"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API key"),
    (r"-----BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----", "Private key header"),
    (r"(?i)(mongodb|postgres|mysql|redis|amqp):\/\/[^\s]+:[^\s]+@", "Connection string"),
    (r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}", "Bearer token"),
    (r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "JWT token"),
]

# Paths where security discussion is expected (avoid false positives)
DOCUMENTATION_PATHS = [
    "SECURITY.md",
    "docs/",
    "CLAUDE.md",
    ".claude/",
    "scripts/detect-secrets.py",
]

# Known false positive patterns
FALSE_POSITIVES = [
    r"example",
    r"placeholder",
    r"your[_-]?key",
    r"your[_-]?token",
    r"<.*>",
    r"\{\{.*\}\}",
    r"xxxx",
    r"test",
    r"dummy",
    r"sample",
]


def is_documentation_file(file_path: str) -> bool:
    """Check if the file is documentation that may legitimately discuss secrets."""
    for doc_path in DOCUMENTATION_PATHS:
        if doc_path in file_path:
            return True
    return False


def is_false_positive(match_text: str) -> bool:
    """Check if a match is a known false positive."""
    for pattern in FALSE_POSITIVES:
        if re.search(pattern, match_text, re.IGNORECASE):
            return True
    return False


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check Edit and Write operations
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    # Get the file path and content
    file_path = tool_input.get("file_path", "")
    content = ""

    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        content = " ".join(e.get("new_string", "") for e in edits)

    if not content:
        sys.exit(0)

    # Skip documentation files (they discuss security concepts)
    if is_documentation_file(file_path):
        sys.exit(0)

    # Scan for secrets
    findings = []
    for pattern, name in SECRET_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            match_text = match.group(0)
            if not is_false_positive(match_text):
                findings.append(name)

    if findings:
        counts = {}
        for f in findings:
            counts[f] = counts.get(f, 0) + 1

        summary = ", ".join(f"{name} ({count}x)" for name, count in counts.items())

        print(
            json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "decision": {
                        "behavior": "block",
                        "message": f"Potential secrets detected in file content: {summary}. "
                        "Remove credentials before writing. Use a secrets manager instead."
                    }
                }
            })
        )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
