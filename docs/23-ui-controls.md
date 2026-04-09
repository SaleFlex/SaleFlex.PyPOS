# UI Controls Catalog

All custom Qt widgets live under `user_interface/control/`. They extend standard PySide6 classes and are instantiated by `BaseWindow._create_*()` and `DynamicDialog._create_*()` from the database control definitions loaded by `DynamicFormRenderer`.

---

## Standard Controls

### Button (`control/button.py`)

**Base:** `QPushButton`

| Behaviour | Detail |
|-----------|--------|
| Focus policy | `Qt.NoFocus` — never steals keyboard focus from the NumPad or textboxes |
| Auto font sizing | `font_auto_height=True` (default) — font size and text wrapping are adjusted automatically to fit the button rectangle |
| Font | Verdana, 20 pt base (reduced as needed) |

**FormControl `type` value:** `"button"` or `"BUTTON"`

#### Dual-Function Buttons

A button becomes a **dual-function button** when both `form_control_function2` and `caption2` are set in the `FormControl` record **and** `form_control_function1` is not a sale/PLU event (`SALE_PLU_CODE`, `SALE_PLU_BARCODE`, `SALE_DEPARTMENT` — those buttons derive their label from product data and cannot participate in dual-function mode).

| DB field | Role |
|----------|------|
| `form_control_function1` | Event called when the button is in **state 1** (normal) |
| `caption1` | Label shown in state 1 |
| `form_control_function2` | Event called when the button is in **state 2** (alternate) |
| `caption2` | Label shown in state 2 |

**How labels change:** Only the **FUNC** button (see below) flips dual-function controls between state 1 and state 2. Tapping a dual-function button does **not** change its caption.

**Behaviour on each dual-button click:**
1. The event for the *currently displayed* state is dispatched (`form_control_function1` or `form_control_function2`).
2. **All** dual-function buttons on the same form are reset to **state 1** (`caption1`): the FUNC “alternate mode” flag is cleared so the next FUNC press behaves from a known baseline.

**Visual indicator:** A small circular **"F"** badge is drawn in the top-right corner of every dual-function button so operators can immediately identify them at a glance.

**Examples in the default SALE form:**

| Button name | State 1 (normal) | State 2 (alternate) |
|-------------|-----------------|---------------------|
| `PAYMENT_SUSPEND` | `SUSPEND` → `SUSPEND_SALE` | `CANCEL` → `CANCEL_DOCUMENT` |
| `DISCOUNT_PERCENT_BTN` | `DISC %` → `DISCOUNT_BY_PERCENT` | `MARK %` → `MARKUP_BY_PERCENT` |
| `DISCOUNT_AMOUNT_BTN` | `DISC AMT` → `DISCOUNT_BY_AMOUNT` | `MARK AMT` → `MARKUP_BY_AMOUNT` |

**Limitation:** Dual-function mode is not available for buttons whose `form_control_function1` is a sale or PLU event, because the renderer overwrites `caption1` with the product name from the database.

---

#### FUNC Button — Global Function-Mode Toggle

The **FUNC** button (`name="FUNC"`) is a special control. It has no sale/event of its own. Each press toggles **only the visible labels** on **all** dual-function buttons on the current form between state 1 (`caption1`) and state 2 (`caption2`). It does **not** run `form_control_function1` or `form_control_function2`.

| Press | Effect |
|-------|--------|
| While buttons show `caption1` | All dual-function buttons switch to **state 2** (`caption2`) |
| While buttons show `caption2` | All dual-function buttons switch back to **state 1** (`caption1`) |

Using any dual-function button runs that button’s handler for the visible state and then **resets every dual-function button on the form to state 1**, so operators who need an alternate action press **FUNC** first, then tap the desired control.

This design allows alternate functions (e.g. CANCEL instead of SUSPEND, CUSTOMER instead of SUB TOTAL) without a separate physical key for each.

**FormControl configuration for the FUNC button:**

| DB field | Value |
|----------|-------|
| `name` | `FUNC` |
| `form_control_function1` | `NULL` |
| `form_control_function2` | `NULL` |
| `caption1` | `FUNC` |
| `caption2` | `NULL` |

---

### Label (`control/label.py`)

**Base:** `QLabel`

Displays static or dynamic text. Used as field labels beside textboxes and checkboxes inside panel forms, and as read-only display fields.

**FormControl `type` value:** `"label"` or `"LABEL"`

---

### TextBox (`control/textbox.py`)

**Base:** `QLineEdit`

Standard text input field. When focused, the virtual keyboard is displayed automatically (if enabled). In panels, the control name maps directly to a model field name via `.lower()`.

