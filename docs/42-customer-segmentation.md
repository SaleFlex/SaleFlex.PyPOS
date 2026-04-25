# Customer segmentation (marketing)

Customer segments (`CustomerSegment`, `CustomerSegmentMember`) are **separate** from loyalty tiers (`LoyaltyTier`, `CustomerLoyalty`). Segments target campaigns and messaging; tiers drive rewards. Combine them in application code via **`CustomerSegmentService.marketing_profile()`** — do not put loyalty tier codes inside `criteria_json`.

## Automatic assignment

**`CustomerSegmentService`** (`pos/service/customer_segment_service.py`):

- Builds a **`SegmentEvaluationContext`** from **`CustomerLoyalty`** when present (annual / lifetime spend, purchase count, last activity), otherwise aggregates completed **sale** rows from **`TransactionHead`** for the customer.
- Reads **`CustomerSegment.criteria_json`** per active segment and sets **`CustomerSegmentMember`** rows with **`assigned_by = AUTO`**.
- **Removes** auto memberships (`assigned_by` empty, `AUTO`, or `SYSTEM`) when criteria no longer match. Rows that will be managed manually should use **`assigned_by = MANUAL`** (future UI); those are not auto-deactivated.

### When sync runs

- After each **completed sale**, from **`PaymentService.copy_temp_to_permanent`** (after loyalty updates), via **`CustomerSegmentService.on_sale_transaction_completed`**.
- After **Customer Detail SAVE** (create or update), via **`CustomerSegmentService.sync_for_customer_id`** — useful for **NEW_CUSTOMER** and **BIRTHDAY** without waiting for a sale.

Walk-in customers are skipped.

### VIP flag (preferences)

If a segment’s JSON includes **`"honor_preferences_vip": true`** (the seeded **VIP** segment does), the customer qualifies when **`preferences_json`** contains any of **`vip`**, **`is_vip`**, or **`marketing_vip`** set to true (alongside the usual spend thresholds, which use **OR** logic for VIP).

### Seed `criteria_json` behaviour

| `segment_type`   | How rules are applied |
|------------------|-------------------------|
| `VIP`            | Annual or lifetime spend thresholds **OR** preferences VIP when `honor_preferences_vip` is true |
| `NEW_CUSTOMER`   | Registered within **`days_since_registration`** days and **`max_purchases`** not exceeded |
| `FREQUENT_BUYER` | **`min_total_purchases`** reached (`min_purchases_per_month` in seed is reserved for a future rule) |
| `HIGH_VALUE`     | **`min_annual_spending`** and **`min_avg_transaction`** (both, when present) |
| `INACTIVE`       | At least one purchase and **`days_since_last_purchase`** since last sale |
| `BIRTHDAY`       | **`birthday_month`** = `current` and `date_of_birth` in the current calendar month |
| Other / `CUSTOM` | Optional generic keys with **`"join": "any"`** or default **all** |

### Cached counts

After changes affecting a segment, **`customer_count`** on **`CustomerSegment`** is refreshed for that segment only.

## `marketing_profile(session, customer_id)`

Returns:

```python
{"segment_codes": ["VIP", "HIGH_VALUE", ...], "loyalty_tier_code": "GOLD" or None}
```

Use this in campaign or promotion logic instead of duplicating tier logic inside segment criteria.

## Related documentation

- [Customer Management](17-customer-management.md)
- [Loyalty Programs](41-loyalty-programs.md)
- [Database Models Overview](21-database-models.md)
- [Service Layer](25-service-layer.md)

---

**Last Updated:** 2026-04-10  
**Version:** 1.0.0b8  
**License:** MIT
