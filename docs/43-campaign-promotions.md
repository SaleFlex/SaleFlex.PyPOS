# Campaign & Promotions (design and cart snapshot)

This document describes **promotional campaigns** in SaleFlex.PyPOS: database entities, the **initial runtime contract** (cart snapshot + stacking rules), and how it connects to **SaleFlex.GATE** / third-party campaign connectors.

**Current status:** Campaign **models and seed data** exist (`Campaign`, `CampaignType`, `CampaignRule`, `CampaignProduct`, usage/coupon tables — see [Database Models → Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)). The **`transaction_discount_type`** table includes **`CAMPAIGN`** (new installs and patched DBs on startup). **`CampaignService.evaluate_proposals()`** runs a **read-only local evaluation** (basket, time-based, product-linked types — see below) but **does not attach discounts to the open document**; wiring SALE/PAYMENT to create **`TransactionDiscountTemp`** rows from proposals is still outstanding. Completed sales already persist **`CAMPAIGN`** discount lines when something creates them on the temp document.

---

## Cart snapshot (`schema_version` 1.0)

Module: `pos/service/campaign/`.

| File | Role |
|------|------|
| `application_policy.py` | Documented rules: when to evaluate, **merchandise subtotal** definition, **`priority` / `is_combinable`** greedy stacking, relationship to line discounts and **loyalty BONUS** |
| `cart_snapshot.py` | `CartSnapshot`, `CartLineSnapshot`, `CartTotalsSnapshot`; `build_cart_snapshot_from_document_data()`; `cart_snapshot_to_dict()`; `normalize_cart_data_for_campaign_request()` |
| `campaign_service.py` | **`CampaignService.evaluate_proposals(document_data, …)`** → **`CampaignDiscountProposal`** list (local engine; see below) |
| `__init__.py` | Re-exports snapshot helpers, **`CampaignService`**, **`CampaignDiscountProposal`**, **`SUPPORTED_TYPE_CODES`** |

### Building from `document_data`

`DocumentManager` keeps an in-memory `document_data` dict with `head`, `products`, `discounts`, etc. The builder reads ORM temp rows on that structure and produces:

- **Lines:** one entry per `TransactionProductTemp` with UUIDs, quantities, prices, `line_total`, cancel/void flags, department and product FKs (as strings), VAT rate — all **decimal amounts as strings** for stable JSON.
- **Header context:** `transaction_head_temp_id`, `transaction_unique_id`, `pos_id`, `fk_store_id`, `fk_customer_id`, `loyalty_member_id`, `currency_code` (`base_currency`), `evaluated_at` (UTC ISO-8601).
- **Totals:** `merchandise_subtotal` (sum of non-cancelled, non-voided line `total_price`), head `total_amount` / `total_discount_amount`, sum of non-cancelled `TransactionDiscountTemp` rows, and **`document_discount_non_campaign_total`** (same sum but **excluding** rows whose `discount_type` is `CAMPAIGN`, case-insensitive) for future basket-threshold logic.

Reserved lists (empty until wired): `customer_segment_codes`, `active_coupon_codes`.

### Normalizing `cart_data` for integrations

`normalize_cart_data_for_campaign_request(cart_data)`:

1. If `cart_data["schema_version"] == "1.0"`, returns a plain `dict` copy (already canonical).
2. Else if `head` and `products` are present (embedded `document_data`), builds and serializes a snapshot.
3. Otherwise returns `dict(cart_data)` unchanged for legacy callers.

`pos/integration/hooks.py` → `apply_campaign_discounts` documents this expectation.

### GATE serializer

`pos/integration/gate/serializers/campaign_serializer.py` — `CampaignSerializer.build_discount_request()` now returns the **normalized** body (still a stub regarding real HTTP field names to GATE, but no longer the empty `lines` / `total` placeholder). `GatePullService.get_campaign_discounts()` will use the same shape when implemented.

---

## Local evaluation (`CampaignService`)

**`CampaignService.evaluate_proposals(document_data, evaluated_at=None, active_coupon_codes=None, session=None)`**

- **Input:** same **`document_data`** shape as **`DocumentManager`** (`head`, `products`, …). **`active_coupon_codes`** uppercased strings: required when **`Campaign.requires_coupon`** or when **`is_auto_apply`** is false (then a code must be supplied to consider the row).
- **Output:** list of **`CampaignDiscountProposal`**: `scope` **`DOCUMENT`** (basket) or **`LINE`** (one sale line), suggested **`discount_amount`** / optional **`discount_rate`**, **`temp_discount_type`** = **`CAMPAIGN`**, **`discount_code`** = truncated **`Campaign.code`**. Caller is responsible for **`TransactionDiscountTemp.line_no`** and head totals when persisting.

