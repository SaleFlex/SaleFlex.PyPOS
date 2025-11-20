"""
SaleFlex.PyPOS - Database Initial Data

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from data_layer.model import PosSettings
from settings.settings import Settings


def _insert_pos_settings(session, admin_cashier_id, gbp_currency=None):
    """Insert default POS settings if not exists
    
    Args:
        session: Database session
        admin_cashier_id: Admin cashier ID for audit fields
        gbp_currency: GBP Currency object (from _insert_currencies) for default current_currency
    """
    print("[DEBUG] _insert_pos_settings called")
    print(f"[DEBUG] admin_cashier_id={admin_cashier_id}, gbp_currency={gbp_currency}")
    
    # Check if POS settings already exist
    pos_settings_exists = session.query(PosSettings).filter_by(is_deleted=False).first()
    if pos_settings_exists:
        print(f"✓ POS settings already exist: id={pos_settings_exists.id}, name={pos_settings_exists.name}")
        return
    
    print("[DEBUG] Creating new POS settings...")
    settings = Settings()
    
    # Get values from settings.toml
    pos_data = settings.setting_data.get("pos", {})
    receipt_printer_data = settings.setting_data.get("receipt_printer", {})
    invoice_printer_data = settings.setting_data.get("invoice_printer", {})
    weighing_scales_data = settings.setting_data.get("weighing_scales", {})
    backend_data = settings.setting_data.get("backend_integration", {})
    
    # Get GBP currency ID if provided, otherwise query for it
    gbp_currency_id = None
    if gbp_currency:
        gbp_currency_id = gbp_currency.id
        print(f"[DEBUG] Using provided GBP currency: id={gbp_currency_id}")
    else:
        # Fallback: query for GBP currency
        from data_layer.model import Currency
        gbp_currencies = session.query(Currency).filter_by(sign="GBP", is_deleted=False).first()
        if gbp_currencies:
            gbp_currency_id = gbp_currencies.id
            print(f"[DEBUG] Found GBP currency: id={gbp_currency_id}")
        else:
            print("[DEBUG] WARNING: GBP currency not found!")
    
    if not gbp_currency_id:
        print("[DEBUG] WARNING: GBP currency ID not found, creating PosSettings without currency")
    
    pos_settings = PosSettings(
        name=pos_data.get("name", "Store 1. POS"),
        mac_address=pos_data.get("mac_address", "BC091B5FBEB9"),
        force_to_work_online=pos_data.get("force_to_work_online", True),
        fk_current_currency_id=gbp_currency_id,  # Foreign key to Currency (GBP)
        fk_cashier_create_id=admin_cashier_id,  # AuditMixin field
        fk_cashier_update_id=admin_cashier_id   # AuditMixin field
    )
    
    # Set printer settings from settings.toml if available
    if receipt_printer_data.get("type"):
        pos_settings.receipt_printer_type = receipt_printer_data.get("type")
    if receipt_printer_data.get("port"):
        pos_settings.receipt_printer_port = receipt_printer_data.get("port")
    if invoice_printer_data.get("type"):
        pos_settings.invoice_printer_type = invoice_printer_data.get("type")
    if invoice_printer_data.get("port"):
        pos_settings.invoice_printer_port = invoice_printer_data.get("port")
    
    # Set scale settings if available
    if weighing_scales_data.get("type"):
        pos_settings.scale_type = weighing_scales_data.get("type")
    if weighing_scales_data.get("port"):
        pos_settings.scale_port = weighing_scales_data.get("port")
    
    # Set backend integration settings if available
    backend_conn1 = backend_data.get("backend_connection_1")
    if backend_conn1 and ':' in backend_conn1:
        parts = backend_conn1.split(':')
        pos_settings.server_ip1 = parts[0]
        try:
            pos_settings.server_port1 = int(parts[1]) if len(parts) > 1 else None
        except ValueError:
            pass
    
    backend_conn2 = backend_data.get("backend_connection_2")
    if backend_conn2 and ':' in backend_conn2:
        parts = backend_conn2.split(':')
        pos_settings.server_ip2 = parts[0]
        try:
            pos_settings.server_port2 = int(parts[1]) if len(parts) > 1 else None
        except ValueError:
            pass
    
    print(f"[DEBUG] About to add PosSettings: name={pos_settings.name}, currency_id={pos_settings.fk_current_currency_id}")
    session.add(pos_settings)
    session.flush()  # Flush to get any errors before commit
    
    # Verify the object was added
    print(f"[DEBUG] PosSettings added: id={pos_settings.id}, name={pos_settings.name}, currency_id={pos_settings.fk_current_currency_id}")
    
    # Note: Don't commit here - the context manager in insert_initial_data will commit
    print("✓ Default POS settings added (will be committed with transaction)")

