# Essential Automation Files Catalog

One entry per automation file. Each lists its purpose (copy it into the report), the accepted names and locations, what to read in it, and when it is Incomplete.

## Finding the files

Names are matched case-insensitively. This lists every candidate in one go:

```bash
find <target> -maxdepth 1 -type f 2>/dev/null | grep -iE '/(gnu)?makefile$|/(justfile|taskfile\.ya?ml)$|/(\.gitlab-ci\.ya?ml|jenkinsfile|azure-pipelines\.ya?ml|\.travis\.ya?ml|bitbucket-pipelines\.yml)$|/(renovate\.json5?|\.renovaterc(\.json)?)$|/pull_request_template\.md$'
find <target>/.github -maxdepth 3 2>/dev/null
find <target>/.circleci <target>/docs -maxdepth 1 -type f 2>/dev/null
```

Then keep only the paths each entry accepts. Other near matches (e.g. `.github/workflow/ci.yml`, `.github/dependabot.yml.disabled`) are Missing, with the path in the notes.

In a git repo, also check whether each found file is tracked. GitHub only uses files that are committed:

```bash
git -C <target> ls-files --error-unmatch <path>      # exit 0 = tracked
```

## Detecting the repo's ecosystems

C1 and C3 need to know what the repo builds. Look for these files anywhere outside `node_modules`, `vendor`, `.venv`, `dist`, and `build` (`git -C <target> ls-files` in a git repo):

