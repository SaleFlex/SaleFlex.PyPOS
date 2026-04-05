# Troubleshooting

## General Issues

If you encounter issues during installation or operation:

1. Ensure all system requirements are met (Python 3.13+, PySide6 6.11.0, SQLAlchemy 2.0.48)
2. Check that Python is correctly installed and in your PATH — run `python --version` to verify
3. Verify that the virtual environment is activated before running the application
4. For database connection errors, ensure your database server (if using an external DB) is running
5. Check the application log file at `logs/saleflex.log` for detailed error messages

## Installation Issues

### `pip install` fails or packages conflict

**Solution:** Ensure you are using a fresh virtual environment:
```bash
python -m venv venv
venv\Scripts\activate.bat   # Windows
# or
source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

### Application does not start — `ModuleNotFoundError`

**Symptom:** Error like `ModuleNotFoundError: No module named 'PySide6'`

**Solution:** The virtual environment is not activated, or dependencies were not installed:
```bash
venv\Scripts\activate.bat
pip install -r requirements.txt
python saleflex.py
```

## Database Issues

### Database file not created

**Symptom:** Application fails to start with a database error

**Solution:** Ensure the working directory is the project root (`SaleFlex.PyPOS/`) when running the application. SQLite creates `db.sqlite3` in the current working directory.

### `NOT NULL constraint failed` on first run

**Symptom:** Database initialization error on first launch

**Solution:** Delete `db.sqlite3` to force re-initialization:
```bash
del db.sqlite3   # Windows
# or
rm db.sqlite3    # macOS/Linux
python saleflex.py
```

## Dynamic Forms Issues

### Form Not Found

**Symptom:** "Form not found" error on startup or navigation

**Solution:**
```python
# Check if form exists in the database
forms = Form.filter_by(name='LOGIN', is_deleted=False)
if not forms:
    print("Form not found — re-initialize the database")
    # Delete db.sqlite3 and restart to regenerate seed data
```

### Colors Not Displaying Correctly

**Symptom:** Form backgrounds appear black or white instead of the configured color

**Solution:**
```python
# Color format must be a string with "0x" prefix
form.back_color = "0x3268A8"   # Correct
# form.back_color = 0x3268A8   # Wrong (integer)
# form.back_color = "#3268A8"  # Works but not recommended
```

### Modal Form Not Opening

**Symptom:** Clicking a button that should open a modal form does nothing

**Solution:**
```python
# Ensure transition_mode is uppercase
control.form_transition_mode = "MODAL"   # Correct
# control.form_transition_mode = "modal" # Works (code does upper()) but prefer uppercase
```

### Boolean Fields Saved as `None` — NOT NULL Constraint Error

**Symptom:** `NOT NULL constraint failed: cashier.description` or similar error when saving a form

**Root cause:** Boolean type check ordering — `bool` is a subclass of `int` in Python. The `_save_changes_event` handler uses `type(old_value) is bool` (strict type identity) before `isinstance(..., int)` to prevent misidentification.

**Solution (already applied):** If you see this error after a code change, ensure the type conversion priority order in `_save_changes_event` is: `bool` → `int` → `str`.

## Virtual Keyboard Issues

### Virtual Keyboard Not Showing

1. Check if at least one keyboard theme has `is_active = True` in the `PosVirtualKeyboard` table
2. Verify the database connection is working
3. Check `logs/saleflex.log` for `KeyboardSettingsLoader` initialization errors

### Styles Not Updating After Database Change

1. Call `KeyboardSettingsLoader.reload_settings()` after changing database records
2. Restart the application if settings were changed before initialization

### Custom Theme Not Appearing

1. Ensure `is_deleted` is `False` for the theme record
2. Verify the theme name does not conflict with existing themes
3. Activate the theme by setting `is_active = True` (only one theme should be active at a time)

## Closure Issues

### Closure Number Resets to 1 After a New Day

**Symptom:** After midnight or after restarting the application on a new calendar day, the first closure of the new day is numbered 1 instead of continuing from where it left off.

**Root cause (fixed in `closure_manager.py`):** An earlier implementation of `create_empty_closure()` calculated the next closure number as `max(closure_number WHERE closure_date = today) + 1`. On a new day there are no closures yet, so the query returned `None` and the number defaulted to 1. `_sync_closure_number_sequence()` then synchronised `transaction_sequence.ClosureNumber` down to 1, overwriting the correctly incremented global counter.

**Fix:** `create_empty_closure()` now reads the next closure number directly from `transaction_sequence.ClosureNumber` (the global monotonic counter). `_sync_closure_number_sequence()` also guards against syncing downward — it only corrects the DB value upward.

**If you observe this in an existing database**, the `transaction_sequence.ClosureNumber` row may already have been reset. You can correct it manually:

```sql
-- Find the real highest closure_number across all days
SELECT MAX(closure_number) FROM closure WHERE is_deleted = 0;

-- Update the sequence to match
UPDATE transaction_sequence SET value = <result above> WHERE name = 'ClosureNumber';
```

After the fix is applied, the counter will be maintained correctly across day boundaries and restarts.

### Closure Button Not Working (Non-Admin User)

**Symptom:** Pressing the CLOSURE button shows an error message

**Solution:** Only administrators (`is_administrator = True`) can perform end-of-day closure. Log in with the `admin` account or another administrator account.

## Sale Issues

### Product Not Found When Scanning Barcode

**Symptom:** "Product not found" error after scanning or typing a barcode

**Solution:**
1. Verify the barcode exists in the `ProductBarcode` table
2. Check that the product is not marked as deleted (`is_deleted = False`)
3. Confirm the product data cache was loaded at startup — restart the application if needed
4. Try entering the product code manually instead of scanning

### NumPad Not Responding

**Symptom:** Typing digits on the NumPad has no effect

**Solution:**
1. Ensure the SALE form is fully loaded before typing
2. Click/tap on the NumPad area to ensure it has focus
3. Check if the virtual keyboard is obscuring the NumPad

### Payment Not Completing the Transaction

**Symptom:** After entering payment, the transaction stays open

**Solution:**
1. The payment amount may be less than the remaining balance — check the amount table
2. For credit card payments, the system limits the amount to the remaining balance automatically
3. Press CASH or CREDIT CARD again, or enter the exact amount on the NumPad

## Logging Issues

### No Log File Being Created

**Solution:** Check the `[logging]` section in `settings.toml`:
```toml
[logging]
file = true
log_dir = "logs"
log_file = "saleflex.log"
```
Ensure the application has write permission to the `logs/` directory.

### No Console Output

**Solution:** Set `console = true` in the `[logging]` section of `settings.toml`.

### Too Much or Too Little Log Output

**Solution:** Adjust the `level` setting in `settings.toml`:
- `"DEBUG"` — most verbose, all messages
- `"INFO"` — normal operation messages (default)
- `"WARNING"` — only warnings and errors
- `"ERROR"` — only errors and critical messages

---

[← Back to Table of Contents](README.md) | [Previous: Database Initialization Functions](11-database-initialization.md) | [Next: Support and Resources →](13-support.md)
