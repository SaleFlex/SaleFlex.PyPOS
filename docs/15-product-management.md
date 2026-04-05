# Product Management — Product List & Detail Forms

## Overview

SaleFlex.PyPOS 1.0.0b6 introduces two fully database-driven forms for
product management:

| Form | FormName enum | form_no | Type | Purpose |
|------|---------------|---------|------|---------|
| Product List | `PRODUCT_LIST` | 8 | Full-screen form | Search products and open detail |
| Product Detail | `PRODUCT_DETAIL` | 9 | Modal dialog (`DynamicDialog`) | Read-only tabbed detail view |

Both forms are rendered by `DynamicFormRenderer` from records in
`form.py` / `form_control.py`.  No static Python form classes are
needed — all layout data lives in the database.

---

## New Control: TabControl

**File:** `user_interface/control/tab_control/tab_control.py`  
**Exported from:** `user_interface/control/__init__.py`

`TabControl` is a `QTabWidget` subclass styled to match the POS colour
theme.  It is registered as the `"TABCONTROL"` control type so that
`DynamicFormRenderer` can create it from a database row.

### Public API

```python
tab = TabControl(
    parent=self,
    width=900, height=500,
    location_x=10, location_y=60,
    background_color=0x2F4F4F,
    foreground_color=0xFFFFFF,
    font_size=12
)

# Add a page
tab.add_tab(some_widget, "Tab Title")

# Get active tab index
idx = tab.get_current_tab_index()

# Restyle
tab.set_color(0x1A3232, 0xFFFFFF)
```

### Focus policy

`TabControl` uses `Qt.ClickFocus` (not `Qt.NoFocus`) so that the
internal `QTabBar` can receive mouse-click events and switch tabs
properly on touch screens.

### Using TABCONTROL in a DB-driven form

Set `type = "TABCONTROL"` on the `FormControl` row.

`DynamicFormRenderer` processes `TABCONTROL` rows in the **first pass**
(before child controls) so the tab pages exist when child `DataGrid`
controls are created.  The resulting widget is stored in
`self._tab_controls[name]`.

### Tab pages — database model

Tab page definitions are stored in the `FormControlTab` table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Unique identifier |
| `fk_form_control_id` | UUID FK → `form_control.id` | Parent TABCONTROL record |
| `tab_index` | Integer | Zero-based display order |
| `tab_title` | String(100) | Label shown on the tab |
| `tab_tooltip` | String(200) | Optional tooltip |
| `back_color` / `fore_color` | String | Optional per-tab colours |
| `is_visible` | Boolean | Whether the tab is shown |

`FormControl` rows that belong to a specific tab page carry an
additional `fk_tab_id` column (UUID FK → `form_control_tab.id`).
This column uses `use_alter=True` to resolve the circular FK between
`form_control` ↔ `form_control_tab`.

---

## Product List Form

### Access

**Main Menu → PRODUCTS button**

### Layout (1024 × 768)

| Control | Type | Position | Size | Event |
|---------|------|----------|------|-------|
| Search TextBox | TEXTBOX | x=10, y=10 | 820 × 50 | — |
| Search Button | BUTTON | x=840, y=10 | 170 × 50 | `PRODUCT_SEARCH` |
| DataGrid | DATAGRID | x=10, y=75 | 1000 × 570 | — |
| Detail Button | BUTTON | x=10, y=660 | 150 × 65 | `PRODUCT_DETAIL` |
| Back Button | BUTTON | x=860, y=660 | 150 × 65 | `BACK` |

> **Button convention:** `BACK` is always in the **bottom-right corner**
> (consistent with every other form in the application).
> `DETAIL` is in the bottom-left corner.

### DataGrid columns

| Code | Name | Short Name | Sale Price | Stock |

### Search behaviour

- Typing in the search box and pressing **SEARCH** triggers
  `_product_search_event`.
- An empty search returns **all** non-deleted products (capped at 500
  rows).
- A non-empty search performs a case-insensitive LIKE match on both
  `product.name` and `product.short_name`.

### DETAIL button

- Reads the currently selected row.
- Looks up the product UUID stored in `datagrid._product_ids[row_index]`.
- Stores the UUID in `self.app.current_product_id` (transient, not
  auto-saved).
