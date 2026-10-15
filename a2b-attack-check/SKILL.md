---
name: a2b-attack-check
description: Use when auditing a codebase for Agent-to-Backend (A2B) attack risk - code where LLMs, AI agents, MCP servers, or function/tool calling can reach backend APIs, databases, shells, files, or network. Triggers include "A2B check", "agent security audit", "prompt injection to tool call", "excessive agency", "is my agent safe to ship".
---

# A2B Attack Check

## Overview

An **Agent-to-Backend (A2B) attack** is any path where an attacker influences an AI agent (directly, or via content the agent reads) and the agent then performs a backend action the attacker could not perform directly: data access, writes, command execution, outbound requests, or privilege use.

Core principle: **treat every LLM output as attacker-controlled input, and every tool as a privilege boundary.** A finding is a concrete path from an untrusted source, through the agent, to a backend sink, with a missing or weak control along the way.

This skill is read-only on the target code. Its only write is the report file.

## Workflow

1. **Set scope.** Target = the current repo root unless the user names a path. Record the git commit (`git rev-parse --short HEAD`, or "not a git repo").
2. **Inventory the agent surface** (check A0 in `checks.md`). List every LLM client, agent loop, tool/function definition, MCP server/client, and the endpoints that invoke them. If nothing is found, still write the report with verdict `NOT APPLICABLE` and the searches you ran.
3. **Run checks A1-A12** from `checks.md` against that inventory. For each check, run its searches, then **read the surrounding code** before deciding. A grep hit alone is never a finding.
4. **Trace each candidate finding** source -> agent -> tool -> sink. Record `file:line` for each hop you confirmed. If a hop is unconfirmed, mark the finding `Needs verification` instead of dropping or inflating it.
5. **Group findings by root cause.** One vulnerable tool/code path = one finding, listing every check it fails (e.g. `A2, A4, A5`). Report a second, lower-severity path separately only if it needs its own fix. Issues that do not involve the agent (e.g. a plain SSRF in the endpoint) are reported as `Info` with "outside A2B scope" unless their output feeds the agent.
6. **Rate severity** with the table below.
7. **Write the report** to `<target root>/YYYY-MM-DD-A2B-CHECK.md` using today's date (`date +%F`). If the file already exists, overwrite it (same-day rerun replaces). Use the template exactly.
8. **Reply** with the report path, the verdict, and the count per severity. Do not paste the whole report.

## Severity

| Severity | Meaning |
|---|---|
| Critical | Untrusted input can drive the agent to RCE, arbitrary SQL, auth bypass, or cross-tenant data access, with no effective control. |
| High | Same sinks but one weak/bypassable control, or high-impact write/delete/payment/email action without human confirmation. |
| Medium | Data exfiltration, SSRF to internal hosts, secret exposure to the model, or missing authz on lower-impact tools. |
| Low | Missing defense-in-depth: no rate/iteration limits, weak logging, unpinned tool deps. |
| Info | Observations and hardening suggestions with no current attack path. |

Adjustments:
- Agent endpoint reachable **without authentication** -> raise each finding on that path one level (max Critical) and state it in the attack path.
- Unauthenticated users can trigger **unbounded paid model calls** (A8) -> Medium, not Low.
- Secret that looks like a **placeholder** (e.g. `sk-...-123`, `changeme`) -> Low, noting it must not be replaced by a real key in source.

Verdict = highest severity found: `CRITICAL RISK`, `HIGH RISK`, `MEDIUM RISK`, `LOW RISK`, `NO ISSUES FOUND`, or `NOT APPLICABLE`.

## Report Template

```markdown
# A2B Attack Check - YYYY-MM-DD

- **Target:** <path>
- **Commit:** <sha or "not a git repo">
- **Verdict:** <VERDICT>

## Summary

<2-4 sentences: what the agent surface is, the most serious path found, the top fix.>

| Critical | High | Medium | Low | Info |
|---|---|---|---|---|
| n | n | n | n | n |

## Agent Surface Inventory

| Component | Type (LLM client / agent loop / tool / MCP server / endpoint) | Location | Privileges / reach |
|---|---|---|---|

## Findings

### A2B-001 - <short title>
- **Severity:** <Critical|High|Medium|Low|Info>
- **Checks:** <every check this fails, e.g. A2, A4, A5>
- **Status:** <Confirmed | Needs verification | N/A for Info>
- **Location:** `path/file.ext:line` (one per line if several)
- **Attack path:** <untrusted source> -> <agent/prompt> -> <tool> -> <backend sink> (or "N/A - detection/hardening gap")
- **Evidence:** <short code excerpt or description of what the code does>
- **Impact:** <what an attacker gains>
- **Fix:** <specific change>

<repeat per finding, ordered by severity>

## Check Results

| ID | Check | Result (Fail / Pass / Partial / N/A) | Notes |
|---|---|---|---|
| A0 | Agent surface inventory | Done | <n components> |
| A1 | ... | ... | <finding IDs, or what limited the review if Partial> |

## Limitations

<What was not reviewed: runtime config, deployed IAM policies, third-party MCP servers, prompts stored outside the repo, etc.>
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Reporting raw grep hits as findings | Read the code; a finding needs a traced path. |
| Trusting the system prompt as a control ("the prompt says never delete") | Prompts are not access control. Only code-level checks count. |
| Only checking direct user chat input | Indirect injection (web pages, files, emails, DB rows, tool results, other agents) is the main A2B vector. |
| Checking the tool, not the identity it runs as | A tool using a service account or admin key is a confused deputy even if the tool looks narrow. |
| Skipping the report when no agent code exists | Always write the file; `NOT APPLICABLE` is a valid result. |
| Fixing code during the audit | Read-only. Put fixes in the report. |
