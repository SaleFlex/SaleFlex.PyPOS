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
- `fk_parent_id`: UUID ForeignKey to parent control (for nested controls like Panel children)
- `parent_name`: String name of parent control (for easier lookup)

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
- Supports all standard controls (button, textbox, checkbox, combobox, panel, etc.)
- Automatic cleanup

### Panel Control

**File:** `user_interface/control/panel.py`

A scrollable container control that can hold child controls. Designed for touch screens with a 30px scrollbar for easy interaction. Panels enable creating scrollable form sections, especially useful for forms with many fields (like configuration forms).

**Features:**
- QScrollArea-based with vertical and horizontal scrollbars
- Touch-optimized 30px scrollbar width/height
- Supports child controls (textboxes, checkboxes, labels, buttons, comboboxes)
- Parent-child relationship support via `fk_parent_id` and `parent_name`
- Automatic content sizing based on child controls

**Usage in FormControl:**
```python
# Create a panel
panel = FormControl(
    name="POS_SETTINGS",  # Panel name (matches model name)
    type="PANEL",
    type_no=10,
    width=900,
    height=550,
    location_x=62,
    location_y=50,
    back_color="0x2F4F4F",
    fore_color="0xFFFFFF"
)

# Create child controls (textboxes, labels) with parent reference
textbox = FormControl(
    name="POS_NO_IN_STORE",  # Uppercase name, lowercase for model attribute
    fk_parent_id=panel.id,  # Reference to panel
    parent_name="POS_SETTINGS",  # Panel name for easier lookup
    type="TEXTBOX",
    type_no=2,
    # ... other properties
)
```

### CheckBox control

**File:** `user_interface/control/checkbox.py`

`CheckBox` is a `QCheckBox` subclass used for **boolean** model fields on dynamic forms. Checked means `True`, unchecked means `False`. Values are collected on SAVE as the strings `"true"` / `"false"` and converted with the same bool logic as text fields in `GeneralEvent._save_changes_event()`.

**FormControl (database):**
- `type="CHECKBOX"`, `type_no=11`
- `input_type="BOOLEAN"` (metadata; renderer uses `type` for the widget)
- Control `name` is uppercase and maps to the model attribute via `.lower()` (same rule as textboxes)

**Seeded forms:** In `data_layer/db_init_data/form_control.py`, the SETTING form (`POS_SETTINGS` panel) uses a checkbox for `force_to_work_online`; the CASHIER form uses checkboxes for `is_administrator` and `is_active`.

**Rendering:** `DynamicFormRenderer` emits `type: "checkbox"` in the design dict. `BaseWindow._create_checkbox()` and `DynamicDialog._create_checkbox()` bind to the panel model and load/save like textboxes. Non-admin users: `is_administrator` and `is_active` checkboxes are **disabled** (not only read-only text) on the main window’s CASHIER form.

**Panel-Based Form Saving:**
When a form contains a SAVE button and panels, the system automatically:
1. Collects all **textbox** and **checkbox** values from each panel (`BaseWindow.get_panel_textbox_values()`)
2. Maps panel names to model classes (e.g., "POS_SETTINGS" → "PosSettings")
3. Updates model instances with collected field values
4. Saves changes to database

**Generic Model Form Pattern:**
The system implements a generic panel-based form save mechanism that works with **any model** by following a simple naming convention:

**Rules:**
1. **Panel Name = Model Name**: Panel name must match the model name in uppercase with underscores
   - `POS_SETTINGS` → `PosSettings` model
   - `CASHIER` → `Cashier` model
   - `CUSTOMER_INFO` → `CustomerInfo` model

2. **Control Name = Model Field**: Names of **TEXTBOX** and **CHECKBOX** children inside the panel must match model field names (uppercase → lowercase)
   - `BACKEND_IP1` textbox → `backend_ip1` model field
   - `USER_NAME` textbox → `user_name` model field
   - `FORCE_TO_WORK_ONLINE` checkbox → `force_to_work_online` model field
   - `IS_ACTIVE` checkbox → `is_active` model field

3. **Automatic Data Loading**: On form open, textbox and checkbox values are automatically loaded from:
   - CurrentData cache (if model is cached: `pos_settings`, `cashier_data`)
   - Database (first instance found or new instance created)

4. **Automatic Data Saving**: On SAVE button click:
   - All panel textbox and checkbox values are collected
   - Model instance is found or created
   - Values are converted to appropriate types (int, bool, string)
   - Model is updated and saved to database
   - Cache is updated if model is cached

