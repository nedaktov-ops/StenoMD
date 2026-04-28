# StenoMD + OpenCode Best Practices

A curated guide to efficient, reliable development with StenoMD using OpenCode (or Claude Code). It consolidates proven workflows from the StenoMD team and the broader Claude Code community.

---

## Table of Contents

1. [General Workflow](#general-workflow)
2. [Essential Commands](#essential-commands)
3. [Permission & Context Hygiene](#permission--context-hygiene)
4. [Testing & Verification](#testing--verification)
5. [Project Configuration](#project-configuration)
6. [Skill Usage](#skill-usage)
7. [Common Pitfalls](#common-pitfalls)

---

## General Workflow

1. **Start with `/status`** – verify your installation, model, and project context.
2. **Use `/diff` frequently** – review what you/Claude changed before committing.
3. **Run `/doctor` periodically** – catches environment issues early.
4. **Leverage `/focus`** during long sessions to reduce visual noise.

---

## Essential Commands

| Command | Purpose | When to use |
|---------|---------|-------------|
| `/status` | Show version, model, connectivity | Start of session, after errors |
| `/diff` | Interactive diff viewer | Before PR, after a batch of edits |
| `/doctor` | Diagnose installation & settings | Anomalies, slowness, config questions |
| `/plugins` | List and manage plugins | Adding/removing skill sets |
| `/skills` | List available skills | Discover automation |
| `/memory` | View or edit persistent memory files | Adjust long-term preferences |
| `/config` | Open settings UI | Change theme, model, defaults |
| `/usage` or `/cost` | Track token usage and plan limits | Budget awareness |
| `/compact` | Summarize conversation to free context | Long chats getting close to limit |
| `/branch <name>` | Create a conversation branch | Explore an alternative approach |
| `/copy[N]` | Copy response or code blocks to clipboard | Quick extraction |
| `/export [filename]` | Export entire conversation | Sharing, documentation |
| `/review` | Review current git diff with multi‑agent code review | Pre‑commit quality gate |
| `/security-review` | Scan diff for security issues | Especially for auth, data exposure |
| `/init` | Initialize project CLAUDE.md guide | New project setup |
| `/recap` | One‑line summary of current session | When returning after break |

---

## Permission & Context Hygiene

- **Use `/permissions`** to view and tweak allow/deny rules.  
  Add safe commands (e.g., `pytest`, `git status`) to the allowlist to avoid repeated prompts.
- **Set `CLAUDE_CODE_ALLOWED_TOOLS`** for headless automation (CI, scripts).
- **Avoid `/clear`** in long investigations; prefer `/compact` to retain history while freeing tokens.
- **Use `/context`** to visualize context usage. If you’re near 90%, compact or archive old branches.

---

## Testing & Verification

StenoMD requires end‑to‑end validation at each step.

1. **Run the full test suite** before pushing:
   ```bash
   pytest -x --tb=short
   ```
2. **Check the health score** after merges:
   ```bash
   python3 scripts/planner_agent.py --health
   ```
3. **Validate vault → KG sync**:
   ```bash
   python3 scripts/analyze_vault.py --gaps
   ```
4. **Use `/review`** on your PR branch; treat suggestions as mandatory if they highlight robustness or data integrity concerns.

**Verification pattern** (Boris Cherny’s tip):
> Make sure Claude has a way to verify its work. For StenoMD, verification means:
> - Scripts execute without errors
> - `analyze_vault.py` reports zero missing critical fields
> - Health score remains ≥95
> - Derived data (laws, committees) reconcile with source CSVs

---

## Project Configuration

Keep all configuration in `scripts/config.py` and environment variables. Never hardcode absolute paths.

**Important env vars for StenoMD:**

```bash
STENOMD_DIR               # project root override
STENOMD_ALLOWED_ORIGIN    # CORS for REST API (default: localhost)
STENOMD_MAX_ID            # max session ID for scrapers (default: 200)
STENOMD_USE_MEM_PALACE    # enable long‑term memory (default: false)
STENOMD_USE_RUFLO         # use Ruflo orchestration (default: false)
STENOMD_DEBUG             # verbose logging (default: false)
```

The planner agent (`scripts/planner_agent.py`) respects these and writes its own `STRATEGY.md` and `project-logs.md` after each phase.

---

## Skill Usage

OpenCode skills are stored in `.opencode/skills/`. StenoMD ships with the **Superpowers** suite, providing skills for:

- `subagent-driven-development` – decompose a task into parallel sub‑agents
- `test-driven-development` – create tests before implementation
- `systematic-debugging` – trace root causes with condition‑based waiting
- `code-review` – request or provide reviews
- `using-git-worktrees` – safe experimentation
- `writing-plans` – create structured implementation plans
- `verification-before-completion` – final checks before PR

**How to invoke:** Use natural language; Claude auto‑loads skills based on intent. You can also trigger explicitly via `/skill-name` if configured.

---

## Common Pitfalls

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Permission prompts loop | Missing allowlist rule | Run `/permissions` and add safe tools (pytest, python3) |
| Context fills up quickly | Long session with many file reads | Use `/compact` or `/branch` to offload history |
| KG and vault out of sync | Merge step skipped | Run `python3 scripts/merge_vault_to_kg.py` |
| Tests fail after config change | Hardcoded path in a script | Replace with `config.VAULT_DIR` etc. |
| Ruflo not starting | `ruflo` not installed or not in PATH | Install ruflo globally or set `STENOMD_USE_RUFLO=false` |
| Memory not learning | `USE_MEM_PALACE` not set | Export `STENOMD_USE_MEM_PALACE=true` |

---

## Version History

- **2026‑04‑28** – Initial best practices based on StenoMD v3.0 and community tips.

---

*Adapted from Claude Code Best Practice and StenoMD team experience.*