**FormControl `type` value:** `"textbox"` or `"TEXTBOX"`

Read-only state is applied via grey background stylesheet when the field should not be edited (e.g. non-admin cashier viewing another's profile).

#### ENTER Key — `form_control_function1`

When `form_control_function1` is set to a valid event name (anything other than `NONE`), pressing **Enter/Return** on the physical keyboard while the TextBox is focused triggers that event — equivalent to clicking the corresponding button on the form.

**Use case:** Forms used with a physical keyboard (not just touch screen). For example, on the LOGIN form you can set the PASSWORD textbox's `form_control_function1` to `LOGIN` so the user can press Enter after typing the password instead of tapping the LOGIN button.

| DB field | Value |
|----------|-------|
| `form_control_function1` | Event name (e.g. `LOGIN`, `PRODUCT_SEARCH`) |
| `type_no` | `4` (TEXT_BOX) |

> If `form_control_function1` is `NULL` or `NONE` the TextBox behaves as a plain input field and Enter is ignored.

---

### CheckBox (`control/checkbox.py`)

**Base:** `QCheckBox`

Boolean model field binding. Checked = `True`, unchecked = `False`. The value is collected as the string `"true"` or `"false"` on SAVE.

**FormControl `type` value:** `"checkbox"` or `"CHECKBOX"`

| DB field | Value |
|----------|-------|
| `input_type` | `"BOOLEAN"` |
| `type_no` | `11` |

Non-admin users: `IS_ADMINISTRATOR` and `IS_ACTIVE` checkboxes are **disabled** (not just read-only).

---

### ComboBox (`control/combobox.py`)

**Base:** `QComboBox`

Drop-down selector. Some comboboxes are auto-populated at render time based on their `name`:

| Control name | Form | Auto-populated with |
|---|---|---|
| `CASHIER_NAME_LIST` | LOGIN | All active cashiers (+ optional SUPERVISOR entry) |
| `CASHIER_MGMT_LIST` | CASHIER | All cashiers (admin) or own account only (non-admin) |

Other comboboxes are populated by their event handler (e.g. product group lists).

**FormControl `type` value:** `"combobox"` or `"COMBOBOX"`

---

### DataGrid (`control/datagrid.py`)

**Base:** `QTableWidget`

Read-only grid for displaying lists of records. Used in:

- **Suspended Sales** form — lists parked carts
- **Product List** form — product search results

A hidden **Id** column (index 0) carries the database UUID for each row so that action buttons can reference the correct record.

**FormControl `type` value:** `"datagrid"` or `"DATAGRID"`

---

### Panel (`control/panel.py`)

**Base:** `QScrollArea`

Scrollable container that can hold child controls (textboxes, checkboxes, labels, buttons). Designed for touch screens with **30 px** wide/tall scrollbars.

| Feature | Detail |
|---------|--------|
| Scroll direction | Vertical and horizontal |
| Child positioning | Absolute (`QWidget` content widget with fixed size) |
| Parent-child DB link | `fk_parent_id` / `parent_name` on child `FormControl` rows |
| Data loading | Automatically loads model field values into children on form open |
| Data saving | `get_panel_textbox_values()` collects all textbox/checkbox values on SAVE |

**FormControl `type` value:** `"panel"` or `"PANEL"` (`type_no = 10`)

---

### StatusBar (`control/statusbar.py`)

**Base:** `QStatusBar`

Displays session information at the bottom of the SALE screen:

| Field | Content |
|-------|---------|
| Quantity multiplier | `x1`, `x3`, etc. (updated by X button) |
| Receipt / closure number | From the active `TransactionHeadTemp` |
| Cashier name | From `cashier_data` |

---

### ToolBar (`control/toolbar.py`)

**Base:** `QToolBar`

Top-of-window toolbar that holds branding or navigation shortcuts. Populated from `FormControl` records with the toolbar position flag set.

---

## Composite Controls

### NumPad (`control/numpad/`)

**Files:** `numpad.py` + `numpad_button.py`

A 4Ã—4 grid of digit buttons plus ENTER, BACKSPACE, and CLEAR. Its callback is wired to the `form_control_function1` value of its `FormControl` row (e.g. `SALE_PLU_BARCODE`).

| Key pressed | Callback call | Effect |
|-------------|--------------|--------|
| Digit (0–9) | `callback("3")` | Single character — handler ignores it |
| ENTER | `callback("5000157070008")` | Full accumulated string — triggers lookup or payment |
| BACKSPACE | — | Removes last character from display |
| CLEAR | — | Resets entire NumPad buffer |

**FormControl `type` value:** `"numpad"` or `"NUMPAD"`

> For the four NumPad operating modes see [Sale Transactions — NumPad](10-sale-transactions.md#numpad--four-operating-modes).

---

### SaleList (`control/sale_list/`)

**File:** `sale_list.py`

Custom `QTableWidget` that displays active transaction lines. Tapping a row opens the **Item Actions** popup (REPEAT / DELETE / CANCEL).

| Column | Content |
|--------|---------|
| (hidden) reference_id | UUID of the `TransactionProductTemp` or `TransactionDepartmentTemp` row |
| Product / Department | Name |
| Quantity | Sale quantity |
| Unit price | Price per unit |
| Total | Line total |
| Status | Empty = active; strikethrough style = cancelled |

**FormControl `type` value:** `"sale_list"` or `"SALE_LIST"` (custom control type)

---

### PaymentList (`control/payment_list/`)

**File:** `payment_list.py`

Read-only `QTableWidget` listing payments made against the current transaction.

| Column | Content |
|--------|---------|
| Payment type | CASH, CREDIT, etc. |
| Amount | Payment amount |

**FormControl `type` value:** `"payment_list"` or `"PAYMENT_LIST"` (custom control type)

---

### AmountTable (`control/amount_table/`)

**File:** `amount_table.py`

Summary table showing live running totals for the active transaction. Updated after every product addition, deletion, or payment.

| Row | Content |
|-----|---------|
| Sales Amount | Sum of active lines |
| Discount Amount | Applied discounts |
| Payment Amount | Sum of payments received |
| Change Amount | Change due |

**FormControl `type` value:** `"amount_table"` or `"AMOUNT_TABLE"` (custom control type)

---

### TabControl (`control/tab_control/`)

**File:** `tab_control.py`

**Base:** `QWidget` with `QVBoxLayout` pages (not `QTabWidget` — pages are rendered as stacked DB-driven forms inside a tab bar).

Used in the **Product Detail** dialog to show multiple views of one product:

| Tab | Content |
|-----|---------|
| Product Info | Core product fields + unit + manufacturer |
| Barcodes | Barcode list |
| Attributes | Product attributes |
| Variants | Product variants |

Tab definitions come from `FormControlTab` rows linked to the parent `FormControl` record.

**FormControl `type` value:** `"tabcontrol"` or `"TABCONTROL"` (`type_no = 12`)

---

### TransactionStatus (`control/transaction_status/`)

**File:** `transaction_status.py`

Compact status indicator showing the current document state (DRAFT, ACTIVE, COMPLETED, etc.) in the sale screen header.

---

### VirtualKeyboard (`control/virtual_keyboard/`)

**Files:** `alphanumeric_virtual_keyboard.py`, `keyboard_button.py`, `keyboard_settings_loader.py`, `key_animation_thread.py`, `key_press_handler_thread.py`, `signal.py`

On-screen QWERTY keyboard displayed when a textbox receives focus. All visual properties (colours, sizes, fonts) are loaded from the `PosVirtualKeyboard` database table.

Key features:
- Threaded key press handling to avoid blocking the UI thread
- CSS animation per key press (via `KeyAnimationThread`)
- Automatic positioning — accounts for panel scroll offset using global widget coordinates
- `is_active = False` in the database completely disables the keyboard (physical keyboard mode)

> Full configuration reference: [Virtual Keyboard Configuration](06-virtual-keyboard.md).

---

## Control Type Mapping Summary

| `FormControl.type` | Widget class | `type_no` |
|-------------------|-------------|-----------|
| `BUTTON` | `Button` (QPushButton) | 1 |
| `TEXTBOX` | `TextBox` (QLineEdit) | 2 |
| `LABEL` | `Label` (QLabel) | 3 |
| `COMBOBOX` | `ComboBox` (QComboBox) | 4 |
| `DATAGRID` | `DataGrid` (QTableWidget) | 5 |
| `NUMPAD` | `NumPad` | 6 |
| `SALE_LIST` | `SaleList` | 7 |
| `PAYMENT_LIST` | `PaymentList` | 8 |
| `AMOUNT_TABLE` | `AmountTable` | 9 |
| `PANEL` | `Panel` (QScrollArea) | 10 |
| `CHECKBOX` | `CheckBox` (QCheckBox) | 11 |
| `TABCONTROL` | `TabControl` | 12 |
| `TRANSACTION_STATUS` | `TransactionStatus` | 13 |
| `TOOLBAR` | `ToolBar` | — |
| `STATUSBAR` | `StatusBar` | — |

---

[← Back to Table of Contents](README.md) | [Previous: Dynamic Forms System](22-dynamic-forms-system.md) | [Next: Event System →](24-event-system.md)
