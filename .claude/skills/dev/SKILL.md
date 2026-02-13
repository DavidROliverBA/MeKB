---
name: dev
---

# /dev

Skill development workflow - create, test, and manage MeKB skills.

## Usage

```
/dev list                # List all skills with metadata
/dev validate            # Validate all skill files
/dev validate /q         # Validate specific skill
/dev create /my-skill    # Create a new skill from template
/dev export /q           # Export skill as portable package
/dev test                # Run all tests
```

## Instructions

### /dev list

Show all skills with line counts, sections, and script references:

```bash
python3 scripts/skill-tools.py list
```

### /dev validate

Check all skills for format issues:

```bash
python3 scripts/skill-tools.py validate
```

Issues checked:
- Header matches filename (`# /name` matches `name.md`)
- Has Usage or When to Use section
- Has Instructions or How It Works section
- Referenced scripts exist

### /dev create /my-skill

Create a new skill file from the standard template:

1. Create `.claude/skills/my-skill/SKILL.md` with this structure:

```markdown
# /my-skill

Brief description of what this skill does.

## Usage

\`\`\`
/my-skill <args>
\`\`\`

## Instructions

### Step 1: [Action]

Detailed instructions for Claude to follow.

### Step 2: [Action]

More instructions.

## Notes

- Additional tips and context
```

2. If the skill needs a script, create it in `scripts/`
3. Update `CLAUDE.md` skills table
4. Run validation: `python3 scripts/skill-tools.py validate /my-skill`

### /dev export

Package a skill for sharing:

```bash
python3 scripts/skill-tools.py export /q
```

Creates a `q.mekb-skill/` directory containing:
- The skill `.md` file
- Any referenced scripts
- A `manifest.yaml` with metadata

### /dev test

Run the full test suite:

```bash
python3 -m pytest scripts/tests/ -v
```

Or individual test files:
```bash
python3 -m pytest scripts/tests/test_skills.py -v
python3 -m pytest scripts/tests/test_search.py -v
python3 -m pytest scripts/tests/test_graph.py -v
python3 -m pytest scripts/tests/test_security.py -v
```

Without pytest:
```bash
python3 -m unittest discover scripts/tests/ -v
```

## Tips

- Always validate after creating or modifying skills
- Keep skills focused on one task
- Reference scripts rather than embedding complex logic
- Test with both pytest and unittest for compatibility