- Opens the `PRODUCT_DETAIL` form as a modal dialog via
  `self.interface.show_modal(form_name=FormName.PRODUCT_DETAIL.name)`.
- If no row is selected the button does nothing (logs a warning).

---

## Product Detail Form

**Form no:** 9  
**Renderer:** `DynamicDialog` (DB-driven modal dialog, 1024 × 768)

The Product Detail form is fully database-driven.  Its controls are
defined in `form_control.py` and rendered at runtime by
`DynamicFormRenderer` + `DynamicDialog`.

### Controls

| Control | Type | Description |
|---------|------|-------------|
| `PRODUCT_DETAIL_TAB` | TABCONTROL | x=10, y=10, 1004 × 694 — four tabs |
| `PRODUCT_INFO_GRID` | DATAGRID | Tab 0 — Product Info |
| `PRODUCT_BARCODE_GRID` | DATAGRID | Tab 1 — Barcodes |
| `PRODUCT_ATTRIBUTE_GRID` | DATAGRID | Tab 2 — Attributes |
| `PRODUCT_VARIANT_GRID` | DATAGRID | Tab 3 — Variants |
| `CLOSE_DETAIL` | BUTTON | x=432, y=712, 160 × 48 — closes dialog |

Each DataGrid is parented to its tab page via a `QVBoxLayout`, so it
automatically fills the available tab content area.

### Tab 0 — Product Info

Key/value DataGrid (two columns: **Field**, **Value**).  
Rows come from three tables:

| Field | Source |
|-------|--------|
| Code, Name, Short Name | `product` |
| Sale Price, Purchase Price | `product` |
| Stock, Min Stock, Max Stock | `product` |
| Unit | `product_unit` (via `fk_product_unit_id`) |
| Manufacturer | `product_manufacturer` (via `fk_manufacturer_id`) |

### Tab 1 — Barcodes

Columns: **Barcode**, **Old Barcode**, **Purchase Price**, **Sale Price**

Source: `product_barcode` rows where `fk_product_id` matches the
selected product.

### Tab 2 — Attributes

Columns: **Attribute**, **Value**, **Category**, **Unit**

Source: `product_attribute` rows sorted by `display_order`.

### Tab 3 — Variants

Columns: **Name**, **Code**, **Color**, **Size**, **Additional Info**

Source: `product_variant` rows for the selected product.

---

## Data Loading — UUID handling

`current_product_id` is stored as a plain string (e.g.
`"479dae0e-d25d-4438-97a7-bf392746100c"`).  SQLAlchemy's `UUID` column
type requires a `uuid.UUID` object when used in a `filter()` clause.
`_get_current_product()` (in both `DynamicDialog` and `BaseWindow`)
converts the string before calling `Product.get_by_id()`:

```python
from uuid import UUID as _UUID
if isinstance(product_id, str):
    product_id = _UUID(product_id)
product = Product.get_by_id(product_id)
```

The same `_to_uuid()` helper is used when loading `ProductUnit` and
`ProductManufacturer` via their FK columns.

---

## VirtualKeyboard — explicit hide on init

`DynamicDialog` and `BaseWindow` both create a `VirtualKeyboard` child
widget in `__init__`.  Qt's `showChildren()` mechanism auto-shows
any child widget that has never been explicitly hidden when the parent
is shown.  The keyboard's `resizeEvent` override resizes it to
`970 × 315` px, and `draw_window` calls `raise_()` — the combination
was placing an invisible but event-blocking overlay over the top
~315 px of every dialog, preventing tab-bar clicks and top DataGrid
row clicks.

**Fix:** `self.keyboard.hide()` is called immediately after the
keyboard is created so Qt marks it as *explicitly hidden* and will not
auto-show it with the parent.

```python
self.keyboard = VirtualKeyboard(source=None, parent=self)
self.keyboard.hide()   # prevent auto-show via showChildren
```

---

## New Enums

### FormName

```python
PRODUCT_LIST   = 27   # Product list / search form
PRODUCT_DETAIL = 28   # Product detail modal dialog
```

### EventName

```python
PRODUCT_LIST_FORM = "PRODUCT_LIST_FORM"  # Navigate to product list
PRODUCT_SEARCH    = "PRODUCT_SEARCH"     # Execute search
PRODUCT_DETAIL    = "PRODUCT_DETAIL"     # Open detail dialog
```

