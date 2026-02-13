# /schedule

Manage scheduled vault maintenance jobs.

## Usage

```
/schedule                # Show job status
/schedule install        # Install all scheduled jobs
/schedule install <job>  # Install specific job
/schedule uninstall      # Remove all scheduled jobs
/schedule run <job>      # Run a job now
/schedule list           # List available jobs
```

## Instructions

### /schedule (status)

Show current status of scheduled jobs:

```bash
python3 scripts/schedule.py status
```

### /schedule install

Install scheduled maintenance jobs using platform-native tools:

```bash
python3 scripts/schedule.py install
```

- **macOS:** Creates launchd plists in `~/Library/LaunchAgents/com.mekb.*`
- **Linux:** Adds entries to user's crontab

**Available jobs:**

| Job | Schedule | Purpose |
|-----|----------|---------|
| `rebuild-index` | Daily 06:00 | Rebuild FTS5 search index |
| `rebuild-graph` | Daily 06:05 | Rebuild knowledge graph |
| `rebuild-embeddings` | Weekly (Sun 06:10) | Rebuild vector embeddings |
| `stale-check` | Weekly (Fri 09:00) | Check for stale notes |

### /schedule run <job>

Run a specific job immediately:

```bash
python3 scripts/schedule.py run rebuild-index
```

### Troubleshooting

**macOS TCC restrictions:** If jobs fail silently, grant Full Disk Access to the terminal app in System Settings > Privacy & Security > Full Disk Access.

**Logs:** Check `.mekb/logs/<job-name>.log` for output.

## Notes

- All jobs run within the vault directory
- Logs are stored in `.mekb/logs/` (gitignored)
- Jobs can be installed individually or all at once
- Uninstall removes all MeKB scheduled jobs cleanly
