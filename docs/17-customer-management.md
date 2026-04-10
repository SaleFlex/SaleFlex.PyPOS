# Customer Management

SaleFlex.PyPOS provides a fully DB-driven Customer Management module that is accessible both from the **Main Menu** and directly from the **SALE form**. It covers customer list search, adding new customers, viewing and editing customer details, and browsing each customer's transaction activity history. When accessed from the SALE form, the selected or newly created customer is automatically linked to the active sale transaction.

---

## Overview

| Form | Form No | Display Mode | Purpose |
|------|---------|-------------|---------|
| `CUSTOMER_LIST` | 17 | MAIN | Search and browse the customer database; add new customers |
| `CUSTOMER_DETAIL` | 18 | MODAL | View, edit, or create a customer record; review activity history |

---

## Accessing Customer Management

### From the Main Menu

1. Log in with any cashier account.
2. From the **Main Menu**, press the **CUSTOMER** button (purple, bottom row).
3. The **Customer List** form opens.

![Customer List (management context: DETAIL / ADD / BACK)](../static_files/images/sample_customer_list_form.jpg)

### From the SALE Form (Assign Customer to a Sale)

1. While on the **SALE** form, press **FUNC** to activate the alternate button functions.
2. The **SUB TOTAL** button switches to **CUSTOMER**.
3. Press **CUSTOMER** — the Customer List form opens in *sale-assignment context*.
4. Search for an existing customer, select a row, and press **DETAIL** or **SELECT** (to view/edit or confirm assignment), **or** press **ADD** to create a brand-new customer.
5. Press **BACK** to return to the SALE form.
   - If a customer was selected via **DETAIL** or saved via **ADD**, they are automatically assigned to the active sale transaction.

In *sale-assignment context*, the list may show **SELECT** instead of **DETAIL** for the primary action on the bottom row.

![SALE form — CUSTOMER path (after FUNC)](../static_files/images/sample_sale_customer_form.jpg)

---

## SALE Form — CUSTOMER Dual Button

The **SUB TOTAL** button on the SALE form is a **dual-function** button:

| State | Caption | Function | Trigger |
|-------|---------|----------|---------|
| Normal | `SUB TOTAL` | Calculate transaction subtotal | Default |
| Alternate | `CUSTOMER` | Open Customer List to assign a customer | After pressing **FUNC** |

Pressing **FUNC** toggles **labels** on all dual-function buttons on the SALE form between their normal and alternate states (no sale event is fired by FUNC alone).

After **any** dual-function button on the SALE form is used—including **SUB TOTAL** / **CUSTOMER**—every dual-function control returns to its **normal** caption; press **FUNC** again if you still need alternate labels.

![SALE form — alternate dual-function labels after FUNC](../static_files/images/sample_sale_func_dual_functions_form.jpg)

---

