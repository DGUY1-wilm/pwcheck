# Repository security settings as code. Everything here was first set up by
# hand in the GitHub UI, then imported (imports.tf), so this file is now the
# source of truth: a change to a rule goes through a PR like any code change.

locals {
  github_actions_app_id = 15368 # GitHub's ID for the "GitHub Actions" app that reports these checks
}

# ---------------------------------------------------------------- main branch
resource "github_repository_ruleset" "main" {
  name        = "protect-main"
  repository  = var.repository
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  rules {
    creation         = true
    deletion         = true # main can't be deleted
    non_fast_forward = true # no force pushes rewriting history

    pull_request {
      # Solo repo: GitHub doesn't allow approving your own PR, so 1 would lock
      # the owner out. On a team this would be 1+ with CODEOWNERS.
      required_approving_review_count   = 0
      required_review_thread_resolution = true
      dismiss_stale_reviews_on_push     = false
      require_code_owner_review         = false
      require_last_push_approval        = false
    }

    required_status_checks {
      strict_required_status_checks_policy = true # branch must be up to date with main

      dynamic "required_check" {
        for_each = var.required_checks
        content {
          context        = required_check.value
          integration_id = local.github_actions_app_id
        }
      }
    }

    required_code_scanning {
      dynamic "required_code_scanning_tool" {
        for_each = var.code_scanning_tools
        content {
          tool                      = required_code_scanning_tool.value
          security_alerts_threshold = "high_or_higher"
          alerts_threshold          = "errors"
        }
      }
    }
  }
}

# ---------------------------------------------------------------- release tags
resource "github_repository_ruleset" "release_tags" {
  name        = "protect-release-tags"
  repository  = var.repository
  target      = "tag"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/tags/v*"]
      exclude = []
    }
  }

  rules {
    # Creation stays allowed so new versions can be tagged; once published,
    # a tag can never be moved, deleted or force-pushed.
    update           = true
    deletion         = true
    non_fast_forward = true
  }
}

# ---------------------------------------------------------------- Actions token
resource "github_workflow_repository_permissions" "this" {
  repository                       = var.repository
  default_workflow_permissions     = "read" # workflows that forget a permissions: block get read-only
  can_approve_pull_request_reviews = false  # a workflow can never approve its own PR
}

# ---------------------------------------------------------------- Dependabot
resource "github_repository_dependabot_security_updates" "this" {
  repository = var.repository
  enabled    = true
}
