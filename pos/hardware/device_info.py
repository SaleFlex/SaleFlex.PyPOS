"""
SaleFlex.PyPOS - Hardware Device Information

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

import platform
import uuid
import hashlib
import subprocess
import re


def get_mac_address():
    """Get MAC address of the primary network interface
    
    Returns:
        str: MAC address in format XX:XX:XX:XX:XX:XX or None if not found
    """
    try:
        # Get MAC address using uuid.getnode()
        mac_int = uuid.getnode()
        if mac_int != uuid.getnode():  # Check if MAC is valid (not random)
            mac = ':'.join(['{:02x}'.format((mac_int >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
            return mac.upper()
        
        # Fallback: Try to get MAC from network interfaces
        if platform.system() == "Windows":
            try:
                result = subprocess.run(['getmac', '/fo', 'csv', '/nh'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line and ',' in line:
                            mac = line.split(',')[0].strip().replace('-', ':')
                            if mac and mac != 'N/A':
                                return mac.upper()
            except:
                pass
        else:
            # Linux/Mac
            try:
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extract MAC address from output
                    match = re.search(r'([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', 
                                    result.stdout, re.IGNORECASE)
                    if match:
                        return match.group(1).upper()
            except:
                pass
        
        return None
    except Exception:
        return None


def get_disk_serial_number():
    """Get disk serial number
    
    Returns:
        str: Disk serial number or None if not found
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            try:
                # Use wmic command to get disk serial number
                result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and line.upper() != 'SERIALNUMBER':
                            # Remove whitespace and return first valid serial
                            serial = ''.join(line.split())
                            if serial:
                                return serial
            except:
                pass
            
            # Alternative: Use powershell
            try:
                result = subprocess.run(['powershell', '-Command', 
                                       'Get-WmiObject Win32_PhysicalMedia | Select-Object -ExpandProperty SerialNumber'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    serial = result.stdout.strip()
                    if serial and serial.upper() != 'N.A.':
                        return serial.strip()
            except:
                pass
                
        elif system == "Linux":
            try:
                # Try to get disk serial from /dev/disk/by-id/
                result = subprocess.run(['lsblk', '-o', 'SERIAL', '-n'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        serial = line.strip()
                        if serial:
                            return serial
            except:
                pass
                
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(['system_profiler', 'SPStorageDataType'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extract serial number from output
                    match = re.search(r'Serial Number:\s*([^\n]+)', result.stdout)
                    if match:
                        return match.group(1).strip()
            except:
                pass
        
        return None
    except Exception:
        return None


def get_device_serial_number():
    """Generate a unique device serial number by combining MAC address and disk serial
    
    Returns:
        str: Unique device serial number
    """
    mac = get_mac_address()
    disk_serial = get_disk_serial_number()
    
    # Combine MAC and disk serial to create unique identifier
    combined = ""
    if mac:
        combined += mac.replace(':', '')
    if disk_serial:
        combined += disk_serial.strip().replace(' ', '').replace('-', '')
    
    if not combined:
        # Fallback: Use UUID if we can't get hardware info
        combined = str(uuid.uuid4()).replace('-', '')
    
    # Create a hash to ensure consistent length and uniqueness
    hash_obj = hashlib.md5(combined.encode())
    serial_hash = hash_obj.hexdigest().upper()
    
    # Format as SF-XXXXXXXX (SaleFlex prefix + 8 char hash)
    return f"SF-{serial_hash[:8]}"


def get_operation_system():
    """Get operating system information
    
    Returns:
        str: Operating system version string (e.g., "Windows 10", "Ubuntu 22.10")
    """
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        
        if system == "Windows":
            return f"Windows {release}"
        elif system == "Linux":
            # Try to get distribution name
            try:
                result = subprocess.run(['lsb_release', '-d'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    distro = result.stdout.split(':')[1].strip()
                    return distro
            except:
                pass
            return f"Linux {release}"
        elif system == "Darwin":
            return f"macOS {release}"
        else:
            return f"{system} {release}"
    except Exception:
        return platform.platform()

