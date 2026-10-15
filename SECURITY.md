# Security Policy

## Supported versions

Only the latest commit on `main` is supported. Fixes are not backported.

## Reporting a vulnerability

Do not open a public issue. Report privately through [GitHub private vulnerability reporting](https://github.com/sIldefonsoRR/useful-skills/security/advisories/new) (Security tab -> Report a vulnerability).

Please include:

- the skill and file affected (e.g. `a2b-attack-check/SKILL.md`)
- the agent and model you ran it with
- steps or a minimal fixture repo that reproduces the issue
- the impact you observed or expect

Reports are handled on a best-effort basis. You will get a reply on the advisory, and credit in the fix unless you ask otherwise.

## What counts as a vulnerability here

These skills are instructions that an AI agent follows on your machine, often against code you did not write. Report it if a skill:

- leads an agent to modify, delete, or write files outside the single report file the skill declares
- leads an agent to run commands that execute code from the audited repository, or that send data over the network
- can be hijacked by content in the audited repository (prompt injection in code comments, docs, or commit messages) so the agent follows those instructions instead of the skill
- puts secrets or personal data from the audited repository into the report beyond the minimal evidence needed
- has a supply-chain issue, such as a mismatch between the files and the hashes in `sbom.cdx.json`

Not in scope: false positives or missed findings in a report. Open a regular issue for those.

## Safe use

Treat any repository you audit as untrusted input. Run the skills with your agent's permission prompts enabled, and review the generated report before you share it.
