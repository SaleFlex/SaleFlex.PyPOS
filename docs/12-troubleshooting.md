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

---

[← Back to Table of Contents](README.md) | [Previous: Database Initialization Functions](11-database-initialization.md) | [Next: Support and Resources →](13-support.md)