**Examples:**

**PosSettings Configuration Form:**
- Panel name: `POS_SETTINGS` (matches model name)
- Mostly **TEXTBOX** controls; boolean `force_to_work_online` is a **CHECKBOX**
- On form load: Values from `CurrentData.pos_settings` are automatically loaded into panel controls
- On SAVE: All panel field values are saved to `PosSettings` model

**Cashier Management Form:**
- Panel name: `CASHIER` (matches model name)
- Text fields: `NO`, `USER_NAME`, `NAME`, `LAST_NAME`, `PASSWORD`, `IDENTITY_NUMBER`, `DESCRIPTION`
- Boolean fields: `IS_ADMINISTRATOR`, `IS_ACTIVE` as **CHECKBOX** controls
- On form load: Values from `CurrentData.editing_cashier` (or fallback `cashier_data`) are loaded automatically
- On SAVE: Values are saved to the currently selected cashier (`editing_cashier`)

**Cashier Selection Combobox (`CASHIER_MGMT_LIST`):**  
A combobox placed above the CASHIER panel enables multi-cashier management:
- If the **logged-in user is an admin** (`is_administrator = True`): all cashiers are listed and any of them can be selected and edited
- If the **logged-in user is not an admin** (`is_administrator = False`): only their own account is shown
- Selecting a cashier from the combobox updates `CurrentData.editing_cashier` and redraws the form with that cashier's data
- Signals are blocked during initial population (`blockSignals`) to prevent spurious `SELECT_CASHIER` events

**Field Read-Only Rules:**

| Cashier being edited | Password field | Other text fields | `IS_ADMINISTRATOR` / `IS_ACTIVE` checkboxes |
|---|---|---|---|
| `is_administrator = True` | Editable | Editable | Editable |
| `is_administrator = False` | Editable | **Read-only** (grey background) | **Disabled** |

This means a non-admin cashier can only update their own password. An admin cashier can edit all fields of any account.

**`editing_cashier` vs `cashier_data`:**
- `cashier_data` — the currently **logged-in** cashier (set at login, never changed while session is active)
- `editing_cashier` — the cashier whose data is **currently displayed** in the form (set when opening the form or changing the combobox selection; defaults to `cashier_data` on form open)

**Creating Forms for Any Model:**
To create a form for any model, simply:
1. Create a form with a SAVE button
2. Add a PANEL with name matching the model (e.g., `MY_MODEL` → `MyModel`)
3. Add labels and **TEXTBOX** / **CHECKBOX** controls inside the panel with names matching model fields (booleans → checkbox)
4. The system automatically handles data loading and saving!

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

## TextBox ENTER Key — `form_control_function1`

When `form_control_function1` is set on a `TEXTBOX` control (and its value is not `NONE`), pressing **Enter** or **Return** on a physical keyboard while that textbox is focused fires the corresponding event handler — exactly as if the user had clicked the button with the same function.

This feature is designed for environments where both touch-screen and physical-keyboard users need to be supported.

### Example: LOGIN form with keyboard support

```python
# PASSWORD textbox that triggers LOGIN when Enter is pressed
password_textbox = FormControl(
    name="PASSWORD",
    fk_form_id=login_form.id,
    type="textbox",
    input_type="PASSWORD",
    caption1="Şifre",
    width=300,
    height=50,
    location_x=50,
    location_y=200,
    back_color="0xFFFFFF",
    fore_color="0x000000",
    form_control_function1="LOGIN",   # ← ENTER triggers LOGIN event
)
password_textbox.save()
```

When the cashier types the password and presses **Enter**, the `LOGIN` event is executed automatically. The LOGIN button on the same form can also be clicked for touch-screen users.

> **Rule:** If `form_control_function1` is `NULL` or `"NONE"` the TextBox behaves as a plain input field and Enter has no special action.

---

## NUMPAD Control — Operating Modes

The `NUMPAD` custom control (`type="NUMPAD"`) in the **SALE** form supports four
distinct interaction modes depending on which action follows the numeric input.

### How the NUMPAD Callback Works

`base_window.py` wires the numpad's callback to the event function specified in
`form_control_function1`.  For the SALE form this is `SALE_PLU_BARCODE`.

- **Digit key press** → the callback is called with the individual character
  (e.g. `"3"`).  The handler ignores single-character calls.
- **Enter key press** → the callback is called with the full accumulated string
  (e.g. `"5000157070008"`).  This triggers **Mode 1** barcode/code lookup.

