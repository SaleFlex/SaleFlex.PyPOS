# Campaign & Promotions (design and cart snapshot)

This document describes **promotional campaigns** in SaleFlex.PyPOS: database entities, the **initial runtime contract** (cart snapshot + stacking rules), and how it connects to **SaleFlex.GATE** / third-party campaign connectors.

**Current status:** Campaign **models and seed data** exist (`Campaign`, `CampaignType`, `CampaignRule`, `CampaignProduct`, **`Coupon`**, **`CouponUsage`**, **`CampaignUsage`**, … — see [Database Models → Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)). The **`transaction_discount_type`** table includes **`CAMPAIGN`** (new installs and patched DBs on startup). **`ActiveCampaignCache`** speeds local evaluation by caching active campaign rows (see [Active campaign cache](#active-campaign-cache)). **Administrators** can maintain **`Campaign`** rows from the POS UI (see [Management UI (administrators)](#management-ui-administrators)). On the **SALE** and **PAYMENT** flows, the local engine **writes** matching discounts to the open document as **`TransactionDiscountTemp`** rows with **`discount_type="CAMPAIGN"`** (see [Sale document sync (local engine)](#sale-document-sync-local-engine) below). **`CampaignService.evaluate_proposals()`** is the core evaluator (see [Local evaluation](#local-evaluation-campaignservice)); it does not persist by itself — **`sync_campaign_discounts_on_document`** applies the result. **[Coupon activation](#coupon-activation-on-sale)** wires **`Coupon`** validation and **`document_data["applied_coupon_ids"]`** into that flow; **`PaymentService.copy_temp_to_permanent`** runs **`CampaignAuditService.record_after_completed_sale`** (**`CampaignUsage`**, **`CouponUsage`**, **`Campaign.total_usage_count`**, **`Coupon.usage_count`**) when the sale completes, copies **`CAMPAIGN`** lines to permanent discounts, and thermal receipts show **`CAMPAIGN (code)`** via **`document_adapter`**. **`CampaignAuditService.distinct_applied_campaign_count(document_data)`** matches the cardinality of **`CampaignUsage`** rows for that receipt and should populate **`CashierTransactionMetrics.number_of_promotions_applied`** when transaction metrics are written. Optional **`active_coupon_codes`** may still be supplied by callers alongside applied coupons.

---

## Cart snapshot (`schema_version` 1.0)

Module: `pos/service/campaign/`.

| File | Role |
|------|------|
| `application_policy.py` | Documented rules: when to evaluate, **merchandise subtotal** definition, **`priority` / `is_combinable`** greedy stacking, relationship to line discounts and **loyalty BONUS** |
| `cart_snapshot.py` | `CartSnapshot`, `CartLineSnapshot`, `CartTotalsSnapshot`; `build_cart_snapshot_from_document_data()`; `cart_snapshot_to_dict()`; `normalize_cart_data_for_campaign_request()` |
| `campaign_service.py` | **`CampaignService.evaluate_proposals(document_data, …)`** → **`CampaignDiscountProposal`** list; **`campaign_discount_proposal_to_dict()`** for integration payloads |
| `campaign_document_sync.py` | **`sync_campaign_discounts_on_document`**, **`recompute_head_total_discount_amount`**, **`gate_manages_campaign()`** — applies proposals to **`document_data`** (see below) |
| `coupon_activation_service.py` | **`CouponActivationService`**: validate **`Coupon`** for the open sale; derive campaign codes for evaluation; **`record_coupon_usages_in_session`** (used by audit service) |
| `campaign_usage_limits.py` | **`CampaignUsageLimits`**: **`total_usage_limit`** / **`usage_limit_per_customer`** from **`CampaignUsage`** row counts |
| `campaign_audit_service.py` | **`CampaignAuditService`**: **`CampaignUsage`** + **`Campaign.total_usage_count`** on completed sale; **`distinct_applied_campaign_count`** for metrics alignment; **`revoke_entitlements_for_transaction_head`** for void/refund hooks |
| `active_campaign_cache.py` | **`ActiveCampaignCache`**: in-memory snapshot of active **`Campaign`** / **`CampaignType`** / **`CampaignRule`** / **`CampaignProduct`** for **`CampaignService`** (expunged ORM rows) |
| `__init__.py` | Re-exports snapshot helpers, sync entry points, **`CampaignService`**, **`ActiveCampaignCache`**, **`CouponActivationService`**, **`CampaignDiscountProposal`**, **`SUPPORTED_TYPE_CODES`** |

### Active campaign cache

**`ActiveCampaignCache`** avoids reloading every campaign-related table on each cart evaluation. **`CampaignService.evaluate_proposals`** uses the snapshot when present; if missing or unloadable, it falls back to a per-session DB read.

**Warm-up:** **`Application`** calls **`refresh_active_campaign_cache()`** ( **`CacheManager`** ) after **`populate_product_data`**.

**Refresh:** **`ActiveCampaignCache.reload()`** (or **`reload_safely()`** when errors must not abort the caller) runs after:

- **`hooks.pull_updates_from_gate`** (after product/campaign/notification pull),
- **`SyncWorker`** pull cycle (same pattern; aligns with GATE **`campaign_update`** handling once notifications drive cache signals),
- **`CampaignSerializer.apply_updates`** after local DB writes from GATE payloads.

**Admin / custom tools:** After persisting campaign rows outside these paths, call **`application.refresh_active_campaign_cache()`** so the next evaluation sees new definitions. **`CampaignUsage`** / segment checks still query the database each time.

### Management UI (administrators)

Dynamic forms **CAMPAIGN_LIST** (form_no **21**) and **CAMPAIGN_DETAIL** (**22**) are defined in **`data_layer/db_init_data/forms/campaign_management.py`**. **Administrators** open the list from **Main Menu → SETTINGS → CAMPAIGN SETTINGS** (**`GOTO_CAMPAIGN_SETTINGS`** → **`CAMPAIGN_LIST_FORM`**). The list screen uses **`CAMPAIGN_SEARCH`**, **`CAMPAIGN_LIST_DATAGRID`**, **DETAIL**, and **BACK**; **`current_campaign_id`** selects the row loaded into the **`CAMPAIGN`** panel on the modal. **`CAMPAIGN_DETAIL_SAVE`** writes scalar fields in a DB session and calls **`refresh_active_campaign_cache()`**. Non-administrators do not see controls whose **`form_control_function1`** is **`CAMPAIGN_LIST_FORM`** (**`base_window._create_button()`**, same idea as **ADD NEW CASHIER**). Older databases: **`ensure_campaign_management_forms`** during **`Application`** startup. Full form pattern: [Dynamic Forms — Campaign management](22-dynamic-forms-system.md#campaign-management-administrators).

### Building from `document_data`

`DocumentManager` keeps an in-memory `document_data` dict with `head`, `products`, `discounts`, etc. The builder reads ORM temp rows on that structure and produces:

- **Lines:** one entry per `TransactionProductTemp` with UUIDs, quantities, prices, `line_total`, cancel/void flags, department and product FKs (as strings), VAT rate — all **decimal amounts as strings** for stable JSON.
- **Header context:** `transaction_head_temp_id`, `transaction_unique_id`, `pos_id`, `fk_store_id`, `fk_customer_id`, `loyalty_member_id`, `currency_code` (`base_currency`), `evaluated_at` (UTC ISO-8601).
- **Totals:** `merchandise_subtotal` (sum of non-cancelled, non-voided line `total_price`), head `total_amount` / `total_discount_amount`, sum of non-cancelled `TransactionDiscountTemp` rows, and **`document_discount_non_campaign_total`** (same sum but **excluding** rows whose `discount_type` is `CAMPAIGN`, case-insensitive) for future basket-threshold logic.

Reserved / optional lists: `customer_segment_codes` (empty until wired); `active_coupon_codes` (optional uppercased strings for integrations or future UI). **`document_data["applied_coupon_ids"]`** holds **`Coupon.id`** UUID strings applied on this open sale (see [Coupon activation on SALE](#coupon-activation-on-sale)).

### Normalizing `cart_data` for integrations

`normalize_cart_data_for_campaign_request(cart_data)`:

1. If `cart_data["schema_version"] == "1.0"`, returns a plain `dict` copy (already canonical).
2. Else if `head` and `products` are present (embedded `document_data`), builds and serializes a snapshot.
3. Otherwise returns `dict(cart_data)` unchanged for legacy callers.

`pos/integration/hooks.py` → `apply_campaign_discounts` documents this expectation.

### GATE serializer

`pos/integration/gate/serializers/campaign_serializer.py` — `CampaignSerializer.build_discount_request()` now returns the **normalized** body (still a stub regarding real HTTP field names to GATE, but no longer the empty `lines` / `total` placeholder). `GatePullService.get_campaign_discounts()` will use the same shape when implemented.

---

## Sale document sync (local engine)

Module: **`pos/service/campaign/campaign_document_sync.py`**.

**`sync_campaign_discounts_on_document(document_data, *, active_coupon_codes=None)`**

- Runs only for an **open sale** receipt: **`transaction_type`** **`sale`**, **`transaction_status`** **`ACTIVE`** (see **`TransactionType`** / **`TransactionStatus`**).
- **Skips entirely** when **`gate.enabled`** and **`gate.manages_campaign`** are true — the terminal assumes GATE owns real-time campaign lines on the cart (see [Integration Layer — Campaign discount routing](40-integration-layer.md#campaign-discount-routing)).
- **Cancels** previous engine-owned rows: every non-cancelled **`TransactionDiscountTemp`** with **`discount_type`** matching **`CAMPAIGN_DISCOUNT_TYPE_CODE`** (`"CAMPAIGN"`) is set to **`is_cancel=True`** and saved.
- Builds the code list passed to evaluation as the **deduplicated union** of **`active_coupon_codes`** (if any) and **`CouponActivationService.evaluation_campaign_codes(document_data)`** (from **`applied_coupon_ids`**).
- Calls **`CampaignService.evaluate_proposals(document_data, active_coupon_codes=…)`**, then creates **new** **`TransactionDiscountTemp`** rows (`create()` + append to **`document_data["discounts"]`**) with **`line_no`** allocated after the current max discount line number, **`fk_transaction_product_id`** set for **LINE**-scope proposals, **`fk_transaction_payment_id`** set when a proposal is tied to a **`PAYMENT_DISCOUNT`** tender line, **`discount_code`** truncated to 15 characters, **`discount_rate`** quantized for the DB column where present.
- **`recompute_head_total_discount_amount`** sums **all** non-cancelled temp discount rows (including **LOYALTY** and **CAMPAIGN**) into **`head.total_discount_amount`** and saves the head — same bucket the **Amount Table** and **net due** use.

**Call sites (cart or customer changed):**

- **`SaleService.add_sale_to_document`** — after merchandise totals are updated (PLU / department line added).
- **`SaleService.refresh_campaign_discounts_after_cart_change`** — used from **SaleEvent** after line **discount / markup**, **DELETE** (when lines remain), **REPEAT**; from **CustomerEvent** after assigning a customer to the sale. When a **window** is passed, **`update_sale_screen_controls`** refreshes **sale_list** (discount lines) and **amount_table**.
- **`PaymentService.process_payment`** — after appending a **`TransactionPaymentTemp`**, runs **`sync_campaign_discounts_on_document`** so **`PAYMENT_DISCOUNT`** campaigns (and stacked recomputation) see the current tender lines.

**Limits (unchanged from evaluation):** only **`TransactionProductTemp`** lines feed **`CampaignService._collect_lines`** — **department-only** carts do not contribute to merchandise-based basket/product rules until that is extended.

---

## Local evaluation (`CampaignService`)

**`CampaignService.evaluate_proposals(document_data, evaluated_at=None, active_coupon_codes=None, session=None)`**

- **Input:** same **`document_data`** shape as **`DocumentManager`** (`head`, `products`, …). **`active_coupon_codes`** uppercased strings: required when **`Campaign.requires_coupon`** or when **`is_auto_apply`** is false (then a code must be supplied to consider the row).
- **Output:** list of **`CampaignDiscountProposal`**: `scope` **`DOCUMENT`** (basket / buy-X-get-Y / payment promo) or **`LINE`** (one sale line), suggested **`discount_amount`** / optional **`discount_rate`**, optional **`fk_transaction_payment_temp_id`** for payment-scoped promos, **`temp_discount_type`** = **`CAMPAIGN`**, **`discount_code`** = truncated **`Campaign.code`**. **`sync_campaign_discounts_on_document`** assigns **`TransactionDiscountTemp.line_no`** and updates **`head.total_discount_amount`** when persisting to the open document; other callers (e.g. integration preview) may only read the list.

**Supported `CampaignType.code` values:**

| Code | Behaviour |
|------|-----------|
| **`BASKET_DISCOUNT`** | **`min_purchase_amount` / `max_purchase_amount`** vs **eligible net** after prior campaign proposals in the same pass (see **Stacking**). Lines filtered by **`CampaignRule`** (**`PRODUCT`**, **`DEPARTMENT`**, **`BRAND`**, **`BARCODE_PATTERN`**, **`CATEGORY`** — see below). **`discount_type`** **`PERCENTAGE`** or **`FIXED_AMOUNT`**; optional **`max_discount_amount`** cap on percentage. |
| **`TIME_BASED`** | Same discount math as basket, plus **`days_of_week`** (1–7 ISO, comma-separated) and optional daily **`start_time` / `end_time`** (supports overnight window when start > end). |
| **`PRODUCT_DISCOUNT`** | Requires at least one **`CampaignProduct`** row. Each active sale line whose product matches a row (and passes line rules, **`min_quantity` / `max_quantity`**) gets a **LINE** proposal; per-line **`discount_percentage`** or **`discount_value`** can override the campaign defaults. Percent/fixed apply to the line total **after earlier line-level campaign amounts in the same pass**. |
| **`BUY_X_GET_Y`** | **`discount_type`** **`BUY_X_GET_Y`** with **`buy_quantity`** / **`get_quantity`**. Eligible units (rules + optional **`CampaignProduct`** filter) are grouped as “buy + get” sets; discount is **DOCUMENT** scope, value = sum of the cheapest **`get_quantity`** unit prices per full set (integer line quantities only). Respects **`min_purchase` / `max_purchase`** and **`max_discount_amount`** on the stacked net base. |
| **`PAYMENT_DISCOUNT`** | Evaluates when **`document_data["payments"]`** has rows. **`PAYMENT_TYPE`** rules (include/exclude) match tender lines using **`TransactionPaymentTemp.payment_type`** (**`EventName`**, e.g. **`CASH_PAYMENT`**) mapped to seeded **`PaymentType`** rows. Discount **`PERCENTAGE`** or **`FIXED_AMOUNT`** applies to the same stacked merchandise net as basket rules (**`line_rules`** still filter which merchandise counts). **DOCUMENT** proposal; **`fk_transaction_payment_temp_id`** references the first matching payment by **`line_no`**. |

**Rule types on lines:** **`PRODUCT`**, **`DEPARTMENT`** (main group), **`BRAND`** (**`fk_product_manufacturer_id`** vs product master), **`BARCODE_PATTERN`** (**`rule_value`**: plain prefix, `*` / `?` via **`fnmatch`**, or **`re:`** + regex), **`CATEGORY`** (**`rule_value`** = UUID of **`department_sub_group`** matching **`fk_department_sub_group_id`** on the sale line). **`PAYMENT_TYPE`** rules apply only to **`PAYMENT_DISCOUNT`** evaluation.

**Not evaluated yet:** **`WELCOME_BONUS`** (and any other campaign types not listed above).

**Filters on every campaign:** **`Campaign` / `CampaignType` active, not soft-deleted**; date range uses **calendar-day** inclusion on **`start_date` / `end_date`** (naive vs aware normalized for comparison); **`fk_store_id`** null = all stores; **`fk_customer_segment_id`** requires an active **`CustomerSegmentMember`** row for the document customer (campaigns with a segment skip walk-in–only flows without a customer id). **`total_usage_limit`** (global cap) and **`usage_limit_per_customer`** are enforced via non-deleted **`CampaignUsage`** rows: **`CampaignUsageLimits.allows_new_application`** in **`CampaignService`** (auto-apply and coupon-backed paths) and **`CouponActivationService.validate_for_open_sale`**. Walk-in sales (**`fk_customer_id`** null) do not consume the per-customer quota (limit applies only when a customer is on the document).

**Stacking:** candidates sorted by **`priority` descending**; proposals emitted in that order; after a campaign with **`is_combinable=False`** produces at least one proposal, evaluation stops (see **`application_policy.py`**). Within one pass, later campaigns see reduced **merchandise net**: prior **DOCUMENT** proposal amounts and **LINE** proposal amounts (per temp line id) reduce thresholds and percentage bases.

Sample seed end dates are **~365 days** from insert time so new databases stay valid longer; refresh **`Campaign`** rows if your dev DB is older.

---

## Stacking and order (summary)

Full text lives in `application_policy.py`. In short:

- **Merchandise subtotal** for thresholds = active lines’ `total_price` (line-level cashier discount/markup already baked in).
- Eligible campaigns sorted by **`Campaign.priority` descending**; walk the list; if a chosen campaign has **`is_combinable == False`**, stop applying further campaigns in that pass.
- Within a single evaluation pass, **`CampaignService`** reduces the **merchandise net** used for thresholds and percentage bases after each **DOCUMENT** proposal and tracks **per-line** reductions after **LINE** proposals (see [Local evaluation](#local-evaluation-campaignservice)).
- **Loyalty redemption** at payment continues to use **net due** after all document discounts, including **CAMPAIGN** lines.

---

## CAMPAIGN transaction discount type

- **`transaction_discount_type`** includes a row with code **`CAMPAIGN`** (seeded on new databases; existing databases get it from **`ensure_transaction_discount_type_campaign`** on startup, same pattern as other reference patches).
- On each discount line, set **`TransactionDiscountTemp.discount_type`** / **`TransactionDiscount.discount_type`** (string on temp; permanent rows use **`fk_discount_type_id`**) to **`CAMPAIGN`**, matching **`CAMPAIGN_DISCOUNT_TYPE_CODE`** in `pos/service/campaign/application_policy.py`.
- **`discount_code`** (max **15** characters on the model): store **`Campaign.code`** (e.g. `WELCOME10`) or a short coupon token. Longer barcodes require a future column length or separate field. **`PaymentService.copy_temp_to_permanent`** copies **`discount_code`** to the permanent **`TransactionDiscount`** row. Thermal receipts show **`CAMPAIGN (code)`** when `document_adapter` formats the line.

---

## Coupon activation on SALE

Module: **`pos/service/campaign/coupon_activation_service.py`**. UI: **`user_interface/form/coupon_input_dialog.py`**. Event: **`APPLY_COUPON`** → **`SaleEvent._apply_coupon_event`** (`pos/manager/event/sale.py`).

**Document field:** Each open **`document_data`** dict includes **`applied_coupon_ids`**: a list of **`Coupon.id`** strings (UUID text) appended when the cashier successfully applies a code. New and loaded documents initialise it in **`DocumentManager`**.

**SALE form:** The **COUPON** control is added by seed data and by **`ensure_sale_form_coupon_button`** on startup for databases that predate the button. When **`gate.manages_campaign`** is true, the handler does **not** validate or mutate the cart; it shows an informational message that GATE owns campaigns.

**Validation (`CouponActivationService.validate_for_open_sale`):** Resolves **`Coupon`** by **`code`** or **`barcode`** (case-insensitive where applicable). Checks campaign and coupon active flags, date range, store scope, customer segment (when the campaign targets a segment), **`requires_coupon`**, **`PERSONAL`** (coupon must belong to the document customer), **`SINGLE_USE`** / existing **`CouponUsage`**, and **`usage_limit`** vs **`Coupon.usage_count`**. On success, the coupon id is appended to **`applied_coupon_ids`** (no duplicate ids); **`refresh_campaign_discounts_after_cart_change`** runs so **`sync_campaign_discounts_on_document`** re-evaluates with the merged code list.

**Completion:** After **`PaymentService.copy_temp_to_permanent`** creates the permanent head and **`TransactionDiscount`** rows, **`CampaignAuditService.record_after_completed_sale`** (single DB transaction) writes one **`CampaignUsage`** row per distinct campaign present on non-cancelled **CAMPAIGN** discount lines (amount = sum of those lines; **`coupon_code`** filled when an applied coupon maps to that campaign), increments **`Campaign.total_usage_count`** once per campaign on that receipt, then inserts **`CouponUsage`** rows and increments **`Coupon.usage_count`** for applied coupons whose campaign produced a **CAMPAIGN** discount (same **`discount_code`** / 15-character match as before).

**Demo data:** Sample coupon **`WELCOME10-DEMO`** and linked campaign product seed support trying **`requires_coupon`** product discounts on a dev database — **`ensure_sample_coupon_welcome_demo`**, **`ensure_welcome10_demo_campaign_product`** run from **`Application`** startup alongside the SALE form patch.

---

## Usage audit and reversal (void / refund)

**Audit trail:** **`CampaignUsage`** stores **`fk_transaction_head_id`**, **`fk_customer_id`**, **`discount_amount`**, optional **`coupon_code`**, and store/cashier FKs for reporting.

**Reversal:** **`CampaignAuditService.revoke_entitlements_for_transaction_head(fk_transaction_head_id, reason=…)`** soft-deletes matching **`CampaignUsage`** and **`CouponUsage`** rows and decreases **`Campaign.total_usage_count`** / **`Coupon.usage_count`** accordingly. Call this from a void-or-refund flow when policy requires campaign benefit to be rolled back (for example after a completed sale is reversed in the back office). The standard **CANCEL** path on an unpaid open sale does not create usage rows, so nothing to revoke there.

### Cashier transaction metrics (`number_of_promotions_applied`)

**`CampaignAuditService.distinct_applied_campaign_count(document_data)`** counts **distinct** campaigns represented on non-cancelled **`CAMPAIGN`** temp discount lines (resolved via **`discount_code`**), i.e. the same cardinality as **`CampaignUsage`** rows **`record_after_completed_sale`** would insert for that receipt. When your application writes **`CashierTransactionMetrics`** rows, set **`number_of_promotions_applied`** from this value (or an equivalent count at copy-to-permanent time) so cashier performance reporting matches campaign audit aggregates.

---

## Related documentation

- [Database Models — Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)
- [Sale Transactions](10-sale-transactions.md) — loyalty on PAYMENT, **`CAMPAIGN`** / **`CampaignService`** / limits note before Amount Table
- [Service Layer — Campaign cart snapshot](25-service-layer.md#campaign-cart-snapshot)
- [Integration Layer](40-integration-layer.md) (GATE campaign pull/calculate, **`ActiveCampaignCache.reload_safely()`** after pulls, **`IntegrationMixin.apply_campaign`**, **`CampaignAuditService`** on completion / reversal, third-party **`BaseCampaignConnector`**)
- [Data Caching](27-data-caching.md) — **`pos_data`**, **`product_data`**, **`ActiveCampaignCache`**
- [Customer Segmentation](42-customer-segmentation.md) — `marketing_profile()` for future segment-aware campaigns
- [Dynamic Forms — Campaign management](22-dynamic-forms-system.md#campaign-management-administrators) — **CAMPAIGN_LIST** / **CAMPAIGN_DETAIL**, **`ensure_campaign_management_forms`**

---

**Last updated:** 2026-04-11 (`ActiveCampaignCache`, `CampaignUsage` + usage limits, `CampaignAuditService`, reversal API, coupon activation, `apply_campaign`, administrator campaign UI)
