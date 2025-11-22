# Dynamic Forms System

## Overview

SaleFlex.PyPOS uses a **database-driven dynamic form system** instead of TOML files. This change makes forms more flexible and manageable. All form definitions are stored in the database, allowing for dynamic form creation and modification without code changes.

## Key Changes

### Database Model Updates

**Form Model** (`form.py`) - New fields:
- `fore_color`: Form foreground color
- `is_startup`: Boolean flag to determine the initial form to open
- `display_mode`: Which screen to display on ("MAIN", "CUSTOMER", "BOTH")

**FormControl Model** (`form_control.py`) - New fields:
- `fk_target_form_id`: UUID ForeignKey to the target form when button is clicked
- `form_transition_mode`: Transition mode ("MODAL" or "REPLACE")

## New Classes

### DynamicFormRenderer

**File:** `user_interface/render/dynamic_renderer.py`

Reads form and control definitions from the database and converts them to the appropriate format for BaseWindow.

```python
# Usage
renderer = DynamicFormRenderer(form_id=form_id)
# or
renderer = DynamicFormRenderer(form_name='LOGIN')

# Get settings
settings = renderer.settings
toolbar_settings = renderer.toolbar_settings
design = renderer.design
```

**Features:**
- Loads form and control data from database
- Returns data in the same format as TOML interpreter
- Color parsing (hex string -> integer)
- Startup form selection

### DynamicDialog

**File:** `user_interface/window/dynamic_dialog.py`

QDialog-based modal form window. Displays forms loaded from the database as modal dialogs.

```python
# Usage (usually through Interface)
result = interface.show_modal(form_id=target_form_id)
# or
result = interface.show_modal(form_name='CUSTOMER_FORM')
```

**Features:**
- Modal (temporary) form display
- Works without closing the main window
- Supports all standard controls (button, textbox, combobox, etc.)
- Automatic cleanup

## Updated Classes

### Interface (`interface.py`)

Now uses database-based form rendering:

```python
# Old usage (DEPRECATED)
interface.draw(FormName.LOGIN)
interface.redraw(FormName.SALE)

# New usage
interface.draw(form_id=form_uuid)
interface.draw(form_name='LOGIN')
interface.redraw(form_name='SALE')
interface.show_modal(form_name='CUSTOMER_FORM')  # New!
```

### CurrentStatus (`current_status.py`)

Startup form support added:

```python
# New features
current_form_id  # Current form's UUID
startup_form_id  # Startup form's UUID
load_startup_form()  # Loads startup form from database
```

### Application (`application.py`)

Loads startup form from database at startup:

```python
# During init
self.load_startup_form()  # Loads from database

# During run
if self.current_form_id:
    self.interface.draw(form_id=self.current_form_id)
else:
    self.interface.draw(form_name='LOGIN')  # Fallback
```

### GeneralEvent (`event/general.py`)

New form navigation method:

```python
def _navigate_to_form(self, target_form_id, transition_mode="REPLACE"):
    """
    Dynamic form transition.
    
    Args:
        target_form_id: Target form UUID
        transition_mode: "MODAL" or "REPLACE"
    """
```

## Deprecated Files

### Interpreter.py

**DEPRECATED**: Should no longer be used. Use DynamicFormRenderer instead.

The file is preserved but shows a deprecation warning:
```python
warnings.warn(
    "Interpreter class is deprecated. Use DynamicFormRenderer instead.",
    DeprecationWarning
)
```

### settings.toml

The `[design_files]` section has been removed. Form definitions are now in the database.

## Form Transition System

### Button-Based Form Transition

For a button in the FormControl table:

```python
# Database example
button = FormControl(
    name="BTN_CUSTOMER",
    type="button",
    caption1="Müşteri",
    fk_target_form_id="<customer_form_uuid>",
    form_transition_mode="MODAL",  # or "REPLACE"
    ...
)
```

