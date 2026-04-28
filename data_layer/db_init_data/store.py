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

from data_layer.model import Store, Country, City



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_default_store(session):
    """Insert default store if not exists"""
    store_exists = session.query(Store).first()
    if not store_exists:
        # Get United Kingdom country ID (default country)
        United_Kingdom_country = session.query(Country).filter(Country.iso_alpha2 == 'GB').first()
        default_country_id = United_Kingdom_country.id if United_Kingdom_country else None
        
        # Get London city ID if available (optional)
        london_city = session.query(City).filter(City.code == 'LON').first() if default_country_id else None
        default_city_id = london_city.id if london_city else None
        
        default_store = Store(
            # Basic information
            brand_name="SaleFlex",
            company_name="SaleFlex PyPOS",
            web_page_url="https://saleflex.com",
            description="Default POS Store",
            
            # Address information (can be set later)
            street=None,
            block_no=None,
            district=None,
            postal_code=None,
            fk_city_id=default_city_id,
            fk_country_id=default_country_id,
            
            # Contact information (can be set later)
            phone_number=None,
            email=None,
            fax=None,
            
            # Manager information (can be set later)
            manager_name=None,
            manager_contact_number=None,
            
            # Technician information (can be set later)
            technician_name=None,
            technician_contact_number=None,
            
            # Status
            is_active=True
        )
        
        session.add(default_store)
        logger.info("✓ Default store added")
        logger.debug("  - Brand: SaleFlex")
        logger.debug("  - Company: SaleFlex PyPOS")
        logger.debug("  - Default Country: %s", 'United Kingdom' if default_country_id else 'None')
    else:
        logger.info("✓ Store already exists")
