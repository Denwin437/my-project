# Security Policy

## Reporting a vulnerability

If you find a security problem in any project here, please open a private report through
**Security → Report a vulnerability** on this repository instead of a public issue.
Include the project name, the steps to reproduce, and the impact you expect.

I aim to acknowledge reports within a few days.

## Automated checks

Every push runs `bandit` (static security analysis) and `pip-audit` (known vulnerable dependencies), and Dependabot proposes updates.

## Supply-chain hardening

GitHub Actions are pinned to exact commit hashes, workflows run with read-only permissions and do not persist credentials, and CodeQL scans the code weekly and on every push.

## Scope

These are learning and portfolio projects. They follow good practices (parameterized SQL,
HTML escaping, secure randomness), but they have not had a professional security audit.
Do not use them to protect real secrets without your own review.