**Transition Modes:**
- `MODAL`: Form opens as a modal dialog (temporary, on top)
- `REPLACE`: Current form closes, new form opens (saves RAM)

### Programmatic Form Transition

```python
# From event handler
self._navigate_to_form(
    target_form_id="<uuid>",
    transition_mode="MODAL"  # or "REPLACE"
)

# Or through Interface
self.interface.show_modal(form_id="<uuid>")
self.interface.redraw(form_id="<uuid>")
```

## Startup Form System

### Setting in Database

```python
# Mark a form as startup form
login_form = Form.get_by_name("LOGIN")
login_form.is_startup = True
login_form.save()
```

**Important:**
- Multiple forms can have `is_startup=True` (accidentally)
- System sorts by ID and uses the first one
- If no startup form exists, searches for form with `name='LOGIN'`
- If that doesn't exist, returns None as fallback

### Startup Form Priority Order

1. Forms with `is_startup=True` (first by ID)
2. Form with `name='LOGIN'`
3. None (error condition)

## Database Migration

### New Columns

The database schema will be automatically updated (SQLAlchemy). For existing data:

```python
# Default values for all forms
for form in Form.get_all():
    if form.fore_color is None:
        form.fore_color = "0x000000"
    if form.is_startup is None:
        form.is_startup = False
    if form.display_mode is None:
        form.display_mode = "MAIN"
    form.save()

# Default values for all controls
for control in FormControl.get_all():
    if control.form_transition_mode is None:
        control.form_transition_mode = "REPLACE"
    # fk_target_form_id can already be None (optional)
    control.save()
```

## Examples

### Example 1: Creating a Customer Form

```python
from data_layer.model import Form, FormControl

# 1. Create form
customer_form = Form(
    name="CUSTOMER_FORM",
    form_no=10,
    caption="Müşteri Tanımı",
    width=800,
    height=600,
    back_color="0xFFFFFF",
    fore_color="0x000000",
    need_login=True,
    is_startup=False,
    display_mode="MAIN"
)
customer_form.save()

# 2. Add controls
# Name textbox
name_textbox = FormControl(
    name="TXT_CUSTOMER_NAME",
    fk_form_id=customer_form.id,
    type="textbox",
    caption1="Ad",
    width=300,
    height=40,
    location_x=50,
    location_y=100,
    back_color="0xFFFFFF",
    fore_color="0x000000"
)
name_textbox.save()

# Save button
save_button = FormControl(
    name="BTN_SAVE",
    fk_form_id=customer_form.id,
    type="button",
    caption1="Kaydet",
    width=150,
    height=50,
    location_x=50,
    location_y=500,
    back_color="0x00AA00",
    fore_color="0xFFFFFF",
    form_control_function1="SAVE_CUSTOMER"
)
save_button.save()

# Close button (with form transition)
close_button = FormControl(
    name="BTN_CLOSE",
    fk_form_id=customer_form.id,
    type="button",
    caption1="Kapat",
    width=150,
    height=50,
    location_x=220,
    location_y=500,
    back_color="0xFF0000",
    fore_color="0xFFFFFF",
    form_control_function1="CLOSE_FORM"
)
close_button.save()
```

### Example 2: Transition from Main Form to Customer Form

```python
# Create a button in main form
customer_button = FormControl(
    name="BTN_OPEN_CUSTOMER",
    fk_form_id=main_form.id,
    type="button",
    caption1="Müşteri",
    width=150,
    height=50,
    location_x=10,
    location_y=10,
    back_color="0x0066CC",
    fore_color="0xFFFFFF",
    fk_target_form_id=customer_form.id,
    form_transition_mode="MODAL"  # Open as modal
)
customer_button.save()
```

## Testing and Debugging

### Form Rendering Test

