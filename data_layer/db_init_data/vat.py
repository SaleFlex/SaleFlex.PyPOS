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

from data_layer.model import Vat


def _insert_vat_rates(session, admin_cashier_id: int):
    """Insert default VAT rates if not exists"""
    vat_exists = session.query(Vat).first()
    if not vat_exists:
        vat_rates = [
            {"name": "%0", "no": 1, "rate": 0, "description": "Zero VAT Rate (0%)"},
            {"name": "%5", "no": 2, "rate": 5, "description": "Reduced VAT Rate (5%)"},
            {"name": "%20", "no": 3, "rate": 20, "description": "Standard VAT Rate (20%)"}
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
        print("✓ Default VAT rates added")