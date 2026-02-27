# Central Logging

SaleFlex.PyPOS uses a **centralized logging** module (`core/logger.py`) so that all components log through a single, configurable pipeline. Log level, console output, and file output are controlled via the `[logging]` section in `settings.toml`.

## Overview

- **Root logger name:** `saleflex`. All application loggers live under this hierarchy (e.g. `saleflex.pos.manager.event_handler`).
- **Configuration:** Read from `settings.toml` → `[logging]`. If the section is missing or incomplete, defaults are used.
- **Usage:** Call `get_logger(__name__)` from any module to get a logger that inherits the root configuration.

## Configuration (`settings.toml`)

```toml
[logging]
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
level = "INFO"
# Write to console? (true/false)
console = true
# Write to log file? (true/false)
file = true
# Log directory (relative to application working directory)
log_dir = "logs"
# Log file name
log_file = "saleflex.log"
```

| Option   | Description                    | Default   |
|----------|--------------------------------|-----------|
| `level`  | Minimum level to log           | `"INFO"`  |
| `console` | Enable stdout handler        | `true`    |
| `file`   | Enable file handler            | `true`    |
| `log_dir`  | Directory for log file      | `"logs"`  |
| `log_file` | Log file name               | `"saleflex.log"` |

If the log directory does not exist, it is created when the file handler is first used.

## Usage in Code

```python
from core.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug message")
logger.info("Normal operation message")
logger.warning("Warning condition")
logger.error("Error condition")
logger.critical("Critical condition")
```

- Use `get_logger(__name__)` so log records are tagged with the module name (e.g. `saleflex.pos.manager.closure_manager`).
- Use `get_logger()` with no argument to get the root `saleflex` logger.

## Log Format

Each log record uses this format:

```
%(asctime)s | %(levelname)-8s | %(name)s | %(message)s
```

- **asctime:** `YYYY-MM-DD HH:MM:SS`
- **levelname:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **name:** Logger name (e.g. `saleflex.pos.manager.event_handler`)
- **message:** The log message

Example:

```
2025-02-27 14:30:00 | INFO     | saleflex.pos.manager.cache_manager | Cache loaded successfully
```

## Where Logging Is Used

The central logger is used across the application, including:

- **POS managers:** `event_handler`, `closure_manager`, `cache_manager`, `document_manager`, `current_data`, `current_status`, `application`
- **Event handlers:** `general`, `sale`, `payment`, `closure`, `configuration`, `service`, `report`, `hardware`, `warehouse`
- **Services:** `vat_service`, `sale_service`, `payment_service`
- **Data layer:** `crud_model`, `db_initializer`, `db_utils`, `auto_save` modules, and `db_init_data` modules
- **UI:** `base_window`, `dynamic_dialog`, `sale_list`, `numpad`, `statusbar`, `keyboard_settings_loader`

## Troubleshooting

- **No log file:** Ensure `file = true` in `[logging]` and that the process has write permission to `log_dir`. The directory is created automatically if it does not exist.
- **No console output:** Set `console = true` in `[logging]`.
- **Too much or too little output:** Change `level` (e.g. `"DEBUG"` for more detail, `"WARNING"` to reduce noise).
- **Wrong encoding:** The file handler uses UTF-8. If you see encoding issues, check that your terminal or log viewer supports UTF-8.

---

**See also:** [Troubleshooting](12-troubleshooting.md) | [Configuration (settings.toml)](03-installation.md#configuration)
