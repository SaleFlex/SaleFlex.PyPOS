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
    
    @staticmethod
    def ensure_customer_for_head(head, cashier_data=None):
        """
        Ensure that TransactionHeadTemp has a valid fk_customer_id.
        If not set, finds or creates a default walk-in customer.
        
        Args:
            head: TransactionHeadTemp instance
            cashier_data: Optional Cashier object for creating default customer
        
        Returns:
            bool: True if customer is set, False otherwise
        """
        try:
            if head.fk_customer_id:
                return True
            
            from data_layer.model import Customer
            from data_layer.engine import Engine
            
            # Try to find or create default customer
            with Engine().get_session() as session:
                walk_in_customer = session.query(Customer).filter(
                    Customer.name.ilike("%walk-in%") | Customer.name.ilike("%anonymous%"),
                    Customer.is_deleted == False
                ).first()
                
                if walk_in_customer:
                    head.fk_customer_id = walk_in_customer.id
                    return True
                
                first_customer = session.query(Customer).filter(
                    Customer.is_deleted == False
                ).first()
                
                if first_customer:
                    head.fk_customer_id = first_customer.id
                    return True
                
                # Create default customer
                default_customer = Customer(
                    name="Walk-in",
                    last_name="Customer",
                    description="Default walk-in customer for POS transactions"
                )
                if cashier_data:
                    default_customer.fk_cashier_create_id = cashier_data.id
                    default_customer.fk_cashier_update_id = cashier_data.id
                default_customer.create()
                head.fk_customer_id = default_customer.id
                return True
                
        except Exception as e:
            print(f"[SaleService.ensure_customer_for_head] Error ensuring customer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def update_document_head_for_sale(head, current_currency=None, closure=None):
        """
        Update TransactionHeadTemp fields for a sale operation.
        
        Args:
            head: TransactionHeadTemp instance
            current_currency: Optional current currency sign (e.g., "GBP")
            closure: Optional closure dictionary containing closure object
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            from datetime import datetime
            from data_layer.model.definition.transaction_status import TransactionStatus
            
            # Set transaction_date_time if empty
            if not head.transaction_date_time:
                head.transaction_date_time = datetime.now()
            
            # Update transaction_status from DRAFT to ACTIVE if still DRAFT
            if head.transaction_status == TransactionStatus.DRAFT.value:
                head.transaction_status = TransactionStatus.ACTIVE.value
            
            # Get closure_number from closure
            if closure and closure.get("closure"):
                closure_obj = closure["closure"]
                if closure_obj and closure_obj.closure_number:
                    head.closure_number = closure_obj.closure_number
            
            # Set base_currency from current_currency
            if current_currency:
                head.base_currency = current_currency
            
            # Set order_source and order_channel
            head.order_source = "in_store"
            head.order_channel = "cashier"
            
            return True
            
        except Exception as e:
            print(f"[SaleService.update_document_head_for_sale] Error updating head: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def add_sale_to_document(document_data: Dict[str, Any], sale_type: str,
                            product=None, department=None, quantity: float = 1.0,
                            unit_price: float = 0.0, product_barcode=None,
                            department_no=None, line_no=None,
                            product_data: Optional[Dict[str, Any]] = None,
                            current_currency: Optional[str] = None,
                            closure: Optional[Dict[str, Any]] = None,
                            cashier_data=None) -> bool:
        """
        Add a sale (PLU or DEPARTMENT) to document_data.
        
        This method handles the complete process of adding a sale:
        1. Updates TransactionHeadTemp fields (customer, dates, status, etc.)
        2. Creates TransactionProductTemp or TransactionDepartmentTemp
        3. Adds to document_data
        4. Saves the temp model to database
        5. Updates document totals
        
        Args:
            document_data: Document data dictionary containing head, products, departments
            sale_type: "PLU_CODE", "PLU_BARCODE", or "DEPARTMENT"
            product: Product object (for PLU sales)
            department: DepartmentMainGroup or DepartmentSubGroup object (for department sales)
            quantity: Quantity sold
            unit_price: Unit price
            product_barcode: ProductBarcode object (for PLU_BARCODE sales)
            department_no: Department number (for department sales)
            line_no: Line number in sale list (row number)
            product_data: Product data cache dictionary
            current_currency: Current currency sign (e.g., "GBP")
            closure: Closure dictionary containing closure object
            cashier_data: Cashier object for customer creation
        
        Returns:
            bool: True if sale added successfully, False otherwise
        """
        try:
            from data_layer.auto_save import AutoSaveModel
            
            if not document_data or not document_data.get("head"):
                print("[SaleService.add_sale_to_document] No document_data or head found")
                return False
            
            head = document_data["head"]
            
            # Unwrap if it's an AutoSaveModel
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()
            
            # Ensure customer is set
            if not SaleService.ensure_customer_for_head(head, cashier_data):
                print("[SaleService.add_sale_to_document] Failed to ensure customer")
                return False
            
            # Update document head fields
            if not SaleService.update_document_head_for_sale(head, current_currency, closure):
                print("[SaleService.add_sale_to_document] Failed to update head")
                return False
            
            # Calculate line_no if not provided
            if line_no is None:
                line_no = len(document_data.get("products", [])) + len(document_data.get("departments", [])) + 1
            
            # Process sale based on type
            if sale_type in ["PLU_CODE", "PLU_BARCODE"]:
                # PLU sale - create TransactionProductTemp
                if not product:
                    print("[SaleService.add_sale_to_document] Product required for PLU sale")
                    return False
                
                if not product_data:
                    print("[SaleService.add_sale_to_document] product_data required for PLU sale")
                    return False
                
                # Calculate sale using SaleService
                sale_calc = SaleService.calculate_plu_sale(
                    quantity=quantity,
                    unit_price=unit_price,
                    product=product,
                    product_data=product_data,
                    currency_sign=current_currency
                )
                
                # Create TransactionProductTemp using SaleService
                product_temp = SaleService.create_transaction_product_temp(
                    head_id=head.id,
                    line_no=line_no,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=sale_calc["total_price"],
                    vat_rate=sale_calc["vat_rate"],
                    total_vat=sale_calc["total_vat"],
                    product_barcode=product_barcode if sale_type == "PLU_BARCODE" else None
                )
                
                # Add to document_data
                if "products" not in document_data:
                    document_data["products"] = []
                document_data["products"].append(product_temp)
                
                # Manually save the product temp model to database
                # AutoSaveDict doesn't trigger save on list.append(), so we need to save manually
                try:
                    product_temp.save()
                    print(f"[SaleService.add_sale_to_document] ✓ Saved TransactionProductTemp to database")
                except Exception as e:
                    print(f"[SaleService.add_sale_to_document] Error saving TransactionProductTemp: {e}")
                    import traceback
                    traceback.print_exc()
                
            elif sale_type == "DEPARTMENT":
                # Department sale - create TransactionDepartmentTemp
                if not department:
                    print("[SaleService.add_sale_to_document] Department required for department sale")
                    return False
                
                if not product_data:
                    print("[SaleService.add_sale_to_document] product_data required for department sale")
                    return False
                
                # Calculate department sale using SaleService
                dept_calc = SaleService.calculate_department_sale(
                    quantity=quantity,
                    unit_price=unit_price,
                    department=department,
                    department_no=department_no,
                    product_data=product_data,
                    currency_sign=current_currency
                )
                
                if not dept_calc["dept_main_group"]:
                    print("[SaleService.add_sale_to_document] Could not determine department main group")
                    return False
                
                # Create TransactionDepartmentTemp using SaleService
                dept_temp = SaleService.create_transaction_department_temp(
                    head_id=head.id,
                    line_no=line_no,
                    dept_main_group=dept_calc["dept_main_group"],
                    dept_sub_group=dept_calc["dept_sub_group"],
                    total_department=dept_calc["total_department"],
                    vat_rate=dept_calc["vat_rate"],
                    total_department_vat=dept_calc["total_department_vat"],
                    department_no=department_no,
                    product_data=product_data
                )
                
                # Add to document_data
                if "departments" not in document_data:
                    document_data["departments"] = []
                document_data["departments"].append(dept_temp)
                
                # Manually save the department temp model to database
                # AutoSaveDict doesn't trigger save on list.append(), so we need to save manually
                try:
                    dept_temp.save()
                    print(f"[SaleService.add_sale_to_document] ✓ Saved TransactionDepartmentTemp to database")
                except Exception as e:
                    print(f"[SaleService.add_sale_to_document] Error saving TransactionDepartmentTemp: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[SaleService.add_sale_to_document] Invalid sale_type: {sale_type}")
                return False
            
            # Update TransactionHeadTemp totals using SaleService
            totals = SaleService.calculate_document_totals(document_data)
            head.total_amount = totals["total_amount"]
            head.total_vat_amount = totals["total_vat_amount"]
            
            print(f"[SaleService.add_sale_to_document] ✓ Added {sale_type} sale to document")
            return True
            
        except Exception as e:
            print(f"[SaleService.add_sale_to_document] Error adding sale to document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def update_sale_list_from_document(sale_list, document_data: Dict[str, Any], 
                                       pos_data: Optional[Dict[str, Any]] = None):
        """
        Update sale_list control with products and departments from document_data.
        Items are added in line_no order.
        
        Args:
            sale_list: SaleList control instance
            document_data: Dictionary containing transaction temp models
            pos_data: Optional POS data cache dictionary (for department names)
        """
        try:
            from data_layer.auto_save import AutoSaveModel
            
            # Clear existing items
            sale_list.clear_products()
            
            # Get products and departments
            products = document_data.get("products", [])
            departments = document_data.get("departments", [])
            discounts = document_data.get("discounts", [])
            
            # Create a combined list with line_no for sorting
            items_to_add = []
            
            # Add products
            for prod in products:
                if isinstance(prod, AutoSaveModel):
                    prod = prod.unwrap()
                
                # Skip canceled products
                if hasattr(prod, 'is_cancel') and prod.is_cancel:
                    continue
                
                items_to_add.append({
                    'type': 'product',
                    'line_no': prod.line_no,
                    'data': prod
                })
            
            # Add departments
            for dept in departments:
                if isinstance(dept, AutoSaveModel):
                    dept = dept.unwrap()
                
                # Skip canceled departments
                if hasattr(dept, 'is_cancel') and dept.is_cancel:
                    continue
                
                items_to_add.append({
                    'type': 'department',
                    'line_no': dept.line_no,
                    'data': dept
                })
            
            # Sort by line_no
            items_to_add.sort(key=lambda x: x['line_no'])
            
            # Add items to sale_list in order
            for item in items_to_add:
                if item['type'] == 'product':
                    prod = item['data']
                    # Create SalesData object
                    from user_interface.control.sale_list.sale_list import SalesData
                    sales_data = SalesData()
                    sales_data.reference_id = str(prod.id) if hasattr(prod, 'id') else 0
                    sales_data.transaction_type = "PLU"
                    sales_data.transaction = "Sale"
                    sales_data.name_of_product = prod.product_name or ""
                    sales_data.barcode = ""
                    sales_data.plu_no = prod.product_code or ""
                    sales_data.department_no = 0
                    sales_data.id = str(prod.fk_product_id) if hasattr(prod, 'fk_product_id') and prod.fk_product_id else 0
                    sales_data.quantity = float(prod.quantity) if hasattr(prod, 'quantity') else 0.0
                    sales_data.unit_quantity = str(sales_data.quantity)
                    sales_data.unit = 1
                    sales_data.price = float(prod.unit_price) if hasattr(prod, 'unit_price') else 0.0
                    sales_data.total_amount = float(prod.total_price) if hasattr(prod, 'total_price') else 0.0
                    sales_data.is_canceled = False
                    
                    sale_list.add_sale_with_data(sales_data)
                    
                elif item['type'] == 'department':
                    dept = item['data']
                    # For departments, we need to get department name from pos_data
                    dept_name = "Department Sale"
                    if pos_data:
                        dept_main_groups = pos_data.get("DepartmentMainGroup", [])
                        for dmg in dept_main_groups:
                            if dmg.id == dept.fk_department_main_group_id:
                                dept_name = dmg.name or "Department Sale"
                                break
                    
                    # Create SalesData object
                    from user_interface.control.sale_list.sale_list import SalesData
                    sales_data = SalesData()
                    sales_data.reference_id = str(dept.id) if hasattr(dept, 'id') else 0
                    sales_data.transaction_type = "DEPARTMENT"
                    sales_data.transaction = "Sale"
                    sales_data.name_of_product = dept_name
                    sales_data.barcode = ""
                    sales_data.plu_no = ""
                    sales_data.department_no = 0
                    sales_data.id = 0
                    sales_data.quantity = 1.0
                    sales_data.unit_quantity = "1"
                    sales_data.unit = 1
                    sales_data.price = float(dept.total_department) if hasattr(dept, 'total_department') else 0.0
                    sales_data.total_amount = float(dept.total_department) if hasattr(dept, 'total_department') else 0.0
                    sales_data.is_canceled = False
                    
                    sale_list.add_sale_with_data(sales_data)
            
            # Add discounts if any
            for disc in discounts:
                if isinstance(disc, AutoSaveModel):
                    disc = disc.unwrap()
                
                # Skip canceled discounts
                if hasattr(disc, 'is_cancel') and disc.is_cancel:
                    continue
                
                discount_amount = float(disc.discount_amount) if hasattr(disc, 'discount_amount') else 0.0
                if discount_amount > 0:
                    # Find associated product name if available
                    product_name = ""
                    if disc.fk_transaction_product_id:
                        for prod in products:
                            if isinstance(prod, AutoSaveModel):
                                prod = prod.unwrap()
                            if prod.id == disc.fk_transaction_product_id:
                                product_name = prod.product_name or ""
                                break
                    
                    if disc.discount_rate:
                        # Percentage discount
                        discount_rate = float(disc.discount_rate) if hasattr(disc, 'discount_rate') else 0.0
                        sale_list.add_discount_by_percent_line(discount_rate, discount_amount, product_name)
                    else:
                        # Amount discount
                        sale_list.add_discount_by_amount_line(discount_amount, product_name)
            
            print(f"[SaleService.update_sale_list] Added {len(items_to_add)} items to sale_list")
            
        except Exception as e:
            print(f"[SaleService.update_sale_list] Error updating sale_list: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def update_amount_table_from_document(amount_table, head):
        """
        Update amount_table control with totals from TransactionHeadTemp.
        
        Updates:
        - Sales Amount: total_amount from head
        - Discount Amount: total_discount_amount from head
        - Net Amount: Sales Amount - Discount Amount (calculated automatically)
        - Payment Amount: total_payment_amount from head
        - Balance: Net Amount - Payment Amount (calculated automatically)
        
        Args:
            amount_table: AmountTable control instance
            head: TransactionHeadTemp instance (may be wrapped in AutoSaveModel)
        """
        try:
            from decimal import Decimal
            from data_layer.auto_save import AutoSaveModel
            
            # Unwrap if it's an AutoSaveModel
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()
            
            # Get totals from head (from document_data)
            total_amount = Decimal(str(head.total_amount)) if hasattr(head, 'total_amount') and head.total_amount else Decimal('0')
            discount_amount = Decimal(str(head.total_discount_amount)) if hasattr(head, 'total_discount_amount') and head.total_discount_amount else Decimal('0')
            payment_amount = Decimal(str(head.total_payment_amount)) if hasattr(head, 'total_payment_amount') and head.total_payment_amount else Decimal('0')
            
            # Set values in correct order:
            # 1. Sales Amount (this will also set Net Amount = Sales Amount initially)
            amount_table.receipt_total_price = total_amount
            
            # 2. Discount Amount (this will recalculate Net Amount = Sales Amount - Discount Amount)
            amount_table.discount_total_amount = discount_amount
            
            # 3. Payment Amount (this will calculate Balance = Net Amount - Payment Amount)
            amount_table.receipt_total_payment = payment_amount
            
            print(f"[SaleService.update_amount_table] Updated totals: sales={total_amount}, discount={discount_amount}, net={total_amount - discount_amount}, payment={payment_amount}")
            
        except Exception as e:
            print(f"[SaleService.update_amount_table] Error updating amount_table: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def update_payment_list_from_document(payment_list, document_data: Dict[str, Any]):
        """
        Update payment_list control with payments from document_data.
        Payments are added in line_no order.
        
        Args:
            payment_list: PaymentList control instance
            document_data: Dictionary containing transaction temp models
        """
        try:
            from data_layer.auto_save import AutoSaveModel
            
            # Clear existing payments
            payment_list.clear_payments()
            
            # Get payments
            payments = document_data.get("payments", [])
            
            # Sort by line_no
            sorted_payments = sorted(payments, key=lambda p: p.line_no if hasattr(p, 'line_no') else 0)
            
            # Add payments to payment_list
            for pay in sorted_payments:
                if isinstance(pay, AutoSaveModel):
                    pay = pay.unwrap()
                
                # Skip canceled payments
                if hasattr(pay, 'is_cancel') and pay.is_cancel:
                    continue
                
                payment_type = pay.payment_type if hasattr(pay, 'payment_type') else ""
                payment_amount = float(pay.payment_total) if hasattr(pay, 'payment_total') else 0.0
                currency_code = pay.currency_code if hasattr(pay, 'currency_code') else ""
                exchange_rate = float(pay.currency_exchange_rate) if hasattr(pay, 'currency_exchange_rate') else 1.0
                payment_id = str(pay.id) if hasattr(pay, 'id') else 0
                
                payment_list.add_payment(
                    payment_type=payment_type,
                    amount=payment_amount,
                    currency=currency_code,
                    rate=exchange_rate,
                    payment_id=payment_id
                )
            
            print(f"[SaleService.update_payment_list] Added {len(sorted_payments)} payments to payment_list")
            
        except Exception as e:
            print(f"[SaleService.update_payment_list] Error updating payment_list: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def update_sale_screen_controls(window, document_data: Dict[str, Any], 
                                   pos_data: Optional[Dict[str, Any]] = None):
        """
        Update all sale screen controls (sale_list, amount_table, payment_list) 
        from document_data when transaction_status is ACTIVE.
        
        This method orchestrates the update of all UI controls for the sale screen.
        It checks if transaction_status is ACTIVE before updating.
        
        Args:
            window: Window instance containing sale_list, amount_table, payment_list controls
            document_data: Dictionary containing transaction temp models (may be wrapped in AutoSaveDict)
            pos_data: Optional POS data cache dictionary (for department names)
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            from data_layer.auto_save import AutoSaveDict, AutoSaveModel
            from data_layer.model.definition.transaction_status import TransactionStatus
            
            # Unwrap if it's an AutoSaveDict
            if isinstance(document_data, AutoSaveDict):
                unwrapped_data = document_data.unwrap()
            else:
                unwrapped_data = document_data
            
            # Get head and check transaction_status
            head = unwrapped_data.get("head")
            if not head:
                print("[SaleService.update_sale_screen_controls] No head found in document_data")
                return False
            
            # Unwrap if it's an AutoSaveModel
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()
            
            # Check transaction_status - only update if ACTIVE
            if head.transaction_status != TransactionStatus.ACTIVE.value:
                print(f"[SaleService.update_sale_screen_controls] Transaction status is '{head.transaction_status}', not ACTIVE. Skipping update.")
                return False
            
            print("[SaleService.update_sale_screen_controls] Updating sale screen controls for ACTIVE transaction...")
            
            # Update sale_list with products and departments
            if hasattr(window, 'sale_list') and window.sale_list:
                SaleService.update_sale_list_from_document(window.sale_list, unwrapped_data, pos_data)
            
            # Update amount_table with totals
            if hasattr(window, 'amount_table') and window.amount_table:
                SaleService.update_amount_table_from_document(window.amount_table, head)
            
            # Update payment_list with payments
            if hasattr(window, 'payment_list') and window.payment_list:
                SaleService.update_payment_list_from_document(window.payment_list, unwrapped_data)
            
            print("[SaleService.update_sale_screen_controls] ✓ Sale screen controls updated successfully")
            return True
            
        except Exception as e:
            print(f"[SaleService.update_sale_screen_controls] Error updating sale screen controls: {e}")
            import traceback
            traceback.print_exc()
            return False

