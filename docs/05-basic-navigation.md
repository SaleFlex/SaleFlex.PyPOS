# Basic Navigation

## Main Menu

After logging in, you'll see the main menu with options for:

- **Sales**: Process transactions and orders
- **Closure**: End-of-day operations and cash drawer reconciliation
- **ClosureCountrySpecific**: Country-specific closure data with template-based initialization
- **Configuration**: System settings and customization
- **Cashier Management**: View and edit cashier accounts (see below)
- **Logout**: Exit current user session

## Using the NumPad

The NumPad interface allows for quick numeric input:

1. Tap the digits to enter numbers
2. Use "Backspace" to delete the last character
3. "Clear" will reset the entire input
4. "Enter" confirms your entry

The current status bar (bottom of the screen) always shows the active quantity
multiplier as **x1**, **x3**, etc.

### NumPad — Four Operating Modes

The NumPad in the **SALE** form supports four distinct workflows:

---

#### Mode 1 — Barcode / PLU Code Lookup (ENTER key)

Enter a number on the NumPad and press **ENTER** to search for and sell a product.

- The system first searches the **barcode** table for an exact match.
- If no barcode match is found it then searches **product codes**.
- On success the product is added to the sale list (quantity = 1 or the active
  multiplier set by the **X** button — see Mode 3).
- On failure an error message is displayed.

> **PLU inquiry (no sale):** If you pressed the green **PLU** button with an *empty*
> NumPad first, the *next* **ENTER** does **not** sell — it opens an info dialog with
> the product **price** and **stock totals per warehouse** (from `WarehouseProductStock`,
> falling back to the product card stock when no rows exist). You can also type the
> barcode or product code first, then press **PLU**, for the same dialog.

**Example:**
```
NumPad: 5000157070008  → ENTER
Result: 1× Coca-Cola added to sale (barcode match)

NumPad: 1001           → ENTER
Result: 1× Salted Crisps added (product code match)
```

---

#### Mode 2 — Inline Quantity × PLU Button

Enter a quantity on the NumPad and immediately press a **PLU / barcode product button**.

The NumPad value is consumed as the sale quantity; the button supplies the product.

**Example:**
```
NumPad: 3  → click [Coca-Cola] button
Result: 3× Coca-Cola added to sale list
```

> **Note:** If the NumPad is empty, the default quantity of **1** is used.

---

#### Mode 3 — PLU (inquiry) and X (Quantity Multiplier) Buttons

Below the payment list, the **SALE** form has **two** buttons on one row: **PLU** (left)
and **X** (right), and **SUSPEND** aligns with that row in the payment column (under **CASH** / **CREDIT CARD**). **PLU** is for **price / warehouse stock lookup** only (see the note
under Mode 1 and the **PLU inquiry** example below). **X** is the quantity multiplier.

For workflows that involve barcode scanning (where you cannot type then click
simultaneously), pre-set the quantity using the **X** button:

1. Enter the desired quantity on the NumPad (e.g. `3`)
2. Press the **X** button — the NumPad clears and the status bar shows **x3**
3. The next sale (PLU button click *or* barcode ENTER) uses that quantity
4. After the sale the multiplier resets to **x1**

**Example:**
```
NumPad: 3  → X button  → status bar shows "x3"
NumPad: 5000157070008  → ENTER
Result: 3× Coca-Cola added to sale
Status bar returns to "x1"
```

**PLU inquiry examples (no line added to the sale):**
```
NumPad: 5000157070008  → PLU
Result: Info dialog — price and stock per warehouse

PLU (NumPad empty)  → NumPad: 5000157070008  → ENTER
Result: Same info dialog
```

---

#### Mode 4 — Payment Amount (CASH / CREDIT buttons)

Enter a tender amount on the NumPad before pressing **CASH** or **CREDIT CARD**.

The value is interpreted in the currency's **minor unit**
(e.g. for GBP with 2 decimal places: enter **10000** for £100.00).

- This applies only to **generic** payment buttons (e.g. the "CASH" button).
- **Preset** denomination buttons (e.g. "20 £", "50 £", "100 £") always use their
  encoded amount and ignore the NumPad.

**Example (GBP):**
```
NumPad: 10000  → CASH
Result: £100.00 cash payment recorded
Change is calculated if total was less than £100.00
```

---

#### SUSPEND (market — hold sale or open suspended list)

Below **CASH** and **CREDIT CARD**, the **SUSPEND** button matches the height of **PLU** and **X** on the same row.

