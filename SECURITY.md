# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately rather than opening a
public issue. Include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (a minimal example if possible)
- Any relevant logs or stack traces (with secrets redacted)

We aim to acknowledge reports within a few business days.

## Supported versions

| Version | Supported |
|---|---|
| 5.x | ✅ |
| 4.x and earlier | ❌ (legacy CSV-based architecture, superseded) |

## Security practices in this project

See `docs/security.md` for the full picture: authentication, RBAC,
secrets handling, CORS, input validation, SQL-injection protection,
audit logging, and known limitations. In short:

- No secrets are committed to source control; all configuration comes
  from environment variables (`.env`, gitignored).
- Passwords are bcrypt-hashed; there is no plaintext password storage
  anywhere in the codebase.
- There is no hardcoded default admin account — `scripts/create_admin.py`
  requires an explicit password.
- Dependencies are scanned on a schedule via `.github/workflows/security.yml`
  (`pip-audit` for Python, `npm audit` for the frontend).
