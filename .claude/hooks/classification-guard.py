#!/usr/bin/env python3
"""
Classification Guard Hook for MeKB
Protects classified files from AI access based on security configuration.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Find vault root (directory containing .mekb/)
def find_vault_root():
    """Find the MeKB vault root by looking for .mekb directory."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".mekb").is_dir():
            return parent
        if (parent / "CLAUDE.md").exists():
            return parent
    return current

VAULT_ROOT = find_vault_root()
CONFIG_FILE = VAULT_ROOT / ".mekb" / "security.json"
STATE_DIR = Path.home() / ".claude"
LOG_FILE = VAULT_ROOT / ".mekb" / "access-log.jsonl"

# Default configuration
DEFAULT_CONFIG = {
    "ai_access_control": {
        "enabled": True,
        "mode": "interactive",
        "levels": {
            "public": "allow",
            "personal": "allow",
            "confidential": "ask",
            "secret": "block"
        },
        "write_protection": True,
        "remember_session": True,
        "log_access_attempts": True
    },
    "trusted_ai_providers": {
        "enabled": False,
        "providers": ["bedrock", "local"],
        "trust_level": {
            "bedrock": "confidential",
            "local": "secret"
        }
    },
    "folder_inheritance": {
        "enabled": True,
        "folders": {
            "confidential/": "confidential",
            "secret/": "secret",
            "private/": "confidential"
        }
    }
}


def load_config():
    """Load security configuration."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG


def get_state_file(session_id):
    """Get session-specific state file path."""
    return STATE_DIR / f"mekb_access_state_{session_id}.json"


def load_session_state(session_id):
    """Load remembered access decisions for this session."""
    state_file = get_state_file(session_id)
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"allowed": [], "denied": []}


def save_session_state(session_id, state):
    """Save access decisions for this session."""
    state_file = get_state_file(session_id)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w") as f:
            json.dump(state, f)
    except IOError:
        pass


def log_access(file_path, classification, action, mode):
    """Log access attempt."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": str(file_path),
            "classification": classification,
            "action": action,
            "mode": mode
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except IOError:
        pass


def extract_classification(file_path):
    """Extract classification from file frontmatter."""
    try:
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = VAULT_ROOT / file_path

        if not full_path.exists():
            return None

        if not full_path.suffix == ".md":
            return None

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(4096)  # Read first 4KB

        # Check for YAML frontmatter
        if not content.startswith("---"):
            return None

        # Find end of frontmatter
        end_match = content.find("\n---", 3)
        if end_match == -1:
            return None

        frontmatter = content[3:end_match]

        # Extract classification
        match = re.search(r'^classification:\s*(\w+)', frontmatter, re.MULTILINE)
        if match:
            return match.group(1).lower()

        return None
    except (IOError, UnicodeDecodeError):
        return None


def get_folder_classification(file_path, config):
    """Check if file is in a classified folder."""
    if not config.get("folder_inheritance", {}).get("enabled", False):
        return None

    folders = config.get("folder_inheritance", {}).get("folders", {})
    file_str = str(file_path)

    for folder, classification in folders.items():
        if folder in file_str or file_str.startswith(folder):
            return classification

    return None


def get_ai_provider():
    """Detect current AI provider from environment."""
    if os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1":
        return "bedrock"
    if os.environ.get("CLAUDE_LOCAL") == "1":
        return "local"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "api"
    return "consumer"


def check_trusted_provider(classification, config):
    """Check if current provider is trusted for this classification level."""
    trust_config = config.get("trusted_ai_providers", {})
    if not trust_config.get("enabled", False):
        return False

    provider = get_ai_provider()
    trust_levels = trust_config.get("trust_level", {})

    if provider not in trust_levels:
        return False

    provider_trust = trust_levels[provider]

    # Define classification hierarchy
    hierarchy = ["public", "personal", "confidential", "secret"]

    try:
        classification_idx = hierarchy.index(classification)
        trust_idx = hierarchy.index(provider_trust)
        return classification_idx <= trust_idx
    except ValueError:
        return False


