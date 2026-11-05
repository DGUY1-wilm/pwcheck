variable "owner" {
  description = "GitHub account that owns the repository."
  type        = string
  default     = "DGUY1-wilm"
}

variable "repository" {
  description = "Repository these settings apply to."
  type        = string
  default     = "pwcheck"
}

variable "required_checks" {
  description = "Job names that must pass before a PR can merge into main."
  type        = list(string)
  default = [
    "Lint & type check",
    "Tests (Python 3.10)",
    "Tests (Python 3.14)",
    "SAST (Bandit)",
    "SAST (CodeQL)",
    "Dependency audit (pip-audit)",
    "Secret scan (Gitleaks)",
    "Workflow audit (zizmor)",
    "Build & scan image",
  ]
}

variable "code_scanning_tools" {
  description = "Code scanning tools whose new High+ alerts block a merge (names as they appear in SARIF)."
  type        = list(string)
  default     = ["Bandit", "CodeQL", "Trivy", "gitleaks", "zizmor"]
}