### Mode 1 — Barcode / PLU Code Search via ENTER

Handler: `SaleEvent._sale_plu_numpad_enter_event(text)`

1. If `self.awaiting_plu_inquiry` is **True** and the numpad text is non-empty,
   clear the flag and run **PLU inquiry** (`_plu_inquiry_execute`) — no sale.
2. Otherwise: search `ProductBarcode.barcode` for an exact match.
3. If not found, search `Product.code` for an exact match.
4. On success: add product to sale list using `pending_quantity` (or 1).
5. On failure: show an error dialog ("Product not found").

```python
# Triggered when numpad Enter is pressed with accumulated text
def _sale_plu_numpad_enter_event(self, text): ...
```

### Mode 2 — Inline Quantity × PLU Button

When a PLU or barcode **button** is clicked, `_get_and_reset_pending_quantity`
is called first.  Priority order:

1. `self.pending_quantity` if > 1 (set by X button, Mode 3)
2. Current numpad text converted to float
3. Default: 1.0

After reading, `pending_quantity` is reset to 1.0 and the numpad is cleared.

### Mode 3 — PLU Inquiry and X (Quantity Multiplier) Buttons

The default **SALE** form uses **two** adjacent buttons (same row, 115×90 each;
formerly a single 230×90 `QTY_MULTIPLIER` control).

#### PLU inquiry — `PLU_INQUIRY` → `PLU_INQUIRY`

Handler: `SaleEvent._plu_inquiry_event(button)`

- If the numpad has text: resolve product (same rules as Mode 1), show
  `MessageForm` with **price** (currency-aware via `VatService`) and **stock by
  warehouse** (sums `WarehouseProductStock` by parent `Warehouse` name; if no
  stock rows, falls back to `Product.stock`), clear the numpad.
- If the numpad is empty: set `self.awaiting_plu_inquiry = True` so the next
  **Enter** runs inquiry instead of a sale (see Mode 1 step 1).

`awaiting_plu_inquiry` is cleared when a quantity is committed with **X**
(`_input_quantity_event`).

```python
# State on EventHandler (event_handler.py __init__)
self.awaiting_plu_inquiry = False
```

`base_window.py` / `dynamic_dialog.py` pass the button into `_plu_inquiry_event`
because `PLU_INQUIRY` is in the `quantity_events` list (same pattern as
`INPUT_QUANTITY`).

#### X (quantity multiplier) — `QTY_MULTIPLIER` → `INPUT_QUANTITY`

Handler: `SaleEvent._input_quantity_event(button)`

1. Read the current numpad text as a float.
2. Store as `self.pending_quantity` (persists until the next sale clears it).
3. Clear `awaiting_plu_inquiry`.
4. Clear the numpad.
5. Refresh the status bar immediately (shows "x{qty}").

The status bar always shows the active multiplier:
- Default: **x1**
- After pressing X with 3 on the numpad: **x3** (until the next sale)

```python
# State persisted on EventHandler
self.pending_quantity = 1.0  # initialised in event_handler.py __init__
```

> **Seed data (split row):**
> ```python
> FormControl(
>     name="PLU_INQUIRY",
>     form_control_function1=EventName.PLU_INQUIRY.value,
>     type="BUTTON",
>     caption1="PLU",
>     width=115, height=90, location_x=547, location_y=652,
>     back_color="0x5CB85C",
>     ...
> )
> FormControl(
>     name="QTY_MULTIPLIER",
>     form_control_function1=EventName.INPUT_QUANTITY.value,
>     type="BUTTON",
>     caption1="X",
>     width=115, height=90, location_x=662, location_y=652,
>     back_color="0xFFD700",
>     ...
> )
> ```
> Existing databases keep old layout until `FormControl` rows are updated or
> the DB is re-initialized from seed data.

### Mode 4 — Payment Amount from NumPad

For **generic** payment buttons (no digit suffix in the button name, e.g.
`PAYMENT_CASH`, `PAYMENT_CREDIT`), `_cash_payment_event` /
`_credit_payment_event` read the current numpad value **before** calling
`_process_payment`:

- The raw integer from the numpad is divided by `10^decimal_places` to produce
  the monetary amount (e.g. 10000 → £100.00 for GBP with `decimal_places=2`).
- **Preset denomination buttons** (e.g. `CASH2000` = £20.00, `CASH5000` = £50.00)
  always use their encoded amount; the numpad is ignored.

