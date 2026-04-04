# Troubleshooting

## General Issues

If you encounter issues during installation or operation:

1. Ensure all system requirements are met
2. Check that Python is correctly installed and in your PATH
3. Verify that the virtual environment is activated before running the application
4. For database connection errors, ensure your database server (if using external DB) is running

## Dynamic Forms Issues

### Form Not Found
**Symptom:** "Form not found" error

**Solution:**
```python
# Check if form exists
forms = Form.filter_by(name='LOGIN', is_deleted=False)
if not forms:
    print("Form not found, creating...")
    # Create form
```

### Colors Not Displaying Correctly
**Symptom:** Colors appear black or white

**Solution:**
```python
# Color format: "0xRRGGBB" must be a string
form.back_color = "0x3268A8"  # Correct
# form.back_color = 0x3268A8   # Wrong (integer)
# form.back_color = "#3268A8"  # Works but not recommended
```

### Modal Form Not Opening
**Symptom:** Modal form not displaying

**Solution:**
```python
# Ensure transition_mode is written correctly
control.form_transition_mode = "MODAL"  # Correct (uppercase)
# control.form_transition_mode = "modal"  # Works (code does upper())
```

## Virtual Keyboard Issues

### Virtual Keyboard Not Showing
1. Check if `is_active` is `True` for at least one keyboard theme
2. Verify database connection
3. Check KeyboardSettingsLoader initialization in logs

### Styles Not Updating
1. Call `KeyboardSettingsLoader.reload_settings()` after database changes
2. Restart application if settings were changed before initialization

### Custom Theme Not Appearing
1. Ensure `is_deleted` is `False`
2. Check that theme name doesn't conflict with existing themes
3. Activate the theme by setting `is_active=True`

## Closure Issues

### Closure Number Resets to 1 After a New Day

**Symptom:** After midnight (or after restarting the application on a new calendar day), the first closure of the new day is numbered 1 instead of continuing from where it left off.

**Root cause (fixed in `closure_manager.py`):** The old implementation of `create_empty_closure()` calculated the next closure number as `max(closure_number WHERE closure_date = today) + 1`. On a new day there are no closures yet, so the query returned `None` and the number defaulted to 1. `_sync_closure_number_sequence()` then synchronised `transaction_sequence.ClosureNumber` down to 1, overwriting the correctly incremented global counter.

**Fix:** `create_empty_closure()` now reads the next closure number directly from `transaction_sequence.ClosureNumber` (the global monotonic counter). `_sync_closure_number_sequence()` also guards against syncing downward — it only corrects the DB value upward.

**If you observe this in an existing database**, the `transaction_sequence.ClosureNumber` row may already have been reset. You can correct it manually:

```sql
-- Find the real highest closure_number across all days
SELECT MAX(closure_number) FROM closure WHERE is_deleted = 0;

-- Update the sequence to match
UPDATE transaction_sequence SET value = <result above> WHERE name = 'ClosureNumber';
```

After the fix is applied, the counter will be maintained correctly across day boundaries and restarts.

---

[← Back to Table of Contents](README.md) | [Previous: Database Initialization Functions](11-database-initialization.md) | [Next: Support and Resources →](13-support.md)

