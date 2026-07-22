---
name: "planning-with-files"
description: "Manus-style persistent file-based planning: task_plan.md, findings.md, progress.md survive context loss and crashes. Use for multi-step tasks."
---

# Planning with Files

Work like Manus: Use persistent markdown files as your "working memory on disk."

## The Core Pattern

```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)

→ Anything important gets written to disk.
```

## Quick Start

Before ANY complex task in OpenClaw:

1. **Create `task_plan.md`** in the project root — phases, status, decisions
2. **Create `findings.md`** — research discoveries and context
3. **Create `progress.md`** — action log and session notes

## File Purposes

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Phases, progress, decisions | After each phase |
| `findings.md` | Research, discoveries | After ANY discovery |
| `progress.md` | Session log, test results | Throughout session |

## Critical Rules for OpenClaw Agents

### 1. Create Plan First
Never start a complex task without `task_plan.md`. Non-negotiable.

### 2. Read Before Decide
Before major decisions, read the plan file. This keeps goals in your attention window.

### 3. Update After Act
After completing any phase:
- Mark phase status: `in_progress` → `complete`
- Log any errors encountered
- Note files created/modified

### 4. Log ALL Errors
Every error goes in the plan file. This builds knowledge and prevents repetition.

```markdown
## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError | 1 | Created default config |
| API timeout | 2 | Added retry logic |
```

### 5. Never Repeat Failures
Track what you tried. Mutate the approach.

### 6. Session Recovery After Restart
If resuming a session:
- Read `task_plan.md` to reorient
- Check `progress.md` for last actions
- Read `findings.md` for accumulated knowledge
- Update plan state based on `git diff --stat` if applicable

## Read vs Write Decision Matrix

| Situation | Action | Reason |
|-----------|--------|--------|
| Just wrote a file | DON'T read | Content still in context |
| Browser/search returned data | Write to findings.md | Persist before lost |
| Starting new phase | Read plan/findings | Re-orient if context stale |
| Error occurred | Read relevant file | Need current state to fix |
| Resuming after gap | Read all planning files | Recover state |

## The 5-Question Reboot Test

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases |
| What's the goal? | Goal statement in plan |
| What have I learned? | findings.md |
| What have I done? | progress.md |

## The 3-Strike Error Protocol

```
ATTEMPT 1: Diagnose & Fix → Read error → Identify root cause → Apply targeted fix
ATTEMPT 2: Alternative Approach → Try different method, tool, or library
ATTEMPT 3: Broader Rethink → Question assumptions → Search for solutions → Update plan
AFTER 3 FAILURES: Escalate to user — explain what you tried and ask for guidance
```

## When to Use

**Use for:**
- Multi-step tasks (3+ steps)
- Research tasks
- Building/creating projects
- Tasks spanning many tool calls
- Anything requiring organization

**Skip for:**
- Simple questions
- Single-file edits
- Quick lookups

## Templates (in planning-with-files/templates/)

- `templates/task_plan.md` — Phase tracking with phases, status, decisions
- `templates/findings.md` — Research storage
- `templates/progress.md` — Session logging

## Scripts (in planning-with-files/scripts/)

- `scripts/init-session.sh` — Initialize all planning files
- `scripts/check-complete.sh` — Verify all phases complete
- `scripts/session-catchup.py` — Recover context from previous session

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| State goals once and forget | Re-read plan before decisions |
| Hide errors and retry silently | Log errors to plan file |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan file FIRST |
| Repeat failed actions | Track attempts, mutate approach |