| File | Ecosystem | Dependabot `package-ecosystem` |
|---|---|---|
| `package.json` | Node.js | `npm` |
| `requirements*.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python | `pip` |
| `go.mod` | Go | `gomod` |
| `Cargo.toml` | Rust | `cargo` |
| `Gemfile` | Ruby | `bundler` |
| `pom.xml` | Java (Maven) | `maven` |
| `build.gradle`, `build.gradle.kts` | Java/Kotlin (Gradle) | `gradle` |
| `composer.json` | PHP | `composer` |
| `*.csproj`, `*.sln` | .NET | `nuget` |
| `Dockerfile`, `*.dockerfile` | Docker | `docker` |
| `.github/workflows/*.yml` | GitHub Actions | `github-actions` |

Other CI files (`.gitlab-ci.yml` etc.) and container images named inside CI (`image: python:3.12`) are not ecosystems. Dependabot's `directory` values are not checked against where the manifests live; only the ecosystem name is.

## C1 - .github/workflows/*.yml

- **Tier:** Essential.
- **Purpose:** GitHub Actions workflows run automation on every push and pull request: building the code, running tests and linters, and deploying. They catch broken changes before they are merged and make releases repeatable.
- **Accepted names:** `.github/workflows/*.yml` and `.github/workflows/*.yaml`. A different CI system also satisfies C1, with the system named in the notes: `.gitlab-ci.yml`, `.circleci/config.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `.travis.yml`, `bitbucket-pipelines.yml`. Judge all files found together, as one item.
- **Read for:** for each workflow file, its `name`, its triggers (`on:`), its jobs, and what they run (build, test, lint, deploy, release). Name the test and build commands found (e.g. `npm test`, `pytest`, `go test ./...`, `cargo test`, `mvn test`, `make test`).
- **Incomplete if:** no workflow both runs on code changes and runs a build, test, or lint command. A repo with only scheduled, manual (`workflow_dispatch`), or release workflows is Incomplete.
  - **Runs on code changes:** GitHub `push`, `pull_request`, or `pull_request_target`; GitLab with no `rules`/`only`, or rules matching `merge_request_event` or branch pipelines; for other systems, any push or pull/merge request trigger (CircleCI, Jenkins, Travis, Bitbucket run on push by default).
  - **Build, test, or lint command:** a command whose name says it builds, tests, or lints (`npm test`, `npm run build`, `pytest`, `go test`, `go build`, `cargo test`, `mvn verify`, `make test`, `eslint`, `ruff`, ...). Installing dependencies alone (`npm ci`, `pip install`) does not count. The command does not have to work: a `make test` with no `test` target still counts here and is reported under C2.
- **Security notes (GitHub Actions only; never change the status):** a workflow using `pull_request_target` together with `actions/checkout` of the pull request head (`ref: ${{ github.event.pull_request.head.sha }}` or `head.ref`), since that runs untrusted code with write access; and any workflow that has neither a top-level `permissions:` key nor one on each of its jobs, since it gets the repo's default token permissions. For other CI systems write "not checked (not GitHub Actions)". Report no other observations as notes.

## C2 - Makefile

- **Tier:** Recommended.
- **Purpose:** Gives every developer and the CI the same short commands for common tasks (`make build`, `make test`, `make lint`), so nobody has to remember long tool invocations and CI runs exactly what developers run locally.
- **Accepted names (root only):** `Makefile`, `makefile`, `GNUmakefile`. A `justfile` or `Taskfile.yml` also satisfies C2, with the tool named in the notes.
- **Read for:** the list of targets (`grep -nE '^[A-Za-z0-9_.-]+:' Makefile`), and whether it has `test`, `build`, `lint`, and `help` targets.
- **Incomplete if:** a CI file (any file C1 accepts) or the README calls a target that the file does not define (e.g. a workflow runs `make test` and there is no `test:` target). For a `justfile` or `Taskfile.yml`, look for `just <target>` or `task <target>` instead. This form also works in zsh when some paths do not exist:

```bash
find <target>/.github/workflows <target>/.gitlab-ci.yml <target>/.circleci <target>/Jenkinsfile <target>/azure-pipelines.yml <target>/.travis.yml <target>/bitbucket-pipelines.yml <target> -maxdepth 1 -type f \( -name '*.y*ml' -o -name 'Jenkinsfile' -o -iname 'README*' \) 2>/dev/null \
  | xargs grep -hoE '(make|just|task) [A-Za-z0-9_.-]+' 2>/dev/null | sort -u
```

## C3 - .github/dependabot.yml

- **Tier:** Essential.
- **Purpose:** Configures Dependabot to open pull requests that keep dependencies and GitHub Actions up to date, including security fixes. Without it, known-vulnerable dependency versions stay in place until someone notices.
- **Accepted names:** `.github/dependabot.yml`, `.github/dependabot.yaml`. A Renovate config also satisfies C3, with the tool named in the notes: `renovate.json`, `renovate.json5`, `.renovaterc`, `.renovaterc.json`, `.github/renovate.json`, `.github/renovate.json5`.
- **Read for:** Dependabot: `version: 2`, and each `updates` entry's `package-ecosystem`, `directory`, and `schedule.interval`. Renovate: `extends`, `enabledManagers`, `schedule`, and the number of `packageRules`.
- **Incomplete if:** Dependabot: `version: 2` is missing, or an ecosystem the repo uses (table above) has no `updates` entry; list the uncovered ecosystems. Renovate: only if `enabledManagers` is set and leaves out an ecosystem the repo uses.
- **Not applicable:** when the repo uses none of the ecosystems in the table above (so it also has no GitHub Actions workflows).

## C4 - .github/ISSUE_TEMPLATE/*.yml

- **Tier:** Recommended.
- **Purpose:** Issue forms give bug reports and feature requests a fixed structure (steps to reproduce, expected and actual behaviour, version), so maintainers get the information they need the first time.
- **Accepted names:** `.github/ISSUE_TEMPLATE/*.yml` and `*.yaml`, other than `config.yml`. Markdown templates (`.github/ISSUE_TEMPLATE/*.md`, or a single `.github/ISSUE_TEMPLATE.md`, `ISSUE_TEMPLATE.md`, or `docs/ISSUE_TEMPLATE.md`) also satisfy C4, with the notes saying they are Markdown templates rather than forms. `config.yml` on its own does not satisfy C4.
- **Read for:** the name of each template, and what it asks for. Mention `config.yml` in Contents (or in Notes when C4 is Missing), with its `blank_issues_enabled` value; never list it under Path(s).
- **Incomplete if:** a `.yml` form lacks any of the top-level keys GitHub requires for a form (`name`, `description`, `body`). Name the file and the missing key.

## C5 - .github/PULL_REQUEST_TEMPLATE.md

- **Tier:** Recommended.
- **Purpose:** Pre-fills every pull request description with the sections the project expects (what changed, why, how it was tested, a checklist), so reviewers get context and authors remember the required steps.
- **Accepted names (`.github/`, root, `docs/`):** `PULL_REQUEST_TEMPLATE.md`, `pull_request_template.md`, or a folder `.github/PULL_REQUEST_TEMPLATE/` holding one or more `.md` files.
- **Read for:** its sections (e.g. description, related issue, testing, checklist).
- **Incomplete if:** it contains a leftover template placeholder (see the Placeholders rule in `SKILL.md`). HTML comments (`<!-- ... -->`) with guidance for the author are normal and are not placeholders.

## C6 - .github/labeler.yml

- **Tier:** Recommended.
- **Purpose:** Configures the `actions/labeler` workflow, which adds labels to pull requests based on the files they change (e.g. `docs`, `frontend`, `ci`). It makes pull requests easy to triage and filter.
- **Accepted names:** `.github/labeler.yml`, `.github/labeler.yaml`.
- **Read for:** the labels it defines and the paths each one matches, and the workflow that runs `actions/labeler` (with its version tag).
- **Incomplete if:** no workflow uses `actions/labeler` (the file does nothing alone), or a workflow uses `actions/labeler@v5` or later while the config has no `changed-files` key (the v4 format, which v5 does not read).

```bash
grep -rnE 'uses:\s*actions/labeler@' <target>/.github/workflows
```
