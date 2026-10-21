# useful-skills

A collection of read-only audit skills for Claude Code. The six skills check a repository for a specific class of issue — agent-to-backend attack paths, AI-authored files, missing core files, missing CI/CD automation, OWASP Top 10 risks, and obfuscated Python — and each writes a dated report at the audited repo's root without changing its code. Each skill lives in its own folder with a `SKILL.md` and any supporting files.

## Skills

| Skill | Description |
|---|---|
| [a2b-attack-check](a2b-attack-check/) | Audits a codebase for Agent-to-Backend (A2B) attack risks and writes a dated report. |
| [ai-created-check](ai-created-check/) | Checks code, docs, and git history for evidence that files were created or updated with AI tools, and writes a dated report. |
| [core-repo-files-check](core-repo-files-check/) | Checks that a repo has its core files (README, LICENSE, .gitignore, .env.example, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, SBOM), explains each one, and writes a dated report. |
| [essential-automation-check](essential-automation-check/) | Checks that a repo has its CI/CD and test automation files (workflows, Dependabot, Makefile, issue and PR templates, labeler), checks they work, and writes a dated report. |
| [owasp-code-check](owasp-code-check/) | Reviews source code against the OWASP Top 10:2025, ranks each risk, and writes a dated report with evidence and prioritized next actions. |
| [obfuscation-check](obfuscation-check/) | Detects obfuscated, packed, or deliberately unreadable Python (tool markers, encoded payloads, mangled identifiers, bytecode-only modules) and writes a dated report. |

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

## essential-automation-check

Checks whether a repo has six CI/CD and test automation files, explains what each one is for, and checks that the present ones actually work. For example, a workflow must run a build, test, or lint command on push or pull request. Dependabot must cover every ecosystem the repo uses.

**Usage:** in your agent, from the repo you want to check:

```
Run an essential automation check on this repo
```

**Output:** `YYYY-MM-DD-ESSENTIAL-AUTOMATION-CHECK.md` in the target repo root. It contains:
- a verdict (`ESSENTIAL AUTOMATION MISSING`, `GAPS FOUND`, or `ALL AUTOMATION PRESENT`)
- the ecosystems detected in the repo
- a status for each file
- for each present file: its purpose, what it does, and any problems (including risky `pull_request_target` workflows)
- for each missing file: its purpose and why it matters for this repo

The skill only reads your code. It never runs workflows or `make`, and never creates the missing files. The report is the only file it writes.

**Files:**

