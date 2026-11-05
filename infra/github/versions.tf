terraform {
  required_version = ">= 1.16.0, < 2.0.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.13" # any 6.x from 6.13 up; .terraform.lock.hcl pins the exact build
    }
  }

  # No remote backend on purpose. CI only runs `plan`, and the import blocks in
  # imports.tf let a plan with no state compare code against the live settings.
  # `apply` is run locally by the repo owner (see README.md in this folder).
}

provider "github" {
  owner = var.owner
  # Token is read from the GITHUB_TOKEN environment variable, never from a file.
}
