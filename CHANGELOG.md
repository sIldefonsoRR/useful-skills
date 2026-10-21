# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project has not yet tagged a release, so changes accumulate under Unreleased.

## [Unreleased]

### Added

- **owasp-code-check** skill: reviews source code against the OWASP Top 10:2025 (checks O0–O10, mapped to A01–A10), ranks each finding Critical–Info with deterministic rules, and writes a dated report with `file:line` evidence, source-to-sink paths, and a prioritized (P0–P3) next-actions table. Read-only; never runs the app, tests, or scanners.
- **obfuscation-check** skill: detects obfuscated, packed, or deliberately unreadable Python — tool markers, encoded blobs reaching `exec`/`eval`/`compile`, bytecode-only modules, freezer artifacts (hard signals B1–B4), and mangled names, constant codification, control-flow flattening, dynamic execution (soft signals B5–B8). Levels Confirmed/Likely/Possible/No evidence, written to a dated report. Read-only; never runs, imports, decodes, or deobfuscates the target.

### Fixed

- `_scripts/generate_sbom.py` now exits with a clear message naming the offending `SKILL.md` when its frontmatter has no `description:` line, instead of crashing with an unqualified `AttributeError`.
