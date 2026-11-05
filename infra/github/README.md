# infra/github: repository settings as code

Terraform for this repo's own security settings: the `main` and release-tag
rulesets, the default Actions token permissions, and Dependabot security updates.

| Where | What runs | Token |
|---|---|---|
| Every PR touching `infra/` | `fmt`, `validate`, `plan` (result in the job summary) | read-only `TF_PLAN_TOKEN` |
| Daily schedule | `plan`; fails if live settings drifted from this code | read-only `TF_PLAN_TOKEN` |
| Owner's machine | `apply` | short-lived admin token, never stored in GitHub |

`apply` is deliberately **not** automated: it needs admin rights on the repo, and
an admin token stored in CI would be the most valuable secret in the project.

## Apply a change (Windows PowerShell)

```powershell
cd infra\github
$env:GITHUB_TOKEN = (gh auth token)   # or paste a fine-grained PAT with Administration: Read and write
terraform init
terraform plan
terraform apply
Remove-Item Env:GITHUB_TOKEN
```

State is kept locally (`terraform.tfstate`, git-ignored). If it's lost, nothing
breaks: the import blocks in `imports.tf` re-adopt the live settings on the next plan.

## Cost and teardown

$0: this only talks to the GitHub API. To stop managing the settings with
Terraform **without** changing them, remove them from state:

```powershell
terraform state rm github_repository_ruleset.main github_repository_ruleset.release_tags `
  github_workflow_repository_permissions.this github_repository_dependabot_security_updates.this
```

`terraform destroy` would actually delete the rulesets, so don't run it unless that's the goal.
