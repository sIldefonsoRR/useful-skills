---
name: ai-created-check
description: Use when asked whether code, docs, or files in a repository were written or modified with AI assistance (Claude, Copilot, Cursor, ChatGPT, Codex, Gemini, aider, Devin, etc.), or for an AI-usage / AI-provenance / AI-generated-code audit of a codebase or its git history.
---

# AI-Created Check

## Overview

Estimates whether files in a repository were created or updated with AI tools, and writes a dated report with the evidence.

Core principle: **evidence decides the level, not impressions.** Explicit markers (commit trailers, bot authors, generator headers, chat leftovers) can confirm AI involvement. Stylistic signals can only raise likelihood. Absence of evidence never proves human authorship: most AI-assisted code carries no marker at all.

This skill is read-only on the target. Its only write is the report file.

## Likelihood Levels

| Level | Rule |
|---|---|
| Confirmed | At least one **hard** signal (H1-H5 in `signals.md`) tied to this file or a commit that changed it. |
| Likely | No hard signal, but 3+ **soft** signals from at least 2 different categories (S1-S5), each with a concrete example. Each distinct quoted example counts once. |
| Possible | 1-2 soft signals, or 3+ soft signals all in one category. |
| No evidence | Nothing found. State "no evidence", never "human-written". |

Rules that decide edge cases:
- A hard signal always wins. An AI tool config file (e.g. `CLAUDE.md`) added by an AI-marked commit is Confirmed like any other file.
- Repo context (R1) never sets or raises a file's level. Report it once in its own section.
- Commits by non-AI bots (dependabot, renovate, github-actions) are ignored entirely.

Repo verdict = the highest level any file reached: `CONFIRMED AI INVOLVEMENT`, `LIKELY AI INVOLVEMENT`, `POSSIBLE AI INVOLVEMENT`, or `NO EVIDENCE FOUND`. State the share of scanned files at Confirmed + Likely.

**Files scanned** = tracked files (`git ls-files`, or all files if not a git repo) minus exclusions and minus the report. Report the excluded count separately.

## Workflow

1. **Set scope.** Target = current repo root unless the user names a path. Record commit (`git rev-parse --short HEAD`, or "not a git repo"), branch, and the history window checked (default: full history; if over 2000 commits, the last 2000 and say so).
2. **Repo context (R1).** Look for AI tool config and instruction files. These show tooling is in use, not which files it touched.
3. **Git history (H1-H3).** Search commit messages, trailers, author/committer names and emails, and branch names. For each match, list the files that commit changed (`git show --name-only --format= <sha>`); those files become Confirmed.
4. **File content (H4-H5, S1-S4).** Search for generator headers and chat leftovers, then sample files for stylistic signals. Read the file before recording a soft signal; a pattern match alone is not a signal.
5. **History shape (S5).** Skip when there is no git history or timestamps are unusable (e.g. every commit in the same second).
6. **Classify each flagged file** with the levels above. Files with no signals are counted, not listed.
7. **Write the report** to `<target root>/YYYY-MM-DD-AI-CREATED-CHECK.md` using today's date (`date +%F`). If it exists, overwrite it. Use the template exactly.
8. **Reply** with the report path, the verdict, counts per level plus excluded, and a note that the report is an untracked file the user may want to commit or ignore. Do not edit `.gitignore`. Do not paste the whole report.

## Reporting Rules

- Report on **files and commits**, not people. Do not rank, score, or summarize contributors by AI usage. Commit SHAs are fine; author names appear only when they are themselves the evidence (e.g. a bot account like `copilot-swe-agent[bot]`).
- Quote the exact evidence (trailer line, header text, code excerpt) with `file:line` or commit SHA.
- Do not count the report file itself, or files this skill created, as evidence.
- Exclude vendored and generated code (`node_modules`, `vendor`, `dist`, `build`, lockfiles, codegen output such as `*.pb.go`, `*_generated.*`); tool-generated is not AI-generated.

## Report Template

```markdown
# AI-Created Check - YYYY-MM-DD

- **Target:** <path>
- **Commit:** <sha or "not a git repo"> on <branch>
- **History window:** <full / last N commits / none>
- **Verdict:** <VERDICT>

## Summary

<2-4 sentences: strongest evidence, which tools appear to be involved, roughly what share of files is affected, and the main limitation.>

| Confirmed | Likely | Possible | No evidence | Files scanned | Excluded |
|---|---|---|---|---|---|
| n | n | n | n | n | n |

## AI Tools Detected

| Tool | Evidence type | Where |
|---|---|---|

## Repository Context

<R1 findings: AI config/instruction files present, or "none found".>

## AI-Marked Commits

| Commit | Date | Evidence | Files changed |
|---|---|---|---|

## File Results

### <path/to/file>
- **Level:** <Confirmed | Likely | Possible>
- **Signals:** <IDs, e.g. H1, S2, S3>
- **Evidence:**
  - <quote + location for each signal>

<repeat per flagged file, ordered Confirmed -> Likely -> Possible>

## Limitations

AI-assisted code often leaves no trace; this check cannot detect unmarked AI use and cannot prove human authorship. Stylistic signals also occur in human-written code. <Add scope-specific limits: shallow clone, squashed history, rewritten commits, binary files skipped, etc.>
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling a file "human-written" | Use "No evidence". |
| Marking a file Confirmed from style alone | Confirmed needs a hard signal. |
| Treating `CLAUDE.md` / `.cursor/` as proof every file is AI-made | That is repo context (R1); it never sets a file's level. |
| Flagging codegen output (protobuf, OpenAPI clients, migrations) | Tool-generated is not AI-generated; exclude it. |
| One soft signal reported as Likely | Likely needs 3+ soft signals across 2+ categories. |
| Per-developer AI scores | Report on files and commits, not people. |
