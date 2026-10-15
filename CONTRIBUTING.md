# Contributing

Thanks for helping improve these skills. By contributing, you agree that your work is licensed under the [MIT License](LICENSE), and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Bug or false positive/negative in a report:** open an issue. Include the skill, the agent and model you used, and a minimal snippet that reproduces it.
- **Security issue:** follow [SECURITY.md](SECURITY.md). Do not open a public issue.
- **New skill or change to a skill:** open a pull request as described below.

## Skill layout

Each skill lives in its own folder, named in lowercase with hyphens:

```
my-skill/
  SKILL.md       # required
  <reference>.md # optional: detailed catalog of checks/signals
```

`SKILL.md` starts with YAML frontmatter:

```yaml
---
name: my-skill
description: Use when <the situations that should trigger this skill>
---
```

- `description` says only **when** to use the skill. Do not summarize the workflow in it; agents may follow the summary instead of the full skill.
- The body covers an overview, the workflow steps, any rating rules, the exact output template, and common mistakes.
- Keep detailed catalogs in a separate reference file and refer to entries by ID. Keep the IDs consistent across `SKILL.md`, the reference file, and the README.

## Rules for audit skills

- Read-only on the target. The only file a skill writes is a dated report at the target root, named `YYYY-MM-DD-<NAME>-CHECK.md`.
- Never edit the target's `.gitignore`, and never run code from the audited repository.
- A search match is not a finding. Findings quote evidence with `file:line` or a commit SHA.
- Rating rules are explicit thresholds, so that different agents reach the same result.
- Agent-neutral: use only file reading, search, and standard shell tools (`git`, `grep`, `date`). Do not depend on one agent's tools.

## Testing a change

There is no test suite. Test each skill change like this:

1. Build a small fixture repo outside this repository, with issues planted that the skill should catch, plus clean files it should not flag.
2. Have a fresh agent session follow the skill against the fixture, without telling it what was planted.
3. Compare its report with what you planted. Ask the agent to list any instructions that were unclear or contradictory, and fix them.
4. Describe the fixture and the result in your pull request.

## Pull request checklist

- [ ] Skill folder follows the layout above
- [ ] Tested against a fixture as described above
- [ ] `README.md` updated: the Skills table, a section on the skill, and the Report files section if the skill writes a report
- [ ] `.gitignore` updated with the report pattern, if any
- [ ] `sbom.cdx.json` regenerated if skill files changed
- [ ] Commits are focused, and messages explain why
