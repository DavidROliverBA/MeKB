#!/usr/bin/env python3
"""
Scheduling Manager for MeKB
Manages scheduled maintenance jobs using platform-native tools.

Usage:
    python3 scripts/schedule.py list                # Show available jobs
    python3 scripts/schedule.py install              # Install all scheduled jobs
    python3 scripts/schedule.py install rebuild-index # Install specific job
    python3 scripts/schedule.py uninstall             # Remove all scheduled jobs
    python3 scripts/schedule.py status               # Show active jobs
    python3 scripts/schedule.py run <job>            # Run a job now

Platforms:
    macOS: Uses launchd (~/Library/LaunchAgents/com.mekb.*)
    Linux: Uses crontab

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Job definitions
JOBS = {
    "rebuild-index": {
        "description": "Rebuild SQLite FTS5 search index",
        "command": "python3 scripts/build-index.py",
        "schedule": "daily",
        "time": "06:00",
        "day": None,
    },
    "rebuild-graph": {
        "description": "Rebuild knowledge graph",
        "command": "python3 scripts/build-graph.py",
        "schedule": "daily",
        "time": "06:05",
        "day": None,
    },
    "rebuild-embeddings": {
        "description": "Rebuild vector embeddings (requires sentence-transformers)",
        "command": "python3 scripts/build-embeddings.py",
        "schedule": "weekly",
        "time": "06:10",
        "day": "Sunday",
    },
    "stale-check": {
        "description": "Check for stale notes needing review",
        "command": "python3 scripts/stale-check.py --summary",
        "schedule": "weekly",
        "time": "09:00",
        "day": "Friday",
    },
}

LABEL_PREFIX = "com.mekb"
DAY_MAP = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
           "Friday": 5, "Saturday": 6, "Sunday": 7}


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def is_macos():
    return platform.system() == "Darwin"


def is_linux():
    return platform.system() == "Linux"


def get_python():
    """Get the Python 3 executable path."""
    return shutil.which("python3") or sys.executable


def get_launch_agents_dir():
    """Get the LaunchAgents directory for macOS."""
    return Path.home() / "Library" / "LaunchAgents"


def generate_plist(job_name, job, vault_root):
    """Generate a macOS launchd plist for a job."""
    label = f"{LABEL_PREFIX}.{job_name}"
    python = get_python()
    script = str(vault_root / job["command"].split(" ", 1)[1])
    script_args = job["command"].split(" ")[2:] if len(job["command"].split(" ")) > 2 else []
    hour, minute = job["time"].split(":")
    log_dir = vault_root / ".mekb" / "logs"

    # Build program arguments
    args_xml = f"        <string>{python}</string>\n"
    args_xml += f"        <string>{script}</string>\n"
    for arg in script_args:
        args_xml += f"        <string>{arg}</string>\n"

    # Build calendar interval
    if job["schedule"] == "daily":
        calendar = f"""        <dict>
            <key>Hour</key>
            <integer>{int(hour)}</integer>
            <key>Minute</key>
            <integer>{int(minute)}</integer>
        </dict>"""
    elif job["schedule"] == "weekly":
        weekday = DAY_MAP.get(job.get("day", "Sunday"), 7)
        calendar = f"""        <dict>
            <key>Weekday</key>
            <integer>{weekday}</integer>
            <key>Hour</key>
            <integer>{int(hour)}</integer>
            <key>Minute</key>
            <integer>{int(minute)}</integer>
        </dict>"""
    else:
        calendar = ""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml.rstrip()}
    </array>
    <key>WorkingDirectory</key>
    <string>{vault_root}</string>
    <key>StartCalendarInterval</key>
{calendar}
    <key>StandardOutPath</key>
    <string>{log_dir}/{job_name}.log</string>
    <key>StandardErrorPath</key>
    <string>{log_dir}/{job_name}.error.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""


def generate_crontab_entry(job_name, job, vault_root):
    """Generate a crontab entry for a job."""
    python = get_python()
    hour, minute = job["time"].split(":")
    log_dir = vault_root / ".mekb" / "logs"

    if job["schedule"] == "daily":
        schedule = f"{minute} {hour} * * *"
    elif job["schedule"] == "weekly":
        weekday = DAY_MAP.get(job.get("day", "Sunday"), 0)
        # Crontab uses 0=Sunday
        cron_day = weekday % 7
        schedule = f"{minute} {hour} * * {cron_day}"
    else:
        return ""

    cmd = f"cd {vault_root} && {python} {job['command'].split(' ', 1)[1]}"
    return f"{schedule} {cmd} >> {log_dir}/{job_name}.log 2>&1 # mekb:{job_name}"


def install_macos(jobs_to_install, vault_root):
    """Install launchd jobs on macOS."""
    agents_dir = get_launch_agents_dir()
    agents_dir.mkdir(parents=True, exist_ok=True)
    log_dir = vault_root / ".mekb" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    for name, job in JOBS.items():
        if jobs_to_install and name not in jobs_to_install:
            continue

        label = f"{LABEL_PREFIX}.{name}"
        plist_path = agents_dir / f"{label}.plist"
        plist_content = generate_plist(name, job, vault_root)

        # Unload existing if present
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)],
                         capture_output=True)

        plist_path.write_text(plist_content)

        # Load the job
        result = subprocess.run(["launchctl", "load", str(plist_path)],
                              capture_output=True, text=True)
        if result.returncode == 0:
            installed.append(name)
            print(f"  Installed: {name} ({job['schedule']} at {job['time']})")
        else:
            print(f"  Failed: {name} - {result.stderr.strip()}")

    if installed:
        print(f"\n{len(installed)} job(s) installed.")
        print("\nNote: macOS TCC restrictions may block scheduled scripts.")
        print("If jobs fail, grant Full Disk Access to the terminal app in")
        print("System Settings > Privacy & Security > Full Disk Access.")


def install_linux(jobs_to_install, vault_root):
    """Install crontab entries on Linux."""
    log_dir = vault_root / ".mekb" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Read existing crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Remove existing mekb entries
    lines = [l for l in existing.strip().split("\n") if "# mekb:" not in l]

    # Add new entries
    installed = []
    for name, job in JOBS.items():
        if jobs_to_install and name not in jobs_to_install:
            continue
        entry = generate_crontab_entry(name, job, vault_root)
        if entry:
            lines.append(entry)
            installed.append(name)

    # Write new crontab
    new_crontab = "\n".join(lines) + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True,
                         capture_output=True)
    if proc.returncode == 0:
        for name in installed:
            job = JOBS[name]
            print(f"  Installed: {name} ({job['schedule']} at {job['time']})")
        print(f"\n{len(installed)} job(s) installed.")
    else:
        print(f"Failed to install crontab: {proc.stderr}")


def uninstall_macos():
    """Remove all launchd jobs."""
    agents_dir = get_launch_agents_dir()
    removed = 0
    for name in JOBS:
        label = f"{LABEL_PREFIX}.{name}"
        plist_path = agents_dir / f"{label}.plist"
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)],
                         capture_output=True)
            plist_path.unlink()
            removed += 1
            print(f"  Removed: {name}")
    print(f"\n{removed} job(s) removed.")


def uninstall_linux():
    """Remove all crontab entries."""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("No crontab found.")
        return

    lines = [l for l in result.stdout.strip().split("\n") if "# mekb:" not in l]
    new_crontab = "\n".join(lines) + "\n" if lines else ""
    subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)
    print("MeKB crontab entries removed.")


def show_status():
    """Show status of scheduled jobs."""
    if is_macos():
        agents_dir = get_launch_agents_dir()
        print("\nScheduled jobs (macOS launchd):\n")
        found = False
        for name, job in JOBS.items():
            label = f"{LABEL_PREFIX}.{name}"
            plist_path = agents_dir / f"{label}.plist"
            if plist_path.exists():
                found = True
                # Check if loaded
                result = subprocess.run(
                    ["launchctl", "list", label],
                    capture_output=True, text=True
                )
                status = "loaded" if result.returncode == 0 else "installed (not loaded)"
                print(f"  {name:<25} {status:<20} {job['schedule']} at {job['time']}")
            else:
                print(f"  {name:<25} {'not installed':<20} {job['schedule']} at {job['time']}")
        if not found:
            print("  No jobs installed. Run: python3 scripts/schedule.py install")
    elif is_linux():
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        print("\nScheduled jobs (crontab):\n")
        if result.returncode == 0:
            found = False
            for line in result.stdout.split("\n"):
                if "# mekb:" in line:
                    found = True
                    job_name = line.split("# mekb:")[1].strip()
                    print(f"  {job_name}: {line.split('#')[0].strip()}")
            if not found:
                print("  No MeKB jobs in crontab. Run: python3 scripts/schedule.py install")
        else:
            print("  No crontab found.")
    else:
        print(f"Unsupported platform: {platform.system()}")


def run_job(job_name, vault_root):
    """Run a specific job now."""
    if job_name not in JOBS:
        print(f"Unknown job: {job_name}")
        print(f"Available: {', '.join(JOBS.keys())}")
        sys.exit(1)

    job = JOBS[job_name]
    print(f"Running: {job_name} ({job['description']})")
    parts = job["command"].split()
    result = subprocess.run(parts, cwd=str(vault_root), text=True)
    return result.returncode


def list_jobs():
    """List available jobs."""
    print("\nAvailable scheduled jobs:\n")
    for name, job in JOBS.items():
        day_str = f" ({job['day']})" if job.get("day") else ""
        print(f"  {name:<25} {job['schedule']:<8} at {job['time']}{day_str}")
        print(f"    {job['description']}")
        print(f"    Command: {job['command']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="MeKB job scheduler")
    parser.add_argument("action", choices=["list", "install", "uninstall", "status", "run"],
                       help="Action to perform")
    parser.add_argument("job", nargs="?", help="Specific job name (for install/run)")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()

    if args.action == "list":
        list_jobs()

    elif args.action == "install":
        jobs_filter = [args.job] if args.job else None
        if jobs_filter and args.job not in JOBS:
            print(f"Unknown job: {args.job}")
            print(f"Available: {', '.join(JOBS.keys())}")
            sys.exit(1)

        print(f"\nInstalling scheduled jobs for: {vault_root}\n")
        if is_macos():
            install_macos(jobs_filter, vault_root)
        elif is_linux():
            install_linux(jobs_filter, vault_root)
        else:
            print(f"Unsupported platform: {platform.system()}")
            print("Manual setup required. Jobs:")
            for name, job in JOBS.items():
                print(f"  {job['schedule']} at {job['time']}: {job['command']}")

    elif args.action == "uninstall":
        if is_macos():
            uninstall_macos()
        elif is_linux():
            uninstall_linux()
        else:
            print(f"Unsupported platform: {platform.system()}")

    elif args.action == "status":
        show_status()

    elif args.action == "run":
        if not args.job:
            print("Specify a job to run. Available:")
            for name in JOBS:
                print(f"  {name}")
            sys.exit(1)
        sys.exit(run_job(args.job, vault_root))


if __name__ == "__main__":
    main()
