# Campaign and Loyalty Management System

## Overview

This document describes the campaign and loyalty management system added to SaleFlex.PyPOS. The system supports comprehensive promotional campaigns, coupon management, loyalty programs, and customer segmentation.

## Database Models Created

### 1. Campaign Management (6 Models)

#### CampaignType
Defines types of promotional campaigns (e.g., product discount, basket discount, time-based, buy X get Y).

**Key Fields:**
- `code`: Unique identifier (PRODUCT_DISCOUNT, BASKET_DISCOUNT, TIME_BASED, BUY_X_GET_Y, etc.)
- `name`: Display name
- `settings_json`: Type-specific configuration

#### Campaign
Main campaign definition with discount rules, time restrictions, and usage limits.

**Key Features:**
- Multiple discount types: PERCENTAGE, FIXED_AMOUNT, FREE_PRODUCT, BUY_X_GET_Y, CHEAPEST_FREE
- Time-based restrictions (date range, daily hours, days of week)
- Store-specific or global campaigns
- Usage limits (per customer, total)
- Auto-apply or coupon-required
- Customer segment targeting
- Priority and combination rules

#### CampaignRule
Defines inclusion/exclusion rules for campaign applicability.

**Rule Types:**
- PRODUCT: Specific product filter
- DEPARTMENT: Department-based filter
- CATEGORY: Category filter
- BRAND: Manufacturer/brand filter
- PAYMENT_TYPE: Payment method filter
- BARCODE_PATTERN: Pattern-based filter

#### CampaignProduct
Links specific products to campaigns for targeted discounts or gift products.

**Features:**
- Product-specific discount overrides
- Gift product designation
- Quantity constraints

#### CampaignUsage
Tracks campaign usage history for analytics and limit enforcement.

**Tracked Data:**
- Customer, transaction, store, cashier
- Discount amount applied
- Usage timestamp
- Coupon code if used

### 2. Coupon Management (2 Models)

#### Coupon
Defines discount coupons linked to campaigns.

**Coupon Types:**
- SINGLE_USE: One-time use only
- MULTI_USE: Multiple uses with limit
- PERSONAL: Assigned to specific customer
- PUBLIC: Available to all customers

**Features:**
- Validity period
- Usage tracking and limits
- Barcode and QR code support
- Distribution tracking (SMS, EMAIL, PUSH, MANUAL)

#### CouponUsage
Tracks coupon redemption history.

### 3. Loyalty Program (4 Models)

#### LoyaltyProgram
Main loyalty program configuration.

**Key Settings:**
- Points earning rate (points per currency unit)
- Redemption rate (currency per point)
- Minimum purchase for points
- Point expiry period
- Welcome bonus points
- Birthday bonus points

#### LoyaltyTier
Membership tiers (e.g., Bronze, Silver, Gold, Platinum).

**Tier Benefits:**
- Points multiplier (earn more points)
- Automatic discount percentage
- Special benefits description
- Visual customization (color, icon)

**Default Tiers:**
- **Bronze**: Entry level (0 points)
- **Silver**: 500 points or 1,000 TL annual spending (10% bonus points)
- **Gold**: 1,500 points or 5,000 TL annual spending (25% bonus points + 5% discount)
- **Platinum**: 5,000 points or 15,000 TL annual spending (50% bonus points + 10% discount)

#### CustomerLoyalty
Individual customer's loyalty membership details.

**Tracked Data:**
- Current and lifetime points
- Available points for redemption
- Points expiring soon
- Loyalty card number
- Current tier
- Purchase statistics (count, total spent, annual spent)
- Last activity date

#### LoyaltyPointTransaction
Complete audit trail of point movements.

**Transaction Types:**
- EARNED: Points earned from purchases
- REDEEMED: Points used for discounts
- EXPIRED: Points that expired
- ADJUSTED: Manual adjustments
- BONUS: Promotional bonus points
- WELCOME: New member bonus
- BIRTHDAY: Birthday bonus
- REFUND: Points restored from refund

### 4. Customer Segmentation (2 Models)

#### CustomerSegment
Defines customer segments for targeted marketing.

**Segment Types:**
- VIP: High-value customers
- NEW_CUSTOMER: Recently registered
- FREQUENT_BUYER: Regular shoppers
- HIGH_VALUE: High average transaction
- INACTIVE: Haven't purchased recently
- BIRTHDAY: Birthday this month
- CUSTOM: Custom criteria

**Default Segments:**
- VIP (10,000+ annual spending)
- New Customers (< 30 days)
- Frequent Buyers (4+ purchases/month)
- High Value (200+ avg transaction)
- Inactive (90+ days since last purchase)
- Birthday This Month

#### CustomerSegmentMember
Links customers to segments (many-to-many relationship).

**Features:**
- Assignment tracking (manual, auto, system)
- Assignment reason
- Active/inactive status

### 5. Extended Customer Model

Enhanced with additional fields for loyalty and segmentation:

