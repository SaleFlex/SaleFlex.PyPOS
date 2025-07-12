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

from data_layer.model import ProductBarcode, Product


def _insert_product_barcodes(session, admin_cashier_id: str):
    """Insert sample product barcodes if not exists"""
    barcode_exists = session.query(ProductBarcode).first()
    if not barcode_exists:
        # Sample product barcodes based on C# TablePluBarcode data
        # Map C# FkPluId to Product code for lookup
        barcode_data = [
            {
                "product_code": "4",
                "barcode": "5000157070008",
                "old_barcode": "5000157070008",
                "purchase_price": 10000,  # 100 * 100 (cents)
                "sale_price": 11000   # 110 * 100 (cents)
            },
            {
                "product_code": "5",
                "barcode": "7622210449283",
                "old_barcode": "7622210449283",
                "purchase_price": 8000,   # 80 * 100 (cents)
                "sale_price": 8800    # 88 * 100 (cents)
            },
            {
                "product_code": "6",
                "barcode": "5000328721575",
                "old_barcode": "5000328721575",
                "purchase_price": 15000,  # 150 * 100 (cents)
                "sale_price": 16500   # 165 * 100 (cents)
            },
            {
                "product_code": "7",
                "barcode": "8711200334532",
                "old_barcode": "8711200334532",
                "purchase_price": 20000,  # 200 * 100 (cents)
                "sale_price": 22000   # 220 * 100 (cents)
            },
            {
                "product_code": "8",
                "barcode": "5449000000996",
                "old_barcode": "5449000000996",
                "purchase_price": 17200,  # 172 * 100 (cents)
                "sale_price": 19000   # 190 * 100 (cents)
            },
            {
                "product_code": "9",
                "barcode": "0746817004304",
                "old_barcode": "0746817004304",
                "purchase_price": 35000,  # 350 * 100 (cents)
                "sale_price": 38500   # 385 * 100 (cents)
            },
            {
                "product_code": "10",
                "barcode": "7622210700394",
                "old_barcode": "7622210700394",
                "purchase_price": 18000,  # 180 * 100 (cents)
                "sale_price": 20000   # 200 * 100 (cents)
            },
            {
                "product_code": "11",
                "barcode": "5000328355037",
                "old_barcode": "5000328355037",
                "purchase_price": 13500,  # 135 * 100 (cents)
                "sale_price": 15000   # 150 * 100 (cents)
            },
            {
                "product_code": "12",
                "barcode": "5000157077916",
                "old_barcode": "5000157077916",
                "purchase_price": 11000,  # 110 * 100 (cents)
                "sale_price": 12000   # 120 * 100 (cents)
            },
            {
                "product_code": "13",
                "barcode": "5010044003089",
                "old_barcode": "5010044003089",
                "purchase_price": 13600,  # 136 * 100 (cents)
                "sale_price": 15000   # 150 * 100 (cents)
            },
            {
                "product_code": "14",
                "barcode": "5740900802725",
                "old_barcode": "5740900802725",
                "purchase_price": 45500,  # 455 * 100 (cents)
                "sale_price": 50000   # 500 * 100 (cents)
            },
            {
                "product_code": "15",
                "barcode": "8001090390021",
                "old_barcode": "8001090390021",
                "purchase_price": 54600,  # 546 * 100 (cents)
                "sale_price": 60000   # 600 * 100 (cents)
            },
            {
                "product_code": "16",
                "barcode": "8714100852703",
                "old_barcode": "8714100852703",
                "purchase_price": 9100,   # 91 * 100 (cents)
                "sale_price": 10000   # 100 * 100 (cents)
            },
            {
                "product_code": "17",
                "barcode": "5000171054815",
                "old_barcode": "5000171054815",
                "purchase_price": 27200,  # 272 * 100 (cents)
                "sale_price": 30000   # 300 * 100 (cents)
            }
        ]

        # Create product barcodes
        for barcode_item in barcode_data:
            # Find the product by code
            product = session.query(Product).filter_by(code=barcode_item["product_code"]).first()
            
            if product:
                product_barcode = ProductBarcode(
                    fk_product_id=product.id,
                    barcode=barcode_item["barcode"],
                    old_barcode=barcode_item["old_barcode"],
                    purchase_price=barcode_item["purchase_price"],
                    sale_price=barcode_item["sale_price"]
                )
                
                # Set audit fields
                product_barcode.fk_cashier_create_id = admin_cashier_id
                product_barcode.fk_cashier_update_id = admin_cashier_id
                
                session.add(product_barcode)
            else:
                print(f"⚠ Product with code '{barcode_item['product_code']}' not found for barcode '{barcode_item['barcode']}'")

        print(f"✓ Inserted {len(barcode_data)} sample product barcodes") 