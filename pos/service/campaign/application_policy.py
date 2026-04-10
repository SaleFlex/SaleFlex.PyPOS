"""
Campaign / promotion application order and stacking (design contract).

Copyright (c) 2025-2026 Ferhat Mousavi

This module documents behaviour agreed for the local campaign engine and for GATE payloads.
Runtime code should follow these rules unless settings override them later.

## Evaluation moment

- **Sale / cart screen:** Auto campaigns (`Campaign.is_auto_apply`) are evaluated when
  the open sale document changes in ways that affect eligibility (line add/remove,
  line discount or markup, customer assignment, etc.) via `sync_campaign_discounts_on_document`.
- **Payment screen:** **Loyalty BONUS** (`LOYALTY` `TransactionDiscountTemp`) is applied
  only during payment on **net due** (see `PaymentService`); it does not change how
  campaign eligibility is computed on merchandise, but net due includes all document
  discounts, including **CAMPAIGN** lines already on the temp document.

## Base amount for thresholds (basket minimum / maximum)

- **Merchandise subtotal** = sum of `total_price` over active product lines:
  `TransactionProductTemp` rows where `is_cancel` is false (and `is_voided` is false
  if present). Line-level cashier **discount/markup** is already reflected in
  `unit_price` / `total_price` (replacement-line pattern).

## Stacking (`priority`, `is_combinable`)

1. Consider only campaigns that pass date/time/store/segment/product rules and
   `is_auto_apply` / coupon flags (coupon flow is later).
2. Sort eligible campaigns by **`priority` descending** (higher runs first).
3. **Greedy application:** walk the sorted list; a campaign applies if still eligible
   given the cart after previous applications.
4. If an applied campaign has **`is_combinable == False`**, **stop** — no further
   campaigns apply in that evaluation pass.
5. If **`is_combinable == True`**, continue to the next eligible campaign.

Non-combinable campaigns are therefore mutually exclusive by order of priority;
combinable ones can stack until a non-combinable campaign is applied (if any).

## Relative to manual discounts

- Per-line **DISC % / DISC AMT / MARK** are part of line totals before campaign
  evaluation; the engine does not reopen those lines.
- Document-level discounts that are **not** campaign-driven (e.g. future manager
  header discounts) should be excluded from the campaign engine’s own outputs or
  handled explicitly when we add them; this policy assumes campaign discounts are the main
  document-level promotional lines besides **LOYALTY** at payment.

## Loyalty earning / redemption

- **Redemption:** After campaign discounts exist on the temp document, loyalty
  redemption still uses **net due** (gross − total discounts) per existing payment
  rules.
- **Earning:** Unchanged; earn services run on completed sale as today.
"""

# Reserved ``discount_type`` on ``TransactionDiscountTemp`` / ``TransactionDiscount`` when the row
# comes from the local campaign engine or a GATE / connector response. Use ``discount_code`` for
# the campaign ``Campaign.code`` or a short coupon token (DB column max length 15).
CAMPAIGN_DISCOUNT_TYPE_CODE = "CAMPAIGN"

__all__ = ["CAMPAIGN_DISCOUNT_TYPE_CODE"]
