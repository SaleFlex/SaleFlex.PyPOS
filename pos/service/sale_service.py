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

from decimal import Decimal
from typing import Optional, Dict, Any
from pos.service.vat_service import VatService


class SaleService:
    """
    Sale business logic service.
    
    This service contains the business logic for processing sales including:
    - Department sales
    - PLU code sales
    - PLU barcode sales
    
    All sale calculations and VAT computations are handled here, using
    the centralized VatService for VAT calculations.
    """
    
    @staticmethod
    def get_vat_rate_for_product(product, product_data: Dict[str, Any]) -> float:
        """
        Get VAT rate for a product based on its department.
        
        Args:
            product: Product object
            product_data: Product data cache dictionary
        
        Returns:
            float: VAT rate percentage (0.0 if not found)
        """
        if not product:
            return 0.0
        
        # Get department from product
        dept_main_group_id = product.fk_department_main_group_id
        if not dept_main_group_id:
            return 0.0
        
        # Get VAT rate from department
        dept_main_groups = product_data.get("DepartmentMainGroup", [])
        dept_main_group = next((d for d in dept_main_groups if d.id == dept_main_group_id), None)
        
        if dept_main_group and dept_main_group.fk_vat_id:
            vats = product_data.get("Vat", [])
            vat = next((v for v in vats if v.id == dept_main_group.fk_vat_id), None)
            if vat:
                return float(vat.rate)
        
        return 0.0
    
    @staticmethod
    def get_vat_rate_for_department(department, department_no: Optional[int], 
                                   product_data: Dict[str, Any]) -> tuple[float, Any]:
        """
        Get VAT rate for a department sale.
        
        Args:
            department: DepartmentMainGroup or DepartmentSubGroup object
            department_no: Department number (for sub groups > 99)
            product_data: Product data cache dictionary
        
        Returns:
            tuple: (vat_rate, dept_main_group) - VAT rate and main group object
        """
        from data_layer.model import DepartmentMainGroup
        from data_layer.model import DepartmentSubGroup
        
        dept_main_group = None
        dept_sub_group = None
        
        if isinstance(department, DepartmentMainGroup):
            dept_main_group = department
        elif isinstance(department, DepartmentSubGroup):
            dept_sub_group = department
            # Find main group from sub group
            # First try main_group_id if it exists
            if hasattr(department, 'main_group_id') and department.main_group_id:
                dept_main_groups = product_data.get("DepartmentMainGroup", [])
                dept_main_group = next((d for d in dept_main_groups if d.id == department.main_group_id), None)
            
            # If main_group_id didn't work, try to find by department_no logic
            if not dept_main_group and department_no:
                if department_no > 99:
                    # For sub groups > 99, extract first digit(s) to find main group
                    # For example: 101 -> main group 1, 201 -> main group 2
                    main_group_code = str(department_no)[0]  # First digit
                    dept_main_groups = product_data.get("DepartmentMainGroup", [])
                    dept_main_group = next((d for d in dept_main_groups if d.code == main_group_code), None)
                
                # If still not found, use first main group as fallback
                if not dept_main_group:
                    dept_main_groups = product_data.get("DepartmentMainGroup", [])
                    if dept_main_groups:
                        dept_main_group = dept_main_groups[0]  # Fallback to first main group
        
        if not dept_main_group:
            return (0.0, None)
        
        # Get VAT rate from department main group
        vat_rate = 0.0
        if dept_main_group.fk_vat_id:
            vats = product_data.get("Vat", [])
            vat = next((v for v in vats if v.id == dept_main_group.fk_vat_id), None)
            if vat:
                vat_rate = float(vat.rate)
        
        return (vat_rate, dept_main_group)
    
    @staticmethod
    def calculate_plu_sale(quantity: float, unit_price: float, product, 
                          product_data: Dict[str, Any], 
                          currency_sign: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate PLU sale (code or barcode) totals and VAT.
        
        Args:
            quantity: Quantity sold
            unit_price: Unit price
            product: Product object
            product_data: Product data cache dictionary
            currency_sign: Optional currency sign for VAT rounding
        
        Returns:
            dict: Dictionary containing:
                - total_price: Total price (quantity * unit_price)
                - vat_rate: VAT rate percentage
                - total_vat: Calculated VAT amount (rounded)
                - dept_main_group_id: Department main group ID
                - dept_sub_group_id: Department sub group ID
        """
        # Calculate total price
        total_price = float(quantity) * float(unit_price)
        
        # Get VAT rate
        vat_rate = SaleService.get_vat_rate_for_product(product, product_data)
        
        # Calculate VAT using VatService
        total_vat = VatService.calculate_vat(total_price, vat_rate, currency_sign, product_data)
        
        return {
            "total_price": total_price,
            "vat_rate": vat_rate,
            "total_vat": total_vat,
            "dept_main_group_id": product.fk_department_main_group_id if product else None,
            "dept_sub_group_id": product.fk_department_sub_group_id if product else None
        }
    
    @staticmethod
    def calculate_department_sale(quantity: float, unit_price: float, department,
                                  department_no: Optional[int],
                                  product_data: Dict[str, Any],
                                  currency_sign: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate department sale totals and VAT.
        
        Args:
            quantity: Quantity sold (usually 1.0 for department sales)
            unit_price: Unit price
            department: DepartmentMainGroup or DepartmentSubGroup object
            department_no: Department number (for sub groups > 99)
            product_data: Product data cache dictionary
            currency_sign: Optional currency sign for VAT rounding
        
        Returns:
            dict: Dictionary containing:
                - total_department: Total department amount
                - vat_rate: VAT rate percentage
                - total_department_vat: Calculated VAT amount (rounded)
                - dept_main_group: DepartmentMainGroup object
                - dept_sub_group: DepartmentSubGroup object or None
        """
        # Calculate total department amount
        total_department = float(quantity) * float(unit_price)
        
        # Get VAT rate and main group
        vat_rate, dept_main_group = SaleService.get_vat_rate_for_department(
            department, department_no, product_data
        )
        
        # Calculate VAT using VatService
        total_department_vat = VatService.calculate_vat(
            total_department, vat_rate, currency_sign, product_data
        )
        
        # Determine sub group
        from data_layer.model import DepartmentSubGroup
        dept_sub_group = None
        if isinstance(department, DepartmentSubGroup):
            dept_sub_group = department
        
        return {
            "total_department": total_department,
            "vat_rate": vat_rate,
            "total_department_vat": total_department_vat,
            "dept_main_group": dept_main_group,
            "dept_sub_group": dept_sub_group
        }
    
    @staticmethod
    def create_transaction_product_temp(head_id, line_no: int, product, 
                                        quantity: float, unit_price: float,
                                        total_price: float, vat_rate: float,
                                        total_vat: float,
                                        product_barcode=None):
        """
        Create a TransactionProductTemp record.
        
        Args:
            head_id: TransactionHeadTemp ID
            line_no: Line number
            product: Product object
            quantity: Quantity sold
            unit_price: Unit price
            total_price: Total price
            vat_rate: VAT rate percentage
            total_vat: Total VAT amount
            product_barcode: Optional ProductBarcode object
        
        Returns:
            TransactionProductTemp: Created transaction product temp record
        """
        from data_layer.model import TransactionProductTemp
        
        product_temp = TransactionProductTemp()
        product_temp.fk_transaction_head_id = head_id
        product_temp.line_no = line_no
        product_temp.fk_department_main_group_id = product.fk_department_main_group_id
        product_temp.fk_department_sub_group_id = product.fk_department_sub_group_id
        product_temp.fk_product_id = product.id
        product_temp.product_code = product.code
        product_temp.product_name = product.short_name if product.short_name else product.name
        product_temp.product_description = product.description
        product_temp.vat_rate = Decimal(str(vat_rate))
        product_temp.unit_price = Decimal(str(unit_price))
        product_temp.quantity = Decimal(str(quantity))
        product_temp.total_price = Decimal(str(total_price))
        product_temp.total_vat = Decimal(str(total_vat))
        
        # Set product_barcode_id if provided
        if product_barcode:
            product_temp.fk_product_barcode_id = product_barcode.id
        
        return product_temp
    
    @staticmethod
    def create_transaction_department_temp(head_id, line_no: int,
                                          dept_main_group, dept_sub_group,
                                          total_department: float, vat_rate: float,
                                          total_department_vat: float,
                                          department_no: Optional[int] = None,
                                          product_data: Optional[Dict[str, Any]] = None):
        """
        Create a TransactionDepartmentTemp record.
        
        Args:
            head_id: TransactionHeadTemp ID
            line_no: Line number
            dept_main_group: DepartmentMainGroup object
            dept_sub_group: Optional DepartmentSubGroup object
            total_department: Total department amount
            vat_rate: VAT rate percentage
            total_department_vat: Total department VAT amount
            department_no: Optional department number (for finding sub group)
            product_data: Optional product data cache dictionary
        
        Returns:
            TransactionDepartmentTemp: Created transaction department temp record
        """
        from data_layer.model import TransactionDepartmentTemp
        
        dept_temp = TransactionDepartmentTemp()
        dept_temp.fk_transaction_head_id = head_id
        dept_temp.line_no = line_no
        dept_temp.fk_department_main_group_id = dept_main_group.id
        dept_temp.vat_rate = Decimal(str(vat_rate))
        dept_temp.total_department = Decimal(str(total_department))
        dept_temp.total_department_vat = Decimal(str(total_department_vat))
        
        # Set fk_department_sub_group_id if department_no > 99 or if we have a sub group
        if dept_sub_group:
            dept_temp.fk_department_sub_group_id = dept_sub_group.id
        elif department_no and department_no > 99:
            # Find department_sub_group
            if product_data:
                dept_sub_groups = product_data.get("DepartmentSubGroup", [])
                found_sub_group = next((d for d in dept_sub_groups if d.code == str(department_no)), None)
                if found_sub_group:
                    dept_temp.fk_department_sub_group_id = found_sub_group.id
        
        return dept_temp
    
    @staticmethod
    def calculate_document_totals(document_data: Dict[str, Any]) -> Dict[str, Decimal]:
        """
        Calculate total amounts for a document from all products and departments.
        
        Args:
            document_data: Document data dictionary containing products and departments
        
        Returns:
            dict: Dictionary containing:
                - total_amount: Sum of all product and department totals
                - total_vat_amount: Sum of all VAT amounts
        """
        total_amount = Decimal('0')
        total_vat_amount = Decimal('0')
        
        # Sum products
        for prod in document_data.get("products", []):
            if hasattr(prod, 'total_price'):
                total_amount += Decimal(str(prod.total_price))
            if hasattr(prod, 'total_vat'):
                total_vat_amount += Decimal(str(prod.total_vat))
        
        # Sum departments
        for dept in document_data.get("departments", []):
            if hasattr(dept, 'total_department'):
                total_amount += Decimal(str(dept.total_department))
            if hasattr(dept, 'total_department_vat'):
                total_vat_amount += Decimal(str(dept.total_department_vat))
        
        return {
            "total_amount": total_amount,
            "total_vat_amount": total_vat_amount
        }