```python
# DynamicFormRenderer test
renderer = DynamicFormRenderer(form_name='LOGIN')
print(f"Settings: {renderer.settings}")
print(f"Design controls: {len(renderer.design)}")

# Check each control
for control in renderer.design:
    print(f"Control: {control['type']} - {control.get('caption', 'N/A')}")
```

### Startup Form Test

```python
# Startup form check
from user_interface.render.dynamic_renderer import DynamicFormRenderer

startup_form = DynamicFormRenderer.get_startup_form()
if startup_form:
    print(f"Startup form: {startup_form.name}")
else:
    print("No startup form found!")
```

## Known Issues and Solutions

### Issue 1: Form Not Found

**Symptom:** "Form not found" error

**Solution:**
```python
# Check if form exists
forms = Form.filter_by(name='LOGIN', is_deleted=False)
if not forms:
    print("Form not found, creating...")
    # Create form
```

### Issue 2: Colors Not Displaying Correctly

**Symptom:** Colors appear black or white

**Solution:**
```python
# Color format: "0xRRGGBB" must be a string
form.back_color = "0x3268A8"  # Correct
# form.back_color = 0x3268A8   # Wrong (integer)
# form.back_color = "#3268A8"  # Works but not recommended
```

### Issue 3: Modal Form Not Opening

**Symptom:** Modal form not displaying

**Solution:**
```python
# Ensure transition_mode is written correctly
control.form_transition_mode = "MODAL"  # Correct (uppercase)
# control.form_transition_mode = "modal"  # Works (code does upper())
```

## Performance Tips

1. **In-Memory Data Caching**: All reference data (Cashier, CashierPerformanceMetrics, CashierPerformanceTarget, CashierTransactionMetrics, CashierWorkBreak, CashierWorkSession, City, Country, CountryRegion, District, Form, FormControl, LabelValue, PaymentType, PosSettings, PosVirtualKeyboard, ReceiptFooter, ReceiptHeader, Store, Table, TransactionDiscountType, TransactionDocumentType, TransactionSequence, etc.) is loaded once at application startup into `pos_data` dictionary. This minimizes disk I/O and improves performance, especially important for POS devices with limited disk write cycles.
2. **Product Data Caching**: All product-related models (Currency, CurrencyTable, Vat, Product, ProductBarcode, DepartmentMainGroup, DepartmentSubGroup, Warehouse, etc.) are loaded once at application startup into `product_data` dictionary. Sale operations, button rendering, product lookups, currency calculations, and VAT rate lookups use cached data instead of database queries.
3. **Auto-Save Optimization**: The auto-save system (AutoSaveModel, AutoSaveDict, AutoSaveDescriptor) automatically persists model changes to the database without manual save operations, ensuring data integrity while maintaining performance.
4. **RAM Management**: Consider a cache system for frequently used forms instead of `REPLACE`
5. **Database Queries**: Forms, controls, and products are loaded into cache dictionaries at application startup - no repeated database reads during runtime
6. **Cache Synchronization**: When reference data is modified (e.g., new cashier created), the cache is automatically updated via `update_pos_data_cache()` method. When product data is modified, use `update_product_data_cache()` method.
7. **Modal Dialog Cleanup**: Modal dialogs are automatically cleaned up (no memory leaks)
8. **Login Performance**: Login operations use cached `pos_data` instead of database queries, significantly reducing disk I/O
9. **Sale Performance**: All sale operations (PLU code lookup, barcode lookup, department lookup) use cached `product_data`, eliminating database queries during transactions

## Future Enhancements

- [ ] Form cache system (for frequently used forms)
- [ ] Form template system (common form templates)
- [ ] Form validation (required fields, format checks)
- [ ] Form wizard (multi-step forms)
- [ ] Drag & drop form designer (GUI tool)
- [ ] Form versioning (form history)

---

[← Back to Table of Contents](README.md) | [Previous: Basic Navigation](05-basic-navigation.md) | [Next: Virtual Keyboard Configuration →](07-virtual-keyboard.md)