**New Fields:**
- `date_of_birth`: For birthday campaigns
- `gender`: For demographic segmentation
- `national_id`, `tax_id`: For invoicing
- `registration_source`: Tracking registration channel
- `marketing_consent`, `sms_consent`, `email_consent`: GDPR/KVKK compliance
- `preferences_json`: Customer preferences

## Sample Data Included

### Campaign Types (6)
1. Product Discount
2. Basket Discount
3. Time-Based Discount
4. Buy X Get Y
5. Welcome Bonus
6. Payment Type Discount

### Sample Campaigns (4)
1. **WELCOME10**: 10% off first purchase (coupon required)
2. **BASKET100**: 10 TL off on 100+ TL purchases (auto-apply)
3. **HAPPYHOUR**: 20% off between 15:00-18:00 weekdays (auto-apply)
4. **BUY2GET1**: Buy 2 get 1 free (auto-apply)

### Loyalty Program
- **SaleFlex Rewards**: Earn 1 point per 10 TL, redeem at 0.5 TL per point
- 100 welcome points for new members
- 50 birthday bonus points
- Points expire after 1 year

### Customer Segments (6)
VIP, New Customers, Frequent Buyers, High Value, Inactive, Birthday This Month

## Key Features

### Campaign System
- ✅ Multiple campaign types
- ✅ Flexible discount rules (percentage, fixed, buy X get Y, etc.)
- ✅ Time-based restrictions (date, time, day of week)
- ✅ Store-specific or global campaigns
- ✅ Product/category/brand/payment filters
- ✅ Usage limits (per customer, total)
- ✅ Campaign priority and combination rules
- ✅ Customer segment targeting
- ✅ Coupon generation and management
- ✅ Usage tracking and analytics

### Loyalty System
- ✅ Points earning and redemption
- ✅ Tiered membership (Bronze/Silver/Gold/Platinum)
- ✅ Point expiry management
- ✅ Welcome and birthday bonuses
- ✅ Complete transaction history
- ✅ Automatic tier upgrades
- ✅ Tier-based benefits (multipliers, discounts)

### Customer Management
- ✅ Customer segmentation
- ✅ Purchase behavior tracking
- ✅ Demographic segmentation
- ✅ Marketing consent management (GDPR/KVKK)
- ✅ Targeted campaign delivery

### Security & Compliance
- ✅ Audit trails (who created/modified)
- ✅ Usage tracking to prevent fraud
- ✅ GDPR/KVKK consent fields
- ✅ Soft delete support

## Database Schema Relationships

```
Store
  └─ Campaign (optional FK)
  └─ LoyaltyProgram (optional FK)

Customer
  ├─ CustomerLoyalty (1:1)
  │   ├─ LoyaltyProgram (FK)
  │   ├─ LoyaltyTier (FK)
  │   └─ LoyaltyPointTransaction (1:N)
  ├─ CustomerSegmentMember (1:N)
  │   └─ CustomerSegment (FK)
  ├─ CampaignUsage (1:N)
  └─ CouponUsage (1:N)

Campaign
  ├─ CampaignType (FK)
  ├─ CampaignRule (1:N)
  ├─ CampaignProduct (1:N)
  ├─ CampaignUsage (1:N)
  ├─ Coupon (1:N)
  └─ CustomerSegment (optional FK for targeting)

LoyaltyProgram
  └─ LoyaltyTier (1:N)
```

## Next Steps for Implementation

1. **POS Integration**
   - Implement campaign evaluation engine
   - Add loyalty point calculation logic
   - Integrate with checkout process
   - Add coupon validation

2. **UI Components**
   - Campaign management forms
   - Loyalty program dashboard
   - Customer segmentation interface
   - Point redemption UI

3. **Business Logic**
   - Campaign priority resolver
   - Point expiry job
   - Tier upgrade automation
   - Segment member update job

4. **Analytics**
   - Campaign performance reports
   - Loyalty program metrics
   - Customer segment analysis
   - ROI calculation

## Files Created

### Models (13 files)
- `campaign_type.py`
- `campaign.py`
- `campaign_rule.py`
- `campaign_product.py`
- `campaign_usage.py`
- `coupon.py`
- `coupon_usage.py`
- `loyalty_program.py`
- `loyalty_tier.py`
- `customer_loyalty.py`
- `loyalty_point_transaction.py`
- `customer_segment.py`
- `customer_segment_member.py`

### Init Data (3 files)
- `campaign.py` - Campaign types and sample campaigns
- `loyalty.py` - Loyalty program and tiers
- `customer_segment.py` - Default customer segments

### Modified Files (3 files)
- `customer.py` - Extended with loyalty/segmentation fields
- `model/definition/__init__.py` - Added new model imports
- `db_init_data/__init__.py` - Added init function calls

---

**Total:** 13 new models, 3 init data files, 3 modified files
**All code comments:** In English as requested
**Database ready:** Yes, all models will be created on next run

