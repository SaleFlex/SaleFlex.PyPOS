"""
SaleFlex.PyPOS - Office Data Seeder

Copyright (c) 2025-2026 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Populates a freshly-created PyPOS database using initialization data fetched
from a SaleFlex.OFFICE instance.  Called in place of the default
``insert_initial_data`` function when:

  * the database file does not yet exist, AND
  * ``[app].mode = "office"`` in settings.toml

The seeder preserves all primary-key UUIDs received from OFFICE so that every
foreign-key reference inside the payload remains internally consistent after
being written into the local SQLite database.
"""

from __future__ import annotations

import uuid
from datetime import datetime, date, time
from typing import Any

from sqlalchemy import DateTime, Date, Time, String, Text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.logger import get_logger
from data_layer.engine import Engine

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_column_names(model_class) -> set[str]:
    """Return the set of column names defined in the underlying table."""
    return {col.name for col in model_class.__table__.columns}


def _get_column_types(model_class) -> dict[str, Any]:
    """Return a mapping of column name → SQLAlchemy type instance."""
    return {col.name: col.type for col in model_class.__table__.columns}


def _coerce_uuid(value: Any) -> Any:
    """
    Convert a string UUID representation to a ``uuid.UUID`` instance.

    Returns the original value unchanged when conversion is not possible
    (e.g. the value is already a UUID, is None, or is a non-UUID string).
    """
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError):
        return value


def _coerce_time(value: Any) -> Any:
    """
    Convert an ISO-8601 time string (``"HH:MM:SS"`` or ``"HH:MM"``) to a
    Python ``time`` object.

    SQLAlchemy's SQLite ``Time`` type rejects plain strings; they must be
    converted before passing to the ORM layer.

    Returns the value unchanged when it is already a ``time`` object, is
    ``None``, or cannot be parsed.
    """
    if value is None or isinstance(value, time):
        return value
    if not isinstance(value, str):
        return value

    for fmt in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    return value  # Give up — SQLAlchemy will surface the error with context.


def _coerce_datetime(value: Any) -> Any:
    """
    Convert an ISO-8601 datetime string to a Python ``datetime`` object.

    ``to_dict()`` serialises datetime columns as ISO strings for JSON
    transport.  Before writing them back to SQLite, SQLAlchemy's DateTime
    type requires a native Python ``datetime`` (or ``date``) object.

    Returns the value unchanged when it is already a datetime/date, is None,
    or cannot be parsed.
    """
    if value is None or isinstance(value, (datetime, date)):
        return value
    if not isinstance(value, str):
        return value

    # Normalise the common UTC "Z" suffix to "+00:00" (accepted by fromisoformat
    # on Python 3.11+; harmless on earlier versions that strip it below).
    cleaned = value.rstrip("Z") if value.endswith("Z") else value

    # Try progressively simpler formats so both microsecond-precision and
    # second-precision timestamps are handled.
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(cleaned[:len(fmt)], fmt)
        except ValueError:
            continue

    # Last resort: Python 3.7+ fromisoformat (handles +HH:MM offsets).
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        pass

    return value  # Give up — SQLAlchemy will surface the error with context.


def _prepare_row(
    row: dict[str, Any],
    allowed_columns: set[str],
    col_types: dict[str, Any],
) -> dict[str, Any]:
    """
    Filter *row* to only the keys present in *allowed_columns*, normalise
    sentinel strings, and coerce values to the types that SQLAlchemy expects.

    Normalisation
    -------------
    * The string ``"None"`` → ``None``.  Defensive guard against older OFFICE
      instances whose ``to_dict()`` serialised Python ``None`` as ``"None"``.

    Type coercion
    -------------
    * DateTime / Date columns   → Python ``datetime`` / ``date`` objects.
    * UUID columns (``"id"``, ``*_id``, ``*_by``) → ``uuid.UUID`` objects.
    """
    result: dict[str, Any] = {}
    for key, value in row.items():
        if key not in allowed_columns:
            continue

        # Guard against legacy "None" string serialisation.
        # Only convert the literal string "None" to Python None for non-text
        # column types (UUID foreign keys, integers, etc.).  For String / Text
        # columns the value "None" is a legitimate display name and must be
        # preserved as-is.
        if value == "None":
            col_type_check = col_types.get(key)
            if not isinstance(col_type_check, (String, Text)):
                value = None

        if value is not None:
            col_type = col_types.get(key)

            if isinstance(col_type, Time):
                value = _coerce_time(value)
            elif isinstance(col_type, (DateTime, Date)):
                value = _coerce_datetime(value)
            elif isinstance(value, str) and (
                key == "id" or key.endswith("_id") or key.endswith("_by")
            ):
                value = _coerce_uuid(value)

        result[key] = value
    return result


