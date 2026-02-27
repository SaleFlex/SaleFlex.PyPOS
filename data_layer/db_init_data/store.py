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
