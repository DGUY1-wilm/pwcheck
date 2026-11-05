# AI Usage

This project was built with substantial help from an AI assistant. This file says exactly how, so anyone reviewing the repo (including employers) can judge the work accurately.

**Assistant:** Claude, Anthropic's AI assistant, used through the Claude desktop app.
**Scope:** the DevSecOps work in November 2026: pull requests #1–#6, #9 and #10 (#7 and #8 were opened by Dependabot), and release v0.2.0. The original pwcheck program (v0.1.0: entropy scoring, the HaveIBeenPwned lookup and its first 11 tests) existed before this work, and this document doesn't cover how it was written.

## Who did what

### What I (Daniel) did

- **Set the goals and the plan:** close the CI/CD, infrastructure-as-code and container gap in my resume; the six-stage plan; free tools only; and a requirement that I understand every piece well enough to explain it in an interview.
- **Made the decisions:** for example, choosing Terraform for GitHub settings over a cloud deployment in Stage 6, and closing the Dependabot PR that would have moved the container to an untested Python version.
- **Ran everything on my own machine and accounts:** every `git` command, branch, commit and push; every pull request, review and merge; every release tag.
- **Configured GitHub myself:** rulesets, Actions permissions, secret scanning and push protection, Dependabot settings, private vulnerability reporting, package visibility and access.
- **Handled every credential myself:** logging in with the GitHub CLI, creating the fine-grained token, and storing it as a repository secret.
- **Installed and set up the local tooling:** Docker Desktop, WSL, Terraform, the GitHub CLI.
- **Ran Terraform locally:** `init`, the provider lock file, `plan`, and the import `apply`.
- **Verified the results myself:** pulled and ran the published image, and checked the job logs and summaries in the GitHub UI.

### What the AI did

- **Wrote the first drafts of almost all new files:** the five workflows, the Dockerfile, `dependabot.yml`, the Terraform configuration, `SECURITY.md`, `.gitleaks.toml`, the README's CI/CD section and diagram, and this file and `GETTING_STARTED.md`.
- **Changed the application code:**
  - Added input validation to `fetch_range` in `hibp.py` (only exactly 5 hex characters can be sent).
  - Marked the SHA-1 call `usedforsecurity=False`.
  - Wrote formatting and type fixes.
  - Wrote new tests, taking the suite from 11 to 43 tests and branch coverage from 71% to 100%.
- **Researched and pinned versions:** looked up current releases, chose ones at least two weeks old, and resolved commit SHAs and checksums.
- **Tested before handing files over:**
  - Ran the linters, tests and scanners against the code in its own sandbox: actionlint, shellcheck, zizmor, Trivy, Gitleaks, Bandit, pip-audit, and schema validation.
  - Rendered the pipeline diagram to check it displays correctly.
- **Monitored CI and diagnosed failures:**
  - Read GitHub's public API and pages in a browser.
  - Found the misplaced workflow files, the stale release tag, the GHCR permission failure, and a scanner name mismatch in the ruleset.
- **Explained concepts and wrote prep material:** explained each security choice, and drafted resume bullets and practice interview answers. Those are a starting point; anything I use, I put in my own words.
- **Wrote files into my project folder** through the desktop app's file access, which I granted. Everything it wrote went through `git status` and a pull request before reaching `main`.

### What the AI did not do

- It **never pushed, merged, tagged or changed GitHub settings.** I did all of those.
- It **never handled credentials.** When I pasted a token into the chat by mistake, it refused to use it and told me to revoke it, which I did.
- It **didn't run anything against my GitHub account.** Its access to GitHub was read-only: public API and web pages.

## Mistakes along the way

Both of us made mistakes. Some of the AI's were caught by the pipeline it was helping to build:

| Mistake | Whose | How it was caught | Fix |
|---|---|---|---|
| A test was written using the word "password", which also appears in the API's web address, so the test failed | AI | The test run | Used a different test password |
| The release workflow used a dependency cache, a cache-poisoning risk (2 high-severity findings) | AI | **zizmor** scan | Cache removed from `release.yml` |
| Six places pasted workflow values straight into shell scripts (template-injection risk) | AI | **zizmor** scan | Moved into environment variables |
| Setup instructions used `git init` + `git reset` instead of `git clone`, so local `main` never tracked GitHub. Months-old code got the first `v0.2.0` tag | AI's instructions | The Release workflow didn't run; the AI traced the tag to the wrong commit | Fixed branch tracking, re-tagged |
| Downloaded files landed in a `Claude outputs` folder and were committed there twice, so workflows didn't run | Both | PR file lists | `.gitignore` entry; files written directly to the right place |
| A ruleset tool name was entered as `Gitleaks` instead of `gitleaks` | Me | AI read back the ruleset via the API | Corrected the name |
| A token pasted into the chat | Me | AI flagged it | Token revoked and replaced |

## How I made sure I understand it

- I asked for every file to come with an explanation of what each part does and why. I did the work stage by stage, one pull request at a time, rather than accepting one big generated drop.
- I ran each stage myself and watched its checks pass before merging.
- I debugged the real failures (the stale tag, the GHCR `denied` error, Docker needing WSL) with the AI's help, and learned what caused each one.
- The design choices I'm expected to be able to defend are: SHA pinning, least-privilege tokens, SARIF, non-root containers, `--ignore-unfixed`, build provenance, drift detection, and why `apply` isn't automated.

If you're reviewing this project, ask me about any file.
