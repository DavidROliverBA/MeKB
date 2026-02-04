# /calendar

Sync with calendar to create meeting notes automatically.

## When to Use

- Before meetings to prep notes with attendees
- After meetings to capture what happened
- User says "meeting prep", "calendar sync", "upcoming meetings"

## Instructions

### Prerequisites

Calendar integration requires:
1. **Google Calendar** - OAuth credentials or API key
2. **Outlook/Microsoft 365** - Graph API credentials
3. **Apple Calendar** - AppleScript (macOS only)

Set environment variables:
```bash
# Google Calendar
export GOOGLE_CALENDAR_CREDENTIALS="path/to/credentials.json"

# Microsoft Graph
export MS_GRAPH_CLIENT_ID="your-client-id"
export MS_GRAPH_CLIENT_SECRET="your-client-secret"
```

### Option 1: Manual Calendar Check

Without API setup, guide user to:
1. Check their calendar manually
2. Provide meeting title, time, and attendees
3. Create meeting note from that info

### Option 2: Google Calendar Integration

```bash
# Fetch today's events
curl -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=$(date -I)T00:00:00Z&timeMax=$(date -I)T23:59:59Z"
```

### Option 3: Apple Calendar (macOS)

```applescript
tell application "Calendar"
    set today to current date
    set eventList to (every event of calendar "Work" whose start date is today)
    repeat with e in eventList
        get {summary of e, start date of e, attendees of e}
    end repeat
end tell
```

### Skill Flow

```
User: /calendar

Claude: Let me check your calendar...

## Today's Meetings (3 Feb 2026)

1. **10:00 - Architecture Review** (1 hour)
   Attendees: Jane Smith, Bob Jones
   [Create Meeting Note]

2. **14:00 - Sprint Planning** (2 hours)
   Attendees: Dev Team
   [Create Meeting Note]

3. **16:30 - 1:1 with Manager** (30 min)
   Attendees: Sarah Wilson
   [Create Meeting Note]

Which meeting would you like to prep for?
```

### Create Meeting Note

When user selects a meeting:

```yaml
---
type: Meeting
title: {{meeting_title}}
created: {{date}}
date: {{meeting_date}}
time: {{meeting_time}}
duration: {{duration}}
tags: []
attendees:
  - "[[Person - Jane Smith]]"
  - "[[Person - Bob Jones]]"
calendar_event_id: {{event_id}}
---

# {{meeting_title}}

**Date:** {{meeting_date}} {{meeting_time}}
**Duration:** {{duration}}
**Attendees:** {{attendees}}

## Agenda

_Add meeting agenda_

## Notes

_Capture key points during the meeting_

## Decisions

- 

## Action Items

- [ ] _Action_ - [[Person - Owner]]

## Follow-up

_What needs to happen next?_
```

### Auto-Create People Notes

If attendees don't have Person notes:
- Offer to create `Person - Name.md` for each
- Pre-fill with email from calendar

### Options

```
/calendar                  # Show today's meetings
/calendar tomorrow         # Show tomorrow's meetings  
/calendar week             # Show this week's meetings
/calendar sync             # Full calendar sync
/calendar prep <meeting>   # Create prep note for specific meeting
```

### Post-Meeting Workflow

After a meeting:
1. Update the meeting note with actual notes
2. Extract action items to Task notes
3. Link to people mentioned
4. Add to daily note

### Tips

- Create meeting notes before the meeting for prep
- Link attendees to Person notes for relationship tracking
- Extract action items immediately after meetings
- Review meeting notes in weekly review