```python
# PaymentService.calculate_payment_amount signature
def calculate_payment_amount(
    button_name: str,
    remaining_amount: Decimal,
    payment_type: str,
    numpad_value: Optional[Decimal] = None,   # ← new parameter
) -> Decimal: ...
```

### Helpers

| Method | Location | Purpose |
|--------|----------|---------|
| `_get_and_reset_pending_quantity(window)` | `SaleEvent` | Read qty from `pending_quantity` or numpad, reset state |
| `_refresh_status_bar()` | `SaleEvent` | Trigger immediate status bar redraw |
| `_read_numpad_payment_amount(button)` | `PaymentEvent` | Parse numpad value for generic payment buttons |
| `_resolve_product_by_barcode_or_code(lookup_text)` | `SaleEvent` | Shared barcode / product-code match for sale and PLU inquiry |
| `_warehouse_stock_summary_text(product_id)` | `SaleEvent` | Aggregate `WarehouseProductStock` by warehouse name for dialogs |
| `_plu_inquiry_execute(lookup_text, window=..., clear_numpad=...)` | `SaleEvent` | Show price + stock info without selling |

---

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

### Issue 4: Boolean Fields Saved as `None` — NOT NULL Constraint Error

**Symptom:** `NOT NULL constraint failed: cashier.description` or similar when saving a form that includes bool/string fields left empty.

**Root cause:** Python's `bool` is a subclass of `int` (`isinstance(False, int) == True`). If the type check is `isinstance(old_value, int)`, boolean fields are misidentified as integers, the conversion of `"True"` / `"False"` to `int()` raises `ValueError`, the field is skipped, and the empty model default (`None`) violates the NOT NULL constraint.

**Solution (applied in `_save_changes_event`):**
- Use `type(old_value) is bool` (strict identity) to check bool **before** the int check.
- Empty bool → `False` (not `None`).
- Empty string → `""` (not `None`).
- Empty int → skip (`continue`), do not default to `None`.

### Issue 5: `RuntimeError: dictionary changed size during iteration` in `_save_changes_event`

**Symptom:** Error logged after a successful save when adding a new cashier:  
`[SAVE_CHANGES] ✗ Error in save_changes: dictionary changed size during iteration`

**Root cause:** `_save_changes_event` iterates over `window._panels`. When a new cashier is saved, `_update_model_cache` triggers `interface.redraw()`, which calls `window.clear()` → `self._panels.clear()`. This mutates the dictionary while the `for` loop is still running.

