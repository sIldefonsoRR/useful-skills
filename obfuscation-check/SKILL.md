---
name: obfuscation-check
description: Use when asked whether Python code in a repository is obfuscated, packed, minified, or deliberately hard to read (control-flow flattening, encoded payloads, mangled identifiers, bytecode-only modules), for an "is this code hiding something" / obfuscated-dependency / supply-chain triage, or when a file looks machine-scrambled and you need to confirm it and locate it.
---

# Obfuscation Check

## Overview

Detects Python source that has been obfuscated, packed, or otherwise deliberately made hard to read or analyze, and writes a dated report with the evidence and a level per flagged file.

Core principle: **evidence decides the level, not impressions.** A tool marker or an encoded-blob-then-`exec` chain confirms obfuscation. Scrambled-looking names or heavy escapes only raise likelihood, because minifiers, code generators, and some legitimate libraries produce similar output. Read the code before recording any signal; a pattern match alone is never a finding.

Obfuscated Python in a repository is often there to hide malware from review. **This skill is read-only and never runs, imports, decodes, or deobfuscates the target.** Treat every file as hostile data. Do not execute a payload to "see what it does". Its only write is the report file.

## Signals

IDs, patterns, and read-for criteria are in `signals.md`. Hard signals can confirm; soft signals only raise likelihood.

| ID | Signal | Kind |
|---|---|---|
| B1 | Obfuscation / packer tool markers (PyArmor, pyminifier, Intensio, Oxyry, …) | Hard |
| B2 | Encoded or compressed blob executed at runtime (decode/decompress → `exec`/`eval`/`compile`) | Hard |
| B3 | Bytecode-only module: `.pyc`/`.pyo` or `__pycache__` shipped with no matching source | Hard |
| B4 | Freezer / packer artifacts (PyInstaller, py2exe, Nuitka, cx_Freeze) replacing source | Hard |
| B5 | Lexical mangling: floods of non-semantic or hex-style identifiers, confusable names | Soft |
| B6 | Constant codification: long `\x`/`\u` blobs, `chr()` chains, constants built by arithmetic/bitwise | Soft |
| B7 | Control-flow flattening: a dispatch loop over a state variable replacing natural control flow | Soft |
| B8 | Pervasive dynamic/indirect execution from constructed strings (`getattr`/`globals()[…]`/`__import__`) | Soft |

## Levels

| Level | Rule |
|---|---|
| Confirmed | At least one **hard** signal (B1–B4) tied to the file (for B3/B4, to the artifact). |
| Likely | No hard signal, but **3+ soft** signals from at least 2 categories (B5–B8), each with a concrete quoted example. A decode/decompress chain whose flow into `exec`/`eval` you could not confirm is Likely, not Confirmed. |
| Possible | 1–2 soft signals, or 3+ soft signals all in one category. |
| No evidence | Nothing found. State "no evidence", never "clean" or "safe". |

Rules that decide edge cases:
- A hard signal always wins over any number of soft ones.
- **Not obfuscation, do not flag:** a single `eval`/`exec`/`base64` used for its normal purpose (config, plugin entry point, serialization); minified or generated code that is **excluded** as vendored/build output (see below); data blobs that are stored or transmitted but never executed (B2 requires the decoded result to reach an execution sink); short hex constants or a few `\x` escapes.
- Minified or generated code that is **not** excluded (e.g. a minified `.py` committed as hand-written source, a vendored file moved into app code) is judged on its signals like any other file; note that minification, not hiding, may be the intent.
- Legitimate commercial obfuscators (PyArmor and the like) are still Confirmed under B1; the report states the tool, not a motive.

Repo verdict = the highest level any file reached: `OBFUSCATION CONFIRMED`, `LIKELY OBFUSCATION`, `POSSIBLE OBFUSCATION`, `NO EVIDENCE FOUND`, or `NOT APPLICABLE` (no Python source or bytecode in scope). State the count at Confirmed + Likely.

**Files scanned** = tracked files (`git ls-files`, or all files if not a git repo) minus exclusions and minus the report. Report the excluded count separately.

