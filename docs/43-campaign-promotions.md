# Campaign & Promotions (design and cart snapshot)

This document describes **promotional campaigns** in SaleFlex.PyPOS: database entities, the **initial runtime contract** (cart snapshot + stacking rules), and how it connects to **SaleFlex.GATE** / third-party campaign connectors.

**Current status:** Campaign **models and seed data** exist (`Campaign`, `CampaignType`, `CampaignRule`, `CampaignProduct`, usage/coupon tables — see [Database Models → Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)). **Automatic discount application on the SALE screen is not wired yet**; this document’s snapshot and policy describe the shared payload so the local engine and GATE can use the same shape.

---

## Cart snapshot (`schema_version` 1.0)

Module: `pos/service/campaign/`.

| File | Role |
|------|------|
| `application_policy.py` | Documented rules: when to evaluate, **merchandise subtotal** definition, **`priority` / `is_combinable`** greedy stacking, relationship to line discounts and **loyalty BONUS** |
| `cart_snapshot.py` | `CartSnapshot`, `CartLineSnapshot`, `CartTotalsSnapshot`; `build_cart_snapshot_from_document_data()`; `cart_snapshot_to_dict()`; `normalize_cart_data_for_campaign_request()` |
| `__init__.py` | Re-exports `CAMPAIGN_DISCOUNT_TYPE_CODE` (`"CAMPAIGN"`) and snapshot helpers |

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

## Stacking and order (summary)

Full text lives in `application_policy.py`. In short:

- **Merchandise subtotal** for thresholds = active lines’ `total_price` (line-level cashier discount/markup already baked in).
- Eligible campaigns sorted by **`Campaign.priority` descending**; walk the list; if a chosen campaign has **`is_combinable == False`**, stop applying further campaigns in that pass.
- **Loyalty redemption** at payment continues to use **net due** after all document discounts, including future **CAMPAIGN** lines.

---

## Reserved `discount_type` for campaign engine output

`CAMPAIGN_DISCOUNT_TYPE_CODE` = `"CAMPAIGN"` — intended for `TransactionDiscountTemp.discount_type` (and permanent `TransactionDiscount`) when a row is produced by the local campaign engine or merged from GATE. A dedicated **`TransactionDiscountType`** row with code `CAMPAIGN` is planned in a follow-up change.

---

## Related documentation

- [Database Models — Campaign and Promotion](21-database-models.md#campaign-and-promotion-models)
- [Service Layer — Campaign cart snapshot](25-service-layer.md#campaign-cart-snapshot)
- [Integration Layer](40-integration-layer.md) (GATE campaign pull/calculate, `IntegrationMixin.apply_campaign`, third-party `BaseCampaignConnector`)
- [Customer Segmentation](42-customer-segmentation.md) — `marketing_profile()` for future segment-aware campaigns

---

**Last updated:** 2026-04-11