def _seed_table(
    conn,
    model_class,
    records: list[dict[str, Any]],
    label: str,
) -> int:
    """
    Bulk-insert *records* into the table backing *model_class*.

    Uses ``INSERT OR IGNORE`` (SQLite ``on_conflict_do_nothing``) wrapped in
    a per-row **savepoint** so that a single bad row never corrupts the
    surrounding transaction and subsequent rows / tables are still processed.

    Returns the number of rows that were actually inserted.
    """
    if not records:
        return 0

    allowed   = _get_column_names(model_class)
    col_types = _get_column_types(model_class)
    inserted  = 0
    skipped   = 0

    for row in records:
        prepared = _prepare_row(row, allowed, col_types)
        if not prepared:
            continue
        try:
            stmt = (
                sqlite_insert(model_class.__table__)
                .values(**prepared)
                .on_conflict_do_nothing()
            )
            sp = conn.begin_nested()   # SAVEPOINT – isolates this single row
            try:
                result = conn.execute(stmt)
                sp.commit()            # RELEASE SAVEPOINT
                inserted += result.rowcount
            except Exception:
                sp.rollback()          # ROLLBACK TO SAVEPOINT
                raise
        except Exception as exc:
            skipped += 1
            logger.warning(
                "  ✗ Skipping %s row – %s: %s", label, type(exc).__name__, exc
            )

    if skipped:
        logger.warning("  %s: %d row(s) skipped due to errors", label, skipped)

    return inserted


