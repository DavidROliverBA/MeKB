#!/usr/bin/env python3
"""
File Protection Hook for Claude Code
Blocks edits to sensitive files.

Hook Type: PreToolUse
Matcher: Edit|Write
Exit Codes:
  0 - Success (file is safe to edit)
  1 - Error (non-blocking)
  2 - Block (protected file)
"""

import json
import re
import sys

# Files and paths to protect
PROTECTED_PATHS = [
    # Environment files
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",

    # Lock files
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Gemfile.lock",
    "poetry.lock",
    "Cargo.lock",

    # Version control
    ".git/",

    # Credentials directories
    ".aws/",
    ".ssh/",
    ".gnupg/",

    # Common secret files
    "credentials",
    "credentials.json",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    ".secrets",

    # Private keys and certificates
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",

    # Token files
    ".npmrc",
    ".pypirc",
    ".netrc",

    # Local configuration with secrets
    "config.local.json",
]

# Sensitive keywords in filenames - block creation of files containing these
SENSITIVE_FILENAME_KEYWORDS = [
    "api key",
    "apikey",
    "api-key",
    "api_key",
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "private key",
    "privatekey",
]

# Keywords that must match as whole words only
SENSITIVE_WHOLE_WORD_KEYWORDS = [
    "pin",
    "pat",
]

# Files that are allowed exceptions to the sensitive keyword rule
ALLOWED_EXCEPTIONS = [
    ".secrets.baseline",
    ".pre-commit-config.yaml",
    "secret-detection.py",
    "secret-file-scanner.py",
    "secret-scanner.py",
    "classification-guard.py",
]

# Directories where sensitive keywords in filenames are allowed
ALLOWED_DIRECTORIES = [
    ".claude/skills/",
    ".claude/rules/",
    ".claude/hooks/",
    ".claude/scripts/",
]

# File prefixes that are allowed (notes about security concepts, not actual secrets)
ALLOWED_PREFIXES = [
    "Decision - ",
    "Concept - ",
    "Note - ",
    "Resource - ",
]


def is_protected(file_path: str) -> tuple[bool, str]:
    """Check if file path matches any protected pattern."""
    from pathlib import Path

    path_parts = Path(file_path).parts
    filename = Path(file_path).name
    filename_lower = filename.lower()

    if filename in ALLOWED_EXCEPTIONS:
        return False, ""

    for allowed_dir in ALLOWED_DIRECTORIES:
        if allowed_dir in file_path:
            return False, ""

    for prefix in ALLOWED_PREFIXES:
        if filename.startswith(prefix):
            return False, ""

    for protected in PROTECTED_PATHS:
        if protected.startswith("*"):
            if file_path.endswith(protected[1:]):
                return True, f"Protected file type: {protected}"
        elif protected.endswith("/"):
            dir_name = protected[:-1]
            if dir_name in path_parts:
                return True, f"Protected directory: {protected}"
        else:
            if filename == protected or file_path.endswith("/" + protected):
                return True, f"Protected file: {protected}"

    for keyword in SENSITIVE_FILENAME_KEYWORDS:
        if keyword in filename_lower:
            return True, f"Sensitive keyword in filename: '{keyword}'"

    for keyword in SENSITIVE_WHOLE_WORD_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', filename_lower):
            return True, f"Sensitive keyword in filename: '{keyword}'"

    return False, ""


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input or not raw_input.strip():
            sys.exit(0)
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, ValueError, EOFError):
        sys.exit(0)
    except Exception:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    file_path = input_data.get("tool_input", {}).get("file_path", "")

    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    if not file_path:
        sys.exit(0)

    is_blocked, reason = is_protected(file_path)

    if is_blocked:
        output = {
            "decision": "block",
            "reason": f"🛡️ {reason}\nFile: {file_path}\nUse --force or edit manually if you really need to modify this file."
        }
        print(json.dumps(output))
        sys.exit(0)

    if any(kw in file_path.lower() for kw in ["config", "settings", "setup"]):
        output = {
            "additionalContext": f"Note: {file_path} may contain configuration. Ensure no secrets are included."
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
