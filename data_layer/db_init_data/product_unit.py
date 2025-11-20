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