def _reseed_table(
    conn,
    model_class,
    records: list[dict[str, Any]],
    label: str,
) -> tuple[int, int]:
    """
    Upsert *records* into the table backing *model_class*.

    Uses ``INSERT OR REPLACE`` (SQLite ``on_conflict_do_update``) so that rows
    which already exist in the local database are overwritten with the latest
    values from OFFICE.  New rows are inserted normally.

    Unlike :func:`_seed_table` (which silently skips existing rows), this
    function is intended for **post-closure refreshes** where OFFICE is the
    authoritative source and local changes must reflect the current OFFICE state.

    Returns a ``(upserted, skipped)`` tuple.
    """
    if not records:
        return 0, 0

    allowed   = _get_column_names(model_class)
    col_types = _get_column_types(model_class)
    upserted  = 0
    skipped   = 0

    # Collect all non-PK column names for the SET clause.
    pk_names  = {col.name for col in model_class.__table__.primary_key.columns}
    update_cols = [c for c in allowed if c not in pk_names]

    for row in records:
        prepared = _prepare_row(row, allowed, col_types)
        if not prepared:
            continue
        try:
            stmt = sqlite_insert(model_class.__table__).values(**prepared)
            if update_cols:
                stmt = stmt.on_conflict_do_update(
                    index_elements=list(pk_names),
                    set_={col: stmt.excluded[col] for col in update_cols if col in prepared},
                )
            else:
                stmt = stmt.on_conflict_do_nothing()

            sp = conn.begin_nested()
            try:
                conn.execute(stmt)
                sp.commit()
                upserted += 1
            except Exception:
                sp.rollback()
                raise
        except Exception as exc:
            skipped += 1
            logger.warning(
                "  ✗ Skipping %s upsert row – %s: %s", label, type(exc).__name__, exc
            )

    if skipped:
        logger.warning("  %s: %d row(s) skipped during upsert", label, skipped)

    return upserted, skipped


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def seed_from_office_data(engine: Engine, data: dict[str, Any]) -> None:
    """
    Populate the local SQLite database using *data* received from OFFICE.

    Parameters
    ----------
    engine:
        The already-initialised Engine instance (tables must already exist).
    data:
        The ``"data"`` dict from the OFFICE ``/api/v1/pos/init`` response.
    """
    # Lazy imports keep startup time low when the module is not used
    # (standalone / gate modes) and prevent circular import issues.
    from data_layer.model.definition.cashier import Cashier
    from data_layer.model.definition.country import Country
    from data_layer.model.definition.country_region import CountryRegion
    from data_layer.model.definition.city import City
    from data_layer.model.definition.district import District
    from data_layer.model.definition.store import Store
    from data_layer.model.definition.currency import Currency
    from data_layer.model.definition.currency_table import CurrencyTable
    from data_layer.model.definition.payment_type import PaymentType
    from data_layer.model.definition.vat import Vat
    from data_layer.model.definition.product_unit import ProductUnit
    from data_layer.model.definition.product_manufacturer import ProductManufacturer
    from data_layer.model.definition.department_main_group import DepartmentMainGroup
    from data_layer.model.definition.department_sub_group import DepartmentSubGroup
    from data_layer.model.definition.product import Product
    from data_layer.model.definition.product_variant import ProductVariant
    from data_layer.model.definition.product_attribute import ProductAttribute
    from data_layer.model.definition.product_barcode import ProductBarcode
    from data_layer.model.definition.product_barcode_mask import ProductBarcodeMask
    from data_layer.model.definition.warehouse import Warehouse
    from data_layer.model.definition.warehouse_location import WarehouseLocation
    from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
    from data_layer.model.definition.transaction_discount_type import TransactionDiscountType
    from data_layer.model.definition.transaction_document_type import TransactionDocumentType
    from data_layer.model.definition.transaction_sequence import TransactionSequence
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl
    from data_layer.model.definition.label_value import LabelValue
    from data_layer.model.definition.pos_settings import PosSettings
    from data_layer.model.definition.pos_virtual_keyboard import PosVirtualKeyboard
    from data_layer.model.definition.cashier_performance_target import CashierPerformanceTarget
    from data_layer.model.definition.campaign_type import CampaignType
    from data_layer.model.definition.campaign import Campaign
    from data_layer.model.definition.campaign_rule import CampaignRule
    from data_layer.model.definition.campaign_product import CampaignProduct
    from data_layer.model.definition.coupon import Coupon
    from data_layer.model.definition.loyalty_program import LoyaltyProgram
    from data_layer.model.definition.loyalty_tier import LoyaltyTier
    from data_layer.model.definition.loyalty_earn_rule import LoyaltyEarnRule
    from data_layer.model.definition.loyalty_redemption_policy import LoyaltyRedemptionPolicy
    from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy
    from data_layer.model.definition.customer_segment import CustomerSegment
    from data_layer.model.definition.customer import Customer

    # Insertion order matters: parent tables must be populated before child
    # tables to satisfy SQLite foreign-key constraints.
    SEED_PLAN: list[tuple[str, type]] = [
        ("cashiers",                    Cashier),
        ("countries",                   Country),
        ("country_regions",             CountryRegion),
        ("store",                       Store),           # single dict or list
        ("cities",                      City),
        ("districts",                   District),
        ("currencies",                  Currency),
        ("currency_table",              CurrencyTable),
        ("payment_types",               PaymentType),
        ("vat_rates",                   Vat),
        ("product_units",               ProductUnit),
        ("product_manufacturers",       ProductManufacturer),
        ("department_main_groups",      DepartmentMainGroup),
        ("department_sub_groups",       DepartmentSubGroup),
        ("products",                    Product),
        ("product_variants",            ProductVariant),
        ("product_attributes",          ProductAttribute),
        ("product_barcodes",            ProductBarcode),
        ("product_barcode_masks",       ProductBarcodeMask),
        ("warehouses",                  Warehouse),
        ("warehouse_locations",         WarehouseLocation),
        ("warehouse_product_stock",     WarehouseProductStock),
        ("transaction_discount_types",  TransactionDiscountType),
        ("transaction_document_types",  TransactionDocumentType),
        ("transaction_sequences",       TransactionSequence),
        ("forms",                       Form),
        ("form_controls",               FormControl),
        ("label_values",                LabelValue),
        ("pos_settings",                PosSettings),
        ("pos_virtual_keyboards",       PosVirtualKeyboard),
        ("cashier_performance_targets", CashierPerformanceTarget),
        ("campaign_types",              CampaignType),
        ("campaigns",                   Campaign),
        ("campaign_rules",              CampaignRule),
        ("campaign_products",           CampaignProduct),
        ("coupons",                     Coupon),
        ("loyalty_programs",            LoyaltyProgram),
        ("loyalty_tiers",               LoyaltyTier),
        ("loyalty_earn_rules",          LoyaltyEarnRule),
        ("loyalty_redemption_policies", LoyaltyRedemptionPolicy),
        ("loyalty_program_policies",    LoyaltyProgramPolicy),
        ("customer_segments",           CustomerSegment),
        ("customers",                   Customer),
    ]

    total_inserted = 0
    total_received = 0

    logger.info("Starting OFFICE data seeding...")

    # Use a single engine-level connection wrapped in one transaction so that
    # every table is committed atomically.  Per-row savepoints inside
    # _seed_table isolate individual bad rows without rolling back the whole
    # import.
    with engine.engine.begin() as conn:
        for key, model_cls in SEED_PLAN:
            raw = data.get(key)
            if raw is None:
                logger.debug("  %-35s (not in payload – skipped)", key)
                continue

            # OFFICE returns the store as a single dict; normalise to a list.
            records: list[dict[str, Any]] = [raw] if isinstance(raw, dict) else raw
            received = len(records)
            total_received += received

            count = _seed_table(conn, model_cls, records, label=key)
            total_inserted += count
            logger.info(
                "  %-35s %4d / %4d record(s) inserted",
                key, count, received,
            )

    logger.info(
        "✓ Office seeding complete – %d of %d total records inserted",
        total_inserted, total_received,
    )


