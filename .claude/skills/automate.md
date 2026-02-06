# /automate

Create custom recurring tasks and automation routines.

## Usage

```
/automate                           # List current automations
/automate add "Weekly inbox review" # Add a recurring reminder
/automate remove <name>             # Remove an automation
```

## Instructions

### /automate (list)

Show all configured automations from `.mekb/automations.yaml`:

```markdown
## Active Automations

| Name | Schedule | Last Run | Next Run |
|------|----------|----------|----------|
| Weekly inbox review | Friday 09:00 | 2026-01-31 | 2026-02-07 |
| Monthly stale check | 1st of month | 2026-01-01 | 2026-02-01 |
```

### /automate add

1. Ask the user:
   - **Name:** What to call this automation
   - **Action:** What should happen (run script, create note, reminder)
   - **Schedule:** When (daily, weekly, monthly, specific day/time)

2. Add to `.mekb/automations.yaml`:

```yaml
automations:
  - name: Weekly inbox review
    action: reminder
    message: "Time to review your inbox and process notes"
    schedule: weekly
    day: Friday
    time: "09:00"
    enabled: true
    created: 2026-02-06

  - name: Monthly stale check
    action: script
    command: "python3 scripts/stale-check.py --summary"
    schedule: monthly
    day: 1
    time: "09:00"
    enabled: true
    created: 2026-02-06
```

3. Optionally install as a scheduled job:
   ```bash
   python3 scripts/schedule.py install
   ```

### /automate remove

Remove an automation by name from `.mekb/automations.yaml`.

### Action Types

| Type | Description | Example |
|------|-------------|---------|
| `reminder` | Show a message in daily note | "Review stale notes" |
| `script` | Run a Python script | `stale-check.py --summary` |
| `create` | Create a note from template | Weekly review note |

## Notes

- Automations are stored in `.mekb/automations.yaml` (gitignored)
- Reminders appear in the daily note when `/daily` is run
- Script automations can be installed as scheduled jobs
- This is a lightweight layer on top of `/schedule`
