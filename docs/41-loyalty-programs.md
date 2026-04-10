# Loyalty Programs (Local)

This document describes the **local** loyalty stack: data models, seed data, phone-based customer identity, automatic membership when a customer is linked to a sale, **point earning** and **redemption** on sales, **tier reassignment** from points and calendar-year spending, and what is **not** implemented yet (void/refund clawback automation, GATE/third-party).

## Overview

- **Program and tiers**: `LoyaltyProgram` and `LoyaltyTier` are seeded by `_insert_loyalty()` (default program name *SaleFlex Rewards*, Bronze → Platinum tiers). Point rates and welcome/birthday fields live on `LoyaltyProgram`.
- **Policy tables** (per program, seeded with the default program):
  - **`LoyaltyProgramPolicy`**: Customer identifier mode (`PHONE` vs legacy `LOYALTY_CARD`), whether a phone is required to enroll, default country calling code for normalization (seed uses `90`), void/refund point policy placeholder (`NONE` / future values), integration provider (`LOCAL` | `GATE` | `EXTERNAL` — only `LOCAL` is active).
  - **`LoyaltyEarnRule`**: Ordered rules (`priority` ascending) evaluated by **`LoyaltyEarnService`** at checkout completion (see **Earning engine** below).
  - **`LoyaltyRedemptionPolicy`**: Caps and steps for POS redemption (`max_basket_amount_share_from_points`, `minimum_points_to_redeem`, `points_redemption_step`, `allow_partial_redemption`); consumed by **`LoyaltyRedemptionService`** when the cashier uses **BONUS** (`BONUS_PAYMENT`).
- **Membership**: `CustomerLoyalty` (one row per customer for the program). Optional `loyalty_card_number` remains for legacy or external card IDs; **primary recognition is the customer’s phone**.
- **Ledger**: `LoyaltyPointTransaction` records movements. New enrollments can create a `WELCOME` row when `LoyaltyProgram.welcome_points` is greater than zero. Completed sales create **`EARNED`** and, when applicable, **`REDEEMED`** (negative `points_amount`) rows linked to the permanent `TransactionHead`.

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

## Tier assignment

- **`LoyaltyService.member_qualifies_for_tier`**: For each `LoyaltyTier`, if both `min_points_required` and `min_annual_spending` are set, the member qualifies when **either** `lifetime_points` meets the point floor **or** `annual_spent` meets the spending floor (matching the model docstring). If only one threshold is set, that condition alone applies.
- **`LoyaltyService.recalculate_membership_tier`**: Among active tiers for the program, ordered by `tier_level` descending, the member is assigned the **first** (highest) tier they qualify for. Called after new enrollment (including welcome points), when an existing member is loaded at sale assignment, and after a completed sale **once** spending and any **earned** points for that receipt have been applied.
- **`LoyaltyService.apply_completed_sale_to_membership`**: On each completed **sale** transaction, increments `total_purchases`, adds `total_amount` to `total_spent`, updates `annual_spent` for the **calendar year** of `transaction_date_time` (resets annual spending when the sale year is after the year of `last_activity_date`), sets `last_activity_date`. Tier recalculation can be deferred when points are credited in the same session (`recalculate_tier=False`).

## Earning engine (`LoyaltyEarnService`)

On **`PaymentService.copy_temp_to_permanent()`**, **before** the permanent `TransactionHead` is inserted:

1. **`LoyaltyEarnService.stage_document_earn(document_data)`** runs for **sale** transactions with a **non–walk-in** customer and an active `CustomerLoyalty` row linked to the active program.
2. **Document net total** (v1): `TransactionHeadTemp.total_amount` (must be ≥ `LoyaltyProgram.min_purchase_for_points` when that field is set). Base points:  
   `floor(total_amount × points_per_currency × tier.points_multiplier)`  
   Tier multiplier is taken from the member’s **`fk_loyalty_tier_id`** at earn time (before this sale’s earned points are added to `lifetime_points`).  
   **Payment mix filter**: If `LoyaltyProgram.settings_json` contains `earn_eligible_payment_types` (array of `EventName` payment strings such as `CASH_PAYMENT`), **every** non-cancelled `TransactionPaymentTemp.payment_type` on the receipt must appear in that list or **no** points are earned on that sale (default seed lists common tenders; omit the key to allow all payment types).
3. **`LoyaltyEarnRule`** rows for that program, **`priority` ascending**, by `rule_type`:
   - **`DOCUMENT_TOTAL`**: Adds `extra_points` or `bonus_points` from `config_json` (after applying the same tier multiplier).
   - **`LINE_ITEM`**: Per active line (`is_cancel` / `is_voided` excluded). `config_json` may include `fk_product_id` or `product_code` / `plu`, plus `extra_points` / `bonus_points_per_line` and/or `points_per_currency` on the line’s `total_price`.
   - **`CATEGORY`** or **`DEPARTMENT`**: Same line filters; match `fk_department_main_group_id` and optionally `fk_department_sub_group_id`, then `extra_points` and/or `points_per_currency` on matched line totals.
   - **`PRODUCT_SET`** or **`BUNDLE`**: If every UUID in `product_ids` (or `required_product_ids`) appears on at least one active line with a non-null `fk_product_id`, adds `bonus_points` or `extra_points` (tier multiplier applied). `bundle_id` alone does not match until catalog wiring exists.