### ControlName

```python
PRODUCT_SEARCH_TEXTBOX  = "PRODUCT_SEARCH_TEXTBOX"
PRODUCT_LIST_DATAGRID   = "PRODUCT_LIST_DATAGRID"
PRODUCT_DETAIL_TAB      = "PRODUCT_DETAIL_TAB"
PRODUCT_INFO_GRID       = "PRODUCT_INFO_GRID"
PRODUCT_BARCODE_GRID    = "PRODUCT_BARCODE_GRID"
PRODUCT_ATTRIBUTE_GRID  = "PRODUCT_ATTRIBUTE_GRID"
PRODUCT_VARIANT_GRID    = "PRODUCT_VARIANT_GRID"
```

---

## New Event Handlers (ProductEvent)

**File:** `pos/manager/event/product.py`  
**Class:** `ProductEvent`

| Method | Description |
|--------|-------------|
| `_product_list_form_event()` | Navigate to Product List form |
| `_product_search_event()` | Query DB and populate DataGrid |
| `_product_detail_event()` | Store `current_product_id` and open modal |

`ProductEvent` is mixed into `EventHandler` alongside the existing
event classes.

---

## State Management

`Application.current_product_id` (added to `CurrentData.__init__` as a
plain instance attribute — **not** an `AutoSaveDescriptor`) carries the
UUID string of the product selected in the Product List.  It is set by
`_product_detail_event` and read by the DataGrid populate helpers
inside `DynamicDialog`.

---

## Database Initialisation

| File | Change |
|------|--------|
| `data_layer/db_init_data/form.py` | Added form_no=8 (`PRODUCT_LIST`), form_no=9 (`PRODUCT_DETAIL`, 1024×768) |
| `data_layer/db_init_data/form_control.py` | Product List controls (5); Product Detail TABCONTROL + 4 × FormControlTab + 4 × DATAGRID + CLOSE button; PRODUCTS nav button on Main Menu |

> **Note:** After adding these changes, delete the existing database
> (`db.sqlite3`) and restart so `_insert_default_forms` and
> `_insert_form_controls` can seed the new records.

---

## File Summary

| Path | Type | Description |
|------|------|-------------|
| `user_interface/control/tab_control/tab_control.py` | New | `TabControl` widget (`Qt.ClickFocus`) |
| `user_interface/control/tab_control/__init__.py` | New | Package init |
| `user_interface/control/__init__.py` | Modified | Exports `TabControl` |
| `data_layer/model/definition/form_control_tab.py` | New | `FormControlTab` model (tab page definitions) |
| `data_layer/model/definition/form_control.py` | Modified | Added `fk_tab_id` column + relationships |
| `data_layer/model/__init__.py` | Modified | Exports `FormControlTab` |
| `data_layer/enums/form_name.py` | Modified | Added `PRODUCT_LIST`, `PRODUCT_DETAIL` |
| `data_layer/enums/event_name.py` | Modified | Added product events |
| `data_layer/enums/control_name.py` | Modified | Added product control names |
| `data_layer/db_init_data/form.py` | Modified | Added form_no=8 and form_no=9 |
| `data_layer/db_init_data/form_control.py` | Modified | Product List + Product Detail controls |
| `pos/manager/event/product.py` | New | `ProductEvent` handler class |
| `pos/manager/event/__init__.py` | Modified | Exports `ProductEvent` |
| `pos/manager/event_handler.py` | Modified | Inherits `ProductEvent`; maps events |
| `pos/manager/current_data.py` | Modified | Added `current_product_id` (transient) |
| `user_interface/render/dynamic_renderer.py` | Modified | Handles `TABCONTROL` type + `FormControlTab` loading |
| `user_interface/window/base_window.py` | Modified | `_create_tab_control()` (QVBoxLayout pages), `keyboard.hide()`, `_get_current_product()` + populate helpers |
| `user_interface/window/dynamic_dialog.py` | Modified | Same as `base_window.py`; also `keyboard.hide()` |

---

[← Back to Table of Contents](README.md) | [Previous: Cashier Management](14-cashier-management.md) | [Next: Project Structure →](20-project-structure.md)