## Customer List Form

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Search textbox (820px wide)                         ] [SEARCH]      │
│                                                                      │
│ ┌──────────────────────────── DataGrid ───────────────────────────┐  │
│ │ First Name │ Last Name │ Phone          │ E-mail │ City         │  │
│ │ ...        │ ...       │ ...            │ ...    │ ...          │  │
│ └─────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ [DETAIL]  [ADD]                                        [BACK]        │
└──────────────────────────────────────────────────────────────────────┘
```

### Controls

| Control | Type | Position | Function |
|---------|------|----------|----------|
| Search textbox | TextBox | Top | Enter search query (name, phone, e-mail) |
| **SEARCH** | Button (green) | Top-right | Execute search — populates the DataGrid |
| DataGrid | DataGrid | Centre | Displays matching customers |
| **DETAIL** / **SELECT** | Button (purple) | Bottom-left | **DETAIL**: open Customer Detail for selected row (management). **SELECT**: confirm assignment when opened from SALE after **FUNC** → **CUSTOMER** |
| **ADD** | Button (green) | Bottom-left (next to DETAIL) | Open blank Customer Detail to create a new customer |
| **BACK** | Button (blue) | Bottom-right | Return to previous form (assigns selected/added customer to sale when in sale-assignment context) |

### Search Behaviour

- Matching is case-insensitive `LIKE` on `name`, `last_name`, `phone_number`, and `email_address`.
- If the search text can be normalized to a digits-only phone key (using the default country calling code from **`LoyaltyProgramPolicy`**, e.g. `90`), an **exact match** on **`Customer.phone_normalized`** is also included in the filter.
- An empty search term returns all active, non-deleted customers (max 500 rows).
- Walk-in Customer (`is_walkin = True`) is **always excluded** from results.
- Results are sorted by Last Name, then First Name.

---

## Phone number and loyalty (local)

- **`phone_number`**: What the cashier types (display format).
- **`phone_normalized`**: Digits-only canonical value, **unique** per customer when set. Maintained on **SAVE** from the Customer Detail form via `LoyaltyService`; used for loyalty de-duplication and phone-first lookup. Saving fails with a dialog if another customer already has the same normalized phone.
- When a **non–walk-in** customer is assigned to the **active sale** (BACK from the list or SELECT in sale-assignment context), `LoyaltyService.ensure_loyalty_on_sale_assignment()` may create **`CustomerLoyalty`**, set **`TransactionHeadTemp.loyalty_member_id`**, record **welcome** points per `LoyaltyProgram.welcome_points`, and **recompute tier**. Enrollment requires a valid phone when `LoyaltyProgramPolicy.require_customer_phone_for_enrollment` is true. Walk-in customers are never enrolled.
- On **`FormName.PAYMENT`**, **BONUS** (`BONUS_PAYMENT`) redeems **whole points** from the numpad via **`LoyaltyRedemptionService`**: a **`LOYALTY`** discount line reduces the amount due; on completion **`LoyaltyService`** posts **`LoyaltyPointTransaction`** (`REDEEMED`). See [Loyalty Programs — Redemption](41-loyalty-programs.md#redemption-at-payment-loyaltyredemptionservice-bonus_payment).
- When that sale is **fully paid** and copied to permanent tables, **`LoyaltyEarnService`** stages **`loyalty_points_earned`** (subject to optional **`earn_eligible_payment_types`** in program **`settings_json`**) and a **`TransactionLoyalty`** snapshot; **`LoyaltyService`** then updates **`CustomerLoyalty`** spending fields, debits **`REDEEMED`** if points were redeemed, credits **`LoyaltyPointTransaction`** (`EARNED`) when points > 0, and refreshes **`fk_loyalty_tier_id`** (see [Loyalty Programs](41-loyalty-programs.md) — *Earning engine* and *Tier assignment*). **`CustomerSegmentService`** also refreshes **marketing** segment memberships from **`CustomerSegment.criteria_json`** (independent of tier).
- Saving the Customer Detail form runs the same segment sync so rules such as **NEW_CUSTOMER** or **BIRTHDAY** can apply without a new sale.

Full data model and seed behaviour: [Loyalty Programs](41-loyalty-programs.md) · [Customer Segmentation](42-customer-segmentation.md).

---

## Customer Detail Form (Modal)

Pressing **DETAIL** (with a row selected) or **ADD** opens the `CUSTOMER_DETAIL` modal dialog.

- **DETAIL mode**: The panel is pre-populated with the selected customer's data (edit mode).
- **ADD mode**: The panel is blank (create mode). The SAVE button creates a new `Customer` record.

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

Press **SAVE** (green, bottom) to write changes or create the record in the database.

![Customer Detail — Customer Info tab](../static_files/images/sample_customer_detail_form.jpg)

> Walk-in Customer cannot be edited — SAVE is blocked when `is_walkin = True`.

### Tab 1 — Activity History

A read-only **DataGrid** (`CUSTOMER_ACTIVITY_GRID`) listing the customer's **completed** sales stored in the permanent `transaction_head` table. Rows are loaded when the modal opens by `DynamicDialog._populate_customer_activity_grid`: all non-deleted heads with `fk_customer_id` equal to the open customer, ordered by date/time (newest first), up to **500** rows.

| Column | Source |
|--------|--------|
| Receipt No | `receipt_number` |
| Closure No | `closure_number` |
| Date/Time | `transaction_date_time` |
| Type | `document_type` |
| Total / Payment / Change | `total_amount`, `total_payment_amount`, `total_change_amount` |
| Status | `transaction_status` |

Open (draft) carts in `transaction_head_temp` do not appear here — only finalized documents copied to `TransactionHead` when a sale completes or is cancelled (and persisted). After **SAVE** on **ADD** (first creation of a customer), the grid is refreshed so the **Activity History** tab reflects the new `current_customer_id` (typically still empty until that customer completes a sale).

### Buttons

| Button | Position | Action |
|--------|----------|--------|
| **SAVE** | Bottom-left (green) | Persist Customer Info panel changes, or create a new customer |
| **BACK** | Bottom-right (blue) | Close the dialog (discards unsaved changes) |

---

## Sale-Assignment Workflow

When the Customer List is opened from the SALE form via the **CUSTOMER** dual button:

```
SALE form
  └─ [FUNC] → CUSTOMER button appears
       └─ [CUSTOMER] ──► CUSTOMER_LIST (sale-assignment context)
                              ├─ [DETAIL] ──► CUSTOMER_DETAIL (modal, edit mode)
                              │                   └─ [BACK] ──► CUSTOMER_LIST
                              ├─ [ADD]    ──► CUSTOMER_DETAIL (modal, add mode)
                              │                   └─ [SAVE]  → new customer created
                              │                   └─ [BACK] ──► CUSTOMER_LIST
                              └─ [BACK]  ──► SALE (customer assigned to transaction)
