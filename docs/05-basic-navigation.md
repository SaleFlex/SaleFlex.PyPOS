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

#### Mode 3 — X (Quantity Multiplier) Button

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

## Processing a Sale

1. From the main menu, select **Sales**
2. Add products using one of these methods:
   - Click a **PLU / barcode product button** (optionally prefix with a NumPad quantity)
   - Type a **barcode or product code** on the NumPad and press **ENTER**
3. To sell multiple units of the next scan, press the **X** button after typing the quantity
4. When all items are added, select the payment method:
   - Click a **denomination button** (e.g. "20 £") for exact cash amounts
   - Or enter a custom amount on the NumPad, then press **CASH** or **CREDIT CARD**
5. Print a receipt for the customer

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

