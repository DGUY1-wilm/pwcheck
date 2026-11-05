# Getting Started

This guide has two parts:

- **[Part 1: Use pwcheck](#part-1-use-pwcheck)**: check a password on your own computer in a few minutes.
- **[Part 2: Build this project yourself](#part-2-build-this-project-yourself)**: a plain-language walkthrough of how this repo's automated testing, security scanning and release pipeline was built, so you can build the same thing for your own project.

No programming experience is needed for Part 1. Part 2 assumes you're willing to copy commands into a terminal and read what comes back; every term is explained in the [glossary](#glossary) at the end.

> **Safety first:** when testing, use throwaway passwords, never ones you actually use.

---

# Part 1: Use pwcheck

There are two ways to run it. **Option A** is easiest if you already have Docker. **Option B** needs only Python.

## Option A: Run it with Docker (nothing else to install)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and open it. Wait until the bottom-left corner says **Engine running**.
   - On Windows, if Docker says *"WSL not installed"*, open PowerShell **as Administrator**, run `wsl --install --no-distribution`, then **restart your computer** and open Docker Desktop again.
2. Open a terminal (on Windows: **PowerShell**; on Mac: **Terminal**) and run:
   ```
   docker run --rm -it ghcr.io/dguy1-wilm/pwcheck:latest
   ```
3. Type a password at the `Password:` prompt and press Enter. Nothing appears while you type; that's on purpose, so nobody can read it over your shoulder.

## Option B: Run it with Python

### What you need

- A computer (Windows, Mac, or Linux)
- Python 3.10 or newer. Check by opening a terminal and typing `python --version`. If you don't have it, download it from https://www.python.org/downloads/ (on Windows, tick **"Add Python to PATH"** during install).

### Step 1: Download the project

1. Go to https://github.com/DGUY1-wilm/pwcheck
2. Click the green **Code** button
3. Click **Download ZIP**
4. Unzip the file (right-click, then "Extract All" on Windows)

### Step 2: Open a terminal in the project folder

**Windows:** Open the unzipped folder in File Explorer, click the address bar at the top, type `powershell`, and press Enter.

**Mac:** Right-click the folder, then choose **New Terminal at Folder**.

**Linux:** Right-click inside the folder, then choose **Open in Terminal**.

Make sure the folder you're in contains a file called `pyproject.toml`.

### Step 3: Set up a virtual environment

This keeps the project separate from the rest of your computer.

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
```

**Mac / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` at the start of your terminal line.

### Step 4: Install the project

```
pip install -e .
```

### Step 5: Run it

```
pwcheck
```

Type a password and press Enter. Your result will look something like this:

```
Strength : [####----------------] Very weak
Entropy  : 10.0 bits (pool size 26, length 8)
Crack time (offline, fast hash): instantly
  ! This is a very common password.
  ! Shorter than 12 characters; length matters most.

Breach check: PWNED, seen 9,545,824 times in known breaches. Do not use it.
```

Only the first 5 characters of a scrambled version (hash) of your password are sent to the breach database. The password itself never leaves your computer. The [README](README.md#how-it-works) explains how.

### Step 6 (optional): Run the tests

```
pip install -e ".[dev]"
pytest -v
```

You should see every test pass, followed by a coverage table.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognized | Reinstall Python and tick "Add Python to PATH" |
| `source` not recognized (Windows) | Use `.venv\Scripts\activate` instead |
| `pwcheck` not recognized | Activate the virtual environment again (Step 3) |
| "Breach check: unavailable" | Your network or VPN is blocking the lookup. The strength score still works |
| `docker` not recognized | Docker Desktop isn't installed, or you need to open a new terminal window after installing it |
| `failed to connect to the docker API` | Docker Desktop isn't running. Open it and wait for **Engine running** |
| Docker says "Debug this container error" after a result | Not an error. pwcheck exits with code 2 when a password is breached (1 = weak, 0 = OK), and Docker notices the non-zero code |

---

# Part 2: Build this project yourself

pwcheck itself is small. What makes this repo a portfolio project is the **pipeline** around it: every change is automatically checked, scanned for security problems, packaged into a container, and released, and the rules protecting the project are themselves written as code.

This part walks through how that was built, in the same six stages, so you can do it for **your own** project. It's written from real experience: each stage has a **"What went wrong for me"** box with the actual problems hit while building this repo, and how they were fixed.

## Before you start

### The big idea, in plain language

Think of the pipeline as a factory line with inspectors:

1. You propose a change (a **pull request**).
2. Robots (**GitHub Actions**) automatically test it, check its style, and scan it for security problems.
3. A **rule** on the main branch refuses the change unless every inspector says OK.
4. When you're ready to ship, you put a version label on it (a **tag**), and another robot packages it, scans it one last time, and publishes it.

You never push changes straight to the main copy of the code. Everything goes through the line.

### What you'll need (all free)

| Tool | What it's for | How to get it |
|---|---|---|
| A **GitHub account** and a **public repository** | Where the code and the robots live. Public repos get the security features for free | https://github.com |
| **Git** | Sends your changes to GitHub | https://git-scm.com/downloads |
| **Python 3.10+** | Runs the project and its tests | https://www.python.org/downloads/ |
| **GitHub CLI** (`gh`) | Logging in to GitHub from the terminal | Windows: `winget install -e --id GitHub.cli` |
| **Docker Desktop** (Stage 3, optional) | Running the container on your own computer | https://www.docker.com/products/docker-desktop/ |
| **Terraform** (Stage 6, optional) | Managing GitHub settings as code | Windows: `winget install -e --id Hashicorp.Terraform` |

> **After installing any tool, close and reopen your terminal.** New tools aren't visible to terminal windows that were already open. This caused several "not recognized" errors while building this project.

> **Use a normal terminal, not "Run as Administrator".** Only install steps that ask for it need admin rights.

### The everyday routine (you'll repeat this for every change)

```
git switch main                      # go to the main copy
git pull                             # get the latest version from GitHub
git switch -c my-change-name         # make a new branch for your change
#  ...edit or add files...
git add -A                           # include all changes
git status                           # CHECK the list before committing
git commit -m "what you changed"
git push -u origin my-change-name    # send it to GitHub
```

Then open GitHub, click **Compare & pull request**, describe the change, and click **Create pull request**. Watch the checks; merge when they're green.

### Stage 0: Connect your folder to GitHub properly

**What:** make sure your local folder and GitHub are linked.

**How:** the simplest, safest way is to **clone** your repo instead of copying files around:

```
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
```

> **What went wrong for me:** the folder was set up with `git init` instead of `git clone`, so my local `main` branch wasn't linked to GitHub's. Every `git pull` on `main` quietly failed, and weeks later a release tag landed on a two-month-old commit. If `git pull` ever says *"There is no tracking information"*, fix it once with:
> ```
> git branch --set-upstream-to=origin/main main
> ```

> **What also went wrong:** files downloaded from an AI assistant landed in a `Claude outputs` folder instead of where they belonged, and got committed in the wrong place twice. **Always read `git status` before committing**, and add download folders to `.gitignore`.

---

## Stage 1: Quality gates (automatic checks on every change)

**What:** a robot that, on every pull request, checks code style (**ruff**), checks that types line up (**mypy**), runs the tests (**pytest**), and measures how much of the code the tests cover.

**Why it matters:** a check that *fails the build* can't be ignored the way a warning can. If coverage drops below a minimum, the change can't merge.

**Files in this repo to look at:**
- `.github/workflows/ci.yml`: the robot's instructions
- `pyproject.toml`: the tool settings (ruff rules, mypy strict mode, the coverage minimum `fail_under`)

**Steps:**
1. Copy those two files into your project and change names to match yours.
2. Run the same checks on your computer first:
   ```
   pip install -e ".[dev]"
   ruff check .
   ruff format --check .
   mypy
   pytest
   ```
3. Set `fail_under` a few points **below** the coverage number `pytest` reports, not an invented number.
4. Push on a branch and open a pull request.

**How to confirm it works:** the pull request shows the checks running, then green ticks. Then try to break it on purpose: add an unused `import os` to a file and push. The lint check should turn red. Remove it again.

**Key choices worth understanding:**
- `permissions: contents: read`: the robot's access key can only *read* your code.
- Tests must **never** call real websites. pwcheck's tests use a fake version of the breach database, so tests can't fail just because a website is down.

---

## Stage 2: Security scanning (the "Sec" in DevSecOps)

**What:** five scanners that look for different kinds of problems, and send what they find to your repo's **Security** tab:

| Scanner | Looks for |
|---|---|
| **Bandit** | Risky patterns in Python code |
| **CodeQL** | Deeper problems, by following how data moves through the code |
| **pip-audit** | Known vulnerabilities in the tools and libraries you use |
| **Gitleaks** | Passwords or keys accidentally saved anywhere in your project's history |
| **zizmor** (added in Stage 5) | Security mistakes in the robot instructions themselves |

**Files:** `.github/workflows/security.yml`, `.gitleaks.toml`, the `security` section of `pyproject.toml`.

**Steps:**
1. Copy the files and push them in a pull request.
2. On GitHub: **Settings → Advanced Security** (may be called **Code security**) → turn on **Secret Protection** and **Push protection**. Leave CodeQL on **Advanced setup** (don't pick "Default"; it clashes with the workflow).

**How to confirm:** all scanner checks go green, and the pull request shows extra checks named after each tool ("Code scanning results / Bandit" etc.). Those prove the results reached the Security tab.

> **What went wrong for me:** the scanners found things on their first run. Bandit flagged a web request, and Gitleaks found three "secrets" in old commits. **Both were false alarms**: the web address was fixed and safe, and the "secret" was the publicly known scrambled form of the word "password", used as an example. The fix was to check each one, then mark it as safe *with a written reason* (`# nosec B310` with a comment; an allowlist entry in `.gitleaks.toml`). Never just switch a scanner off.

---

## Stage 3: Put it in a container

**What:** a **Dockerfile** that packages the app with everything it needs, so it runs the same everywhere. A robot builds it, test-runs it, and scans it with **Trivy**.

**Files:** `Dockerfile`, `.dockerignore`, `.github/workflows/container.yml`.

**Key choices worth understanding:**
- **Two-stage build:** the first stage builds the app; the second stage contains only the finished app. Build tools never ship.
- **Runs as a normal user, not "root" (the all-powerful admin).** If someone broke in, they'd have very little power.
- **Base image pinned by its exact fingerprint (digest)**, so it can't change under you without a visible update.
- The build fails only on serious vulnerabilities **that have a fix available**. Failing on ones nobody can fix yet would keep the build permanently red, and people would learn to ignore it.

**How to confirm:** the **Build & scan image** check goes green. If you have Docker Desktop, you can also build and run it yourself:
```
docker build -t myapp .
docker run --rm -it myapp
```

> **What went wrong for me:** Docker on Windows needs **WSL** (a built-in Linux layer). Docker Desktop showed *"WSL not installed"*. The fix: `wsl --install --no-distribution` in an Administrator PowerShell, **restart the computer**, then open Docker Desktop and wait for **Engine running** before running any `docker` command.

---

## Stage 4: Automatic releases

**What:** when you put a version tag like `v0.2.0` on the code, a robot checks the tag, builds and scans the container, publishes it to **GitHub Container Registry**, signs a certificate of where it came from (**provenance**), and creates a **GitHub Release** with a changelog written from your pull request titles.

**Files:** `.github/workflows/release.yml`; the version number lives in one place, `src/pwcheck/__init__.py`.

**Steps:**
1. Merge the workflow and a version bump in a pull request.
2. Then tag the release **from an up-to-date `main`**:
   ```
   git switch main
   git pull
   git log --oneline -1          # make sure this is the latest merge
   git tag -a v0.2.0 -m "v0.2.0"
   git push origin v0.2.0
   ```
3. After the first release, open your profile → **Packages** → your package → **Package settings**: check it's **Public**, and under **Manage Actions access** that your repo has **Write**.

**How to confirm:** the **Releases** page shows the new version with files attached, and anyone can run your image with `docker run`. With the GitHub CLI you can check the signed certificate:
```
gh attestation verify oci://ghcr.io/YOUR-USERNAME/YOUR-REPO:0.2.0 --repo YOUR-USERNAME/YOUR-REPO
```
It should end with **Verification succeeded!**

**Why no passwords are stored:** the robot uses a temporary key that GitHub creates for each run and throws away afterwards.

> **What went wrong for me (twice):**
> 1. The tag went on an old commit (see Stage 0), so the release robot never ran. Always check `git log --oneline -1` before tagging.
> 2. The very first publish failed with `denied` while writing tags: the package didn't exist yet, so the repo didn't have permission on it. Once the package existed, clicking **Re-run failed jobs** worked.

---

## Stage 5: Lock the doors

**What:** rules that stop anyone (including you) from skipping the pipeline, and automatic updates for everything the project depends on.

**Files:** `.github/dependabot.yml`, plus every `uses:` line in the workflows now ends in a long code (a commit **SHA**) instead of `@v4`.

**Why pin to a SHA?** `@v4` is a label the tool's owner can move. If their account were hacked, everyone using `@v4` would run the attacker's code. A SHA is a fingerprint of one exact version and can't be moved. **Dependabot** then proposes updates for you each week, waiting 7 days after a new release in case it turns out to be bad.

**Settings to click on GitHub** (GitHub may ask you to confirm with an emailed code; that's normal):

1. **Settings → Rules → Rulesets → New branch ruleset**: name `protect-main`, **Active**, target **default branch**; tick *Restrict deletions*, *Block force pushes*, *Require a pull request* (0 approvals if you work alone; GitHub won't let you approve your own), *Require status checks* (add each check by its exact name), and *Require code scanning results* (type each tool name **exactly** as it appears in your checks, including lower/upper case).
2. **New tag ruleset**: name `protect-release-tags`, pattern `v*`; tick *Restrict updates*, *Restrict deletions*, *Block force pushes*. Leave *Restrict creations* off, or you can't make new releases.
3. **Settings → Actions → General**: workflow permissions **Read**; untick *Allow GitHub Actions to create and approve pull requests*.
4. **Settings → Advanced Security**: turn on Private vulnerability reporting, Dependabot alerts, Dependabot security updates, Grouped security updates, and Malware alerts.

**How to confirm:** open a pull request and you'll see **Required** next to each check, and the merge button stays grey until all are green.

> **What went wrong for me:**
> - A scanner name was typed as `Gitleaks` but the tool reports itself as `gitleaks`. Mismatched names can block every future pull request. Copy names exactly.
> - zizmor's first run found real problems in *my own* pipeline: a cache that could let a malicious pull request poison a release, and six places where outside text was pasted straight into commands. All were fixed. Scan your pipeline, not just your code.
> - **Not every Dependabot update should be merged.** It proposed moving the container to a brand-new Python version that the tests don't cover yet. That one was closed, and `dependabot.yml` now only allows patch updates for the base image.

---

## Stage 6 (optional): Settings as code with Terraform

**What:** the rules from Stage 5 written as code in `infra/github/`, so changing a rule goes through a pull request like any other change, and a daily robot warns you if someone changes a setting by hand.

**Why not deploy to the cloud?** pwcheck is a command-line tool. Putting it on a web server would mean sending people's passwords to that server, which defeats its whole privacy design. Managing the repo's own settings is a better, free use of Terraform.

**Files:** `infra/github/*.tf`, `infra/github/.terraform.lock.hcl`, `.github/workflows/terraform.yml`. If you copy them, change the owner and repository names in `variables.tf`, and the ruleset numbers in `imports.tf` (find yours under **Settings → Rules → Rulesets**: the number at the end of each ruleset's web address).

**Steps:**
1. Install Terraform and the GitHub CLI, then reopen your terminal and log in: `gh auth login` (choose GitHub.com → HTTPS → Yes → *Login with a web browser*). The one-time code appears **in your terminal**; it's copied for you, so just paste it into the browser page.
2. In the `infra/github` folder:
   ```
   terraform init
   terraform providers lock -platform=linux_amd64 -platform=windows_amd64
   terraform validate
   $env:GITHUB_TOKEN = (gh auth token)        # Windows PowerShell
   terraform plan
   ```
   You want to see **`0 to add, 0 to change, 0 to destroy`**. If it wants to *change* something, stop and fix the code so it matches your real settings; don't let it overwrite them.
3. Save and apply exactly that plan, then clear the token:
   ```
   terraform plan -out=tfplan
   terraform apply tfplan
   Remove-Item Env:GITHUB_TOKEN
   ```
4. For the robot, create a **fine-grained personal access token**: only your repo, **Administration: Read-only**, 90-day expiry. Add it under **Settings → Secrets and variables → Actions** as `TF_PLAN_TOKEN`. The robot can only *read* settings; you apply changes yourself.

> **What went wrong for me:** a token was pasted into a chat by mistake. **Treat any token you've pasted anywhere as leaked:** delete it on GitHub straight away and make a new one. Tokens should only ever be pasted into GitHub's own secret box.

---

## Final checklist

- [ ] Every change goes through a pull request; nothing is pushed straight to `main`
- [ ] CI, Security and Container checks run on every pull request and are marked **Required**
- [ ] The Security tab shows results from every scanner, with no open High alerts
- [ ] A version tag produces a Release, a public container image, and a verifiable attestation
- [ ] Every `uses:` line is pinned to a SHA, and Dependabot is opening update PRs
- [ ] Branch and tag rulesets are **Active** with no bypass
- [ ] (Optional) `terraform plan` shows no changes, and the daily drift check is green

## Glossary

| Term | Plain meaning |
|---|---|
| **Repository (repo)** | The project's folder on GitHub, including its full history |
| **Branch** | A separate copy of the code where you make a change without touching `main` |
| **Pull request (PR)** | A request to merge your branch into `main`; where the checks run |
| **Commit** | A saved snapshot of changes, with a message |
| **Tag** | A permanent label on one commit, like `v0.2.0` |
| **CI/CD** | Continuous Integration / Continuous Delivery: automatically testing every change, and automatically releasing |
| **DevSecOps** | Building security checks into that automation instead of doing them at the end |
| **GitHub Actions / workflow** | GitHub's robots, and the instruction files (`.yml`) that tell them what to do |
| **Lint** | Automatic style and mistake checking |
| **Coverage** | How much of the code the tests actually run |
| **SAST** | Static Application Security Testing: scanning code for security problems without running it |
| **CVE** | A publicly listed, numbered security vulnerability |
| **SARIF** | A standard file format for scanner results, so GitHub can show them all in one place |
| **Container / image** | A packaged app with everything it needs to run. The image is the package; a container is it running |
| **Digest / SHA** | A unique fingerprint of exact contents; if anything changes, the fingerprint changes |
| **Registry (GHCR)** | An online store for container images; GHCR is GitHub's |
| **Provenance / attestation** | A signed certificate saying exactly which robot built a file, and from which commit |
| **Least privilege** | Giving each part only the access it needs, nothing more |
| **Token** | A password-like key that lets a program act on your account. Never share one |
| **Ruleset** | GitHub rules that protect branches or tags |
| **Dependabot** | GitHub's robot that proposes updates to things your project depends on |
| **Terraform / IaC** | Infrastructure as Code: describing settings in files instead of clicking them |
| **Drift** | When live settings no longer match what the code says |

---

*How AI was used to build this project is documented in [AI_USAGE.md](AI_USAGE.md).*
