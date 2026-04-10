# Startup Entry Point (`saleflex.py`)

`saleflex.py` is the single entry point for the entire application.  
Beyond simply calling `Application().run()` it performs a set of
**pre-flight checks** that run before any application module is imported.
This document explains each check, why it exists, and what happens when it
fails.

---

## Overview

```
python saleflex.py
       │
       ├─ 1. Working-directory normalization
       ├─ 2. Python version guard
       ├─ 3. Single-instance lock
       ├─ 4. if __name__ == "__main__" guard
       │       ├─ Startup logging
       │       ├─ Application construction & run
       │       ├─ Global exception handler
       │       └─ Shutdown logging
       └─ (lock released automatically by atexit)
```

---

## 1. Working-Directory Normalization

```python
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _SCRIPT_DIR:
    os.chdir(_SCRIPT_DIR)
```

### Why it is needed

Many files are opened with **relative paths** that are expected to resolve
against the project root:

| File / directory | Used by |
|---|---|
| `settings.toml` | `settings/settings.py` |
| `db.sqlite3` | SQLAlchemy engine (SQLite default) |
| `logs/` | `core/logger.py` |
| `static_files/` | UI assets, closure templates |

If the application is launched from a different directory — for example via a
Windows desktop shortcut, a systemd service unit, or a CI script — the CWD
will not point at the project root and every `open("settings.toml")` call
will raise `FileNotFoundError`.

### Effect

The CWD is corrected to the directory that contains `saleflex.py` *before*
any other module is imported, so all relative-path operations work
regardless of how the script was invoked.

---

## 2. Python Version Guard

```python
_MIN_PYTHON = (3, 13)
if sys.version_info < _MIN_PYTHON:
    sys.exit(
        f"SaleFlex.PyPOS requires Python {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} "
        f"or higher.\n"
        f"Current interpreter: Python {sys.version}"
    )
```

### Why it is needed

SaleFlex.PyPOS uses language features that were introduced in Python 3.13
(e.g. `tomllib` in the standard library, `type X = …` type aliases, improved
`f`-string syntax).  Running under an older interpreter produces confusing
`SyntaxError` or `ImportError` messages deep inside the call stack.

This guard catches the problem at the very first line and prints a clear,
actionable message.

### Effect

The interpreter exits immediately with exit code 1 and a human-readable
message before any PySide6 or SQLAlchemy import is attempted.

> **Note on Python 3.14:** Python 3.14 passes this version check but
> SQLAlchemy does not yet officially support it.  Use Python 3.13 for
> production deployments until official SQLAlchemy 3.14 support is confirmed.

---

## 3. Single-Instance Lock

```python
_LOCK_FILE_PATH = os.path.join(_SCRIPT_DIR, ".saleflex.lock")

def _acquire_single_instance_lock() -> bool: ...
def _release_single_instance_lock() -> None: ...
```

### Why it is needed

A POS terminal must **never run two instances simultaneously**:

- Two instances would share the same SQLite database file, leading to
  write conflicts and corrupted transaction data.
- A second instance could open a duplicate closure or double-count sales.
- Hardware peripherals (cash drawer, receipt printer) cannot be safely
  shared between two processes.

### Implementation

A **file-based process lock** is used because:

- It is automatically released when the process terminates for *any*
  reason (crash, `kill`, power loss) — no manual cleanup is required.
- It works across all supported platforms (Windows / Linux / macOS).
- No external dependency (e.g. Redis, D-Bus) is required.

| Platform | Lock mechanism |
|---|---|
| Windows | `msvcrt.locking` with `LK_NBLCK` |
| Linux / macOS | `fcntl.flock` with `LOCK_EX \| LOCK_NB` |

The lock file is `.saleflex.lock` in the project root.  It is listed in
`.gitignore` and should never be committed.

### Lock lifecycle

```
Process starts → _acquire_single_instance_lock()
                         │ success → continue
                         │ failure → sys.exit("already running")
                         │
                 [application runs]
                         │
Process ends  → atexit calls _release_single_instance_lock()
              → lock file deleted
```

### Effect when another instance is running

```
SaleFlex.PyPOS is already running.
Only one instance of the application can run at a time.
```

The process exits with code 1.

### Stale lock file

If the process was killed without the atexit handler running (e.g. `kill -9`
on Linux, or a hard power-off), the lock file will remain on disk.  On the
next start:

- **Linux / macOS:** `fcntl.flock` attempts to lock the existing file.
  Because no process holds the lock, it succeeds immediately.  A stale
  lock file never blocks a fresh start.
- **Windows:** `msvcrt.locking` behaves identically — the file exists but
  carries no active kernel lock, so the new process acquires it without
  issue.

---

## Database bootstrap and UI schema patches (`Application`)

