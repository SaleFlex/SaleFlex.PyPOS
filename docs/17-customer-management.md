# Customer Management

SaleFlex.PyPOS provides a fully DB-driven Customer Management module accessible from the Main Menu. It covers customer list search, viewing and editing customer details, and browsing each customer's transaction activity history.

---

## Overview

| Form | Form No | Display Mode | Purpose |
|------|---------|-------------|---------|
| `CUSTOMER_LIST` | 17 | MAIN | Search and browse the customer database |
| `CUSTOMER_DETAIL` | 18 | MODAL | View, edit, and review activity for a selected customer |

---

## Accessing Customer Management

1. Log in with any cashier account.
2. From the **Main Menu**, press the **CUSTOMER** button (purple, bottom row).
3. The **Customer List** form opens.

---

## Customer List Form

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Search textbox (820px wide)                         ] [SEARCH]      │
│                                                                      │
│ ┌──────────────────────────── DataGrid ──────────────────────────┐  │
│ │ First Name │ Last Name │ Phone          │ E-mail │ City        │  │
│ │ ...        │ ...       │ ...            │ ...    │ ...         │  │
│ └─────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ [DETAIL]                                              [BACK]         │
└──────────────────────────────────────────────────────────────────────┘
```

### Controls

| Control | Type | Function |
|---------|------|----------|
| Search textbox | TextBox | Enter search query (name, phone, e-mail) |
| **SEARCH** | Button (green) | Execute search — populates the DataGrid |
| DataGrid | DataGrid | Displays matching customers |
| **DETAIL** | Button (purple) | Open Customer Detail for selected row |
| **BACK** | Button (blue) | Return to Main Menu |

### Search Behaviour

- Matching is case-insensitive `LIKE` on `name`, `last_name`, `phone_number`, and `email_address`.
- An empty search term returns all active, non-deleted customers (max 500 rows).
- Walk-in Customer (`is_walkin = True`) is **always excluded** from results.
- Results are sorted by Last Name, then First Name.

---

## Customer Detail Form (Modal)

Pressing **DETAIL** with a row selected opens the `CUSTOMER_DETAIL` modal dialog.

### Tab 0 — Customer Info

Editable fields displayed as label + textbox pairs inside a `CUSTOMER` panel:

| Field | Description |
|-------|-------------|
| First Name | Customer's given name (`name`) |
| Last Name | Customer's family name (`last_name`) |
| Phone | Contact phone number |
| E-mail | E-mail address |
| Address 1 | Street address line 1 |
| Address 2 | Street address line 2 (area, district) |
| City / Area | Town or city |
| Post Code | Postal / ZIP code |
| Description | Free-text notes |

Press **SAVE** (green, bottom) to write changes to the database.

> Walk-in Customer cannot be edited — SAVE is blocked when `is_walkin = True`.

### Tab 1 — Activity History

A read-only DataGrid listing the customer's past transactions (receipts / invoices). Rows are populated from the transaction history linked to `fk_customer_id`.

### Buttons

| Button | Position | Action |
|--------|----------|--------|
| **SAVE** | Bottom-left (green) | Persist Customer Info panel changes |
| **BACK** | Bottom-right (blue) | Close the dialog (discards unsaved changes) |

---

## Walk-in Customer

A special customer record is seeded at database initialisation:

| Field | Value |
|-------|-------|
| `name` | `Walk-in` |
| `last_name` | `Customer` |
| `is_walkin` | `True` |
| `is_active` | `True` |

**Purpose:** Every sale transaction that is finalised without an explicitly selected customer is automatically linked to this Walk-in Customer record. This ensures referential integrity for all transactions in the database and allows aggregate reporting on anonymous sales.

---

## Database Model — Customer

Key fields added or relevant to this module:

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (PK) | Primary key |
| `name` | String(50) | First name |
| `last_name` | String(50) | Family name |
| `phone_number` | String(100) | |
| `email_address` | String(100) | |
| `address_line_1/2/3` | String(100) | Street, area, city |
| `zip_code` | String(50) | Postal code |
| `description` | String(100) | Free-text notes |
| `is_walkin` | Boolean | `True` → Walk-in placeholder; excluded from list search and detail edit |
| `is_active` | Boolean | `False` → soft-hidden (not shown in active queries) |
| `is_deleted` | Boolean (mixin) | Soft-delete flag |
| `date_of_birth` | Date | For birthday campaigns |
| `gender` | String(20) | `MALE`, `FEMALE`, `OTHER`, `PREFER_NOT_TO_SAY` |
| `national_id` | String(50) | National ID number |
| `tax_id` | String(50) | Tax / VAT ID for invoicing |
| `registration_source` | String(50) | `POS`, `MOBILE_APP`, `WEBSITE`, `SOCIAL_MEDIA`, `REFERRAL` |
| `marketing_consent` | Boolean | GDPR/KVKK marketing opt-in |
| `sms_consent` | Boolean | SMS opt-in |
| `email_consent` | Boolean | E-mail opt-in |

---

## Event Handlers

| Event | Handler Method | Description |
|-------|---------------|-------------|
| `CUSTOMER_LIST_FORM` | `_customer_list_form_event` | Navigate to Customer List |
| `CUSTOMER_FORM` | `_customer_list_form_event` | Legacy alias — same as above |
| `CUSTOMER` | `_customer_list_form_event` | Legacy alias |
| `CUSTOMER_SEARCH` | `_customer_search_event` | Execute search, populate DataGrid |
| `CUSTOMER_DETAIL` | `_customer_detail_event` | Open Customer Detail modal |
| `CUSTOMER_DETAIL_SAVE` | `_customer_detail_save_event` | Save Customer Info panel to DB |

All handlers are defined in `pos/manager/event/customer.py` (`CustomerEvent` mixin class) and registered in `pos/manager/event_handler.py`.

---

## Seed Data

### Walk-in Customer

Inserted by `data_layer/db_init_data/customer.py → _insert_customers()`.

### Sample Customers (Development / Demo)

15 sample UK-resident customers are pre-seeded for development and demonstration:

| # | First Name | Last Name | City |
|---|-----------|-----------|------|
| 1 | James | Thornton | London |
| 2 | Sophie | Wentworth | Bristol |
| 3 | Oliver | Blackwood | Leeds |
| 4 | Charlotte | Pemberton | Manchester |
| 5 | Harry | Aldridge | Newcastle upon Tyne |
| 6 | Emily | Forsythe | Edinburgh |
| 7 | George | Hastings | Cambridge |
| 8 | Isabella | Stanhope | East Sussex |
| 9 | William | Carrington | Bristol |
| 10 | Amelia | Blackstone | London |
| 11 | Thomas | Whitfield | Birmingham |
| 12 | Grace | Dunmore | Oxfordshire |
| 13 | Edward | Kingsley | West Yorkshire |
| 14 | Lucy | Davenport | Nottingham |
| 15 | Arthur | Strickland | North Somerset |

Sample data is only inserted once (skipped if any Customer rows already exist).

---

## Form Navigation Flow

```
MAIN_MENU
  └─ [CUSTOMER] ──► CUSTOMER_LIST
                        └─ [DETAIL] ──► CUSTOMER_DETAIL (modal)
                                            └─ [BACK] ──► CUSTOMER_LIST
                        └─ [BACK]  ──► MAIN_MENU
```

---

## Related Documentation

- [Dynamic Forms System](22-dynamic-forms-system.md) — how DB-driven forms and panels work
- [Database Models Overview](21-database-models.md) — Customer, CustomerLoyalty, CustomerSegment models
- [Event System](24-event-system.md) — CustomerEvent handler class
- [Database Initialization](33-database-initialization.md) — `_insert_customers()` seed function

---

**Last Updated:** 2026-04-08  
**Version:** 1.0.0b6  
**License:** MIT
