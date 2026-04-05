# Cashier Management

Access cashier management from the main menu by pressing **CASHIER MANAGEMENT**.

---

## Cashier Roles

| Role | `is_administrator` | Capabilities |
|------|--------------------|-------------|
| Administrator | `True` | View and edit all cashier accounts, create new cashiers, perform end-of-day closure, access all configuration |
| Standard cashier | `False` | Update own password only; all other profile fields are read-only |

Default accounts seeded at first run:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | Administrator |
| `jdoe` | `1234` | Standard cashier |

> Change the `admin` password after the first login.

---

## Cashier Selection Combobox

A `CASHIER_MGMT_LIST` combobox at the top of the form controls which account is displayed:

- **Admin users**: All cashiers are listed. Select any cashier to load their data into the form.
- **Non-admin users**: Only their own account is shown.

Selecting a cashier from the combobox updates `CurrentData.editing_cashier` and redraws the form with that cashier's data loaded.

> `editing_cashier` is the cashier whose data is *displayed*. It may differ from `cashier_data` (the currently logged-in cashier) when an admin is managing another account.

---

## Field Permissions

| Logged-in user | Profile being edited | Password | Other text fields | `IS_ADMINISTRATOR` / `IS_ACTIVE` |
|---------------|---------------------|----------|-------------------|----------------------------------|
| Admin | Any cashier | Editable | Editable | Editable |
| Non-admin | Own account | Editable | **Read-only** (grey) | **Disabled** |

---

## Adding a New Cashier (Admin Only)

1. Press the **ADD NEW CASHIER** button (SaddleBrown, bottom-left).
   - The button is hidden for non-admin users.
2. The form clears; the cashier combobox is temporarily hidden.
3. Fill in the required fields (No, User Name, Name, Last Name, Password, etc.).
4. Press **SAVE**.

The new record is INSERTed (no existing ID), added to the `pos_data["Cashier"]` cache, and the form redraws with the new cashier pre-selected in the combobox.

---

## Saving Changes

Press **SAVE** to persist the currently displayed cashier's data. The generic panel save mechanism:

1. Collects all textbox and checkbox values from the `CASHIER` panel.
2. Maps the panel name to the `Cashier` model.
3. Converts field values to their correct types (bool before int — see [Dynamic Forms — `_save_changes_event`](22-dynamic-forms-system.md#_save_changes_event--type-conversion-rules)).
4. Saves to `editing_cashier` (the selected account).
5. If `editing_cashier` is also the logged-in cashier, `cashier_data` cache is updated too.

---

## Form Controls Reference

| Control name | Type | Description |
|-------------|------|-------------|
| `CASHIER_MGMT_LIST` | COMBOBOX | Cashier selector — lists all (admin) or self (non-admin) |
| `NO` | TEXTBOX | Cashier number (integer) |
| `USER_NAME` | TEXTBOX | Login username |
| `NAME` | TEXTBOX | First name |
| `LAST_NAME` | TEXTBOX | Last name |
| `PASSWORD` | TEXTBOX | Login password |
| `IDENTITY_NUMBER` | TEXTBOX | National ID / employee number |
| `DESCRIPTION` | TEXTBOX | Notes |
| `IS_ADMINISTRATOR` | CHECKBOX | Admin flag |
| `IS_ACTIVE` | CHECKBOX | Active flag (inactive accounts cannot log in) |
| `ADD_NEW_CASHIER` | BUTTON | Create a blank cashier record (admin only) |
| `SAVE` | BUTTON | Persist changes (`SAVE_CHANGES` event) |
| `BACK` | BUTTON | Return to main menu |

---

## Related Events

| `EventName` | Handler | Trigger |
|-------------|---------|---------|
| `CASHIER` / `CASHIER_FORM` | `_cashier_form_event` | Navigate to cashier management form |
| `SELECT_CASHIER` | `_select_cashier_event` | Combobox selection changed |
| `ADD_NEW_CASHIER` | `_add_new_cashier_event` | Add new cashier button pressed |
| `SAVE_CHANGES` | `_save_changes_event` | SAVE button pressed |

---

[← Back to Table of Contents](README.md) | [Previous: End-of-Day Closure](13-end-of-day-closure.md) | [Next: Product Management →](15-product-management.md)