**Supported `CampaignType.code` values (initial set):**

| Code | Behaviour |
|------|-----------|
| **`BASKET_DISCOUNT`** | **`min_purchase_amount` / `max_purchase_amount`** vs **eligible subtotal** (lines matching **`CampaignRule`** include/exclude for **`PRODUCT`** / **`DEPARTMENT`**; if no rules, all lines count). **`discount_type`** **`PERCENTAGE`** or **`FIXED_AMOUNT`**; optional **`max_discount_amount`** cap on percentage. |
| **`TIME_BASED`** | Same discount math as basket, plus **`days_of_week`** (1–7 ISO, comma-separated) and optional daily **`start_time` / `end_time`** (supports overnight window when start > end). |
| **`PRODUCT_DISCOUNT`** | Requires at least one **`CampaignProduct`** row. Each active sale line whose product matches a row (and passes rules, **`min_quantity` / `max_quantity`**) gets a **LINE** proposal; per-line **`discount_percentage`** or **`discount_value`** can override the campaign defaults. |

**Not evaluated yet:** **`BUY_X_GET_Y`**, **`PAYMENT_DISCOUNT`**, **`WELCOME_BONUS`**, and rule types beyond **`PRODUCT`** / **`DEPARTMENT`**.

**Filters on every campaign:** **`Campaign` / `CampaignType` active, not soft-deleted**; date range uses **calendar-day** inclusion on **`start_date` / `end_date`** (naive vs aware normalized for comparison); **`fk_store_id`** null = all stores; **`fk_customer_segment_id`** requires an active **`CustomerSegmentMember`** row for the document customer (campaigns with a segment skip walk-in–only flows without a customer id).

**Stacking:** candidates sorted by **`priority` descending**; proposals emitted in that order; after a campaign with **`is_combinable=False`** produces at least one proposal, evaluation stops (see **`application_policy.py`**).

Sample seed end dates are **~365 days** from insert time so new databases stay valid longer; refresh **`Campaign`** rows if your dev DB is older.

---

## Stacking and order (summary)

Full text lives in `application_policy.py`. In short:

- **Merchandise subtotal** for thresholds = active lines’ `total_price` (line-level cashier discount/markup already baked in).
- Eligible campaigns sorted by **`Campaign.priority` descending**; walk the list; if a chosen campaign has **`is_combinable == False`**, stop applying further campaigns in that pass.
- **Loyalty redemption** at payment continues to use **net due** after all document discounts, including future **CAMPAIGN** lines.

---

## CAMPAIGN transaction discount type

- **`transaction_discount_type`** includes a row with code **`CAMPAIGN`** (seeded on new databases; existing databases get it from **`ensure_transaction_discount_type_campaign`** on startup, same pattern as other reference patches).
- On each discount line, set **`TransactionDiscountTemp.discount_type`** / **`TransactionDiscount.discount_type`** (string on temp; permanent rows use **`fk_discount_type_id`**) to **`CAMPAIGN`**, matching **`CAMPAIGN_DISCOUNT_TYPE_CODE`** in `pos/service/campaign/application_policy.py`.
- **`discount_code`** (max **15** characters on the model): store **`Campaign.code`** (e.g. `WELCOME10`) or a short coupon token. Longer barcodes require a future column length or separate field. **`PaymentService.copy_temp_to_permanent`** copies **`discount_code`** to the permanent **`TransactionDiscount`** row. Thermal receipts show **`CAMPAIGN (code)`** when `document_adapter` formats the line.

---

## Related documentation

- [Database Models — Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)
- [Sale Transactions](10-sale-transactions.md) — loyalty on PAYMENT, **`CAMPAIGN`** / **`CampaignService`** note before Amount Table
- [Service Layer — Campaign cart snapshot](25-service-layer.md#campaign-cart-snapshot)
- [Integration Layer](40-integration-layer.md) (GATE campaign pull/calculate, `IntegrationMixin.apply_campaign`, third-party `BaseCampaignConnector`)
- [Customer Segmentation](42-customer-segmentation.md) — `marketing_profile()` for future segment-aware campaigns

---

**Last updated:** 2026-04-11 (local `CampaignService` + seed horizon)
