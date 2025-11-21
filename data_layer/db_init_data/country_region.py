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

from data_layer.model.definition.country_region import CountryRegion
from data_layer.model.definition.country import Country


def _insert_country_regions(session, admin_cashier_id):
    """
    Insert country regions (states, provinces, special economic zones) if not exists.
    
    This function populates regions for countries that have regional variations:
    - US States (California, New York, Texas, etc.)
    - Canadian Provinces (Ontario, British Columbia, Quebec, etc.)
    - Special Economic Zones (Free trade zones, etc.)
    
    Args:
        session: Database session
        admin_cashier_id: Admin cashier ID for audit fields
    """
    print("[DEBUG] _insert_country_regions called")
    
    # Check if regions already exist
    region_exists = session.query(CountryRegion).first()
    if region_exists:
        print("✓ Country regions already exist")
        return
    
    print("[DEBUG] Creating country regions...")
    
    # Get countries
    usa = session.query(Country).filter_by(code='US').first()
    canada = session.query(Country).filter_by(code='CA').first()
    turkey = session.query(Country).filter_by(code='TR').first()
    germany = session.query(Country).filter_by(code='DE').first()
    france = session.query(Country).filter_by(code='FR').first()
    uk = session.query(Country).filter_by(code='GB').first()
    
    regions_data = []
    
    # United States States
    if usa:
        us_states = [
            {"code": "AL", "name": "Alabama", "iso": "US-AL", "type": "state", "order": "01"},
            {"code": "AK", "name": "Alaska", "iso": "US-AK", "type": "state", "order": "02"},
            {"code": "AZ", "name": "Arizona", "iso": "US-AZ", "type": "state", "order": "03"},
            {"code": "AR", "name": "Arkansas", "iso": "US-AR", "type": "state", "order": "04"},
            {"code": "CA", "name": "California", "iso": "US-CA", "type": "state", "order": "05", "special": True},
            {"code": "CO", "name": "Colorado", "iso": "US-CO", "type": "state", "order": "06"},
            {"code": "CT", "name": "Connecticut", "iso": "US-CT", "type": "state", "order": "07"},
            {"code": "DE", "name": "Delaware", "iso": "US-DE", "type": "state", "order": "08"},
            {"code": "FL", "name": "Florida", "iso": "US-FL", "type": "state", "order": "09"},
            {"code": "GA", "name": "Georgia", "iso": "US-GA", "type": "state", "order": "10"},
            {"code": "HI", "name": "Hawaii", "iso": "US-HI", "type": "state", "order": "11"},
            {"code": "ID", "name": "Idaho", "iso": "US-ID", "type": "state", "order": "12"},
            {"code": "IL", "name": "Illinois", "iso": "US-IL", "type": "state", "order": "13"},
            {"code": "IN", "name": "Indiana", "iso": "US-IN", "type": "state", "order": "14"},
            {"code": "IA", "name": "Iowa", "iso": "US-IA", "type": "state", "order": "15"},
            {"code": "KS", "name": "Kansas", "iso": "US-KS", "type": "state", "order": "16"},
            {"code": "KY", "name": "Kentucky", "iso": "US-KY", "type": "state", "order": "17"},
            {"code": "LA", "name": "Louisiana", "iso": "US-LA", "type": "state", "order": "18"},
            {"code": "ME", "name": "Maine", "iso": "US-ME", "type": "state", "order": "19"},
            {"code": "MD", "name": "Maryland", "iso": "US-MD", "type": "state", "order": "20"},
            {"code": "MA", "name": "Massachusetts", "iso": "US-MA", "type": "state", "order": "21"},
            {"code": "MI", "name": "Michigan", "iso": "US-MI", "type": "state", "order": "22"},
            {"code": "MN", "name": "Minnesota", "iso": "US-MN", "type": "state", "order": "23"},
            {"code": "MS", "name": "Mississippi", "iso": "US-MS", "type": "state", "order": "24"},
            {"code": "MO", "name": "Missouri", "iso": "US-MO", "type": "state", "order": "25"},
            {"code": "MT", "name": "Montana", "iso": "US-MT", "type": "state", "order": "26"},
            {"code": "NE", "name": "Nebraska", "iso": "US-NE", "type": "state", "order": "27"},
            {"code": "NV", "name": "Nevada", "iso": "US-NV", "type": "state", "order": "28"},
            {"code": "NH", "name": "New Hampshire", "iso": "US-NH", "type": "state", "order": "29"},
            {"code": "NJ", "name": "New Jersey", "iso": "US-NJ", "type": "state", "order": "30"},
            {"code": "NM", "name": "New Mexico", "iso": "US-NM", "type": "state", "order": "31"},
            {"code": "NY", "name": "New York", "iso": "US-NY", "type": "state", "order": "32", "special": True},
            {"code": "NC", "name": "North Carolina", "iso": "US-NC", "type": "state", "order": "33"},
            {"code": "ND", "name": "North Dakota", "iso": "US-ND", "type": "state", "order": "34"},
            {"code": "OH", "name": "Ohio", "iso": "US-OH", "type": "state", "order": "35"},
            {"code": "OK", "name": "Oklahoma", "iso": "US-OK", "type": "state", "order": "36"},
            {"code": "OR", "name": "Oregon", "iso": "US-OR", "type": "state", "order": "37"},
            {"code": "PA", "name": "Pennsylvania", "iso": "US-PA", "type": "state", "order": "38"},
            {"code": "RI", "name": "Rhode Island", "iso": "US-RI", "type": "state", "order": "39"},
            {"code": "SC", "name": "South Carolina", "iso": "US-SC", "type": "state", "order": "40"},
            {"code": "SD", "name": "South Dakota", "iso": "US-SD", "type": "state", "order": "41"},
            {"code": "TN", "name": "Tennessee", "iso": "US-TN", "type": "state", "order": "42"},
            {"code": "TX", "name": "Texas", "iso": "US-TX", "type": "state", "order": "43", "special": True},
            {"code": "UT", "name": "Utah", "iso": "US-UT", "type": "state", "order": "44"},
            {"code": "VT", "name": "Vermont", "iso": "US-VT", "type": "state", "order": "45"},
            {"code": "VA", "name": "Virginia", "iso": "US-VA", "type": "state", "order": "46"},
            {"code": "WA", "name": "Washington", "iso": "US-WA", "type": "state", "order": "47"},
            {"code": "WV", "name": "West Virginia", "iso": "US-WV", "type": "state", "order": "48"},
            {"code": "WI", "name": "Wisconsin", "iso": "US-WI", "type": "state", "order": "49"},
            {"code": "WY", "name": "Wyoming", "iso": "US-WY", "type": "state", "order": "50"},
            {"code": "DC", "name": "District of Columbia", "iso": "US-DC", "type": "district", "order": "51"},
        ]
        
        for state in us_states:
            regions_data.append({
                "fk_country_id": usa.id,
                "region_code": state["code"],
                "region_name": state["name"],
                "iso_code": state["iso"],
                "region_type": state["type"],
                "has_special_requirements": state.get("special", False),
                "display_order": state["order"],
                "fk_cashier_create_id": admin_cashier_id
            })
    
    # Canadian Provinces
    if canada:
        ca_provinces = [
            {"code": "AB", "name": "Alberta", "iso": "CA-AB", "type": "province", "order": "01"},
            {"code": "BC", "name": "British Columbia", "iso": "CA-BC", "type": "province", "order": "02"},
            {"code": "MB", "name": "Manitoba", "iso": "CA-MB", "type": "province", "order": "03"},
            {"code": "NB", "name": "New Brunswick", "iso": "CA-NB", "type": "province", "order": "04"},
            {"code": "NL", "name": "Newfoundland and Labrador", "iso": "CA-NL", "type": "province", "order": "05"},
            {"code": "NS", "name": "Nova Scotia", "iso": "CA-NS", "type": "province", "order": "06"},
            {"code": "ON", "name": "Ontario", "iso": "CA-ON", "type": "province", "order": "07"},
            {"code": "PE", "name": "Prince Edward Island", "iso": "CA-PE", "type": "province", "order": "08"},
            {"code": "QC", "name": "Quebec", "iso": "CA-QC", "type": "province", "order": "09"},
            {"code": "SK", "name": "Saskatchewan", "iso": "CA-SK", "type": "province", "order": "10"},
            {"code": "NT", "name": "Northwest Territories", "iso": "CA-NT", "type": "territory", "order": "11"},
            {"code": "NU", "name": "Nunavut", "iso": "CA-NU", "type": "territory", "order": "12"},
            {"code": "YT", "name": "Yukon", "iso": "CA-YT", "type": "territory", "order": "13"},
        ]
        
        for province in ca_provinces:
            regions_data.append({
                "fk_country_id": canada.id,
                "region_code": province["code"],
                "region_name": province["name"],
                "iso_code": province["iso"],
                "region_type": province["type"],
                "has_special_requirements": False,
                "display_order": province["order"],
                "fk_cashier_create_id": admin_cashier_id
            })
    
    # German States (Länder)
    if germany:
        de_states = [
            {"code": "BW", "name": "Baden-Württemberg", "iso": "DE-BW", "type": "state", "order": "01"},
            {"code": "BY", "name": "Bavaria", "iso": "DE-BY", "type": "state", "order": "02"},
            {"code": "BE", "name": "Berlin", "iso": "DE-BE", "type": "state", "order": "03"},
            {"code": "BB", "name": "Brandenburg", "iso": "DE-BB", "type": "state", "order": "04"},
            {"code": "HB", "name": "Bremen", "iso": "DE-HB", "type": "state", "order": "05"},
            {"code": "HH", "name": "Hamburg", "iso": "DE-HH", "type": "state", "order": "06"},
            {"code": "HE", "name": "Hesse", "iso": "DE-HE", "type": "state", "order": "07"},
            {"code": "MV", "name": "Mecklenburg-Vorpommern", "iso": "DE-MV", "type": "state", "order": "08"},
            {"code": "NI", "name": "Lower Saxony", "iso": "DE-NI", "type": "state", "order": "09"},
            {"code": "NW", "name": "North Rhine-Westphalia", "iso": "DE-NW", "type": "state", "order": "10"},
            {"code": "RP", "name": "Rhineland-Palatinate", "iso": "DE-RP", "type": "state", "order": "11"},
            {"code": "SL", "name": "Saarland", "iso": "DE-SL", "type": "state", "order": "12"},
            {"code": "SN", "name": "Saxony", "iso": "DE-SN", "type": "state", "order": "13"},
            {"code": "ST", "name": "Saxony-Anhalt", "iso": "DE-ST", "type": "state", "order": "14"},
            {"code": "SH", "name": "Schleswig-Holstein", "iso": "DE-SH", "type": "state", "order": "15"},
            {"code": "TH", "name": "Thuringia", "iso": "DE-TH", "type": "state", "order": "16"},
        ]
        
        for state in de_states:
            regions_data.append({
                "fk_country_id": germany.id,
                "region_code": state["code"],
                "region_name": state["name"],
                "iso_code": state["iso"],
                "region_type": state["type"],
                "has_special_requirements": False,
                "display_order": state["order"],
                "fk_cashier_create_id": admin_cashier_id
            })
    
    # French Regions (major regions)
    if france:
        fr_regions = [
            {"code": "ARA", "name": "Auvergne-Rhône-Alpes", "iso": "FR-ARA", "type": "region", "order": "01"},
            {"code": "BFC", "name": "Bourgogne-Franche-Comté", "iso": "FR-BFC", "type": "region", "order": "02"},
            {"code": "BRE", "name": "Brittany", "iso": "FR-BRE", "type": "region", "order": "03"},
            {"code": "CVL", "name": "Centre-Val de Loire", "iso": "FR-CVL", "type": "region", "order": "04"},
            {"code": "COR", "name": "Corsica", "iso": "FR-COR", "type": "region", "order": "05"},
            {"code": "GES", "name": "Grand Est", "iso": "FR-GES", "type": "region", "order": "06"},
            {"code": "HDF", "name": "Hauts-de-France", "iso": "FR-HDF", "type": "region", "order": "07"},
            {"code": "IDF", "name": "Île-de-France", "iso": "FR-IDF", "type": "region", "order": "08"},
            {"code": "NOR", "name": "Normandy", "iso": "FR-NOR", "type": "region", "order": "09"},
            {"code": "NAQ", "name": "Nouvelle-Aquitaine", "iso": "FR-NAQ", "type": "region", "order": "10"},
            {"code": "OCC", "name": "Occitanie", "iso": "FR-OCC", "type": "region", "order": "11"},
            {"code": "PDL", "name": "Pays de la Loire", "iso": "FR-PDL", "type": "region", "order": "12"},
            {"code": "PAC", "name": "Provence-Alpes-Côte d'Azur", "iso": "FR-PAC", "type": "region", "order": "13"},
        ]
        
        for region in fr_regions:
            regions_data.append({
                "fk_country_id": france.id,
                "region_code": region["code"],
                "region_name": region["name"],
                "iso_code": region["iso"],
                "region_type": region["type"],
                "has_special_requirements": False,
                "display_order": region["order"],
                "fk_cashier_create_id": admin_cashier_id
            })
    
    # Create regions
    for region_data in regions_data:
        region = CountryRegion(
            fk_country_id=region_data["fk_country_id"],
            region_code=region_data["region_code"],
            region_name=region_data["region_name"],
            iso_code=region_data["iso_code"],
            region_type=region_data["region_type"],
            has_special_requirements=region_data["has_special_requirements"],
            display_order=region_data["display_order"],
            fk_cashier_create_id=region_data["fk_cashier_create_id"]
        )
        session.add(region)
    
    session.commit()
    print(f"✓ Inserted {len(regions_data)} country regions")

