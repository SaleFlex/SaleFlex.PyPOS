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

import uuid
import platform
import socket
from data_layer.model import Store, Country


def _get_mac_address():
    """Get MAC address of the system"""
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
        return mac
    except:
        return None


def _get_system_info():
    """Get basic system information"""
    try:
        system_info = {
            'os_version': f"{platform.system()} {platform.release()}",
            'hostname': socket.gethostname()
        }
        return system_info
    except:
        return {'os_version': None, 'hostname': None}


def _insert_default_store(session):
    """Insert default store if not exists and update system information"""
    system_info = _get_system_info()
    mac_address = _get_mac_address()
    
    # Generate a serial number based on system info (similar to C# GetDriveSerialNumber())
    serial_number = f"SF-{str(uuid.uuid4())[:8].upper()}"
    
    store_exists = session.query(Store).first()
    if not store_exists:
        # Get United Kingdom country ID (numeric code 826 corresponds to United Kingdom)
        United_Kingdom_country = session.query(Country).filter(Country.iso_alpha2 == 'GB').first()
        default_country_id = United_Kingdom_country.id if United_Kingdom_country else None
        
        default_store = Store(
            # Basic information
            name="SaleFlex POS",
            brand_name="SaleFlex",
            company_name="SaleFlex PyPOS",
            web_page_url="https://saleflex.com",
            description="Default POS Store",
            
            # Hardware and system information
            serial_number=serial_number,
            model="SaleFlex PyPOS v1.0",
            operating_system_version=system_info['os_version'],
            mac_address=mac_address,
            
            # Owner information (can be set later)
            owner_national_id_number=None,
            owner_tax_id_number=None,
            owner_mersis_id_number=None,
            owner_commercial_record_no=None,
            owner_registration_number=None,
            
            # Screen and display settings (defaults)
            cashier_screen_type="Standard",
            customer_screen_type="Standard",
            customer_display_type="None",
            customer_display_port=None,
            
            # Printer settings (defaults)
            receipt_printer_type="None",
            receipt_printer_port_name=None,
            invoice_printer_type="None",
            invoice_printer_port_name=None,
            
            # Scale settings (defaults)
            scale_type="None",
            scale_port_name=None,
            
            # Barcode reader settings (defaults)
            barcode_reader_port=None,
            
            # Server settings (defaults)
            server_ip1=None,
            server_port1=None,
            server_ip2=None,
            server_port2=None,
            
            # System settings
            force_to_work_online=False,  # Default to offline mode
            fk_default_country_id=default_country_id  # United Kingdom country UUID
        )
        
        session.add(default_store)
        print("✓ Default store added with POS configuration")
        print(f"  - Serial Number: {serial_number}")
        print(f"  - MAC Address: {mac_address}")
        print(f"  - OS Version: {system_info['os_version']}")
        print(f"  - Hostname: {system_info['hostname']}")
        print(f"  - Default Country: {'United Kingdom' if default_country_id else 'None'}")
    else:
        # Update existing store with current system information
        store_exists.serial_number = serial_number
        store_exists.mac_address = mac_address
        store_exists.operating_system_version = system_info['os_version']
        
        print("✓ Store system information updated")
        print(f"  - Serial Number: {serial_number}")
        print(f"  - MAC Address: {mac_address}")
        print(f"  - OS Version: {system_info['os_version']}")
        print(f"  - Hostname: {system_info['hostname']}")
