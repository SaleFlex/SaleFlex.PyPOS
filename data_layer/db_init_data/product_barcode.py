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

from data_layer.model import ProductBarcode, Product



from core.logger import get_logger

logger = get_logger(__name__)

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
                "purchase_price": 100.0,
                "sale_price": 110.0
            },
            {
                "product_code": "5",
                "barcode": "7622210449283",
                "old_barcode": "7622210449283",
                "purchase_price": 80.0,
                "sale_price": 88.0
            },
            {
                "product_code": "6",
                "barcode": "5000328721575",
                "old_barcode": "5000328721575",
                "purchase_price": 150.0,
                "sale_price": 165.0
            },
            {
                "product_code": "7",
                "barcode": "8711200334532",
                "old_barcode": "8711200334532",
                "purchase_price": 200.0,
                "sale_price": 220.0
            },
            {
                "product_code": "8",
                "barcode": "5449000000996",
                "old_barcode": "5449000000996",
                "purchase_price": 172.0,
                "sale_price": 190.0
            },
            {
                "product_code": "9",
                "barcode": "0746817004304",
                "old_barcode": "0746817004304",
                "purchase_price": 350.0,
                "sale_price": 385.0
            },
            {
                "product_code": "10",
                "barcode": "7622210700394",
                "old_barcode": "7622210700394",
                "purchase_price": 180.0,
                "sale_price": 200.0
            },
            {
                "product_code": "11",
                "barcode": "5000328355037",
                "old_barcode": "5000328355037",
                "purchase_price": 135.0,
                "sale_price": 150.0
            },
            {
                "product_code": "12",
                "barcode": "5000157077916",
                "old_barcode": "5000157077916",
                "purchase_price": 110.0,
                "sale_price": 120.0
            },
            {
                "product_code": "13",
                "barcode": "5010044003089",
                "old_barcode": "5010044003089",
                "purchase_price": 136.0,
                "sale_price": 150.0
            },
            {
                "product_code": "14",
                "barcode": "5740900802725",
                "old_barcode": "5740900802725",
                "purchase_price": 455.0,
                "sale_price": 500.0
            },
            {
                "product_code": "15",
                "barcode": "8001090390021",
                "old_barcode": "8001090390021",
                "purchase_price": 546.0,
                "sale_price": 600.0
            },
            {
                "product_code": "16",
                "barcode": "8714100852703",
                "old_barcode": "8714100852703",
                "purchase_price": 91.0,
                "sale_price": 100.0
            },
            {
                "product_code": "17",
                "barcode": "5000171054815",
                "old_barcode": "5000171054815",
                "purchase_price": 272.0,
                "sale_price": 300.0
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
                logger.error("⚠ Product with code '%s' not found for barcode '%s'", barcode_item['product_code'], barcode_item['barcode'])

        logger.info("✓ Inserted %s sample product barcodes", len(barcode_data)) 