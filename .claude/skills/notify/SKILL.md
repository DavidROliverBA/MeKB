# /notify

Send notifications via desktop, Slack, Discord, or email.

## Usage

```
/notify "Title" "Message"                # Auto-detect best backend
/notify "Title" "Message" --slack        # Send to Slack
/notify "Title" "Message" --discord      # Send to Discord
/notify "Title" "Message" --email        # Send via email
/notify --test                           # Test all backends
/notify --list                           # Show available backends
```

## Instructions

### Send a Notification

```bash
python3 scripts/notify.py "Title" "Message"
```

Auto-detects the best available backend: desktop > slack > discord > email.

### Specify Backend

```bash
python3 scripts/notify.py "Title" "Message" --backend slack
python3 scripts/notify.py "Title" "Message" --backend desktop
```

### Test Backends

```bash
python3 scripts/notify.py --test
```

### List Available Backends

```bash
python3 scripts/notify.py --list
```

### Configuration

Configure backends in `.mekb/notifications.yaml`:

```yaml
slack:
  webhook_url: "https://hooks.slack.com/services/T.../B.../..."

discord:
  webhook_url: "https://discord.com/api/webhooks/..."

email:
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: you@gmail.com
  smtp_pass: app-password
  to: you@gmail.com
```

### Use in Automations

Combine with `/automate` or `/schedule` for automated alerts:

```bash
# Notify after stale check
python3 scripts/stale-check.py --summary && python3 scripts/notify.py "Stale Notes" "Run /stale to review"
```

## Notes

- Desktop notifications work on macOS only (osascript)
- Slack/Discord use incoming webhooks (no API keys needed)
- Email uses SMTP with optional TLS
- All backends are optional - configure only what you need
- Config file: `.mekb/notifications.yaml`
