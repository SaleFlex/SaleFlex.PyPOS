"""
SaleFlex.PyPOS - Database Initial Data

Copyright (c) 2025 Ferhat Mousavi

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
"""

from data_layer.model import PosSettings
from pos.hardware import get_device_serial_number, get_operation_system



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_pos_settings(session, admin_cashier_id, gbp_currency=None):
    """Insert default POS settings if not exists
    
    Args:
        session: Database session
        admin_cashier_id: Admin cashier ID for audit fields
        gbp_currency: GBP Currency object (from _insert_currencies) for default current_currency
    """
    logger.debug("[DEBUG] _insert_pos_settings called")
    logger.debug("[DEBUG] admin_cashier_id=%s, gbp_currency=%s", admin_cashier_id, gbp_currency)
    
    # Check if POS settings already exist
    pos_settings_exists = session.query(PosSettings).filter_by(is_deleted=False).first()
    if pos_settings_exists:
        logger.info("✓ POS settings already exist: id=%s, name=%s", pos_settings_exists.id, pos_settings_exists.name)
        return
    
    logger.debug("[DEBUG] Creating new POS settings...")
    
    # Get GBP currency ID if provided, otherwise query for it
    gbp_currency_id = None
    if gbp_currency:
        gbp_currency_id = gbp_currency.id
        logger.debug("[DEBUG] Using provided GBP currency: id=%s", gbp_currency_id)
    else:
        # Fallback: query for GBP currency
        from data_layer.model import Currency
        gbp_currencies = session.query(Currency).filter_by(sign="GBP", is_deleted=False).first()
        if gbp_currencies:
            gbp_currency_id = gbp_currencies.id
            logger.debug("[DEBUG] Found GBP currency: id=%s", gbp_currency_id)
        else:
            logger.error("[DEBUG] WARNING: GBP currency not found!")
    
    if not gbp_currency_id:
        logger.error("[DEBUG] WARNING: GBP currency ID not found, creating PosSettings without currency")
    
    # Get United Kingdom country ID
    from data_layer.model import Country
    uk_country = session.query(Country).filter_by(name="United Kingdom").first()
    uk_country_id = None
    if uk_country:
        uk_country_id = uk_country.id
        logger.debug("[DEBUG] Found United Kingdom country: id=%s", uk_country_id)
    else:
        logger.error("[DEBUG] WARNING: United Kingdom country not found!")
    
    # Get device information
    device_serial = get_device_serial_number()
    device_os = get_operation_system()
    logger.debug("[DEBUG] Device serial number: %s", device_serial)
    logger.debug("[DEBUG] Device OS: %s", device_os)
    
    # Create PosSettings with default values
    # Note: Model fields are now managed through the database, not settings.toml
    pos_settings = PosSettings(
        pos_no_in_store=1,  # Default POS number in store
        name="Store 1. POS",  # Default value
        mac_address="BC091B5FBEB9",  # Default value
        force_to_work_online=True,  # Default value
        fk_current_currency_id=gbp_currency_id,  # Foreign key to Currency (GBP)
        fk_working_currency_id=gbp_currency_id,  # Foreign key to Currency (GBP) - working currency
        fk_default_country_id=uk_country_id,  # Foreign key to Country (United Kingdom)
        fk_cashier_create_id=admin_cashier_id,  # AuditMixin field
        fk_cashier_update_id=admin_cashier_id   # AuditMixin field
    )
    
    # Set default display settings
    pos_settings.customer_display_type = "INTERNAL"
    pos_settings.customer_display_port = "INTERNAL"
    
    # Set barcode reader port
    pos_settings.barcode_reader_port = "PS/2"
    
    # Set backend connection settings (default values)
    pos_settings.backend_ip1 = "127.0.0.1"
    pos_settings.backend_port1 = 5000
    pos_settings.backend_ip2 = "127.0.0.1"
    pos_settings.backend_port2 = 5000
    
    # Set backend type (default: GATE)
    pos_settings.backend_type = "GATE"
    
    # Set device information
    pos_settings.device_serial_number = device_serial
    pos_settings.device_operation_system = device_os
    
    # Note: Printer, scale, and backend settings are now managed through the database
    # and should be configured via the application UI or API, not settings.toml
    
    logger.debug("[DEBUG] About to add PosSettings: name=%s, pos_no=%s, currency_id=%s, country_id=%s, serial=%s", pos_settings.name, pos_settings.pos_no_in_store, pos_settings.fk_current_currency_id, pos_settings.fk_default_country_id, pos_settings.device_serial_number)
    session.add(pos_settings)
    session.flush()  # Flush to get any errors before commit
    
    # Verify the object was added
    logger.info("[DEBUG] PosSettings added: id=%s, name=%s, pos_no=%s, currency_id=%s, country_id=%s, serial=%s", pos_settings.id, pos_settings.name, pos_settings.pos_no_in_store, pos_settings.fk_current_currency_id, pos_settings.fk_default_country_id, pos_settings.device_serial_number)
    
    # Note: Don't commit here - the context manager in insert_initial_data will commit
    logger.info("✓ Default POS settings added (will be committed with transaction)")