**Solution (applied in `_save_changes_event`):**
```python
# Take a shallow copy so a redraw triggered inside the loop
# (e.g. after saving a new cashier) can safely call window.clear()
panels = dict(window._panels)
for panel_name, panel_widget in panels.items():
    ...
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

## Parent-Child Control Relationships

### Panel Control Support

Panels can contain child controls (textboxes, checkboxes, labels, buttons, etc.) through parent-child relationships:

**Database Structure:**
- Panel control has `fk_parent_id = None` (top-level control)
- Child controls have `fk_parent_id = <panel_id>` and `parent_name = "<panel_name>"`

**Rendering:**
- Panels are created first
- Child controls are then created and added to panel's content widget
- Child control positions are relative to panel's content widget

**Virtual Keyboard:**
- Panel-contained textboxes automatically have virtual keyboard enabled
- Keyboard positioning accounts for panel scroll position using global coordinates

**Data Loading:**
- On form open, panel textboxes and checkboxes are automatically populated from model data
- System tries to load from CurrentData cache first (for cached models like `pos_settings`, `cashier_data`)
- If not in cache, loads from database (first instance found)
- Panel name is converted to model class name (e.g., "POS_SETTINGS" → "PosSettings")
- Control names are converted to model field names (uppercase → lowercase)
- Example: `POS_SETTINGS` panel controls load from `CurrentData.pos_settings`
- Example: `CASHIER` panel controls load from `CurrentData.editing_cashier` (falls back to `cashier_data`)

**Cashier Panel — Read-Only Rules:**
After loading data, the CASHIER panel applies field-level read-only protection:
- If loaded cashier has `is_administrator = True` → all fields are **editable**
- If loaded cashier has `is_administrator = False` → all fields are **read-only** *except* `PASSWORD`

Text fields are enforced in `base_window._create_textbox()`; `IS_ADMINISTRATOR` / `IS_ACTIVE` checkboxes are disabled for non-admin **logged-in** users in `base_window._create_checkbox()`.

**Data Saving:**
- When SAVE button is clicked, panel textbox and checkbox values are collected (`get_panel_textbox_values()`)
- Panel name is converted to model class name (e.g., "POS_SETTINGS" → "PosSettings")
- For `CASHIER` panel: saves to `CurrentData.editing_cashier` (the cashier currently displayed), not necessarily the logged-in user
- Values are converted to appropriate types (int, bool, string, None)
- Model instance is updated with collected field values
- Model is saved to database
- If the saved cashier is also the logged-in cashier, `cashier_data` cache is updated too
- Works with any model following the naming convention!

## Special Auto-Populated Comboboxes

Some comboboxes are auto-populated at runtime based on their `name` attribute. The logic lives in `base_window._create_combobox()`.

| Control Name | Form | Behaviour |
|---|---|---|
| `CASHIER_NAME_LIST` | LOGIN | Lists all active cashiers + optional `SUPERVISOR` entry |
| `CASHIER_MGMT_LIST` | CASHIER | Admin: lists all cashiers; non-admin: lists only themselves |

### `CASHIER_MGMT_LIST` Detail

```python
# db_init_data/form_control.py (seed data)
FormControl(
    name=ControlName.CASHIER_MGMT_LIST.value,   # "CASHIER_MGMT_LIST"
    type="COMBOBOX",
    form_control_function1=EventName.SELECT_CASHIER.value,  # "SELECT_CASHIER"
    width=600, height=50,
    location_x=212, location_y=5,   # above the CASHIER panel
    ...
)
```

**Event flow:**
1. Form opens → `_cashier_form_event()` sets `editing_cashier = logged_in_cashier`, resets `_is_adding_new_cashier = False`
2. Combobox created → signals blocked → items populated → editing cashier pre-selected → signals unblocked
3. User changes selection → `SELECT_CASHIER` event → `_select_cashier_event(index)` called
4. `_select_cashier_event` → updates `editing_cashier` → calls `interface.redraw()`
5. Form redraws with new cashier's data loaded into panel controls

**New enums added:**

`ControlName` (`data_layer/enums/control_name.py`):
```python
CASHIER_MGMT_LIST = "CASHIER_MGMT_LIST"  # Cashier management selection combobox
ADD_NEW_CASHIER   = "ADD_NEW_CASHIER"    # Add new cashier button (admin only)
```

`EventName` (`data_layer/enums/event_name.py`):
```python
SELECT_CASHIER  = "SELECT_CASHIER"   # Select cashier from management list
ADD_NEW_CASHIER = "ADD_NEW_CASHIER"  # Add new cashier (admin only)
```

`EventHandler` (`pos/manager/event_handler.py`):
```python
EventName.SELECT_CASHIER.name:  self._select_cashier_event,
EventName.ADD_NEW_CASHIER.name: self._add_new_cashier_event,
```

## Add New Cashier (Admin Only)

### Overview

Administrators can create new cashier accounts directly from the CASHIER form without navigating away. A dedicated **ADD NEW CASHIER** button (bottom-left, SaddleBrown `#8B4513`) is visible only to users with `is_administrator = True`. Non-admin users never see this button (`button.hide()` is called in `base_window._create_button()` at render time).

### Button Definition (seed data)

```python
# data_layer/db_init_data/form_control.py
FormControl(
    name=ControlName.ADD_NEW_CASHIER.value,   # "ADD_NEW_CASHIER"
    form_control_function1=EventName.ADD_NEW_CASHIER.value,  # "ADD_NEW_CASHIER"
    type="BUTTON",
    width=300, height=99,
    location_x=20, location_y=630,  # bottom-left, same row as SAVE/BACK
    back_color="0x8B4513",          # SaddleBrown — visually distinct admin action
    fore_color="0xFFFFFF",
    font_size=14,
    ...
)
```

### Event Flow