| Situation | What happens |
|-----------|----------------|
| Open sale with at least one line (product or department) | The document is marked **pending** in the database (`is_pending = True`, `transaction_status = pending`). A **new empty draft** is created for the next sale, and the sale screen is refreshed so you are not still tied to the suspended receipt number. |
| No open document (or only an empty document with no lines) | The **Suspended Sales (Market)** form opens: a table of suspended receipts with **Receipt No**, **Line count**, and **Total** (an internal **Id** column is hidden). Select a row and press **ACTIVATE** to resume that cart on the sale screen (`is_pending` cleared, status **active**). Use **BACK** to return to the previous screen. |

Other business types (for example restaurants) can use different list forms in the future; the default seeded form targets **market / retail** suspended carts.

---

#### CANCEL (cancel the entire transaction document)

Below **20 £**, **50 £** and **100 £** denomination buttons, the **CANCEL** button sits on the same row as **PLU**, **X**, and **SUSPEND**, aligned at the bottom of the payment area.

| Situation | What happens |
|-----------|----------------|
| Open sale with at least one active line | The document is immediately **cancelled**: `transaction_status = CANCELLED`, `is_cancel = True`, `is_closed = True`, and `cancel_reason = "Canceled by cashier: {username}"` are persisted to the database. A confirmation message box is shown with the **Receipt No**, **Closure No**, **Total**, and the cancel reason. After dismissal, a new empty draft document is created automatically for the next sale. |
| No open document, empty draft, already closed/pending/cancelled | An information message box is shown: *"There is no open document to cancel."* No database changes are made. |

> **Note:** The CANCEL button voids the **entire** transaction. To cancel only a single line item, tap the row in the sale list and choose **DELETE** from the Item Actions popup instead.

---

## Processing a Sale

1. From the main menu, select **Sales**
2. Add products using one of these methods:
   - Click a **PLU / barcode product button** (optionally prefix with a NumPad quantity)
   - Type a **barcode or product code** on the NumPad and press **ENTER**
3. To sell multiple units of the next scan, press the **X** button (right) after typing the quantity; use **PLU** (left) only to check price and stock without selling
4. When all items are added, select the payment method:
   - Click a **denomination button** (e.g. "20 £") for exact cash amounts
   - Or enter a custom amount on the NumPad, then press **CASH** or **CREDIT CARD**
5. Print a receipt for the customer

## Sale List Item Actions

Tapping (clicking) any row in the **sale list** opens an **Item Actions** popup with three options:

| Button | Action |
|--------|--------|
| **REPEAT** | Adds an identical new line below all existing items. The repeated line is saved to the database and the document totals are updated immediately. |
| **DELETE** | Soft-cancels the selected line — it remains visible in the list with a strikethrough style but is marked as cancelled (`is_cancel = True`) in the database. Totals are recalculated excluding the cancelled line. |
| **CANCEL** | Closes the popup without any change. |

### REPEAT behaviour

- A new `TransactionProductTemp` (or `TransactionDepartmentTemp`) record is cloned from the original and saved to the database with the next available `line_no`.
- The `Sales Amount` in the amount table increases immediately.
- The repeated row has its own database ID and can itself be individually REPEAT-ed or DELETE-d later.

### DELETE behaviour

- The matching database record is marked `is_cancel = True` and saved immediately.
- `Sales Amount` in the amount table decreases by the cancelled line's total.
- The cancelled row remains visible in the sale list for the rest of the session (strikethrough style), but will **not** appear the next time the sale screen is loaded.
- **If the last active line is deleted**, the document is automatically marked as `CANCELLED` and `is_closed = True`. `document_data` is reset to `None`, the status bar clears, and the amount table shows zeros. The next product sale will start a completely new document.

## Cashier Management

Accessible from the main menu via the **Cashier Management** button.

### Cashier Selection Combobox

A combobox at the top of the form allows switching between cashier accounts:

- **Admin users** (`is_administrator = True`): All cashiers are listed. Selecting a cashier loads their data into the form for viewing or editing.
- **Non-admin users** (`is_administrator = False`): Only their own account is shown.

### Field Permissions

| Logged-in user | Cashier being viewed | Password | Other fields |
|---|---|---|---|
| Admin | Any cashier | Editable | Editable |
| Non-admin | Own account | Editable | **Read-only** |

Non-admin cashiers can update **only their own password**. All other fields are displayed as read-only (grey background).

### Saving Changes

Click the **SAVE** button to persist changes. The system saves to the cashier currently selected in the combobox (`editing_cashier`), which may differ from the logged-in user when an admin is editing another account.

### Default Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Administrator |
| `jdoe` | `1234` | Standard cashier |

---

[← Back to Table of Contents](README.md) | [Previous: First Login](04-first-login.md) | [Next: Dynamic Forms System →](06-dynamic-forms.md)