| ID | File | Tier |
|---|---|---|
| C1 | .github/workflows/*.yml | Essential |
| C2 | Makefile | Recommended |
| C3 | .github/dependabot.yml | Essential |
| C4 | .github/ISSUE_TEMPLATE/*.yml | Recommended |
| C5 | .github/PULL_REQUEST_TEMPLATE.md | Recommended |
| C6 | .github/labeler.yml | Recommended |

**Statuses:** Present, Incomplete (the file exists but does not do its job, e.g. a Makefile missing a target the CI calls), Empty, Missing, and Not applicable (only Dependabot, when the repo uses no package ecosystem). Common alternatives are accepted: GitLab CI, CircleCI, Jenkins and others for C1; Renovate for C3; `justfile` or `Taskfile.yml` for C2; Markdown issue templates for C4.

See [files.md](essential-automation-check/files.md) for each file's purpose, accepted names, and what is checked.

## owasp-code-check

Reviews application source code against the OWASP Top 10:2025. Each finding traces untrusted input to a sensitive operation, or shows a missing control, and quotes the code as evidence.

**Usage:** in your agent, from the repo you want to audit:

```
Run an OWASP code check on this repo
```

**Output:** `YYYY-MM-DD-OWASP-CHECK.md` in the target repo root. It contains:
- a verdict (`CRITICAL RISK` to `NO ISSUES FOUND`, or `NOT APPLICABLE`)
- a count of findings by risk rank
- an inventory of the application surface
- each finding, with `file:line`, the code excerpt, the source-to-sink path, impact, and mitigation
- a prioritized Next Actions table
- a pass/fail table for every check

The skill only reads your code. It never runs the app, tests, or dependency scanners. The report is the only file it writes.

**Risk ranks and priorities:**

| Rank | Priority | Examples |
|---|---|---|
| Critical | P0: fix before the next deploy | Unauthenticated injection or RCE, auth bypass, access to other users' data, committed production secret |
| High | P1: fix in the current sprint | XSS, SSRF, path traversal, weak password hashing, missing authz on writes, fail-open checks |
| Medium | P2: next release | Weak crypto or randomness, no login rate limit, debug mode or stack traces in prod, open redirect |
| Low | P3: hardening backlog | Missing security headers or cookie flags, no lockfile, unpinned CI actions |
| Info | none | Hardening notes, and anything found only in tests or examples |

**Checks:**

| ID | OWASP 2025 | Check |
|---|---|---|
| O0 | — | Application surface inventory |
| O1 | A01 | Broken Access Control |
| O2 | A02 | Security Misconfiguration |
| O3 | A03 | Software Supply Chain Failures |
| O4 | A04 | Cryptographic Failures |
| O5 | A05 | Injection |
| O6 | A06 | Insecure Design |
| O7 | A07 | Authentication Failures |
| O8 | A08 | Software or Data Integrity Failures |
| O9 | A09 | Security Logging and Alerting Failures |
| O10 | A10 | Mishandling of Exceptional Conditions |

See [checks.md](owasp-code-check/checks.md) for the search patterns and pass/fail criteria. Agent-to-backend risks in LLM code are covered by [a2b-attack-check](#a2b-attack-check).

## obfuscation-check

Detects Python source that has been obfuscated, packed, or made deliberately hard to read or analyze. Obfuscated code in a repo is often there to hide malware from review, so this check flags and locates it. It is read-only and **never runs, imports, decodes, or deobfuscates** the target: it reports the obfuscation, it does not reverse it.

**Usage:** in your agent, from the repo you want to check:

```
Run an obfuscation check on this repo
```

**Output:** `YYYY-MM-DD-OBFUSCATION-CHECK.md` in the target repo root. It contains:
- a verdict (`OBFUSCATION CONFIRMED`, `LIKELY OBFUSCATION`, `POSSIBLE OBFUSCATION`, `NO EVIDENCE FOUND`, or `NOT APPLICABLE`)
- a table of tools and artifacts detected
- a level for each flagged file, with the evidence quoted at `file:line`
- a handling note when anything is Confirmed or Likely (review or quarantine before running; never execute it to inspect it)

The skill only reads your code. The report is the only file it writes.

**Levels:**

| Level | Requires |
|---|---|
| Confirmed | A hard signal: an obfuscator/packer tool marker (B1), an encoded blob that reaches `exec`/`eval`/`compile` (B2), a bytecode-only module (B3), or a freezer artifact replacing source (B4) |
| Likely | No hard signal, but 3+ soft signals across 2+ categories (B5–B8), each with a quoted example |
| Possible | 1–2 soft signals, or 3+ in only one category |
| No evidence | Nothing found. This never means "clean" or "safe" |

**Signals:**

| ID | Signal | Kind |
|---|---|---|
| B1 | Obfuscation / packer tool markers | Hard |
| B2 | Encoded or compressed blob executed at runtime | Hard |
| B3 | Bytecode-only module shipped without source | Hard |
| B4 | Freezer / packer artifacts replacing source | Hard |
| B5 | Lexical mangling (non-semantic or hex-style identifiers) | Soft |
| B6 | Constant codification (`\x` blobs, `chr()` chains, arithmetic constants) | Soft |
| B7 | Control-flow flattening (dispatch loop over a state variable) | Soft |
| B8 | Pervasive dynamic/indirect execution from constructed strings | Soft |

Minified code, code generators, and some legitimate libraries can trip the soft signals, so detection is heuristic; see [signals.md](obfuscation-check/signals.md) for the patterns and what each requires. Vendored and build output (`site-packages`, `*.min.*`, `dist/`) is excluded.

## Report files

Each check writes its report to the root of the repo it audits, as an untracked file. The skills never change `.gitignore`. To keep reports out of version control, add these lines to the audited repo's `.gitignore`. This repo already ignores them:

```gitignore
# Skill report outputs
*-A2B-CHECK.md
*-AI-CREATED-CHECK.md
*-CORE-REPO-FILES-CHECK.md
*-ESSENTIAL-AUTOMATION-CHECK.md
*-OWASP-CHECK.md
*-OBFUSCATION-CHECK.md
```

## SBOM

[`sbom.cdx.json`](sbom.cdx.json) is a CycloneDX 1.6 software bill of materials. The repo has no third-party dependencies, so the SBOM lists each skill and its files with SHA-256 hashes. You can use it to check that an installed copy matches this repo:

```bash
shasum -a 256 a2b-attack-check/* ai-created-check/* core-repo-files-check/* essential-automation-check/* owasp-code-check/* obfuscation-check/*
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
