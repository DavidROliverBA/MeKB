---
name: habits
---

# /habits

Simple habit tracking in daily notes.

## When to Use

- Setting up daily habits
- Tracking habits in daily notes
- Reviewing habit streaks
- User says "track habit", "habit tracker", "daily routines"

## Instructions

### Setup Habits

```
/habits setup
```

Creates `.mekb/habits.yaml`:
```yaml
habits:
  - name: Exercise
    emoji: 🏃
    frequency: daily
    goal: 30 minutes
  - name: Read
    emoji: 📚
    frequency: daily
    goal: 20 pages
  - name: Meditate
    emoji: 🧘
    frequency: daily
    goal: 10 minutes
  - name: Journal
    emoji: ✍️
    frequency: daily
    goal: Write 3 things
```

### Add Habit Section to Daily Notes

When creating daily notes with `/daily`, include:

```markdown
## Habits

- [ ] 🏃 Exercise (30 min)
- [ ] 📚 Read (20 pages)
- [ ] 🧘 Meditate (10 min)
- [ ] ✍️ Journal
```

### Track Completion

User checks off habits in their daily note:
```markdown
## Habits

- [x] 🏃 Exercise - ran 5k
- [x] 📚 Read - finished chapter 7
- [ ] 🧘 Meditate - skipped
- [x] ✍️ Journal
```

### View Progress

```
/habits              # Today's status
/habits week         # This week's completion
/habits month        # Monthly overview
/habits streak       # Current streaks
```

### Step 1: Load Habits Config

Read from `.mekb/habits.yaml` or use defaults:
```yaml
habits:
  - name: Exercise
    emoji: 🏃
  - name: Read
    emoji: 📚
  - name: Meditate
    emoji: 🧘
```

### Step 2: Scan Daily Notes

For habit tracking, scan daily notes for:
- Checkbox patterns: `- [x]` (completed) vs `- [ ]` (incomplete)
- Habit names or emojis

### Step 3: Calculate Stats

Generate statistics:
- Completion rate per habit
- Current streak (consecutive days)
- Best streak
- Weekly/monthly totals

### Step 4: Display Progress

```markdown
## Habit Progress (This Week)

| Habit     | Mon | Tue | Wed | Thu | Fri | Sat | Sun | Rate |
|-----------|-----|-----|-----|-----|-----|-----|-----|------|
| 🏃 Exercise | ✅  | ✅  | ❌  | ✅  | ✅  | -   | -   | 80%  |
| 📚 Read    | ✅  | ✅  | ✅  | ✅  | ✅  | -   | -   | 100% |
| 🧘 Meditate| ❌  | ❌  | ✅  | ✅  | ❌  | -   | -   | 40%  |

### Streaks
- 🏃 Exercise: 2 days (best: 14 days)
- 📚 Read: 5 days (best: 21 days) 🔥
- 🧘 Meditate: 0 days (best: 7 days)
```

### Examples

**Setup:**
```
User: /habits setup

Claude: Let's set up your habits! What would you like to track daily?

Suggested starters:
1. 🏃 Exercise
2. 📚 Read
3. 🧘 Meditate
4. ✍️ Journal
5. 💧 Drink water
6. 😴 Sleep 8 hours

Which habits would you like to track? (or add your own)
```

**Weekly review:**
```
User: /habits week

Claude: ## This Week's Habits

Great progress on reading! Meditation needs attention.

| Habit       | Completed | Rate  | Streak |
|-------------|-----------|-------|--------|
| 🏃 Exercise | 4/5       | 80%   | 2 days |
| 📚 Read     | 5/5       | 100%  | 12 days 🔥 |
| 🧘 Meditate | 2/5       | 40%   | 0 days |

**Tip:** Try habit stacking - meditate right after reading.
```

### Adding New Habits

```
/habits add "Drink water" 💧
```

### Removing Habits

```
/habits remove "Meditate"
```

### Tips

- Start with 2-3 habits, not 10
- Track completion, not perfection
- Use the streak as motivation
- Review weekly with `/habits week`
- Adjust goals if completion is consistently low
- Celebrate streaks! 🔥
