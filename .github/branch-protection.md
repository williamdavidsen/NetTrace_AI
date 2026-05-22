# Branch Protection

Protect `main` in GitHub repository settings with these rules:

- Require a pull request before merging.
- Require status checks before merging.
- Require branches to be up to date before merging.
- Block force pushes.
- Block deletions.

Required status checks:

- `Backend lint and tests`
- `Agent tests`
- `Frontend lint and tests`
- `Docker compose build`
- `Docker compose E2E`
