# System Requirements

## Hardware Requirements

- **Display**: Touch screen device running Windows or Linux (single or dual display configurations supported)
- **Secondary Display**: Optional customer-facing display for line display updates
- **Receipt Printer**: ESC/P compatible receipt printer
- **Barcode Scanner**: 2D or 3D barcode reader (PS/2 or USB)
- **Weighing Scale**: Optional, for retail environments that sell by weight
- **Cash Drawer**: Optional, connected via receipt printer or direct port

## Software Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| **Python** | 3.13 or higher | Python 3.14 supported with caveats — see note below |
| **PySide6** | 6.11.0 | Qt-based GUI framework |
| **SQLAlchemy** | 2.0.48 | ORM for database operations |
| **Requests** | 2.33.0 | HTTP client for API communication with SaleFlex.GATE |

> **Note on Python 3.14:** Python 3.14 can be used to run the application, but SQLAlchemy does not yet officially support Python 3.14. You may encounter unexpected issues or incompatibilities. It is recommended to use **Python 3.13** until official SQLAlchemy support for Python 3.14 is confirmed.

### Operating System

- **Windows**: Windows 10 / Windows 11
- **Linux**: Any modern distribution with Qt/PySide6 support

## Supported Database Engines

SaleFlex.PyPOS uses SQLAlchemy ORM and supports the following database backends:

| Database | Notes |
|----------|-------|
| **SQLite** | Default — no additional server required, stored in `db.sqlite3` |
| **PostgreSQL** | Recommended for multi-terminal or high-volume deployments |
| **MySQL / MariaDB** | Supported via SQLAlchemy |
| **Oracle** | Supported via SQLAlchemy |
| **Microsoft SQL Server** | Supported via SQLAlchemy |
| **Firebird** | Supported via SQLAlchemy |
| **Sybase** | Supported via SQLAlchemy |

The database engine is configured in `settings.toml`. SQLite requires no additional configuration and is the recommended choice for single-terminal deployments.

---

[← Back to Table of Contents](README.md) | [Previous: Introduction](01-introduction.md) | [Next: Installation Guide →](03-installation.md)
