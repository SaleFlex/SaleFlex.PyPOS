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

from data_layer.model import Warehouse, Store, City, District


def _insert_warehouses(session, admin_cashier_id: str):
    """Insert default warehouses for UK store if not exists"""
    warehouse_exists = session.query(Warehouse).first()
    if not warehouse_exists:
        # Get required foreign key references
        default_store = session.query(Store).first()
        london_city = session.query(City).filter_by(code="GB-LND").first()
        
        # Get some London districts for different warehouse locations
        westminster_district = session.query(District).filter_by(code="LDN-WES").first()
        croydon_district = session.query(District).filter_by(code="LDN-CRO").first()
        barking_district = session.query(District).filter_by(code="LDN-BAD").first()
        
        if not default_store or not london_city:
            print("⚠ Required references not found. Cannot insert warehouses.")
            return

        # Define warehouse data for a UK retail store
        warehouses_data = [
            {
                "name": "Main Storage Warehouse",
                "code": "MAIN-001",
                "description": "Primary storage facility for bulk inventory",
                "warehouse_type": "MAIN",
                "address": "Unit 42, Industrial Park, Croydon, London CR0 2RJ",
                "district": croydon_district,
                "total_area": 2500.0,
                "usable_area": 2200.0,
                "height": 8.0,
                "max_capacity": 17600.0,
                "temperature_controlled": False,
                "requires_security_access": True,
                "access_code": "MAIN2025",
                "security_level": "HIGH",
                "is_receiving_enabled": True,
                "is_shipping_enabled": True,
                "is_cycle_count_enabled": True,
                "manager_name": "James Morrison",
                "contact_phone": "+44 20 7123 4567",
                "contact_email": "james.morrison@saleflex.com",
                "operating_hours": '{"mon-fri": "06:00-22:00", "sat": "08:00-18:00", "sun": "10:00-16:00"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": True,
                "high_value_items_area": True
            },
            {
                "name": "Store Backroom",
                "code": "BACK-001",
                "description": "Backroom storage for immediate store needs",
                "warehouse_type": "BACKROOM",
                "address": "123 High Street, Westminster, London SW1A 1AA",
                "district": westminster_district,
                "total_area": 150.0,
                "usable_area": 120.0,
                "height": 3.5,
                "max_capacity": 420.0,
                "temperature_controlled": False,
                "requires_security_access": True,
                "access_code": "BACK2025",
                "security_level": "MEDIUM",
                "is_receiving_enabled": True,
                "is_shipping_enabled": False,
                "is_cycle_count_enabled": True,
                "manager_name": "Sarah Johnson",
                "contact_phone": "+44 20 7123 4568",
                "contact_email": "sarah.johnson@saleflex.com",
                "operating_hours": '{"mon-sun": "06:00-00:00"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": False,
                "high_value_items_area": False
            },
            {
                "name": "Display Storage",
                "code": "DISP-001",
                "description": "Display area storage for shop floor items",
                "warehouse_type": "DISPLAY",
                "address": "123 High Street, Westminster, London SW1A 1AA",
                "district": westminster_district,
                "total_area": 200.0,
                "usable_area": 180.0,
                "height": 3.0,
                "max_capacity": 540.0,
                "temperature_controlled": False,
                "requires_security_access": False,
                "security_level": "LOW",
                "is_receiving_enabled": False,
                "is_shipping_enabled": False,
                "is_cycle_count_enabled": True,
                "manager_name": "Michael Thompson",
                "contact_phone": "+44 20 7123 4569",
                "contact_email": "michael.thompson@saleflex.com",
                "operating_hours": '{"mon-sat": "07:00-23:00", "sun": "10:00-22:00"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": False,
                "high_value_items_area": False
            },
            {
                "name": "Cold Storage Facility",
                "code": "COLD-001",
                "description": "Refrigerated storage for perishable goods",
                "warehouse_type": "COLD_STORAGE",
                "address": "Unit 15, Cold Storage Complex, Barking, London IG11 8DR",
                "district": barking_district,
                "total_area": 800.0,
                "usable_area": 700.0,
                "height": 4.5,
                "max_capacity": 3150.0,
                "temperature_controlled": True,
                "min_temperature": 2.0,
                "max_temperature": 8.0,
                "humidity_controlled": True,
                "min_humidity": 85.0,
                "max_humidity": 95.0,
                "requires_security_access": True,
                "access_code": "COLD2025",
                "security_level": "MEDIUM",
                "is_receiving_enabled": True,
                "is_shipping_enabled": True,
                "is_cycle_count_enabled": True,
                "manager_name": "Emma Wilson",
                "contact_phone": "+44 20 7123 4570",
                "contact_email": "emma.wilson@saleflex.com",
                "operating_hours": '{"mon-sun": "24/7"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": True,
                "high_value_items_area": False
            },
            {
                "name": "Security Storage",
                "code": "SEC-001",
                "description": "High-security storage for valuable items",
                "warehouse_type": "SECURITY",
                "address": "Secure Unit 5, Westminster Business Centre, London SW1A 1AA",
                "district": westminster_district,
                "total_area": 50.0,
                "usable_area": 40.0,
                "height": 2.5,
                "max_capacity": 100.0,
                "temperature_controlled": False,
                "requires_security_access": True,
                "access_code": "SEC2025",
                "security_level": "HIGH",
                "is_receiving_enabled": True,
                "is_shipping_enabled": True,
                "is_cycle_count_enabled": True,
                "manager_name": "David Brown",
                "contact_phone": "+44 20 7123 4571",
                "contact_email": "david.brown@saleflex.com",
                "operating_hours": '{"mon-fri": "08:00-18:00"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": False,
                "high_value_items_area": True
            },
            {
                "name": "Temporary Storage",
                "code": "TEMP-001",
                "description": "Temporary storage for returns and pending items",
                "warehouse_type": "TEMPORARY",
                "address": "123 High Street, Westminster, London SW1A 1AA",
                "district": westminster_district,
                "total_area": 75.0,
                "usable_area": 60.0,
                "height": 3.0,
                "max_capacity": 180.0,
                "temperature_controlled": False,
                "requires_security_access": False,
                "security_level": "LOW",
                "is_receiving_enabled": True,
                "is_shipping_enabled": True,
                "is_cycle_count_enabled": False,
                "manager_name": "Lisa Davis",
                "contact_phone": "+44 20 7123 4572",
                "contact_email": "lisa.davis@saleflex.com",
                "operating_hours": '{"mon-sat": "08:00-20:00"}',
                "hazardous_material_allowed": False,
                "fragile_items_area": False,
                "high_value_items_area": False
            }
        ]

        # Create warehouses
        for warehouse_data in warehouses_data:
            warehouse = Warehouse(
                name=warehouse_data["name"],
                code=warehouse_data["code"],
                warehouse_type=warehouse_data["warehouse_type"],
                fk_store_id=default_store.id
            )
            
            # Set all other properties
            warehouse.description = warehouse_data["description"]
            warehouse.address = warehouse_data["address"]
            warehouse.total_area = warehouse_data["total_area"]
            warehouse.usable_area = warehouse_data["usable_area"]
            warehouse.height = warehouse_data["height"]
            warehouse.max_capacity = warehouse_data["max_capacity"]
            warehouse.temperature_controlled = warehouse_data["temperature_controlled"]
            warehouse.requires_security_access = warehouse_data["requires_security_access"]
            warehouse.security_level = warehouse_data["security_level"]
            warehouse.is_receiving_enabled = warehouse_data["is_receiving_enabled"]
            warehouse.is_shipping_enabled = warehouse_data["is_shipping_enabled"]
            warehouse.is_cycle_count_enabled = warehouse_data["is_cycle_count_enabled"]
            warehouse.manager_name = warehouse_data["manager_name"]
            warehouse.contact_phone = warehouse_data["contact_phone"]
            warehouse.contact_email = warehouse_data["contact_email"]
            warehouse.operating_hours = warehouse_data["operating_hours"]
            warehouse.hazardous_material_allowed = warehouse_data["hazardous_material_allowed"]
            warehouse.fragile_items_area = warehouse_data["fragile_items_area"]
            warehouse.high_value_items_area = warehouse_data["high_value_items_area"]
            
            # Set optional temperature and humidity controls
            if warehouse_data.get("min_temperature"):
                warehouse.min_temperature = warehouse_data["min_temperature"]
            if warehouse_data.get("max_temperature"):
                warehouse.max_temperature = warehouse_data["max_temperature"]
            if warehouse_data.get("humidity_controlled"):
                warehouse.humidity_controlled = warehouse_data["humidity_controlled"]
            if warehouse_data.get("min_humidity"):
                warehouse.min_humidity = warehouse_data["min_humidity"]
            if warehouse_data.get("max_humidity"):
                warehouse.max_humidity = warehouse_data["max_humidity"]
            
            # Set access code if provided
            if warehouse_data.get("access_code"):
                warehouse.access_code = warehouse_data["access_code"]
            
            # Set foreign keys
            warehouse.fk_city_id = london_city.id
            if warehouse_data["district"]:
                warehouse.fk_district_id = warehouse_data["district"].id
            
            # Set audit fields
            warehouse.fk_cashier_create_id = admin_cashier_id
            warehouse.fk_cashier_update_id = admin_cashier_id
            
            session.add(warehouse)

        print("✓ UK Store warehouses added:")
        print("  - Main Storage Warehouse (Croydon)")
        print("  - Store Backroom (Westminster)")
        print("  - Display Storage (Westminster)")
        print("  - Cold Storage Facility (Barking)")
        print("  - Security Storage (Westminster)")
        print("  - Temporary Storage (Westminster)")
        print(f"  Total: {len(warehouses_data)} warehouses") 