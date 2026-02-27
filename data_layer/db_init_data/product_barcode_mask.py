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

from data_layer.model import ProductBarcodeMask



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_product_barcode_masks(session, admin_cashier_id: int):
    """Insert default product barcode masks if not exists"""
    barcode_mask_exists = session.query(ProductBarcodeMask).first()
    if not barcode_mask_exists:
        weighed_goods_mask = ProductBarcodeMask()
        weighed_goods_mask.barcode_length = 19
        weighed_goods_mask.starting_digits = '1'
        weighed_goods_mask.code_started_at = 1  # 0-based index
        weighed_goods_mask.code_length = 6
        weighed_goods_mask.weight_started_at = 7
        weighed_goods_mask.weight_length = 6
        weighed_goods_mask.price_started_at = 13
        weighed_goods_mask.price_length = 6
        weighed_goods_mask.description = 'WEIGHED GOODS'
        weighed_goods_mask.fk_cashier_create_id = admin_cashier_id
        weighed_goods_mask.fk_cashier_update_id = admin_cashier_id

        session.add(weighed_goods_mask)
        logger.info("✓ Default product barcode mask added: WEIGHED GOODS")