def prompt_user(file_path, classification):
    """Prompt user for access decision."""
    print(f"\n⚠️  CLASSIFICATION CHECK", file=sys.stderr)
    print(f"File: {file_path}", file=sys.stderr)
    print(f"Level: {classification.upper()}", file=sys.stderr)
    print(f"\nThis file is marked {classification.upper()}.", file=sys.stderr)
    print(f"Allow AI to access this file? [y/N]: ", file=sys.stderr, end="")

    # Note: In actual hook execution, we can't easily prompt interactively
    # So we default to deny and instruct user to whitelist
    return False


def main():
    """Main hook function."""
    config = load_config()

    # Check if AI access control is enabled
    if not config.get("ai_access_control", {}).get("enabled", True):
        sys.exit(0)

    # Read input from stdin
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)  # Allow if can't parse

    session_id = input_data.get("session_id", "default")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Determine if this is a read or write operation
    read_tools = ["Read", "Grep", "Glob"]
    write_tools = ["Write", "Edit", "MultiEdit"]

    is_read = tool_name in read_tools
    is_write = tool_name in write_tools

    if not is_read and not is_write:
        sys.exit(0)

    # Check write protection
    if is_write and not config.get("ai_access_control", {}).get("write_protection", True):
        # Write protection disabled, only check reads
        if not is_read:
            sys.exit(0)

    # Extract file path
    file_path = tool_input.get("file_path", "")
    if not file_path:
        # For Grep/Glob, check the path parameter
        file_path = tool_input.get("path", "")

    if not file_path:
        sys.exit(0)

    # Get classification (from frontmatter or folder)
    classification = extract_classification(file_path)
    if classification is None:
        classification = get_folder_classification(file_path, config)
    if classification is None:
        classification = "personal"  # Default

    # Get access rule for this classification
    levels = config.get("ai_access_control", {}).get("levels", {})
    rule = levels.get(classification, "allow")

    # Check if trusted provider overrides
    if rule in ["ask", "block"] and check_trusted_provider(classification, config):
        rule = "allow"

    mode = config.get("ai_access_control", {}).get("mode", "interactive")

    # Load session state for "ask" decisions
    session_state = load_session_state(session_id)

    # Check if we've already decided for this file
    if file_path in session_state.get("allowed", []):
        rule = "allow"
    elif file_path in session_state.get("denied", []):
        rule = "block"

    # Apply rule
    if rule == "allow":
        if config.get("ai_access_control", {}).get("log_access_attempts", False):
            log_access(file_path, classification, "allowed", mode)
        sys.exit(0)

    elif rule == "block":
        if config.get("ai_access_control", {}).get("log_access_attempts", False):
            log_access(file_path, classification, "blocked", mode)

        action = "read" if is_read else "write to"
        print(f"\n🚫 ACCESS DENIED", file=sys.stderr)
        print(f"File: {file_path}", file=sys.stderr)
        print(f"Classification: {classification.upper()}", file=sys.stderr)
        print(f"\nAI access is blocked for {classification} files.", file=sys.stderr)
        print(f"To allow access:", file=sys.stderr)
        print(f"  1. Change the file's classification, or", file=sys.stderr)
        print(f"  2. Update .mekb/security.json", file=sys.stderr)
        sys.exit(2)

    elif rule == "ask":
        if mode == "strict":
            # In strict mode, "ask" becomes "block"
            if config.get("ai_access_control", {}).get("log_access_attempts", False):
                log_access(file_path, classification, "blocked", "strict")
            print(f"\n🚫 ACCESS DENIED (strict mode)", file=sys.stderr)
            print(f"File: {file_path}", file=sys.stderr)
            print(f"Classification: {classification.upper()}", file=sys.stderr)
            sys.exit(2)
        else:
            # Interactive mode - block but with guidance
            if config.get("ai_access_control", {}).get("log_access_attempts", False):
                log_access(file_path, classification, "prompted", mode)

            print(f"\n⚠️  CLASSIFICATION CHECK", file=sys.stderr)
            print(f"File: {file_path}", file=sys.stderr)
            print(f"Classification: {classification.upper()}", file=sys.stderr)
            print(f"\nThis file is marked {classification.upper()}.", file=sys.stderr)
            print(f"AI access requires explicit approval.", file=sys.stderr)
            print(f"\nTo allow access for this session, run:", file=sys.stderr)
            print(f"  claude --allow-file \"{file_path}\"", file=sys.stderr)
            print(f"\nOr update .mekb/security.json to change the rule.", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
