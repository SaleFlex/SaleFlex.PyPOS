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

from data_layer.model import ProductManufacturer



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_product_manufacturers(session):
    """Insert default product manufacturers if not exists"""
    manufacturer_exists = session.query(ProductManufacturer).first()
    if not manufacturer_exists:
        default_manufacturer = ProductManufacturer(
            name="General Manufacturer",
            description="Default manufacturer for products without specific manufacturer"
        )
        session.add(default_manufacturer)
        logger.info("✓ Default product manufacturer added")
