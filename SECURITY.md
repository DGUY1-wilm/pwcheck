# Security Policy

## Supported versions

Only the latest release receives security fixes.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately through GitHub: **Security** tab → **Report a vulnerability**
([direct link](https://github.com/DGUY1-wilm/pwcheck/security/advisories/new)).

Include what you found, how to reproduce it, and the version or image digest you tested.
You can expect an acknowledgement within 7 days.

## How this project is secured

- Every change goes through a pull request with required checks: lint, strict typing,
  tests with a coverage gate, Bandit, CodeQL, pip-audit, Gitleaks, zizmor and a Trivy image scan.
- All GitHub Actions are pinned to commit SHAs; Dependabot keeps them, the Python tools
  and the base image current.
- Release images are built in CI, scanned before they are pushed, and carry signed SLSA
  build provenance. Verify one with:

  ```bash
  gh attestation verify oci://ghcr.io/dguy1-wilm/pwcheck:<version> --repo DGUY1-wilm/pwcheck
  ```