```
[ADD NEW CASHIER] pressed
        │
        ▼
_add_new_cashier_event()
  ├─ Check is_administrator — deny if False
  ├─ Create Cashier(no=0, is_administrator=False, is_active=False)
  ├─ Set _editing_cashier = new empty Cashier
  ├─ Set _is_adding_new_cashier = True
  ├─ Clear CASHIER panel textboxes in-place; reset `IS_ADMINISTRATOR` / `IS_ACTIVE` checkboxes unchecked
  ├─ Hide CASHIER_MGMT_LIST combobox (inside panel content widget)
  └─ Hide ADD_NEW_CASHIER button (direct window child)

Admin fills in fields → presses [SAVE]
        │
        ▼
_save_changes_event()  (generic — no changes needed)
  ├─ Reads panel textboxes and checkboxes
  ├─ Detects Cashier model via panel name
  ├─ Gets _editing_cashier (new empty instance, no id)
  ├─ Updates fields from collected values
  ├─ Calls model_instance.save()  → SQLAlchemy INSERT (no id → new record)
  └─ Calls _update_model_cache("Cashier", model_instance)

_update_model_cache()
  ├─ Sets _editing_cashier = saved instance (now has id)
  ├─ Calls update_pos_data_cache(model_instance)  → adds to pos_data["Cashier"]
  ├─ Detects _is_adding_new_cashier == True
  ├─ Resets _is_adding_new_cashier = False
  └─ Calls interface.redraw(form_name="CASHIER")
       → Form redraws normally: combobox shows new cashier pre-selected,
         ADD_NEW_CASHIER button reappears for admin
```

### Why In-Place Manipulation Instead of Redraw?

Calling `interface.redraw()` in `_add_new_cashier_event` would clear and recreate all controls, making it feel like a **new form opened**. Instead, the event handler directly manipulates existing Qt widgets:

| Action | Method |
|--------|--------|
| Clear textbox | `child.clear()` / `child.setText("0")` |
| Uncheck bool checkboxes | `content.findChildren(CheckBox)` → `setChecked(False)` for `is_administrator` / `is_active` |
| Hide combobox | `content.findChildren(ComboBox)` → `child.hide()` |
| Hide button | `window.children()` → `child.hide()` |

After the operator saves, `interface.redraw()` IS called (from `_update_model_cache`) to properly restore the combobox and button with updated data.

### Session State

`CurrentData._is_adding_new_cashier` (bool, default `False`) tracks add-new mode:
- Set to `True` by `_add_new_cashier_event`
- Reset to `False` by `_update_model_cache` after successful save
- Also reset to `False` by `_cashier_form_event` (handles BACK-then-return case)

### `no=0` Initial Value

The new `Cashier` instance is initialized with `no=0` (integer) instead of `None`. This ensures the `_save_changes_event` type-detection logic (`type(old_value) is int`) correctly identifies the `no` field as integer and applies `int(stripped)` conversion when the operator enters a value.

---

## `_save_changes_event` — Type Conversion Rules

The generic save handler uses the following priority order for type conversion. **Bool must be checked before int** because Python's `bool` is a subclass of `int` (`isinstance(False, int) == True`).

```python
# Priority order (most specific first)
if type(old_value) is bool or field_type is bool:
    # Boolean: "true"/"1"/"yes"/"on" → True, everything else → False
    # Empty string → False  (never None, to satisfy NOT NULL constraints)
    new_value = stripped.lower() in ('true', '1', 'yes', 'on')

elif type(old_value) is int or field_type is int:
    # Integer: parse with int()
    # Empty string → skip field (continue)
    new_value = int(stripped)

else:
    # String: use as-is (empty string stays "", not None)
    # Empty string → ""  (avoids NOT NULL constraint violations)
    new_value = stripped
```

**Key design decisions:**

| Scenario | Old behaviour | New behaviour | Reason |
|----------|--------------|---------------|--------|
| `is_administrator` empty | `None` (int path, then error) | `False` | bool before int check |
| `description` empty | `None` → DB NOT NULL error | `""` | string fields keep empty string |
| `is_active = "True"` | `int("True")` → ValueError | `True` (bool) | bool path catches it first |
| `no` empty | `None` | skip (continue) | can't default int meaningfully |

**Dictionary iteration safety:**  
`_save_changes_event` now copies `window._panels` before iterating (`dict(window._panels)`). This prevents `RuntimeError: dictionary changed size during iteration` when a redraw (triggered inside the loop by `_update_model_cache`) calls `window.clear()` and clears the original `_panels` dict.

## Future Enhancements

- [ ] Form cache system (for frequently used forms)
- [ ] Form template system (common form templates)
- [ ] Form validation (required fields, format checks)
- [ ] Form wizard (multi-step forms)
- [ ] Drag & drop form designer (GUI tool)
- [ ] Form versioning (form history)
- [ ] Panel nesting (panels within panels)

---

[← Back to Table of Contents](README.md) | [Previous: Database Models](21-database-models.md) | [Next: UI Controls Catalog →](23-ui-controls.md)

