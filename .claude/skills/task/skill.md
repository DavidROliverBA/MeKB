# /task

Quick-create a task.

## Usage

```
/task <title>
```

## Instructions

1. Parse title from command
2. Get today's date
3. Create `Task - <title>.md` from `Templates/Task.md`:
   - Replace `{{title}}` with provided title
   - Replace `{{date}}` with today's date
4. Confirm: "Created [[Task - <title>]]"

## Example

```
/task Review proposal
```

Creates `Task - Review proposal.md`