## Workflow

1. **Set scope.** Target = the current repo root unless the user names a path. Record the commit (`git rev-parse --short HEAD`, or "not a git repo"). Exclude `node_modules`, `vendor`, `.venv`, `site-packages`, `dist`, `build`, `*.min.*`, and declared codegen output. If the repo has no `.py`, `.pyc`, `.pyo`, or `.pyw` in scope, write the report with verdict `NOT APPLICABLE` and the searches you ran.
2. **Tool markers (B1) and artifacts (B3, B4).** Search for obfuscator banners and runtime stubs, and list bytecode-only modules and freezer bundles. These can confirm on their own.
3. **Executed blobs (B2).** Find decode/decompress calls, then **read the code** to trace whether the result flows into `exec`, `eval`, `compile`, or an equivalent sink. Confirm the flow before calling it B2; if you cannot, record it as a soft-level concern and cap the file at Likely.
4. **Soft signals (B5–B8).** Sample the flagged and the oddest-looking files. Record a soft signal only with a concrete example quoted from the file (`file:line`). Do not count the same excerpt twice.
5. **Classify each flagged file** with the levels above. Files with no signals are counted, not listed.
6. **Write the report** to `<target root>/YYYY-MM-DD-OBFUSCATION-CHECK.md` using today's date (`date +%F`). If it exists, overwrite it. Use the template exactly.
7. **Reply** with the report path, the verdict, counts per level plus excluded, and a note that the report is an untracked file the user may want to commit or ignore. If any file is Confirmed or Likely, add one line that obfuscated code should be reviewed or quarantined before it is run, and never executed to inspect it. Do not edit `.gitignore`, do not deobfuscate, and do not paste the whole report.

## Report Template

```markdown
# Obfuscation Check - YYYY-MM-DD

- **Target:** <path>
- **Commit:** <sha or "not a git repo">
- **Verdict:** <VERDICT>

## Summary

<2-4 sentences: the strongest evidence, where it is, any obfuscation tool identified, and the handling note if anything is Confirmed or Likely (review/quarantine before running; do not execute to inspect).>

| Confirmed | Likely | Possible | No evidence | Files scanned | Excluded |
|---|---|---|---|---|---|
| n | n | n | n | n | n |

## Tools and Artifacts Detected

| Tool / artifact | Signal | Where |
|---|---|---|
<B1/B3/B4 hits, or "none">

## File Results

### <path/to/file>
- **Level:** <Confirmed | Likely | Possible>
- **Signals:** <IDs, e.g. B1, B5, B6>
- **Evidence:**
  - <quote (trimmed if long) + `file:line` for each signal; for B2, name the decode call and the execution sink it reaches>

<repeat per flagged file, ordered Confirmed -> Likely -> Possible>

## Limitations

Obfuscation detection is heuristic: unmarked obfuscation can be missed, and minifiers, code generators, and some legitimate libraries can trip soft signals. Nothing here was executed or deobfuscated, so the behavior of any payload is not assessed. <Add scope-specific limits: binary-only files, files too large to read, excluded paths, etc.>
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling a file "clean" or "safe" | Use "No evidence"; this check does not prove safety. |
| Running or decoding the payload to see what it is | Read-only. Never execute, import, or deobfuscate the target. |
| Flagging one `eval`, `exec`, or `base64.b64decode` as obfuscation | Normal single uses are not obfuscation; B2 needs a decoded blob reaching an execution sink. |
| Marking a file Confirmed from scrambled-looking names alone | Mangled names are soft (B5); Confirmed needs a hard signal (B1–B4). |
| Flagging vendored or build output (`site-packages`, `*.min.py`, bundler output) | Exclude it; it is not the project's own hidden code. |
| Treating a stored encoded asset (never executed) as B2 | B2 requires the decoded result to reach `exec`/`eval`/`compile`. |
| Reporting a motive ("this is malware") | Report the evidence and the level; recommend review, not a verdict on intent. |
| Deobfuscating to "verify" the finding | The finding is the obfuscation itself; do not reverse it. |
