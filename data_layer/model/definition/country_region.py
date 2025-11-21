"""
SaleFlex.PyPOS - Point of Sale Application

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

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CountryRegion(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Sub-country regions (US states, Canadian provinces, special economic zones, etc.)
    
    Used for tracking regions within countries that have different tax rates,
    regulations, or compliance requirements. Examples:
    - US States: California (CA), New York (NY), Texas (TX)
    - Canadian Provinces: Ontario (ON), British Columbia (BC), Quebec (QC)
    - Special Economic Zones: Free trade zones, special tax regions
    - EU Regions: German states (Bavaria, Baden-Württemberg), French regions
    
    This model enables:
    - Region-specific closure templates (e.g., usa_ca.json for California)
    - Region-specific tax calculations
    - Compliance reporting by region
    - Multi-region store operations
    """
    __tablename__ = "country_region"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_country_id = Column(UUID, ForeignKey("country.id"), nullable=False, index=True)
    
    # Region code (e.g., "CA", "NY", "ON", "BC")
    # Used for template file naming: {country_code}_{region_code}.json
    region_code = Column(String(10), nullable=False)
    
    # Full region name (e.g., "California", "Ontario", "Bavaria")
    region_name = Column(String(200), nullable=False)
    
    # ISO 3166-2 code (e.g., "US-CA", "CA-ON", "DE-BY")
    # Format: {country_code}-{region_code}
    iso_code = Column(String(15), nullable=True)
    
    # Region type (e.g., "state", "province", "region", "free_zone", "special_economic_zone")
    region_type = Column(String(50), nullable=True)
    
    # Additional metadata stored as JSON
    # Can include: tax rates, time zones, capital city, special regulations, etc.
    metadata_json = Column(Text, nullable=True)
    
    # Description for special regions (free zones, special economic zones, etc.)
    description = Column(Text, nullable=True)
    
    # Indicates if this region has special tax/compliance requirements
    has_special_requirements = Column(Boolean, nullable=False, default=False)
    
    # Display order for UI sorting
    display_order = Column(String(10), nullable=True)

    # Unique constraint: same region code cannot exist twice for the same country
    __table_args__ = (
        UniqueConstraint('fk_country_id', 'region_code', name='uq_country_region_code'),
    )

    def __repr__(self):
        return f"<CountryRegion(country='{self.fk_country_id}', code='{self.region_code}', name='{self.region_name}')>"
    
    def get_template_filename(self, country_code):
        """
        Get the template filename for this region.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
            
        Returns:
            Template filename (e.g., "usa_ca.json")
        """
        return f"{country_code.lower()}_{self.region_code.lower()}.json"

