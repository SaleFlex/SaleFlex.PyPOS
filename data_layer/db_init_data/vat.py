"""
SaleFlex.PyPOS - Database Initial Data
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from data_layer.model import Vat



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_vat_rates(session, admin_cashier_id: int):
    """Insert default VAT rates if not exists"""
    vat_exists = session.query(Vat).first()
    if not vat_exists:
        vat_rates = [
            {"name": "%0", "no": 1, "rate": 1.00, "description": "Zero VAT Rate (0%)"},
            {"name": "%1", "no": 2, "rate": 1.00, "description": "First VAT Rate (1%)"},
            {"name": "%10", "no": 3, "rate": 5.00, "description": "Reduced VAT Rate (5%)"},
            {"name": "%20", "no": 4, "rate": 20.00, "description": "Standard VAT Rate (20%)"}
        ]

        for vat_data in vat_rates:
            vat = Vat(
                name=vat_data["name"],
                no=vat_data["no"],
                rate=vat_data["rate"],
                description=vat_data["description"]
            )
            vat.fk_cashier_create_id = admin_cashier_id
            vat.fk_cashier_update_id = admin_cashier_id
            session.add(vat)
        logger.info("✓ Default VAT rates added")