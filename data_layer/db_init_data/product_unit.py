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

from data_layer.model import ProductUnit


def _insert_product_units(session, admin_cashier_id: int):
    """Insert default product units if not exists"""
    unit_exists = session.query(ProductUnit).first()
    if not unit_exists:
        units = [
            {"code": "PCS", "name": "Pieces", "description": "Pieces unit"},
            {"code": "KG", "name": "Kilogram", "description": "Kilogram unit"},
            {"code": "GR", "name": "Gram", "description": "Gram unit"},
            {"code": "LT", "name": "Liter", "description": "Liter unit"},
            {"code": "M", "name": "Meter", "description": "Meter unit"},
            {"code": "M2", "name": "Square Meter", "description": "Square meter unit"},
            {"code": "PKT", "name": "Package", "description": "Package unit"}
        ]

        for unit_data in units:
            unit = ProductUnit(
                code=unit_data["code"],
                name=unit_data["name"],
                description=unit_data["description"]
            )
            unit.fk_cashier_create_id = admin_cashier_id
            unit.fk_cashier_update_id = admin_cashier_id
            session.add(unit)
        print("✓ Default product units added")
