# Core Repo Files Catalog

One entry per core file. Each lists its purpose (copy it into the report), the accepted names and locations, and what to read in it.

## Finding a file

Each entry lists its accepted locations. Search them in this order: target root, then `.github/`, then `docs/`. GitHub reads `CONTRIBUTING`, `CODE_OF_CONDUCT`, and `SECURITY` from any of those three places. Names are matched case-insensitively. This lists every candidate in one go; then keep only those in a location the file's entry accepts (others go in the notes as near matches):

```bash
find <target> <target>/.github <target>/docs -maxdepth 1 -type f 2>/dev/null \
  | grep -iE '/(readme|licen[cs]e|copying|unlicense|\.gitignore|\.?env[._-]?(example|sample|template|dist)|example\.env|contributing|code[_-]of[_-]conduct|security|changelog|changes|history|news|releases|bom|[^/]*\.cdx|[^/]*\.spdx|sbom)[^/]*$'
```

In a git repo, also check whether each found file is tracked, since an untracked file is not shared with anyone who clones the repo:

```bash
git -C <target> ls-files --error-unmatch <path>      # exit 0 = tracked
git -C <target> check-ignore -q <path>               # exit 0 = ignored
```

Only the accepted names below count. A file with a different name (e.g. `LICENCE_NOTES.txt`, `contrib.txt`) is Missing, with the near match mentioned in the notes.

## F1 - README.md

- **Purpose:** The entry point of the repository. Explains what the project is, how to install and use it, and where to find more. It is the page hosting sites show first.
- **Accepted names (root only):** `README.md`, `README`, `README.rst`, `README.txt`, `README.adoc`.
- **Read for:** project name and description, install steps, usage, links to the other core files.

## F2 - LICENSE

- **Purpose:** States the legal terms under which others may use, copy, change, and share the code. Without one, default copyright applies and nobody else has the right to reuse the code.
- **Accepted names (root only):** `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `LICENCE` (and the same with `.md` / `.txt`), `COPYING`, `COPYING.md`, `UNLICENSE`.
- **Read for:** the license name (e.g. MIT, Apache-2.0, GPL-3.0, proprietary), and the copyright holder and year.
- **Incomplete if:** the license name cannot be identified from the text.

## F3 - .gitignore

- **Purpose:** Tells git which files never to track: build output, dependencies, local settings, and secrets such as `.env`. It keeps the repository clean and stops secrets from being committed by accident.
- **Accepted names (root only):** `.gitignore`.
- **Read for:** what kinds of files it ignores, and whether it ignores `.env` (`grep -nE '^\s*/?\.env' .gitignore`). If `.env.example` is Present but `.env` is not ignored, note it.

## F4 - .env.example

- **Purpose:** Lists every environment variable the project needs, with placeholder values, so a new developer can copy it to `.env` and fill in their own values. It documents configuration without committing real secrets.
- **Accepted names (root only):** `.env.example`, `.env.sample`, `.env.template`, `.env.dist`, `example.env`, `env.example`.
- **Read for:** the number of variables, and whether any value looks like a real secret. Report only the variable name, never the value.
- **Real secret:** a value with a known key prefix (`sk-`, `sk_live_`, `ghp_`, `github_pat_`, `xox[bp]-`, `AKIA`, `AIza`), a `-----BEGIN ... PRIVATE KEY-----` block, or any random-looking string of 20+ letters and digits. **Not a secret:** empty values, values made of placeholder words (`password`, `changeme`, `secret`, `example`, `your_...`, `xxx`, `<...>`, `...`), and connection strings whose only credential is such a word (`postgres://user:password@localhost/db`).
- **Not applicable:** when the project reads no environment variables. Decide with this search; if it returns no source-code match (outside tests, `node_modules`, `vendor`, and docs), use Not applicable and say so:

```bash
git -C <target> grep -I -nE 'process\.env|import\.meta\.env|os\.environ|os\.getenv|getenv\(|ENV\[|ENV\.fetch|System\.getenv|Environment\.GetEnvironmentVariable|env::var|dotenv' -- ':!*.md' ':!docs/' ':!node_modules/' ':!vendor/' ':!test/' ':!tests/' ':!*test*' ':!*spec*'
```

  If not a git repo, run the same pattern with `grep -rnE ... --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=docs --exclude-dir=test --exclude-dir=tests --exclude='*.md' --exclude='*test*' --exclude='*spec*' <target>`. A `docker-compose.yml` with an `environment:` or `env_file:` key also counts as reading environment variables.

## F5 - CONTRIBUTING.md

- **Purpose:** Tells outside contributors how to help: how to report bugs, set up the project, run tests, follow code style, and open a pull request. It lowers the effort of a first contribution and sets expectations.
- **Accepted names (root, `.github/`, `docs/`):** `CONTRIBUTING.md`, `CONTRIBUTING`, `CONTRIBUTING.rst`, `CONTRIBUTING.txt`.
- **Read for:** which of these it covers: issue reporting, setup, tests, style, pull request process.

## F6 - CODE_OF_CONDUCT.md

- **Purpose:** Sets the standards of behaviour for everyone in the project's community, and says how to report unacceptable behaviour and how reports are handled.
- **Accepted names (root, `.github/`, `docs/`):** `CODE_OF_CONDUCT.md`, `CODE_OF_CONDUCT`, `CODE-OF-CONDUCT.md`, `CODE_OF_CONDUCT.rst`, `CODE_OF_CONDUCT.txt`.
- **Read for:** whether it is based on a known text (e.g. Contributor Covenant and its version), and whether it gives a real contact for reports.
- **Incomplete if:** it gives no contact for reports (a leftover `[INSERT CONTACT METHOD]` counts as none).

## F7 - SECURITY.md

- **Purpose:** Tells people how to report a security vulnerability privately instead of in a public issue, and which versions receive security fixes.
- **Accepted names (root, `.github/`, `docs/`):** `SECURITY.md`, `SECURITY`, `SECURITY.rst`, `SECURITY.txt`.
- **Read for:** a private reporting channel (email, GitHub private vulnerability reporting, a form), supported versions, and the expected response time.
- **Incomplete if:** it gives no private reporting channel.

## F8 - CHANGELOG.md

- **Purpose:** A human-readable, dated list of notable changes in each release, so users can see what changed before they upgrade.
- **Accepted names (root, `docs/`):** `CHANGELOG.md`, `CHANGELOG`, `CHANGELOG.rst`, `CHANGELOG.txt`, `CHANGES.md`, `CHANGES`, `HISTORY.md`, `HISTORY`, `NEWS.md`, `NEWS`, `RELEASES.md`.
- **Read for:** the format (e.g. Keep a Changelog), the latest version and date listed, and whether it has entries.
- **Incomplete if:** no section lists at least one change. An empty `## [Unreleased]` heading does not count.

## F9 - sbom.cdx.json

- **Purpose:** A Software Bill of Materials in CycloneDX JSON format. It lists every component and dependency in the project, with versions and hashes, so users can check licenses, track known vulnerabilities, and verify what they installed.
- **Accepted names (root, `.github/`, `docs/`):** `sbom.cdx.json`, `bom.json`, `*.cdx.json`. An SPDX SBOM (`sbom.spdx.json`, `*.spdx`, `*.spdx.json`) counts as Present, with the format noted.
- **Read for:** the format and spec version (`bomFormat`, `specVersion`), the number of components, and the `metadata.timestamp`. If the timestamp is older than the latest commit that changed a dependency manifest (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, etc.), note that it may be out of date. If the command prints nothing (no manifests, or not a git repo), write "no dependency manifest to compare". An SBOM with 0 components is still Present; mention the count in Contents:

```bash
git -C <target> log -1 --format=%cs -- package.json requirements.txt pyproject.toml go.mod Cargo.toml pom.xml build.gradle Gemfile composer.json
```
