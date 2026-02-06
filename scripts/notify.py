#!/usr/bin/env python3
"""
Notification system for MeKB.
Send notifications via multiple backends with graceful fallbacks.

Usage:
    python3 scripts/notify.py "Title" "Message"                # Auto-detect best backend
    python3 scripts/notify.py "Title" "Message" --backend desktop  # macOS notification
    python3 scripts/notify.py "Title" "Message" --backend slack    # Slack webhook
    python3 scripts/notify.py "Title" "Message" --backend discord  # Discord webhook
    python3 scripts/notify.py "Title" "Message" --backend email    # Email via SMTP
    python3 scripts/notify.py --test                               # Test all configured backends
    python3 scripts/notify.py --list                               # List available backends

Dependencies: Python 3.9+ (stdlib only)
Optional: Slack/Discord webhook URLs, SMTP config in .mekb/notifications.yaml
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def load_config(vault_root):
    """Load notification config from .mekb/notifications.yaml."""
    config_path = vault_root / ".mekb" / "notifications.yaml"
    if not config_path.exists():
        return {}

    # Simple YAML parser (no pyyaml dependency)
    config = {}
    current_section = None
    content = config_path.read_text()

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not line.startswith(" ") and stripped.endswith(":"):
            current_section = stripped[:-1]
            config[current_section] = {}
        elif current_section and ":" in stripped:
            key, _, value = stripped.partition(":")
            value = value.strip().strip("\"'")
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.lower() == "null" or value == "":
                value = None
            config[current_section][key.strip()] = value

    return config


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------

def send_desktop(title, message, sound=True):
    """Send macOS desktop notification via osascript."""
    if platform.system() != "Darwin":
        raise RuntimeError("Desktop notifications only supported on macOS")

    # Escape quotes for AppleScript
    title_escaped = title.replace('"', '\\"')
    message_escaped = message.replace('"', '\\"')

    script = f'display notification "{message_escaped}" with title "{title_escaped}"'
    if sound:
        script += ' sound name "default"'

    subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
    return True


def send_slack(title, message, webhook_url):
    """Send Slack notification via webhook."""
    if not webhook_url:
        raise ValueError("Slack webhook URL not configured")

    payload = {
        "text": f"*{title}*\n{message}",
        "unfurl_links": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status == 200


def send_discord(title, message, webhook_url):
    """Send Discord notification via webhook."""
    if not webhook_url:
        raise ValueError("Discord webhook URL not configured")

    payload = {
        "content": f"**{title}**\n{message}",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status == 204 or resp.status == 200


def send_email(title, message, config):
    """Send email via SMTP."""
    import smtplib
    from email.mime.text import MIMEText

    smtp_host = config.get("smtp_host", "localhost")
    smtp_port = int(config.get("smtp_port", 587))
    smtp_user = config.get("smtp_user")
    smtp_pass = config.get("smtp_pass")
    from_addr = config.get("from", smtp_user)
    to_addr = config.get("to")

    if not to_addr:
        raise ValueError("Email 'to' address not configured")

    msg = MIMEText(message)
    msg["Subject"] = f"[MeKB] {title}"
    msg["From"] = from_addr or "mekb@localhost"
    msg["To"] = to_addr

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_port == 587:
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    return True


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

BACKENDS = {
    "desktop": {"name": "Desktop (macOS)", "platforms": ["Darwin"]},
    "slack": {"name": "Slack Webhook", "platforms": ["any"]},
    "discord": {"name": "Discord Webhook", "platforms": ["any"]},
    "email": {"name": "Email (SMTP)", "platforms": ["any"]},
}


def detect_backends(config):
    """Detect which backends are available."""
    available = []
    system = platform.system()

    if system == "Darwin":
        available.append("desktop")

    if config.get("slack", {}).get("webhook_url"):
        available.append("slack")

    if config.get("discord", {}).get("webhook_url"):
        available.append("discord")

    if config.get("email", {}).get("to"):
        available.append("email")

    return available


def send_notification(title, message, backend=None, config=None):
    """Send notification via specified or auto-detected backend."""
    if config is None:
        config = {}

    if backend is None:
        available = detect_backends(config)
        if not available:
            print("No notification backends configured.", file=sys.stderr)
            print("Create .mekb/notifications.yaml or use --backend desktop", file=sys.stderr)
            return False
        backend = available[0]

    try:
        if backend == "desktop":
            return send_desktop(title, message)
        elif backend == "slack":
            webhook = config.get("slack", {}).get("webhook_url")
            return send_slack(title, message, webhook)
        elif backend == "discord":
            webhook = config.get("discord", {}).get("webhook_url")
            return send_discord(title, message, webhook)
        elif backend == "email":
            email_config = config.get("email", {})
            return send_email(title, message, email_config)
        else:
            print(f"Unknown backend: {backend}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Notification failed ({backend}): {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_test(config):
    """Test all configured backends."""
    available = detect_backends(config)
    if not available:
        print("No backends configured.")
        print("\nCreate .mekb/notifications.yaml with your notification settings.")
        print("Or use: python3 scripts/notify.py 'Test' 'Hello' --backend desktop")
        return

    print(f"Testing {len(available)} backend(s)...\n")
    for backend in available:
        try:
            ok = send_notification(
                "MeKB Test",
                f"Notification test from MeKB ({backend})",
                backend=backend,
                config=config,
            )
            status = "OK" if ok else "FAILED"
            print(f"  {BACKENDS[backend]['name']:<25} {status}")
        except Exception as e:
            print(f"  {BACKENDS[backend]['name']:<25} ERROR: {e}")


def cmd_list(config):
    """List all backends and their status."""
    available = detect_backends(config)
    system = platform.system()

    print("\nNotification Backends\n")
    print(f"  {'Backend':<25} {'Status':<12} {'Notes'}")
    print(f"  {'-'*25} {'-'*12} {'-'*30}")

    for key, info in BACKENDS.items():
        is_available = key in available
        status = "Available" if is_available else "Not configured"

        notes = ""
        if key == "desktop" and system != "Darwin":
            status = "Unavailable"
            notes = "macOS only"
        elif key == "slack" and not is_available:
            notes = "Set slack.webhook_url"
        elif key == "discord" and not is_available:
            notes = "Set discord.webhook_url"
        elif key == "email" and not is_available:
            notes = "Set email.to"

        print(f"  {info['name']:<25} {status:<12} {notes}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MeKB notification system")
    parser.add_argument("title", nargs="?", help="Notification title")
    parser.add_argument("message", nargs="?", help="Notification message")
    parser.add_argument("--backend", choices=list(BACKENDS.keys()),
                       help="Notification backend")
    parser.add_argument("--test", action="store_true",
                       help="Test all configured backends")
    parser.add_argument("--list", action="store_true",
                       help="List available backends")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    config = load_config(vault_root)

    if args.test:
        cmd_test(config)
    elif args.list:
        cmd_list(config)
    elif args.title and args.message:
        ok = send_notification(args.title, args.message, backend=args.backend, config=config)
        if ok:
            print(f"Notification sent ({args.backend or 'auto'})")
        else:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
