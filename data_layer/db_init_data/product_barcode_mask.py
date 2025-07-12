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

from data_layer.model import ProductBarcodeMask


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
        print("✓ Default product barcode mask added: WEIGHED GOODS")
