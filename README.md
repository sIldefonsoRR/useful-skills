# useful-skills

A collection of useful skills for Claude Code. Each skill lives in its own folder with a `SKILL.md` and any supporting files.

## Skills

| Skill | Description |
|---|---|
| [a2b-attack-check](a2b-attack-check/) | Audits a codebase for Agent-to-Backend (A2B) attack risks and writes a dated report. |
| [ai-created-check](ai-created-check/) | Checks code, docs, and git history for evidence that files were created or updated with AI tools, and writes a dated report. |
| [core-repo-files-check](core-repo-files-check/) | Checks that a repo has its core files (README, LICENSE, .gitignore, .env.example, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, SBOM), explains each one, and writes a dated report. |

## Install

Symlink a skill folder into your personal skills directory:

```bash
git clone https://github.com/sIldefonsoRR/useful-skills.git
ln -s "$(pwd)/useful-skills/a2b-attack-check" ~/.claude/skills/a2b-attack-check
```

Or copy it into a project's `.claude/skills/` folder to share it with that repo's contributors.

### Other agents

Skills use the open Agent Skills format (`SKILL.md` + frontmatter) and only need file reading and shell access, so they are not tied to Claude. Codex, Gemini CLI, and Copilot CLI load skills from `~/.agents/skills/`:

```bash
ln -s "$(pwd)/useful-skills/a2b-attack-check" ~/.agents/skills/a2b-attack-check
```

For agents without skill support, reference the file directly (e.g. "Follow a2b-attack-check/SKILL.md") or link it from `AGENTS.md`. Skills are tested with Claude; results on other models may vary.

## a2b-attack-check

Checks whether attackers can abuse AI agents in your code to reach backend systems. This covers LLM clients, agent loops, tool and function calling, and MCP servers that can touch databases, shells, files, or the network.

**Usage:** in Claude Code, from the repo you want to audit:

```
Run an A2B check on this repo
```

**Output:** `YYYY-MM-DD-A2B-CHECK.md` in the target repo root. It contains:
- a verdict (`CRITICAL RISK` to `NO ISSUES FOUND`, or `NOT APPLICABLE`)
- a count of findings by severity
- an inventory of the agent surface
- each finding, with `file:line`, the attack path, impact, and fix
- a pass/fail table for every check

The skill only reads your code. The report is the only file it writes.

**Checks:**

| ID | Check |
|---|---|
| A0 | Agent surface inventory |
| A1 | Prompt injection reaching tool calls |
| A2 | LLM output reaching dangerous sinks (shell, eval, SQL, FS, HTTP, HTML) |
| A3 | Authorization on agent-callable actions |
| A4 | Excessive agency |
| A5 | Tool argument validation |
| A6 | Secrets exposure to or through the model |
| A7 | Data exfiltration channels |
| A8 | Resource abuse and loop control |
| A9 | Multi-agent and agent-to-agent trust |
| A10 | MCP server and tool supply chain |
| A11 | Output handling to users and downstream systems |
| A12 | Audit logging and detection |

See [checks.md](a2b-attack-check/checks.md) for the search patterns and pass/fail criteria.

## ai-created-check

Looks for evidence that files in a repo were created or updated with AI tools (Claude, Copilot, Cursor, ChatGPT, Codex, Gemini, aider, Devin, and others).

**Usage:** in your agent, from the repo you want to check:

```
Run an AI-created check on this repo
```

**Output:** `YYYY-MM-DD-AI-CREATED-CHECK.md` in the target repo root. It contains:
- a verdict for the whole repo
- the AI tools detected
- the commits that carry AI markers
- a level for each flagged file, with the evidence quoted

The skill only reads your code. The report is the only file it writes.

**Levels:**

| Level | Requires |
|---|---|
| Confirmed | A hard signal: AI commit trailer, AI bot author, AI branch, generator header, or leftover chat text in the file |
| Likely | 3+ stylistic signals across 2+ categories, with no hard signal |
| Possible | 1–2 stylistic signals, or several in only one category |
| No evidence | Nothing found. This never means "human-written" |

Most AI-assisted code leaves no trace, so this check can only show that AI was used; it can never prove a file was written by a person. The report covers files and commits, not people.

See [signals.md](ai-created-check/signals.md) for every signal and the commands used to find it.

## core-repo-files-check

Checks whether a repo has nine core files, explains what each one is for, and describes what the present ones contain.

**Usage:** in your agent, from the repo you want to check:

```
Run a core repo files check on this repo
```

**Output:** `YYYY-MM-DD-CORE-REPO-FILES-CHECK.md` in the target repo root. It contains:
- a verdict (`ESSENTIAL FILES MISSING`, `GAPS FOUND`, or `ALL CORE FILES PRESENT`)
- a status for each file
- for each present file: its purpose and a summary of its contents
- for each missing file: its purpose and why it matters for this repo

The skill only reads your code. It never creates the missing files. The report is the only file it writes.

**Files:**

| ID | File | Tier |
|---|---|---|
| F1 | README.md | Essential |
| F2 | LICENSE | Essential |
| F3 | .gitignore | Essential |
| F4 | .env.example | Recommended |
| F5 | CONTRIBUTING.md | Recommended |
| F6 | CODE_OF_CONDUCT.md | Recommended |
| F7 | SECURITY.md | Recommended |
| F8 | CHANGELOG.md | Recommended |
| F9 | sbom.cdx.json | Recommended |

**Statuses:** Present, Incomplete (template placeholders left in, or a key item missing), Empty, Missing, and Not applicable (only `.env.example`, when the code reads no environment variables). Files in `.github/` or `docs/`, and common alternate names such as `LICENSE.txt` or `HISTORY.md`, are accepted.

See [files.md](core-repo-files-check/files.md) for each file's purpose, accepted names, and what is checked.

## Report files

Each check writes its report to the root of the repo it audits, as an untracked file. The skills never change `.gitignore`. To keep reports out of version control, add these lines to the audited repo's `.gitignore`. This repo already ignores them:

```gitignore
# Skill report outputs
*-A2B-CHECK.md
*-AI-CREATED-CHECK.md
*-CORE-REPO-FILES-CHECK.md
```

## SBOM

[`sbom.cdx.json`](sbom.cdx.json) is a CycloneDX 1.6 software bill of materials. The repo has no third-party dependencies, so the SBOM lists each skill and its files with SHA-256 hashes. You can use it to check that an installed copy matches this repo:

```bash
shasum -a 256 a2b-attack-check/* ai-created-check/* core-repo-files-check/*
```

The skills use `git`, `grep`, and `date` from the host. These tools are not bundled. Regenerate the SBOM whenever a skill's files change:

```bash
python3 _scripts/generate_sbom.py
```

The generator uses only the Python standard library and git. Every top-level folder that contains a `SKILL.md` is included, so new skills are picked up automatically.

## Contributing

To add or change a skill, see [CONTRIBUTING.md](CONTRIBUTING.md) for the skill layout, the testing process, and the pull request checklist. All participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md). Do not open a public issue. These skills run inside an agent on code you may not trust, so read the "Safe use" section in that file before auditing third-party repos.

## License

[MIT](LICENSE)