```

**Assignment rules:**
- If the cashier pressed **DETAIL** on a row, that customer is marked as the selected sale-customer.
- If the cashier pressed **ADD** and saved a new customer, the new customer is marked as the selected sale-customer.
- On **BACK** from Customer List (in sale-assignment context), the marked customer's UUID is written to `TransactionHeadTemp.fk_customer_id` and saved to the database.
- If neither **DETAIL** nor **ADD** was used, the cashier returns to SALE with no customer assigned (the Walk-in Customer placeholder retains the transaction).

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

Key fields relevant to this module:

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
| `CUSTOMER_LIST_FORM` | `_customer_list_form_event` | Navigate to Customer List; sets sale-context flag if called from SALE |
| `CUSTOMER_FORM` | `_customer_list_form_event` | Legacy alias — same as above |
| `CUSTOMER` | `_customer_list_form_event` | Legacy alias |
| `CUSTOMER_SEARCH` | `_customer_search_event` | Execute search, populate DataGrid |
| `CUSTOMER_DETAIL` | `_customer_detail_event` | Open Customer Detail modal (edit mode) |
| `CUSTOMER_DETAIL_SAVE` | `_customer_detail_save_event` | Save Customer Info panel (create or update) |
| `CUSTOMER_ADD` | `_customer_add_event` | Open blank Customer Detail modal (add mode) |
| `CUSTOMER_LIST_BACK` | `_customer_list_back_event` | Context-aware BACK: assign customer to sale if in sale-context, then navigate back |

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

### From Main Menu

```
MAIN_MENU
  └─ [CUSTOMER] ──► CUSTOMER_LIST
                        ├─ [DETAIL] ──► CUSTOMER_DETAIL (modal)
                        │                   └─ [BACK] ──► CUSTOMER_LIST
                        ├─ [ADD]    ──► CUSTOMER_DETAIL (modal, blank)
                        │                   └─ [SAVE / BACK] ──► CUSTOMER_LIST
                        └─ [BACK]  ──► MAIN_MENU
```

### From SALE Form (Sale-Assignment Context)

```
SALE
  └─ [FUNC → CUSTOMER] ──► CUSTOMER_LIST (sale-assignment context active)
                                ├─ [DETAIL] ──► CUSTOMER_DETAIL (modal, edit mode)
                                │                   └─ [BACK] ──► CUSTOMER_LIST
                                ├─ [ADD]    ──► CUSTOMER_DETAIL (modal, add mode)
                                │                   └─ [SAVE]  → new customer created & selected
                                │                   └─ [BACK] ──► CUSTOMER_LIST
                                └─ [BACK]  ──► SALE (selected/added customer assigned to transaction)
```

---

## Database Reset Note

> **Important:** The Customer List ADD button and the SALE form CUSTOMER dual button are defined in the database-driven form control initialization. If you are upgrading an existing installation, **delete `db.sqlite3`** and restart the application so the new form controls are seeded correctly.

> **Loyalty / phone column:** New installations add **`customer.phone_normalized`** and loyalty policy tables automatically. Older SQLite files do not gain new columns from `create_all()` alone — recreate the database or migrate the schema before relying on phone uniqueness and loyalty seed data.

---

## Related Documentation

- [Dynamic Forms System](22-dynamic-forms-system.md) — how DB-driven forms and panels work
- [Database Models Overview](21-database-models.md) — Customer, CustomerLoyalty, CustomerSegment models
- [Loyalty Programs](41-loyalty-programs.md) — policy tables, `LoyaltyService`, enrollment on sale assignment
- [Customer Segmentation](42-customer-segmentation.md) — `CustomerSegmentService`, `criteria_json`, `marketing_profile`
- [Event System](24-event-system.md) — CustomerEvent handler class
- [Database Initialization](33-database-initialization.md) — `_insert_customers()` seed function
- [Sale Transactions](10-sale-transactions.md) — SALE form NumPad modes and dual-function buttons

---

**Last Updated:** 2026-04-10  
**Version:** 1.0.0b7  
**License:** MIT
