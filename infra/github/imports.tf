# These settings already existed (created in the UI). Import blocks adopt them
# instead of creating duplicates. They are idempotent: once a resource is in
# state they do nothing, and in CI (no state) they let `plan` read the live
# settings and show any difference from the code.

import {
  to = github_repository_ruleset.main
  id = "pwcheck:26646656"
}

import {
  to = github_repository_ruleset.release_tags
  id = "pwcheck:26646860"
}

import {
  to = github_workflow_repository_permissions.this
  id = "pwcheck"
}

import {
  to = github_repository_dependabot_security_updates.this
  id = "pwcheck"
}
