# SaleFlex.PyPOS Comprehensive Guide

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [First Login](#first-login)
5. [Basic Navigation](#basic-navigation)
6. [Dynamic Forms System](#dynamic-forms-system)
7. [Virtual Keyboard Configuration](#virtual-keyboard-configuration)
8. [Database Models Overview](#database-models-overview)
9. [Database Initialization Functions](#database-initialization-functions)
10. [Troubleshooting](#troubleshooting)
11. [Support and Resources](#support-and-resources)

---

## Introduction

SaleFlex.PyPOS is a modern point-of-sale application designed for retail stores, restaurants, and service-oriented businesses. This touch-screen enabled POS system streamlines sales transactions, inventory management, and customer relationship management in a user-friendly interface.

This comprehensive guide covers installation, configuration, and advanced features of SaleFlex.PyPOS.

---

## System Requirements

### Hardware Requirements
- Touch Screen Device running Windows or Linux
- Optional: Secondary customer-facing display
- ESC/P compatible receipt printer
- 2D/3D barcode scanner
- Weighing scale (optional)

### Software Requirements
- Python 3.13 or higher
- Internet connection for installation
- Operating System: Windows 10/11 or Linux

### Supported Database Engines
- **SQLite** (default, included)
- **PostgreSQL**
- **MySQL**
- **Oracle**
- **Microsoft SQL Server**
- **Firebird**
- **Sybase**

---

## Installation Guide

### Step 1: Install Python

1. Visit the [Python downloads page](https://www.python.org/downloads/) and download Python 3.13 or higher.
2. Run the installer and make sure to check "Add Python to PATH" during installation.
3. Verify the installation by opening a command prompt or terminal and typing:
   ```
   python --version
   ```
   You should see the Python version displayed.

### Step 2: Download SaleFlex.PyPOS

1. Visit the [SaleFlex.PyPOS GitHub repository](https://github.com/SaleFlex/SaleFlex.PyPOS).
2. Click the green "Code" button and select "Download ZIP".
3. Extract the ZIP file to a location of your choice (e.g., `D:\GitHub.Projects\` or your home directory).

### Step 3: Set up the Virtual Environment

1. Open a command prompt or terminal.
2. Navigate to the SaleFlex.PyPOS folder you extracted:
   ```
   cd path\to\SaleFlex.PyPOS
   ```
3. Create a virtual environment:
   
   For Windows:
   ```
   python -m venv venv
   ```
   
   For macOS/Linux:
   ```
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   
   For Windows:
   ```
   venv\Scripts\activate.bat
   ```
   
   For macOS/Linux:
   ```
   source venv/bin/activate
   ```

### Step 4: Install Dependencies

With the virtual environment activated, install required packages:

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

1. With the virtual environment activated, run the application:
   
   For Windows:
   ```
   python saleflex.py
   ```
   
   For macOS/Linux:
   ```
   python3 saleflex.py
   ```

2. The SaleFlex.PyPOS application should now start and display the login screen.

### Configuration

- Edit `settings.toml` to configure database connections, hardware settings, and business parameters
- The application uses SQLite by default, stored in `db.sqlite3`

---

## First Login

Upon first launch, you will be presented with a login screen. Use the following default credentials:

- **Username:** admin
- **Password:** admin

> **Important:** For security reasons, please change the default administrator password after your first login.

After successful login, you will be redirected to the main menu.

---

## Basic Navigation

### Main Menu

After logging in, you'll see the main menu with options for:

- **Sales**: Process transactions and orders
- **Closure**: End-of-day operations and cash drawer reconciliation
- **Configuration**: System settings and customization
- **Logout**: Exit current user session

### Using the NumPad

The NumPad interface allows for quick numeric input:

1. Tap the digits to enter numbers
2. Use "Backspace" to delete the last character
3. "Clear" will reset the entire input
4. "Enter" confirms your entry

### Processing a Sale

1. From the main menu, select "Sales"
2. Scan products using a barcode scanner or enter item codes manually using the NumPad
3. Adjust quantities as needed
4. When all items are added, complete the transaction
5. Print a receipt for the customer

---

## Dynamic Forms System

### Overview

SaleFlex.PyPOS uses a **database-driven dynamic form system** instead of TOML files. This change makes forms more flexible and manageable. All form definitions are stored in the database, allowing for dynamic form creation and modification without code changes.

### Key Changes

#### Database Model Updates

**Form Model** (`form.py`) - New fields:
- `fore_color`: Form foreground color
- `is_startup`: Boolean flag to determine the initial form to open
- `display_mode`: Which screen to display on ("MAIN", "CUSTOMER", "BOTH")

**FormControl Model** (`form_control.py`) - New fields:
- `fk_target_form_id`: UUID ForeignKey to the target form when button is clicked
- `form_transition_mode`: Transition mode ("MODAL" or "REPLACE")

### New Classes

#### DynamicFormRenderer

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

#### DynamicDialog

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

### Updated Classes

#### Interface (`interface.py`)

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

#### CurrentStatus (`current_status.py`)

Startup form support added:

```python
# New features
current_form_id  # Current form's UUID
startup_form_id  # Startup form's UUID
load_startup_form()  # Loads startup form from database
```

#### Application (`application.py`)

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

#### GeneralEvent (`event/general.py`)

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

### Deprecated Files

#### Interpreter.py

**DEPRECATED**: Should no longer be used. Use DynamicFormRenderer instead.

The file is preserved but shows a deprecation warning:
```python
warnings.warn(
    "Interpreter class is deprecated. Use DynamicFormRenderer instead.",
    DeprecationWarning
)
```

#### settings.toml

The `[design_files]` section has been removed. Form definitions are now in the database.

### Form Transition System

#### Button-Based Form Transition

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

#### Programmatic Form Transition

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

### Startup Form System

#### Setting in Database

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

#### Startup Form Priority Order

1. Forms with `is_startup=True` (first by ID)
2. Form with `name='LOGIN'`
3. None (error condition)

### Database Migration

#### New Columns

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

### Examples

#### Example 1: Creating a Customer Form

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

#### Example 2: Transition from Main Form to Customer Form

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

### Testing and Debugging

#### Form Rendering Test

```python
# DynamicFormRenderer test
renderer = DynamicFormRenderer(form_name='LOGIN')
print(f"Settings: {renderer.settings}")
print(f"Design controls: {len(renderer.design)}")

# Check each control
for control in renderer.design:
    print(f"Control: {control['type']} - {control.get('caption', 'N/A')}")
```

#### Startup Form Test

```python
# Startup form check
from user_interface.render.dynamic_renderer import DynamicFormRenderer

startup_form = DynamicFormRenderer.get_startup_form()
if startup_form:
    print(f"Startup form: {startup_form.name}")
else:
    print("No startup form found!")
```

### Known Issues and Solutions

#### Issue 1: Form Not Found

**Symptom:** "Form not found" error

**Solution:**
```python
# Check if form exists
forms = Form.filter_by(name='LOGIN', is_deleted=False)
if not forms:
    print("Form not found, creating...")
    # Create form
```

#### Issue 2: Colors Not Displaying Correctly

**Symptom:** Colors appear black or white

**Solution:**
```python
# Color format: "0xRRGGBB" must be a string
form.back_color = "0x3268A8"  # Correct
# form.back_color = 0x3268A8   # Wrong (integer)
# form.back_color = "#3268A8"  # Works but not recommended
```

#### Issue 3: Modal Form Not Opening

**Symptom:** Modal form not displaying

**Solution:**
```python
# Ensure transition_mode is written correctly
control.form_transition_mode = "MODAL"  # Correct (uppercase)
# control.form_transition_mode = "modal"  # Works (code does upper())
```

### Performance Tips

1. **RAM Management**: Consider a cache system for frequently used forms instead of `REPLACE`
2. **Database Queries**: Forms and controls are loaded into `pos_data` dict at application startup
3. **Modal Dialog Cleanup**: Modal dialogs are automatically cleaned up (no memory leaks)

### Future Enhancements

- [ ] Form cache system (for frequently used forms)
- [ ] Form template system (common form templates)
- [ ] Form validation (required fields, format checks)
- [ ] Form wizard (multi-step forms)
- [ ] Drag & drop form designer (GUI tool)
- [ ] Form versioning (form history)

---

## Virtual Keyboard Configuration

### Overview

The SaleFlex POS system supports **database-driven virtual keyboard configuration**. All visual aspects of the virtual keyboard (colors, sizes, fonts, etc.) are stored in the database and can be customized without changing code.

### Features

- **Dynamic Configuration**: All keyboard settings loaded from database  
- **Multiple Themes**: Switch between different keyboard themes instantly  
- **Enable/Disable**: Toggle virtual keyboard on/off (use physical keyboard when disabled)  
- **Hot Reload**: Settings can be reloaded without restarting the application  
- **Fully Customizable**: Font, colors, button sizes, spacing, and more  

### Database Model

#### PosVirtualKeyboard Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | String | Theme name (e.g., "DEFAULT_VIRTUAL_KEYBOARD") |
| `is_active` | Boolean | **Controls if virtual keyboard is shown** |
| `keyboard_width` | Integer | Total keyboard width in pixels |
| `keyboard_height` | Integer | Total keyboard height in pixels |
| `x_position` | Integer | X position (0 = auto-center) |
| `y_position` | Integer | Y position (0 = bottom) |
| `font_family` | String | Button font family |
| `font_size` | Integer | Button font size |
| `button_width` | Integer | Regular button width |
| `button_height` | Integer | Regular button height |
| `button_min_width` | Integer | Min button width |
| `button_max_width` | Integer | Max button width |
| `button_min_height` | Integer | Min button height |
| `button_max_height` | Integer | Max button height |
| `button_background_color` | String | Button background (supports gradients) |
| `button_pressed_color` | String | Button color when pressed |
| `button_border_color` | String | Button border color |
| `button_border_width` | Integer | Border width in pixels |
| `button_border_radius` | Integer | Border radius for rounded corners |
| `space_button_min_width` | Integer | Space bar minimum width |
| `space_button_max_width` | Integer | Space bar maximum width |
| `special_button_min_width` | Integer | Backspace/Enter min width |
| `special_button_max_width` | Integer | Backspace/Enter max width |
| `control_button_width` | Integer | Caps/Sym/Close button width |
| `control_button_active_color` | String | Color when Caps/Sym is active |
| `button_text_color` | String | Optional text color |
| `button_text_color_pressed` | String | Optional text color when pressed |

### Pre-installed Themes

#### 1. DEFAULT_VIRTUAL_KEYBOARD (Active by default)
- **Size**: 970x315 pixels
- **Theme**: Light gradient
- **Font**: Noto Sans CJK JP, 20px
- **Best for**: Standard touchscreen displays

#### 2. DARK_THEME_KEYBOARD
- **Size**: 970x315 pixels
- **Theme**: Dark gradient
- **Font**: Noto Sans CJK JP, 20px
- **Best for**: Night mode or dark UI themes

#### 3. COMPACT_KEYBOARD
- **Size**: 750x250 pixels
- **Theme**: Light gradient (smaller)
- **Font**: Noto Sans CJK JP, 16px
- **Best for**: Smaller screens or when space is limited

### How to Use

#### Using the Test Script

Run the interactive test script:

```bash
python test_virtual_keyboard_settings.py
```

This provides a menu to:
1. View all keyboard themes
2. Switch between themes
3. Create custom themes
4. Disable virtual keyboard

#### Programmatic Usage

##### Enable/Disable Virtual Keyboard

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

# Disable virtual keyboard (use physical keyboard)
with Engine().get_session() as session:
    keyboards = session.query(PosVirtualKeyboard).all()
    for kb in keyboards:
        kb.is_active = False
    session.commit()

# Enable specific theme
with Engine().get_session() as session:
    theme = session.query(PosVirtualKeyboard).filter_by(
        name="DEFAULT_VIRTUAL_KEYBOARD"
    ).first()
    theme.is_active = True
    session.commit()
```

##### Switch Themes

```python
from user_interface.control.virtual_keyboard import KeyboardSettingsLoader

# Reload settings (use after making database changes)
KeyboardSettingsLoader.reload_settings()

# Check if keyboard is enabled
is_enabled = KeyboardSettingsLoader.is_keyboard_enabled()
```

##### Create Custom Theme

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

with Engine().get_session() as session:
    custom = PosVirtualKeyboard(
        name="MY_CUSTOM_THEME",
        is_active=False,  # Don't activate yet
        keyboard_width=800,
        keyboard_height=280,
        font_family="Arial",
        font_size=18,
        button_width=70,
        button_height=35,
        button_background_color="rgb(220, 220, 220)",
        button_pressed_color="rgb(50, 150, 250)",
        button_border_color="#888888",
        button_border_width=2,
        button_border_radius=6,
        # ... set other properties as needed
    )
    session.add(custom)
    session.commit()
```

### Architecture

#### Component Overview

```
┌─────────────────────────────────────────────────────┐
│                  Application Start                   │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│          db_initializer.init_db()                    │
│  - Creates tables                                    │
│  - Inserts initial data                              │
│  - Initializes KeyboardSettingsLoader                │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│       KeyboardSettingsLoader.initialize()            │
│  - Connects to database                              │
│  - Loads active keyboard settings                    │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│     AlphaNumericVirtualKeyboard.display()            │
│  - Checks if keyboard is enabled                     │
│  - Loads settings from KeyboardSettingsLoader        │
│  - Creates KeyboardButton with settings              │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│            KeyboardButton.__init__()                 │
│  - Applies styles from database settings             │
│  - Uses fallback styles if settings unavailable     │
└─────────────────────────────────────────────────────┘
```

#### Files Changed/Created

**New Files:**
- `data_layer/model/definition/pos_virtual_keyboard.py` - Database model
- `data_layer/db_init_data/pos_virtual_keyboard.py` - Initial data
- `user_interface/control/virtual_keyboard/keyboard_settings_loader.py` - Settings loader
- `test_virtual_keyboard_settings.py` - Test/demo script

**Modified Files:**
- `data_layer/model/definition/__init__.py` - Added PosVirtualKeyboard import
- `data_layer/db_init_data/__init__.py` - Added keyboard settings initialization
- `data_layer/db_initializer.py` - Initialize KeyboardSettingsLoader
- `user_interface/control/virtual_keyboard/__init__.py` - Export KeyboardSettingsLoader
- `user_interface/control/virtual_keyboard/keyboard_button.py` - Use database settings
- `user_interface/control/virtual_keyboard/alphanumeric_virtual_keyboard.py` - Load and apply settings

### Benefits

#### For End Users
- Customize keyboard appearance without developer help
- Switch themes instantly (light/dark/compact)
- Disable virtual keyboard when using physical keyboard
- Adjust keyboard size for different screen sizes

#### For Developers
- No hardcoded styles in the code
- Easy to add new themes via database
- Settings centralized in one model
- Backward compatible (fallback to defaults if DB unavailable)

### Examples

#### Example 1: Restaurant POS (Large Touchscreen)
```python
# Use DEFAULT_VIRTUAL_KEYBOARD (970x315px)
# Good for 15" or larger touchscreens
activate_keyboard_theme("DEFAULT_VIRTUAL_KEYBOARD")
```

#### Example 2: Retail POS (Small Touchscreen)
```python
# Use COMPACT_KEYBOARD (750x250px)
# Good for 10-12" touchscreens
activate_keyboard_theme("COMPACT_KEYBOARD")
```

#### Example 3: Night Shift / Dark Mode
```python
# Use DARK_THEME_KEYBOARD
# Easier on eyes in low-light environments
activate_keyboard_theme("DARK_THEME_KEYBOARD")
```

#### Example 4: Physical Keyboard Available
```python
# Disable virtual keyboard entirely
disable_virtual_keyboard()
```

### Future Enhancements

Potential future improvements:
- [ ] Multiple keyboard layouts (QWERTY, AZERTY, numeric-only)
- [ ] Language-specific keyboards
- [ ] Animation settings
- [ ] Sound effects on key press
- [ ] Keyboard layout editor UI
- [ ] Import/export themes

---

## Database Models Overview

SaleFlex.PyPOS uses a comprehensive database schema with over 80 models organized into logical categories. All models inherit from base classes that provide CRUD operations, audit trails, and soft delete functionality.

### Core System Models

#### User and Store Management
- **Cashier**: User accounts for POS operators with authentication, permissions, and personal information
- **Store**: Store/outlet information including hardware configuration, system settings, and business details
- **Table**: Restaurant table management for table service operations

#### Location and Geography
- **Country**: Country master data with ISO codes and names
- **City**: City master data linked to countries
- **District**: District/region master data linked to cities

#### Currency and Payment
- **Currency**: Currency master data (USD, EUR, GBP, etc.)
- **CurrencyTable**: Currency exchange rates with historical tracking
- **PaymentType**: Payment method definitions (Cash, Card, Mobile Payment, etc.)
- **ClosureCurrency**: End-of-day currency reconciliation

### Product Management Models

#### Product Core
- **Product**: Main product catalog with pricing, stock, descriptions, and product attributes
- **ProductVariant**: Product variations (size, color, style) linked to base products
- **ProductAttribute**: Product attributes and specifications (dimensions, weight, materials, etc.)
- **ProductBarcode**: Barcode associations for products (EAN, UPC, custom barcodes)
- **ProductBarcodeMask**: Barcode format definitions and validation rules
- **ProductUnit**: Measurement units (PCS, KG, L, M, etc.)
- **ProductManufacturer**: Manufacturer/brand information

#### Product Organization
- **DepartmentMainGroup**: Main product category groups
- **DepartmentSubGroup**: Sub-categories within main groups

### Transaction Models

#### Transaction Headers
- **TransactionHead**: Main transaction record with customer, date, totals, and status
- **TransactionHeadTemp**: Temporary transaction header during transaction processing
- **TransactionSequence**: Transaction numbering sequences per document type
- **TransactionDocumentType**: Document type definitions (Sale, Return, Refund, etc.)
- **TransactionLog**: Transaction audit log for all transaction events

#### Transaction Details
- **TransactionProduct**: Line items in transactions (products sold)
- **TransactionProductTemp**: Temporary transaction line items
- **TransactionPayment**: Payment records for transactions
- **TransactionPaymentTemp**: Temporary payment records
- **TransactionTax**: Tax calculations per transaction
- **TransactionTaxTemp**: Temporary tax calculations
- **TransactionDiscount**: Discounts applied to transactions
- **TransactionDiscountTemp**: Temporary discount records
- **TransactionSurcharge**: Surcharges applied to transactions
- **TransactionSurchargeTemp**: Temporary surcharge records
- **TransactionTip**: Tip/gratuity records
- **TransactionTipTemp**: Temporary tip records
- **TransactionTotal**: Transaction totals summary
- **TransactionTotalTemp**: Temporary totals

#### Transaction Extensions
- **TransactionDelivery**: Delivery information for transactions
- **TransactionDeliveryTemp**: Temporary delivery records
- **TransactionNote**: Notes and comments on transactions
- **TransactionNoteTemp**: Temporary notes
- **TransactionRefund**: Refund transaction records
- **TransactionRefundTemp**: Temporary refund records
- **TransactionVoid**: Voided transaction records
- **TransactionFiscal**: Fiscal printer records (for compliance)
- **TransactionFiscalTemp**: Temporary fiscal records
- **TransactionKitchenOrder**: Kitchen display system orders
- **TransactionKitchenOrderTemp**: Temporary kitchen orders
- **TransactionLoyalty**: Loyalty points earned/redeemed in transactions
- **TransactionLoyaltyTemp**: Temporary loyalty records

### Warehouse Management Models

- **Warehouse**: Warehouse/depot definitions with location, capacity, and environmental settings
- **WarehouseLocation**: Specific locations within warehouses (aisles, shelves, bins)
- **WarehouseProductStock**: Current stock levels per product per warehouse location
- **WarehouseStockMovement**: Stock movement history (receipts, transfers, adjustments)
- **WarehouseStockAdjustment**: Stock adjustment records with reasons and approvals

### Customer Management Models

- **Customer**: Customer master data with contact information, preferences, and consent management
- **CustomerSegment**: Customer segmentation definitions (VIP, New, Frequent, etc.)
- **CustomerSegmentMember**: Customer membership in segments

### Campaign and Promotion Models

- **CampaignType**: Campaign type definitions (Product Discount, Basket Discount, etc.)
- **Campaign**: Promotional campaigns with rules, dates, and conditions
- **CampaignRule**: Detailed campaign rules (product filters, time restrictions, etc.)
- **CampaignProduct**: Products eligible for campaigns
- **CampaignUsage**: Campaign usage tracking per customer/transaction
- **Coupon**: Coupon/voucher definitions with barcode/QR code support
- **CouponUsage**: Coupon redemption tracking

### Loyalty Program Models

- **LoyaltyProgram**: Loyalty program definitions with point earning rules
- **LoyaltyTier**: Membership tiers (Bronze, Silver, Gold, Platinum) with benefits
- **CustomerLoyalty**: Customer loyalty account with current points and tier
- **LoyaltyPointTransaction**: Point transaction history (earned, redeemed, expired)

### Cashier Performance Models

- **CashierWorkSession**: Cashier work shift sessions with start/end times
- **CashierWorkBreak**: Break records during work sessions
- **CashierPerformanceMetrics**: Performance metrics per cashier (sales, transactions, etc.)
- **CashierPerformanceTarget**: Performance targets and goals for cashiers
- **CashierTransactionMetrics**: Detailed transaction metrics per cashier

### Closure and End-of-Day Models

- **Closure**: End-of-day closure records with cash reconciliation
- **ClosureTotal**: Closure totals summary
- **ClosurePaymentTypeSummary**: Payment type summaries per closure
- **ClosureCurrency**: Currency reconciliation per closure

### Form and UI Models

- **Form**: Dynamic form definitions with layout, colors, and display settings
- **FormControl**: Form controls (buttons, textboxes, comboboxes) with positioning and behavior
- **PosVirtualKeyboard**: Virtual keyboard theme and configuration settings
- **PosSettings**: POS system-wide settings and configuration
- **ReceiptHeader**: Receipt header templates
- **ReceiptFooter**: Receipt footer templates
- **LabelValue**: Label/value pairs for translations and configuration

### Tax and Compliance Models

- **Vat**: VAT/tax rate definitions with percentages and effective dates

### Model Features

All models include:
- **UUID Primary Keys**: Unique identifiers for all records
- **Audit Fields**: Created/updated timestamps and user tracking
- **Soft Delete**: Records are marked as deleted rather than physically removed
- **CRUD Operations**: Standard create, read, update, delete methods
- **Server Synchronization**: Support for multi-store synchronization via `fk_server_id`

---

## Database Initialization Functions

The `data_layer/db_init_data` module contains functions that populate the database with initial/default data when the database is first created. These functions are called in a specific order to respect foreign key dependencies.

### Initialization Flow

The `insert_initial_data()` function in `db_init_data/__init__.py` orchestrates the initialization process:

1. **Admin Cashier** (`_insert_admin_cashier`): Creates default administrator user (username: admin, password: admin)
2. **Countries** (`_insert_countries`): Inserts world countries with ISO codes
3. **Default Store** (`_insert_default_store`): Creates default store with system information (MAC address, OS version, serial number)
4. **Cities** (`_insert_cities`): Inserts city master data
5. **Districts** (`_insert_districts`): Inserts district/region data
6. **Warehouses** (`_insert_warehouses`): Creates default warehouses (Main, Backroom, Sales Floor, etc.)
7. **Currencies** (`_insert_currencies`): Inserts major world currencies (USD, EUR, GBP, etc.)
8. **Currency Table** (`_insert_currency_table`): Sets up currency exchange rates
9. **Payment Types** (`_insert_payment_types`): Creates payment methods (Cash, Credit Card, Debit Card, etc.)
10. **VAT Rates** (`_insert_vat_rates`): Inserts default VAT/tax rates (0%, 5%, 20%, etc.)
11. **Product Units** (`_insert_product_units`): Creates measurement units (PCS, KG, L, M, etc.)
12. **Product Manufacturers** (`_insert_product_manufacturers`): Inserts sample manufacturer data
13. **Department Groups** (`_insert_department_groups`): Creates product category structure (main groups and sub-groups)
14. **Products** (`_insert_products`): Inserts sample products for testing
15. **Product Variants** (`_insert_product_variants`): Creates product variations
16. **Product Attributes** (`_insert_product_attributes`): Inserts product attribute definitions
17. **Product Barcodes** (`_insert_product_barcodes`): Associates barcodes with products
18. **Transaction Document Types** (`_insert_transaction_document_types`): Creates document types (Sale, Return, etc.)
19. **Transaction Sequences** (`_insert_transaction_sequences`): Sets up transaction numbering sequences
20. **Product Barcode Masks** (`_insert_product_barcode_masks`): Defines barcode format rules
21. **Default Forms** (`_insert_default_forms`): Creates LOGIN and MAIN_MENU forms
22. **Form Controls** (`_insert_form_controls`): Populates forms with controls (buttons, textboxes, etc.)
23. **Label Values** (`_insert_label_values`): Inserts translation labels and configuration values
24. **Cashier Performance Targets** (`_insert_cashier_performance_targets`): Sets up performance targets
25. **Virtual Keyboard Settings** (`_insert_virtual_keyboard_settings`): Creates default keyboard theme
26. **Alternative Keyboard Themes** (`_insert_alternative_keyboard_themes`): Adds additional keyboard themes
27. **Campaigns** (`_insert_campaigns`): Creates sample promotional campaigns
28. **Loyalty Programs** (`_insert_loyalty`): Sets up loyalty program with tiers
29. **Customer Segments** (`_insert_customer_segments`): Creates default customer segments
30. **POS Settings** (`_insert_pos_settings`): Configures system-wide POS settings

### Function Details

#### `_insert_admin_cashier(session)`
Creates the default administrator cashier account:
- Username: `admin`
- Password: `admin` (should be hashed in production)
- Name: Ferhat Mousavi
- Administrator privileges enabled
- Returns the created cashier object for use in other initialization functions

#### `_insert_default_store(session)`
Creates the default store with:
- System information (MAC address, OS version, hostname)
- Generated serial number
- Default hardware settings (printers, displays, scales)
- Links to default country (United Kingdom)

#### `_insert_countries(session)`
Inserts comprehensive country master data including:
- ISO country codes
- Country names in multiple languages
- Numeric codes
- Phone country codes

#### `_insert_currencies(session)`
Inserts major world currencies:
- Currency codes (USD, EUR, GBP, TRY, etc.)
- Currency names
- Symbols
- Decimal places
- Returns GBP currency for POS settings reference

#### `_insert_products(session, admin_cashier_id)`
Inserts sample products covering various categories:
- Fresh food items
- Packaged goods
- Beverages
- Different VAT rates
- Various units (PCS, KG)
- Links to departments, manufacturers, and warehouses

#### `_insert_default_forms(session, cashier_id)`
Creates essential forms:
- **LOGIN**: Login screen with authentication fields
- **MAIN_MENU**: Main menu with navigation options
- Forms include layout, colors, and display settings

#### `_insert_form_controls(session, cashier_id)`
Populates forms with controls:
- Buttons for navigation and actions
- Textboxes for input
- Labels for display
- Proper positioning and styling

#### `_insert_virtual_keyboard_settings(session)`
Creates the default virtual keyboard theme:
- Size: 970x315 pixels
- Light gradient theme
- Font: Noto Sans CJK JP, 20px
- Button styling and colors

#### `_insert_loyalty(session, admin_cashier_id)`
Sets up loyalty program:
- Default loyalty program with point earning rules
- Membership tiers (Bronze, Silver, Gold, Platinum)
- Tier benefits and point multipliers

#### `_insert_campaigns(session, admin_cashier_id)`
Creates sample promotional campaigns:
- Product discount campaigns
- Basket discount campaigns
- Time-based promotions
- Campaign rules and conditions

### Initialization Behavior

- **Idempotent**: Functions check if data already exists before inserting
- **Dependency Aware**: Functions are called in order to respect foreign key relationships
- **Error Handling**: SQLAlchemy errors are caught and reported
- **Transaction Safe**: All inserts happen within a single database transaction

### Customization

To customize initial data:
1. Modify the respective `_insert_*` functions in `data_layer/db_init_data/`
2. Add new initialization functions and call them in `insert_initial_data()`
3. Ensure proper ordering to respect foreign key dependencies

---

## Troubleshooting

### General Issues

If you encounter issues during installation or operation:

1. Ensure all system requirements are met
2. Check that Python is correctly installed and in your PATH
3. Verify that the virtual environment is activated before running the application
4. For database connection errors, ensure your database server (if using external DB) is running

### Dynamic Forms Issues

#### Form Not Found
**Symptom:** "Form not found" error

**Solution:**
```python
# Check if form exists
forms = Form.filter_by(name='LOGIN', is_deleted=False)
if not forms:
    print("Form not found, creating...")
    # Create form
```

#### Colors Not Displaying Correctly
**Symptom:** Colors appear black or white

**Solution:**
```python
# Color format: "0xRRGGBB" must be a string
form.back_color = "0x3268A8"  # Correct
# form.back_color = 0x3268A8   # Wrong (integer)
# form.back_color = "#3268A8"  # Works but not recommended
```

#### Modal Form Not Opening
**Symptom:** Modal form not displaying

**Solution:**
```python
# Ensure transition_mode is written correctly
control.form_transition_mode = "MODAL"  # Correct (uppercase)
# control.form_transition_mode = "modal"  # Works (code does upper())
```

### Virtual Keyboard Issues

#### Virtual Keyboard Not Showing
1. Check if `is_active` is `True` for at least one keyboard theme
2. Verify database connection
3. Check KeyboardSettingsLoader initialization in logs

#### Styles Not Updating
1. Call `KeyboardSettingsLoader.reload_settings()` after database changes
2. Restart application if settings were changed before initialization

#### Custom Theme Not Appearing
1. Ensure `is_deleted` is `False`
2. Check that theme name doesn't conflict with existing themes
3. Activate the theme by setting `is_active=True`

---

## Support and Resources

For additional help and resources:

- Visit the [SaleFlex.PyPOS GitHub repository](https://github.com/SaleFlex/SaleFlex.PyPOS)
- Review the README.md file for the latest information
- Contact the development team for technical support
- Submit issues via GitHub Issues
- Email: ferhat.mousavi@gmail.com

## Legal Information

SaleFlex.PyPOS is free software licensed under the MIT License.

Copyright (c) 2025 Ferhat Mousavi

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0b2  
**License:** MIT

