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

from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4
import json
import os
import sys

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureCountrySpecific(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Country-specific closure data stored as JSON with template-based initialization.
    
    This flexible approach supports all countries without creating separate models
    for each. Country-specific data is stored in the country_data_json column as JSON,
    allowing easy extension for any country's requirements.
    
    Template System:
        Closure templates are stored as JSON files in 'static_files/closures/' directory.
        Templates define the structure and default values for country-specific closure data.
        
        Template Resolution Priority:
            1. State/Province-specific: {country_code}_{state_code}.json (e.g., usa_ca.json)
            2. Country-specific: {country_code}.json (e.g., tr.json, usa.json)
            3. Default fallback: default.json
        
        Available Templates:
            - tr.json: Turkey (E-Fatura, E-İrsaliye, Diplomatic, Tourist Tax-Free)
            - usa.json: United States (general)
            - usa_ca.json: California, USA (state tax, tip reporting, gift cards)
            - usa_ny.json: New York, USA
            - usa_tx.json: Texas, USA
            - de.json: Germany (VAT by rate, reverse charge, EU sales)
            - fr.json: France (VAT rates, EU sales)
            - gb.json: United Kingdom (VAT rates)
            - jp.json: Japan (Consumption tax, point programs)
            - default.json: Default fallback template
    
    Usage Examples:
        
        # Method 1: Create from template (Recommended)
        closure = ClosureCountrySpecific.create_from_template(
            fk_closure_id=closure_id,
            country_code='TR',
            state_code=None  # Optional, for state-specific templates
        )
        
        # Method 2: Initialize existing instance from template
        closure = ClosureCountrySpecific()
        closure.fk_closure_id = closure_id
        closure.country_code = 'US'
        closure.initialize_from_template(state_code='CA')  # Load California template
        
        # Method 3: Load template manually
        template_data = ClosureCountrySpecific.load_template('TR')
        closure.set_country_data(template_data)
        
        # Method 4: Merge template with existing data
        closure.set_field('electronic_invoice_count', 100)
        closure.initialize_from_template(merge_with_existing=True)
    
    Template Data Examples:
        
        Turkey (tr.json):
        {
            "electronic_invoice_count": 0,
            "electronic_invoice_amount": 0,
            "canceled_electronic_invoice_count": 0,
            "electronic_waybill_count": 0,
            "electronic_waybill_amount": 0,
            "diplomatic_invoice_count": 0,
            "diplomatic_invoice_amount": 0,
            "tourist_tax_free_count": 0,
            "tourist_tax_free_amount": 0
        }
        
        California, USA (usa_ca.json):
        {
            "state_tax_rate": 7.25,
            "local_tax_enabled": true,
            "special_rules": {
                "food_tax_exempt": true,
                "clothing_taxable": true,
                "bottle_deposit": 0,
                "cannabis_excise_tax": 0
            },
            "sales_tax_by_county": {},
            "tip_reporting": {
                "cash_tips": 0,
                "credit_card_tips": 0,
                "reported_tips": 0
            },
            "gift_card_sales": 0,
            "gift_card_redemptions": 0
        }
        
        Germany (de.json):
        {
            "vat_by_rate": {
                "standard_rate": 19.0,
                "reduced_rate": 7.0,
                "standard_amount": 0,
                "standard_vat": 0,
                "reduced_amount": 0,
                "reduced_vat": 0
            },
            "reverse_charge_count": 0,
            "reverse_charge_amount": 0,
            "intra_eu_sales": 0,
            "extra_eu_sales": 0
        }
    
    GATE Integration:
        When PyPOS is connected to SaleFlex.GATE, templates can be:
        - Downloaded from GATE for centralized management
        - Updated remotely without POS code changes
        - Validated before deployment
    
    See Also:
        static_files/closures/README.md - Detailed template documentation
    """
    __tablename__ = "closure_country_specific"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, unique=True, index=True)
    
    # ISO 3166-1 alpha-2 country code (e.g., "TR", "US", "DE")
    country_code = Column(String(2), nullable=False, index=True)
    
    # Country-specific data stored as JSON
    # This allows flexible schema per country without creating separate tables
    country_data_json = Column(Text, nullable=False, default='{}')
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureCountrySpecific(closure='{self.fk_closure_id}', country='{self.country_code}')>"
    
    # Helper methods for type-safe access to country-specific data
    
    def get_country_data(self):
        """Get country-specific data as dictionary."""
        if not self.country_data_json:
            return {}
        try:
            return json.loads(self.country_data_json)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_country_data(self, data):
        """Set country-specific data from dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Country data must be a dictionary")
        self.country_data_json = json.dumps(data, ensure_ascii=False)
    
    def update_country_data(self, **kwargs):
        """Update specific fields in country data."""
        data = self.get_country_data()
        data.update(kwargs)
        self.set_country_data(data)
    
    def get_field(self, field_name, default=None):
        """Get a specific field from country data."""
        data = self.get_country_data()
        return data.get(field_name, default)
    
    def set_field(self, field_name, value):
        """Set a specific field in country data."""
        data = self.get_country_data()
        data[field_name] = value
        self.set_country_data(data)
    
    # Turkey-specific convenience methods
    def get_turkey_data(self):
        """Get Turkey-specific data (convenience method)."""
        if self.country_code != 'TR':
            return {}
        return self.get_country_data()
    
    def set_turkey_data(self, 
                        electronic_invoice_count=0,
                        electronic_invoice_amount=0,
                        canceled_electronic_invoice_count=0,
                        electronic_waybill_count=0,
                        electronic_waybill_amount=0,
                        diplomatic_invoice_count=0,
                        diplomatic_invoice_amount=0,
                        tourist_tax_free_count=0,
                        tourist_tax_free_amount=0):
        """Set Turkey-specific data (convenience method)."""
        if self.country_code != 'TR':
            self.country_code = 'TR'
        
        turkey_data = {
            "electronic_invoice_count": electronic_invoice_count,
            "electronic_invoice_amount": float(electronic_invoice_amount),
            "canceled_electronic_invoice_count": canceled_electronic_invoice_count,
            "electronic_waybill_count": electronic_waybill_count,
            "electronic_waybill_amount": float(electronic_waybill_amount),
            "diplomatic_invoice_count": diplomatic_invoice_count,
            "diplomatic_invoice_amount": float(diplomatic_invoice_amount),
            "tourist_tax_free_count": tourist_tax_free_count,
            "tourist_tax_free_amount": float(tourist_tax_free_amount)
        }
        self.set_country_data(turkey_data)
    
    @classmethod
    def create_for_turkey(cls, fk_closure_id, **turkey_data):
        """Factory method to create Turkey-specific closure data."""
        instance = cls()
        instance.fk_closure_id = fk_closure_id
        instance.country_code = 'TR'
        instance.set_turkey_data(**turkey_data)
        return instance
    
    # Template loading methods
    
    @staticmethod
    def _get_template_path(country_code, state_code=None):
        """
        Get the path to the closure template file.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., "TR", "US")
            state_code: Optional state/province code (e.g., "CA", "NY") for countries with states
            
        Returns:
            Path to template file, or None if not found
        """
        # Get project root directory
        project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Try state-specific template first (e.g., usa_ca.json)
        if state_code:
            state_template = os.path.join(project_path, 'static_files', 'closures', f"{country_code.lower()}_{state_code.lower()}.json")
            if os.path.exists(state_template):
                return state_template
        
        # Try country-specific template (e.g., tr.json, usa.json)
        country_template = os.path.join(project_path, 'static_files', 'closures', f"{country_code.lower()}.json")
        if os.path.exists(country_template):
            return country_template
        
        # Fall back to default template
        default_template = os.path.join(project_path, 'static_files', 'closures', 'default.json')
        if os.path.exists(default_template):
            return default_template
        
        return None
    
    @staticmethod
    def load_template(country_code, state_code=None):
        """
        Load closure template for a specific country/state.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., "TR", "US")
            state_code: Optional state/province code (e.g., "CA", "NY")
            
        Returns:
            Dictionary with template data, or empty dict if template not found
        """
        template_path = ClosureCountrySpecific._get_template_path(country_code, state_code)
        
        if not template_path or not os.path.exists(template_path):
            return {}
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                # Deep copy to avoid modifying the template
                return json.loads(json.dumps(template_data))
        except (json.JSONDecodeError, IOError, OSError) as e:
            # Log error in production, but return empty dict for now
            return {}
    
    def load_template_for_country(self, state_code=None):
        """
        Load template for this instance's country code.
        
        Args:
            state_code: Optional state/province code
            
        Returns:
            Dictionary with template data
        """
        return self.load_template(self.country_code, state_code)
    
    def initialize_from_template(self, state_code=None, merge_with_existing=False):
        """
        Initialize country_data_json from template file.
        
        Args:
            state_code: Optional state/province code
            merge_with_existing: If True, merge template with existing data; if False, replace
            
        Returns:
            True if template was loaded successfully, False otherwise
        """
        template_data = self.load_template_for_country(state_code)
        
        if not template_data:
            return False
        
        if merge_with_existing:
            # Merge template with existing data (existing data takes precedence)
            existing_data = self.get_country_data()
            merged_data = {**template_data, **existing_data}
            self.set_country_data(merged_data)
        else:
            # Replace with template data
            self.set_country_data(template_data)
        
        return True
    
    @classmethod
    def create_from_template(cls, fk_closure_id, country_code, state_code=None):
        """
        Create a new ClosureCountrySpecific instance initialized from template.
        
        Args:
            fk_closure_id: Foreign key to closure.id
            country_code: ISO 3166-1 alpha-2 country code
            state_code: Optional state/province code
            
        Returns:
            New ClosureCountrySpecific instance with template data loaded
        """
        instance = cls()
        instance.fk_closure_id = fk_closure_id
        instance.country_code = country_code.upper()
        instance.initialize_from_template(state_code, merge_with_existing=False)
        return instance

