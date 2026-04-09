# First Login

Upon first launch, you will be presented with the login screen.

![Login screen](../static_files/images/sample_login.jpg)

## Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | Administrator |
| `jdoe` | `1234` | Standard cashier |

> **Important:** For security reasons, please change the default administrator password after your first login.

## Login Process

1. Select your username from the **cashier name** dropdown (combobox) on the login screen.
2. Enter your password using the on-screen virtual keyboard or a physical keyboard.
3. Press the **LOGIN** button — or simply press **Enter** on your keyboard.

> **Tip (physical keyboard users):** If `form_control_function1` is set to `LOGIN` on the PASSWORD textbox in the database, pressing **Enter** after typing your password is equivalent to clicking the LOGIN button. This makes the login flow keyboard-friendly for workstations with a physical keyboard.

If the credentials are correct, you will be redirected to the **Main Menu**.

![Main Menu](../static_files/images/sample_main_menu.jpg)

## Role Differences

### Administrator (`admin`)

- Can view and edit **all** cashier accounts
- Can create new cashier accounts via the **ADD NEW CASHIER** button
- Can perform **end-of-day closure** operations
- Has full access to POS configuration settings
- All fields in Cashier Management are editable

### Standard Cashier (`jdoe`)

- Can only update **their own password** in Cashier Management
- All other fields in their profile are read-only
- **Cannot** perform closure operations (admin only)
- Cannot manage other cashier accounts

## After Login

After successful login, you will be redirected to the **Main Menu** with options for:

- **SALES** — Start processing transactions
- **CLOSURE** — End-of-day operations (administrators only)
- **SETTING** — POS system configuration
- **CASHIER MANAGEMENT** — Manage cashier accounts
- **LOGOUT** — End the current user session

## Automatic Document Recovery

When logging in, the system automatically checks for any incomplete (non-pending) transactions from a previous session. If an incomplete transaction is found, it is loaded and restored — allowing you to continue from where you left off. If no incomplete transaction exists, a new empty draft document is created ready for the next sale.

---

[← Back to Table of Contents](README.md) | [Previous: Configuration](04-configuration.md) | [Next: Virtual Keyboard Configuration →](06-virtual-keyboard.md)