4. **`TransactionHeadTemp.loyalty_points_earned`** is set to the **sum** of the above (non-negative), subject to the payment-type filter. A **`TransactionLoyaltyTemp`** snapshot row is appended to `document_data["loyalty"]` (`points_earned`, `points_redeemed`, `redemption_amount`, `points_balance_before` / `after` preview, `bonus_multiplier`, `campaign_bonus`).

Then the permanent **`TransactionHead`** is created (copying `loyalty_points_earned` and `loyalty_points_redeemed`), related **`TransactionLoyalty`** and **`TransactionDiscount`** rows are copied from temp snapshots, and **`LoyaltyService.on_sale_transaction_completed(..., permanent_head_id=head.id)`**:

- Applies spending counters (tier recalculation **deferred** during that call).
- Debits **`REDEEMED`** points (reduces **`available_points`** / **`total_points`**; **`lifetime_points`** unchanged) when **`loyalty_points_redeemed`** &gt; 0.
- Credits **`EARNED`** points into balances and inserts the corresponding **`LoyaltyPointTransaction`** rows.
- Runs **`recalculate_membership_tier`** once so new lifetime points affect tier.

Walk-in, missing customer, missing membership, or inactive program → **`loyalty_points_earned`** is set to **0** and no earn snapshot / ledger row.

## Redemption at payment (`LoyaltyRedemptionService`, `BONUS_PAYMENT`)

1. **`LoyaltyProgram.currency_per_point`**: monetary discount per point redeemed (required).
2. On the **PAYMENT** form, the cashier enters **whole points** on the numpad, then presses **BONUS** (`PAY_TYPE_BONUS` → **`EventName.BONUS_PAYMENT`**).
3. **`LoyaltyRedemptionService.apply_points_redemption`** caps redemption by: member **`available_points`**, remaining **net** amount due (`total_amount − total_discount_amount − total_payment_amount`), optional **`max_basket_amount_share_from_points`** on **`LoyaltyRedemptionPolicy`**, and policy **minimum / step / partial** rules.
4. A **`TransactionDiscountTemp`** row is created with **`discount_type="LOYALTY"`**, **`discount_code`** like `100PTS`, and **`discount_amount`** equal to the applied currency value. **`TransactionHeadTemp.total_discount_amount`** and **`loyalty_points_redeemed`** increase; the sale list and amount table refresh so the line appears as a **discount** (not a payment tender).
5. **`PaymentService`** treats **net amount due** (gross minus discounts) everywhere: remaining balance, change, and document completion.
6. On completion, **`LoyaltyService`** posts **`LoyaltyPointTransaction`** `REDEEMED` with negative **`points_amount`** and notes derived from loyalty discount lines.

**Existing databases**: insert a `TransactionDiscountType` row with **`code="LOYALTY"`** (see `_insert_transaction_discount_types`) if missing, or redemption copy to permanent `TransactionDiscount` will be skipped.

**Void / refund / exchange**: **`LoyaltyService.on_void_or_cancel_completed_sale`** is a **stub** for reversing earn/redeem and clawing back redemption value on returns; wire it when refund/exchange flows persist linked heads.

**Tier percentage discount** on product lines remains separate (not applied automatically at sale time).

## Code layout

| Area | Location |
|------|----------|
| Policy / rule models | `data_layer/model/definition/loyalty_program_policy.py`, `loyalty_earn_rule.py`, `loyalty_redemption_policy.py` |
| Customer phone column | `data_layer/model/definition/customer.py` |
| Seed data | `data_layer/db_init_data/loyalty.py` (`_insert_loyalty_program_policy`, `_insert_loyalty_redemption_policy`, `_insert_loyalty_default_earn_rule`) |
| Enrollment / tier / ledger credit | `pos/service/loyalty_service.py` (`LoyaltyService`) |
| Earn calculation + temp staging | `pos/service/loyalty_earn_service.py` (`LoyaltyEarnService`) |
| Redemption (BONUS button) | `pos/service/loyalty_redemption_service.py` (`LoyaltyRedemptionService`); `pos/manager/event/payment.py` (`_bonus_payment_event`) |
| Completed sale hook | `pos/service/payment_service.py` → `LoyaltyEarnService.stage_document_earn`, discount/payment/loyalty permanent copy, `LoyaltyService.on_sale_transaction_completed`, then `CustomerSegmentService.on_sale_transaction_completed` |
| Full temp→perm copy (e.g. cancel path) | `pos/manager/document_manager.py` — payment completion uses the slimmer `PaymentService.copy_temp_to_permanent` |
| UI / events | `pos/manager/event/customer.py` (save, search, assign) |

## Schema upgrades

`metadata.create_all()` creates **new** tables but does **not** add new columns to existing SQLite files. If you upgrade an old `db.sqlite3`, either recreate the database or run a manual migration (e.g. `ALTER TABLE customer ADD COLUMN phone_normalized …`) before relying on phone uniqueness and loyalty seed rows.

## Related documentation

- [Customer Management](17-customer-management.md) — search, save, sale assignment
- [Customer Segmentation](42-customer-segmentation.md) — marketing segments and `marketing_profile()` (tier stays on loyalty side)
- [Database Models Overview](21-database-models.md) — full model list
- [Database Initialization](33-database-initialization.md) — `_insert_loyalty`
- [Service Layer](25-service-layer.md) — `LoyaltyService`, `CustomerSegmentService`

---

**Last Updated:** 2026-04-10  
**Version:** 1.0.0b7  
**License:** MIT