Inside `Application.__init__`, after **`init_db()`** creates tables and seeds empty databases, the code runs **idempotent patches** on every startup. For example:

- **`ensure_transaction_discount_type_campaign`** (`data_layer/db_init_data/transaction_discount_type.py`) inserts the **CAMPAIGN** **`transaction_discount_type`** row when missing (older databases seeded before that type existed) — see [Database Initialization](33-database-initialization.md) (`_insert_transaction_discount_types`, **CAMPAIGN** row) and [Campaign & Promotions](43-campaign-promotions.md).
- **`ensure_sale_form_coupon_button`** (`data_layer/db_init_data/forms/sale.py`) adds the **COUPON** control on the **SALE** form when missing; **`ensure_sample_coupon_welcome_demo`** and **`ensure_welcome10_demo_campaign_product`** (`data_layer/db_init_data/campaign.py`) keep demo **`WELCOME10-DEMO`** coupon / campaign product rows in sync — see [Campaign & Promotions — Coupon activation](43-campaign-promotions.md#coupon-activation-on-sale).
- **`ensure_customer_loyalty_points_grid`** (`data_layer/db_init_data/forms/customer.py`) adds the **Point movements** tab and `CUSTOMER_LOYALTY_POINTS_GRID` on **CUSTOMER_DETAIL** when missing — see [Customer Management — Database Reset Note](17-customer-management.md#database-reset-note) and [Loyalty Programs — Reporting and audit](41-loyalty-programs.md#reporting-and-audit-phase-6).
- **`ensure_setting_form_tabs`** (`data_layer/db_init_data/forms/setting_form.py`) rebuilds form **#3 SETTING** controls when the tab control (`SETTING_TAB_CONTROL`) is absent, migrating legacy flat layouts to the **TABCONTROL** with POS + loyalty tabs — see [Configuration](04-configuration.md).

After **`load_open_closure()`**, **`Application`** calls **`init_integration()`** (**`IntegrationMixin`**) so **`gate`** / **`third_party`** settings load and campaign routing (**`apply_campaign`**) is ready — see [Integration Layer — Campaign discount routing](40-integration-layer.md#campaign-discount-routing).

---

## 4. `if __name__ == "__main__"` Guard

```python
if __name__ == "__main__":
    ...
```

This is the standard Python idiom to prevent entry-point side effects when
the module is imported rather than executed directly (e.g. during unit tests
or type-checking tools).

All application startup code — logger initialisation, `Application()`
construction, and `app.run()` — is contained inside this block.

---

## 5. Startup Logging

```python
_logger.info("=" * 60)
_logger.info("Starting SaleFlex.PyPOS v%s", __version__)
_logger.info("Python %s on %s", sys.version.split()[0], sys.platform)
_logger.info("Working directory: %s", os.getcwd())
_logger.info("=" * 60)
```

Each startup writes a clearly delimited banner to `logs/saleflex.log` (and
to the console if enabled).  This makes it trivial to find the beginning of
each session in the log file and to confirm the exact Python version and
working directory that were active.

See [Central Logging](16-logging.md) for log configuration.

---

## 6. Global Exception Handler

```python
try:
    from pos.manager import Application
    app = Application()
    app.run()
except Exception:
    _logger.critical("Unhandled exception – application terminated", exc_info=True)
    sys.exit(1)
finally:
    _logger.info("SaleFlex.PyPOS v%s – shutdown complete", __version__)
```

### Why it is needed

Without a top-level handler, an unhandled exception:

- Prints a raw traceback to the console (may not be visible on a kiosk or
  headless device).
- Produces no entry in the application log file.
- Exits with code 1 but gives the operator no record of what went wrong.

With the handler:

- The full traceback is written to `logs/saleflex.log` at `CRITICAL` level.
- The process exits with code 1 (allowing a service manager to restart the
  application).
- The `finally` block always logs a shutdown message so the log file always
  has a matching start/end pair.

### What is *not* caught here

Exceptions that originate inside Qt's event loop are not Python exceptions
from the perspective of this `try` block — they are handled by Qt's own
mechanism.  Domain exceptions (`PaymentError`, `DatabaseError`, etc.) are
caught inside their respective handlers and never propagate to this level
under normal operation.  See [Centralized Exception Handling](17-exception-handling.md).

---

## Summary of checks and their failure modes

| Check | Failure condition | Exit behaviour |
|---|---|---|
| Working-directory fix | CWD ≠ script dir | CWD corrected silently |
| Python version guard | Python < 3.13 | `sys.exit` with message |
| Single-instance lock | Lock already held | `sys.exit` with message |
| Global exception handler | Unhandled `Exception` | Log at CRITICAL + `sys.exit(1)` |

---

[← Back to Table of Contents](README.md) | [Previous: Database Initialization](33-database-initialization.md) | [Next: Troubleshooting →](35-troubleshooting.md)
