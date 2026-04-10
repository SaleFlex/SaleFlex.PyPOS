# Security Policy

## Supported Versions

The following versions of SaleFlex.PyPOS are currently supported with security updates:

| Version   | Supported          |
|-----------|--------------------|
| 1.0.0b7   | Yes |
| 1.0.0b6   | No  |
| < 1.0.0b6 | No  |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in SaleFlex.PyPOS, please report it by email:

**Email:** ferhat.mousavi@gmail.com
**Subject:** SECURITY: SaleFlex.PyPOS - <brief description>

### What to include

- A clear description of the vulnerability.
- Steps to reproduce the issue.
- Potential impact and severity estimate.
- Any suggested fix or mitigation (optional but appreciated).

### Response timeline

- **Acknowledgement:** Within 48 hours of receiving your report.
- **Initial assessment:** Within 5 business days.
- **Fix and disclosure:** We aim to release a patch within 30 days for critical issues.

We appreciate responsible disclosure and will credit reporters in the release notes
(unless you prefer to remain anonymous).

## Security Best Practices for POS Deployments

SaleFlex.PyPOS is a desktop POS application. Follow these guidelines to keep your
installation secure:

### Network Isolation

- Run POS terminals on an isolated network segment, separate from guest Wi-Fi.
- Restrict outbound internet access from POS machines to only required endpoints.
- Use a firewall to block unauthorized inbound connections.

### Database Security

- Use a strong, unique password for any network database (PostgreSQL / MySQL).
- Grant the POS application only the minimum required database privileges.
- Enable TLS/SSL for database connections on remote servers.
- Perform regular encrypted backups of the database.

### Access Control

- Change default cashier credentials immediately after installation.
- Use strong passwords for manager and administrator accounts.
- Enable OS-level screen lock and auto-logout on POS terminals.
- Limit physical access to POS hardware.

### Software Hygiene

- Keep Python and all dependencies up to date.
- Monitor logs/saleflex.log for unexpected errors or access patterns.
- Run SaleFlex.PyPOS under a dedicated OS user account with minimal privileges.

---

**Last Updated:** 2026-04-05