def reseed_from_office_data(engine: Engine, data: dict[str, Any]) -> dict[str, int]:
    """
    Upsert (refresh) the local SQLite database using *data* received from OFFICE.

    This function is called **after a successful closure push** so that any
    master-data changes made in OFFICE since the last sync (products, prices,
    cashiers, campaigns, loyalty rules, etc.) are reflected in the local
    database immediately.

    Unlike :func:`seed_from_office_data` (which uses INSERT OR IGNORE and
    skips rows that already exist), this function uses INSERT OR REPLACE so
    that every row from OFFICE overwrites the local copy.  New rows are
    inserted; rows absent from the OFFICE payload are left untouched.

    Parameters
    ----------
    engine:
        The already-initialised Engine instance (tables must already exist).
    data:
        The ``"data"`` dict from the OFFICE ``/api/v1/pos/init`` response.

    Returns
    -------
    dict with keys ``"upserted"`` and ``"skipped"`` containing aggregate counts.
    """
    from data_layer.model.definition.cashier import Cashier
    from data_layer.model.definition.country import Country
    from data_layer.model.definition.country_region import CountryRegion
    from data_layer.model.definition.city import City
    from data_layer.model.definition.district import District
    from data_layer.model.definition.store import Store
    from data_layer.model.definition.currency import Currency
    from data_layer.model.definition.currency_table import CurrencyTable
    from data_layer.model.definition.payment_type import PaymentType
    from data_layer.model.definition.vat import Vat
    from data_layer.model.definition.product_unit import ProductUnit
    from data_layer.model.definition.product_manufacturer import ProductManufacturer
    from data_layer.model.definition.department_main_group import DepartmentMainGroup
    from data_layer.model.definition.department_sub_group import DepartmentSubGroup
    from data_layer.model.definition.product import Product
    from data_layer.model.definition.product_variant import ProductVariant
    from data_layer.model.definition.product_attribute import ProductAttribute
    from data_layer.model.definition.product_barcode import ProductBarcode
    from data_layer.model.definition.product_barcode_mask import ProductBarcodeMask
    from data_layer.model.definition.warehouse import Warehouse
    from data_layer.model.definition.warehouse_location import WarehouseLocation
    from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
    from data_layer.model.definition.transaction_discount_type import TransactionDiscountType
    from data_layer.model.definition.transaction_document_type import TransactionDocumentType
    from data_layer.model.definition.transaction_sequence import TransactionSequence
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl
    from data_layer.model.definition.label_value import LabelValue
    from data_layer.model.definition.pos_settings import PosSettings
    from data_layer.model.definition.pos_virtual_keyboard import PosVirtualKeyboard
    from data_layer.model.definition.cashier_performance_target import CashierPerformanceTarget
    from data_layer.model.definition.campaign_type import CampaignType
    from data_layer.model.definition.campaign import Campaign
    from data_layer.model.definition.campaign_rule import CampaignRule
    from data_layer.model.definition.campaign_product import CampaignProduct
    from data_layer.model.definition.coupon import Coupon
    from data_layer.model.definition.loyalty_program import LoyaltyProgram
    from data_layer.model.definition.loyalty_tier import LoyaltyTier
    from data_layer.model.definition.loyalty_earn_rule import LoyaltyEarnRule
    from data_layer.model.definition.loyalty_redemption_policy import LoyaltyRedemptionPolicy
    from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy
    from data_layer.model.definition.customer_segment import CustomerSegment
    from data_layer.model.definition.customer import Customer

    RESEED_PLAN: list[tuple[str, type]] = [
        ("cashiers",                    Cashier),
        ("countries",                   Country),
        ("country_regions",             CountryRegion),
        ("store",                       Store),
        ("cities",                      City),
        ("districts",                   District),
        ("currencies",                  Currency),
        ("currency_table",              CurrencyTable),
        ("payment_types",               PaymentType),
        ("vat_rates",                   Vat),
        ("product_units",               ProductUnit),
        ("product_manufacturers",       ProductManufacturer),
        ("department_main_groups",      DepartmentMainGroup),
        ("department_sub_groups",       DepartmentSubGroup),
        ("products",                    Product),
        ("product_variants",            ProductVariant),
        ("product_attributes",          ProductAttribute),
        ("product_barcodes",            ProductBarcode),
        ("product_barcode_masks",       ProductBarcodeMask),
        ("warehouses",                  Warehouse),
        ("warehouse_locations",         WarehouseLocation),
        ("warehouse_product_stock",     WarehouseProductStock),
        ("transaction_discount_types",  TransactionDiscountType),
        ("transaction_document_types",  TransactionDocumentType),
        ("transaction_sequences",       TransactionSequence),
        ("forms",                       Form),
        ("form_controls",               FormControl),
        ("label_values",                LabelValue),
        ("pos_settings",                PosSettings),
        ("pos_virtual_keyboards",       PosVirtualKeyboard),
        ("cashier_performance_targets", CashierPerformanceTarget),
        ("campaign_types",              CampaignType),
        ("campaigns",                   Campaign),
        ("campaign_rules",              CampaignRule),
        ("campaign_products",           CampaignProduct),
        ("coupons",                     Coupon),
        ("loyalty_programs",            LoyaltyProgram),
        ("loyalty_tiers",               LoyaltyTier),
        ("loyalty_earn_rules",          LoyaltyEarnRule),
        ("loyalty_redemption_policies", LoyaltyRedemptionPolicy),
        ("loyalty_program_policies",    LoyaltyProgramPolicy),
        ("customer_segments",           CustomerSegment),
        ("customers",                   Customer),
    ]

    total_upserted = 0
    total_skipped  = 0

    logger.info("[OfficeReseed] Starting post-closure data refresh from OFFICE...")

    with engine.engine.begin() as conn:
        for key, model_cls in RESEED_PLAN:
            raw = data.get(key)
            if raw is None:
                logger.debug("  %-35s (not in payload – skipped)", key)
                continue

            records: list[dict[str, Any]] = [raw] if isinstance(raw, dict) else raw
            upserted, skipped = _reseed_table(conn, model_cls, records, label=key)
            total_upserted += upserted
            total_skipped  += skipped
            logger.info(
                "  %-35s %4d upserted, %d skipped",
                key, upserted, skipped,
            )

    logger.info(
        "[OfficeReseed] ✓ Refresh complete – %d row(s) upserted, %d skipped",
        total_upserted, total_skipped,
    )
    return {"upserted": total_upserted, "skipped": total_skipped}
