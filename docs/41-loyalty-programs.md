# Loyalty Programs (Local)

This document describes the **local** loyalty stack: data models, seed data, phone-based customer identity, automatic membership when a customer is linked to a sale, and what is **not** implemented yet (earning at totals, redemption at payment, GATE/third-party).

## Overview

- **Program and tiers**: `LoyaltyProgram` and `LoyaltyTier` are seeded by `_insert_loyalty()` (default program name *SaleFlex Rewards*, Bronze → Platinum tiers). Point rates and welcome/birthday fields live on `LoyaltyProgram`.
- **Policy tables** (per program, seeded with the default program):
  - **`LoyaltyProgramPolicy`**: Customer identifier mode (`PHONE` vs legacy `LOYALTY_CARD`), whether a phone is required to enroll, default country calling code for normalization (seed uses `90`), void/refund point policy placeholder (`NONE` / future values), integration provider (`LOCAL` | `GATE` | `EXTERNAL` — only `LOCAL` is active).
  - **`LoyaltyEarnRule`**: Rows for future earning logic (e.g. `DOCUMENT_TOTAL`); the engine that evaluates rules at checkout is not wired yet.
  - **`LoyaltyRedemptionPolicy`**: Caps and steps for POS redemption; `PaymentService` does not consume these fields yet.
- **Membership**: `CustomerLoyalty` (one row per customer for the program). Optional `loyalty_card_number` remains for legacy or external card IDs; **primary recognition is the customer’s phone**.
- **Ledger**: `LoyaltyPointTransaction` records movements. New enrollments can create a `WELCOME` row when `LoyaltyProgram.welcome_points` is greater than zero.

## Phone normalization (`Customer.phone_normalized`)

- **`phone_normalized`**: Digits-only canonical value, **unique** when set (multiple `NULL` allowed). Used for de-duplication and fast exact lookup.
- **Normalization** is implemented in `LoyaltyService.normalize_phone()` using `LoyaltyProgramPolicy.default_phone_country_calling_code` (e.g. Turkish mobiles: strip a leading `0`, prepend `90` when the number does not already start with the country code).
- **On customer SAVE** (`CustomerEvent._customer_detail_save_event`): the service recomputes `phone_normalized` and blocks the save if another active customer already has the same value (error dialog).
- **Customer list search**: In addition to `LIKE` on name, phone display string, and e-mail, if the search text normalizes to a full key, results can match **`Customer.phone_normalized` exactly**.

## Sale assignment flow

When a **non–walk-in** customer is assigned to the active sale (`_assign_customer_to_sale` in `CustomerEvent`):

1. `LoyaltyService.ensure_loyalty_on_sale_assignment()` runs.
2. The customer’s `phone_normalized` is synced from `phone_number` (same rules as save).
3. If enrollment requires a phone (`require_customer_phone_for_enrollment`) and no normalized phone exists, **no** `CustomerLoyalty` row is created.
4. If the normalized phone duplicates another customer’s row, enrollment is skipped for that assignment (session rolled back for that attempt; sale customer assignment still stands).
5. Otherwise a **`CustomerLoyalty`** row is created on first need (lowest active tier), **`TransactionHeadTemp.loyalty_member_id`** is set, and welcome points plus a **`LoyaltyPointTransaction`** of type `WELCOME` are written when configured.

Walk-in customers are never enrolled.

## Code layout

| Area | Location |
|------|----------|
| Policy / rule models | `data_layer/model/definition/loyalty_program_policy.py`, `loyalty_earn_rule.py`, `loyalty_redemption_policy.py` |
| Customer phone column | `data_layer/model/definition/customer.py` |
| Seed data | `data_layer/db_init_data/loyalty.py` (`_insert_loyalty_program_policy`, `_insert_loyalty_redemption_policy`, `_insert_loyalty_default_earn_rule`) |
| Business helpers | `pos/service/loyalty_service.py` (`LoyaltyService`) |
| UI / events | `pos/manager/event/customer.py` (save, search, assign) |

## Schema upgrades

`metadata.create_all()` creates **new** tables but does **not** add new columns to existing SQLite files. If you upgrade an old `db.sqlite3`, either recreate the database or run a manual migration (e.g. `ALTER TABLE customer ADD COLUMN phone_normalized …`) before relying on phone uniqueness and loyalty seed rows.

## Related documentation

- [Customer Management](17-customer-management.md) — search, save, sale assignment
- [Database Models Overview](21-database-models.md) — full model list
- [Database Initialization](33-database-initialization.md) — `_insert_loyalty`
- [Service Layer](25-service-layer.md) — `LoyaltyService`

---

**Last Updated:** 2026-04-10  
**Version:** 1.0.0b7  
**License:** MIT
