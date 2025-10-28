from data_layer.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from data_layer.db_init_data.cashier import _insert_admin_cashier
from data_layer.db_init_data.city import _insert_cities
from data_layer.db_init_data.country import _insert_countries
from data_layer.db_init_data.currency import _insert_currencies
from data_layer.db_init_data.department_group import _insert_department_groups
from data_layer.db_init_data.district import _insert_districts
from data_layer.db_init_data.form import _insert_default_forms
from data_layer.db_init_data.form_control import _insert_form_controls
from data_layer.db_init_data.label_value import _insert_label_values
from data_layer.db_init_data.payment_type import _insert_payment_types
from data_layer.db_init_data.product import _insert_products
from data_layer.db_init_data.product_barcode import _insert_product_barcodes
from data_layer.db_init_data.product_barcode_mask import _insert_product_barcode_masks
from data_layer.db_init_data.product_manufacturer import _insert_product_manufacturers
from data_layer.db_init_data.product_unit import _insert_product_units
from data_layer.db_init_data.store import _insert_default_store
from data_layer.db_init_data.transaction_document_type import _insert_transaction_document_types
from data_layer.db_init_data.transaction_sequence import _insert_transaction_sequences
from data_layer.db_init_data.vat import _insert_vat_rates
from data_layer.db_init_data.product_variant import _insert_product_variants
from data_layer.db_init_data.product_attribute import _insert_product_attributes
from data_layer.db_init_data.cashier_performance_target import _insert_cashier_performance_targets
from data_layer.db_init_data.warehouse import _insert_warehouses
from data_layer.db_init_data.pos_virtual_keyboard import _insert_virtual_keyboard_settings, _insert_alternative_keyboard_themes

def insert_initial_data(engine: Engine):
    """
    Inserts initial data (only if tables are empty)
    """
    try:
        with engine.get_session() as session:
            # Insert admin cashier
            admin_cashier = _insert_admin_cashier(session)

            # Insert countries (must be before store because of foreign key)
            _insert_countries(session)

            # Insert default store
            _insert_default_store(session)

            # Insert cities
            _insert_cities(session)

            # Insert districts
            _insert_districts(session)

            # Insert warehouses
            _insert_warehouses(session, admin_cashier.id)

            # Insert currencies
            _insert_currencies(session)

            # Insert payment types
            _insert_payment_types(session)

            # Insert VAT rates
            _insert_vat_rates(session, admin_cashier.id)

            # Insert product units
            _insert_product_units(session, admin_cashier.id)

            # Insert product manufacturers
            _insert_product_manufacturers(session)

            # Insert department groups
            _insert_department_groups(session, admin_cashier.id)

            # Insert sample products
            _insert_products(session, admin_cashier.id)

            # Insert product variants
            _insert_product_variants(session, admin_cashier.id)

            # Insert product attributes
            _insert_product_attributes(session, admin_cashier.id)

            # Insert sample product barcodes
            _insert_product_barcodes(session, admin_cashier.id)

            # Insert transaction document types
            _insert_transaction_document_types(session)

            # Insert transaction sequences
            _insert_transaction_sequences(session, admin_cashier.id)

            # Insert product barcode masks
            _insert_product_barcode_masks(session, admin_cashier.id)

            # Insert default forms
            _insert_default_forms(session, admin_cashier.id)

            # Insert form controls
            _insert_form_controls(session, admin_cashier.id)

            # Insert label values
            _insert_label_values(session)

            # Insert cashier performance targets
            _insert_cashier_performance_targets(session, admin_cashier.id)

            # Insert virtual keyboard settings
            _insert_virtual_keyboard_settings(session)
            
            # Insert alternative keyboard themes
            _insert_alternative_keyboard_themes(session)

    except SQLAlchemyError as e:
        print(f"✗ Initial data insertion error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise