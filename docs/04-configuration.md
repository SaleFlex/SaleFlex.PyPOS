# Configuration

SaleFlex.PyPOS has two layers of configuration: the file-based `settings.toml` for infrastructure settings that must be available before the database is open, and the database-driven `PosSettings` model for all runtime POS settings.

Runtime POS and hardware fields (printers, customer display, store identity, etc.) and **local loyalty** program/policy fields are edited from **Main Menu → SETTINGS**, which opens the **SETTINGS_MENU** hub. Choose **POS SETTINGS** (single `POS_SETTINGS` panel), **LOYALTY SETTINGS** (tabbed **Loyalty program** / **Loyalty policy** / **Loyalty redemption**), or **CAMPAIGN SETTINGS** (same **CAMPAIGN_LIST** as before; administrators only). **BACK** on the hub returns to the Main Menu.

![Settings form (POS / hardware fields)](../static_files/images/sample_settings_form.jpg)

---

## `settings.toml`

Located in the project root. This file is read at startup by `settings/settings.py` before the database connection is established.

```toml
[app]
version = "1.0.0b8"
icon = "static_files\\images\\saleflex.ico"

[logging]
level = "INFO"       # DEBUG | INFO | WARNING | ERROR | CRITICAL
console = true       # Print log lines to the terminal
file = true          # Write log lines to a file
log_dir = "logs"     # Folder relative to project root
log_file = "saleflex.log"

[database]
engine = "sqlite"         # sqlite | postgresql | mysql | oracle | mssql | firebird
driver = ""               # SQLAlchemy driver suffix (e.g. "psycopg2" for PostgreSQL)
user_name = ""
password = ""
database_name = "db.sqlite3"
```

### `[app]`

| Key | Description |
|-----|-------------|
| `version` | Application version string, shown on the about screen and in log headers |
| `icon` | Path to the `.ico` file shown in the title bar and taskbar |

### `[logging]`

| Key | Default | Description |
|-----|---------|-------------|
| `level` | `"INFO"` | Minimum severity that is recorded. Use `"DEBUG"` for development, `"WARNING"` or higher in production |
| `console` | `true` | When `true`, log records are printed to stdout (useful during development or when attached to a terminal) |
| `file` | `true` | When `true`, log records are written to `{log_dir}/{log_file}` |
| `log_dir` | `"logs"` | Folder to write log files into, resolved relative to the project root |
| `log_file` | `"saleflex.log"` | Log filename |

> See [Central Logging](31-logging.md) for the full logger API and format.

### `[database]`

| Key | Description |
|-----|-------------|
| `engine` | Database backend. `"sqlite"` requires no additional packages. For others, install the corresponding SQLAlchemy driver. |
| `driver` | Optional driver suffix appended to the connection URL (e.g. `"psycopg2"` produces `postgresql+psycopg2://…`). Leave blank for the default driver. |
| `user_name` | Database user. Not used for SQLite. |
| `password` | Database password. Not used for SQLite. |
| `database_name` | SQLite: path to the `.sqlite3` file. Other engines: the database/schema name on the server. |

**SQLite (default):**
```toml
[database]
engine = "sqlite"
database_name = "db.sqlite3"
```

**PostgreSQL example:**
```toml
[database]
engine = "postgresql"
driver = "psycopg2"
user_name = "sfpos"
password = "secret"
database_name = "saleflex_pos"
```

> For database engine reference see [System Requirements](02-system-requirements.md).

---

## POS Settings (database)

Once the database is initialised, runtime POS configuration lives in the `PosSettings` table, and the active local loyalty stack is editable on **LOYALTY_SETTINGS** (`LoyaltyProgram`, `LoyaltyProgramPolicy`, `LoyaltyRedemptionPolicy`). Existing databases are migrated to the hub + split forms on startup via **`ensure_settings_hub_layout`** (see `data_layer/db_init_data/forms/setting_form.py`).

### POS Settings fields

| Field | Description |
|-------|-------------|
| `pos_no_in_store` | Terminal number within the store (used as `pos_id` on every receipt) |
| `backend_ip1` / `backend_ip2` | Primary/secondary IP addresses of the SaleFlex.GATE backend |
| `backend_port` | TCP port of the backend service |
| `force_to_work_online` | When `true`, the terminal refuses to operate if the backend is unreachable |
| `fk_working_currency_id` | Foreign key to the `Currency` record that is the working (display) currency |
| `serial_number` | Hardware serial number, auto-detected from `pos.hardware.device_info` on first run |
| `os` | Operating system string, auto-detected on first run |

### Editing POS and loyalty settings

1. Log in (e.g. as `admin`) and open **SETTINGS** from the Main Menu.
2. **POS SETTINGS** — one full-screen `POS_SETTINGS` panel; **SAVE** writes `PosSettings` and refreshes the `pos_settings` cache.
3. **LOYALTY SETTINGS** — **TABCONTROL** (`SETTING_TAB_CONTROL`) with `LOYALTY_PROGRAM`, `LOYALTY_PROGRAM_POLICY`, and `LOYALTY_REDEMPTION_POLICY` panels; **SAVE** persists all three tabs via the same generic panel save handler.
4. **CAMPAIGN SETTINGS** opens **CAMPAIGN_LIST** (administrators); **BACK** uses form history to return to the hub or Main Menu.

> Under the hood this uses the generic panel-based save pattern described in [Dynamic Forms System — Generic Model Form Pattern](22-dynamic-forms-system.md#generic-model-form-pattern).

---

## Virtual Keyboard Configuration

The on-screen keyboard appearance is also database-driven. Three built-in themes are seeded at first launch:

| Theme | Size | Use case |
|-------|------|----------|
| `DEFAULT_VIRTUAL_KEYBOARD` | 970 Ã— 315 px | Standard touchscreen |
| `DARK_THEME_KEYBOARD` | 970 Ã— 315 px | Night shift / dark UI |
| `COMPACT_KEYBOARD` | 750 Ã— 250 px | Smaller displays |

To change the active theme or disable the virtual keyboard entirely when a physical keyboard is attached, see [Virtual Keyboard Configuration](06-virtual-keyboard.md).

---

[← Back to Table of Contents](README.md) | [Previous: Installation Guide](03-installation.md) | [Next: First Login →](05-first-login.md)
